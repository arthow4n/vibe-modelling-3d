#!/usr/bin/env -S uv run --locked
"""Evaluate CadQuery and run optional OrcaSlicer reviews from one command.

Run from the repository root with `./evaluate_model.py --help`.
Each invocation builds in a fresh child process. Model code has ordinary user
permissions and may itself write files; process isolation is not a sandbox.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback

VIEWS = {
    "isometric": (1, -1, 1), "isometric_back": (-1, 1, 1),
    "front": (0, -1, 0), "back": (0, 1, 0),
    "left": (-1, 0, 0), "right": (1, 0, 0),
    "top": (0, 0, 1), "bottom": (0, 0, -1),
}
STL_LINEAR_TOLERANCE_MM = 0.003
STL_ANGULAR_TOLERANCE_RAD = 0.5
SLICE_TIMEOUT_SECONDS = 600
REPO_ROOT = Path(__file__).resolve().parent
PROFILE_DIR = Path(".codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg")
DEFAULTS = {
    "printer": PROFILE_DIR / "qidi-q2c-0.4-nozzle.json",
    "process": PROFILE_DIR / "qidi-q2c-0.20-standard-adaptive-cubic-7.json",
    "filament": PROFILE_DIR / "generic-petg-qidi-q2c-0.4.json",
}


def selected_shape(value):
    import cadquery as cq
    shapes = []

    def collect(item):
        if isinstance(item, cq.Workplane):
            for part in item.vals():
                collect(part)
        elif isinstance(item, cq.Assembly):
            collect(item.toCompound())
        elif isinstance(item, cq.Shape):
            if not any(item.isSame(previous) for previous in shapes):
                shapes.append(item)
        elif isinstance(item, (list, tuple)):
            for part in item:
                collect(part)
        elif item is not None:
            raise TypeError(f"Expected a CadQuery shape, Workplane or Assembly; got {type(item).__name__}")

    collect(value)
    if not shapes:
        raise ValueError("No shape produced; assign result or call show_object(shape)")
    return shapes[0] if len(shapes) == 1 else cq.Compound.makeCompound(shapes)


def geometry_data(shape):
    return {"valid": shape.isValid()}


def atomic_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=path.suffix, delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(data)
            file.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def export(shape, item):
    import cadquery as cq
    path = Path(item["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, suffix=path.suffix, delete=False) as file:
        temporary = Path(file.name)
    try:
        if item["format"] == "STL":
            # Orca's GUI STEP import meshes with the same absolute deflection settings.
            if not shape.exportStl(str(temporary), tolerance=STL_LINEAR_TOLERANCE_MM,
                                   angularTolerance=STL_ANGULAR_TOLERANCE_RAD,
                                   relative=False):
                raise RuntimeError("STL export failed")
        else:
            cq.exporters.export(shape, str(temporary), exportType=item["format"])
        temporary.replace(path)
        return {"path": str(path), "ok": True}
    finally:
        temporary.unlink(missing_ok=True)


def view_up(view):
    # Top/bottom look along Z, so Y is their screen-up reference.
    return (0, 1, 0) if view in ("top", "bottom") else (0, 0, 1)


def view_transform(view):
    """Rigid world-to-camera transform; Z stays upright in side/isometric views.

    CadQuery getSVG only accepts a projection direction and gp_Ax2 chooses its
    screen axes implicitly. Project a render-only copy into an explicit frame
    and use getSVG's identity top projection instead of inheriting camera roll.
    """
    import cadquery as cq
    from OCP.gp import gp_Trsf
    direction = cq.Vector(*VIEWS[view]).normalized()
    right = cq.Vector(*view_up(view)).cross(direction).normalized()
    up = direction.cross(right).normalized()
    transform = gp_Trsf()
    transform.SetValues(*[value for axis in (right, up, direction)
                          for value in (*axis.toTuple(), 0)])
    return cq.Matrix(transform)


def render(shape, view, width, height, show_hidden):
    from cadquery.occ_impl.exporters.svg import getSVG
    projected = shape.transformShape(view_transform(view))
    svg = getSVG(projected, opts={"width": width, "height": height,
                                 "projectionDir": (0, 0, 1), "showHidden": show_hidden,
                                 "showAxes": False}).encode("utf-8")
    import cairosvg
    return cairosvg.svg2png(bytestring=svg, output_width=width, output_height=height,
                            background_color="#ffffff")


def worker(request, response):
    import cadquery as cq
    import runpy

    args = json.loads(Path(request).read_text())
    path = Path(args["file_path"])
    root = path.parent
    report = {"ok": False, "file_path": str(path), "errors": [],
              "views": [], "exports": [], "timings_seconds": {},
              "versions": {"python": sys.version.split()[0], "cadquery": cq.__version__}}
    log = io.StringIO()

    def error(stage, exc, **details):
        frames = traceback.extract_tb(exc.__traceback__)
        report["errors"].append({"stage": stage, "type": type(exc).__name__,
                                 "message": str(exc), **details,
                                 "file": getattr(exc, "filename", None) or (frames[-1].filename if frames else None),
                                 "line": getattr(exc, "lineno", None) or (frames[-1].lineno if frames else None),
                                 "traceback": "".join(traceback.format_exception(exc))[-8192:]})

    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        try:
            os.chdir(root)
            sys.path.insert(0, str(root))
            sys.dont_write_bytecode = True
            sys.pycache_prefix = str(Path(response).parent / "pycache")
            outputs = []
            def show_object(obj, *unused, **options):
                outputs.append(obj)
            before = time.monotonic()
            namespace = runpy.run_path(str(path), init_globals={"show_object": show_object}, run_name="__cqgi__")
            report["timings_seconds"]["build"] = time.monotonic() - before
            shape = selected_shape(namespace.get("result") if namespace.get("result") is not None else outputs)
            report["geometry"] = geometry_data(shape)
            if not report["geometry"]["valid"]:
                raise ValueError("Selected geometry is invalid; exports and views skipped")
            for item in args["exports"]:
                try:
                    report["exports"].append(export(shape, item))
                except Exception as exc:
                    report["exports"].append({"path": item["path"], "ok": False})
                    error("export", exc, path=item["path"])
            for view in args["views"]:
                destination = Path(args["output_dir"]) / f'{path.stem}_{view}.png'
                try:
                    data = render(shape, view, args["width"], args["height"],
                                  args["show_hidden"])
                    atomic_bytes(destination, data)
                    report["views"].append({"view": view, "ok": True, "path": str(destination),
                                            "camera": {"from_direction": VIEWS[view],
                                                       "up_direction": view_up(view)}})
                except Exception as exc:
                    report["views"].append({"view": view, "ok": False})
                    error("render", exc, view=view)
        except Exception as exc:
            error("build", exc)
    if report["errors"] and log.getvalue():
        report["diagnostics"] = log.getvalue()[:16384]
    report["ok"] = not report["errors"]
    Path(response).write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["ok"] else 1


def slicer_prefix():
    """Find OrcaSlicer from an explicit environment override or installed app."""
    command = os.environ.get("ORCASLICER_COMMAND")
    if command:
        prefix = shlex.split(command)
    elif shutil.which("orca-slicer"):
        prefix = [shutil.which("orca-slicer")]
    else:
        prefix = ["flatpak", "run", "com.orcaslicer.OrcaSlicer"]
    if not prefix or not shutil.which(prefix[0]):
        raise FileNotFoundError(f"OrcaSlicer command is unavailable: {prefix}")
    return prefix


def _resolve_profile(value):
    path = Path(value).expanduser()
    if not path.is_absolute() and not path.exists() and (REPO_ROOT / path).exists():
        path = REPO_ROOT / path
    return path.resolve(strict=True)


def _settings_summary(settings):
    keys = ("printer_model", "printer_variant", "nozzle_diameter", "printable_area",
            "printable_height", "bed_exclude_area", "filament_type", "filament_settings_id",
            "nozzle_temperature", "nozzle_temperature_initial_layer", "hot_plate_temp",
            "hot_plate_temp_initial_layer", "print_settings_id", "layer_height",
            "wall_loops", "line_width", "outer_wall_line_width", "inner_wall_line_width",
            "initial_layer_line_width", "brim_type", "brim_width", "brim_object_gap",
            "enable_support", "support_type", "support_threshold_angle",
            "bridge_no_support", "max_bridge_length", "filament_flow_ratio", "enable_arc_fitting",
            "sparse_infill_density", "sparse_infill_pattern")
    return {key: settings[key] for key in keys if key in settings}


def _log_notices(text):
    return [line.strip() for line in text.splitlines() if re.search(
        r"warning|error|detected print stability|long bridging|loose extrusions|consider enabling supports",
        line, re.I)]


def _support_roles(run_dir, sliced_plates):
    """Read only Orca's emitted line-type labels, not G-code motion."""
    expected_ids = {int(plate["id"]) for plate in sliced_plates}
    found_ids = set()
    supported = []
    for gcode in sorted(run_dir.glob("*.gcode")):
        match = re.fullmatch(r"plate_(\d+)", gcode.stem)
        if not match:
            raise ValueError(f"Unrecognized Orca G-code plate name: {gcode.name}")
        plate_id = int(match.group(1))
        if plate_id in found_ids:
            raise ValueError(f"Duplicate Orca G-code plate ID: {plate_id}")
        found_ids.add(plate_id)
        roles = set()
        saw_role = False
        with gcode.open(errors="replace") as lines:
            for line in lines:
                if line.startswith(";TYPE:"):
                    saw_role = True
                    role = line.partition(":")[2].strip()
                    if role.casefold().startswith("support"):
                        roles.add(role)
        if not saw_role:
            raise ValueError(f"Orca G-code has no line-type labels: {gcode.name}")
        if roles:
            supported.append({"plate": plate_id, "roles": sorted(roles)})
    if found_ids != expected_ids:
        raise ValueError(f"Orca reported plates {sorted(expected_ids)} but wrote G-code for {sorted(found_ids)}")
    return supported


def _auto_support_probe(command, run_dir, effective, primary_result):
    """Probe the same layout with Orca's automatic support enabled."""
    support_type = str(effective.get("support_type", ""))
    auto_type = (support_type if support_type.endswith("(auto)") else
                 "tree(auto)" if support_type.startswith("tree") else "normal(auto)")
    reuse_primary = (str(effective.get("enable_support", "0")) == "1"
                     and support_type == auto_type
                     and str(effective.get("bridge_no_support", "1")) == "0")
    if reuse_primary:
        probe_dir, probe_effective, probe_result = run_dir, effective, primary_result
    else:
        probe_dir = run_dir / "support_probe"
        probe_dir.mkdir()
        probe_command = command.copy()
        probe_command[probe_command.index("--outputdir") + 1] = str(probe_dir)
        effective_path = probe_dir / "effective-settings.json"
        probe_command[probe_command.index("--export-settings") + 1] = str(effective_path)
        probe_command.extend(("--enable-support=1", "--bridge-no-support=0",
                              f"--support-type={auto_type}"))
        (probe_dir / "command.json").write_text(json.dumps(probe_command, indent=2) + "\n")
        with (probe_dir / "slicer.log").open("w") as log:
            completed = subprocess.run(probe_command, cwd=probe_dir, stdout=log,
                                       stderr=subprocess.STDOUT, timeout=SLICE_TIMEOUT_SECONDS,
                                       check=False)
        result_path = probe_dir / "result.json"
        if completed.returncode != 0 or not result_path.is_file():
            raise RuntimeError("Orca automatic-support probe failed; use --slice-keep-run for its log")
        probe_result = json.loads(result_path.read_text())
        if probe_result.get("return_code") != 0 or not probe_result.get("sliced_plates"):
            raise RuntimeError("Orca automatic-support probe did not complete a plate")
        if not effective_path.is_file():
            raise RuntimeError("Orca automatic-support probe did not export effective settings")
        probe_effective = json.loads(effective_path.read_text())
    if (str(probe_effective.get("enable_support")) != "1"
            or not str(probe_effective.get("support_type", "")).endswith("(auto)")
            or str(probe_effective.get("bridge_no_support")) != "0"):
        raise RuntimeError("Orca did not apply automatic-support probe settings")
    supported = _support_roles(probe_dir, probe_result["sliced_plates"])
    return {
        "ok": True,
        "generated": bool(supported),
        "supported_plates": supported,
        "effective_support_type": probe_effective["support_type"],
        "effective_support_threshold_angle": probe_effective.get("support_threshold_angle"),
        "effective_max_bridge_length_mm": probe_effective.get("max_bridge_length"),
    }


def _review_in_directory(model, profiles, run_dir, placement):
    placement_args = {
        "preserve": ["--arrange", "0", "--orient", "0"],
        "center": ["--arrange", "1", "--orient", "0", "--allow-rotations=0"],
        "assembly": ["--assemble", "--arrange", "1", "--orient", "0", "--allow-rotations=0"],
    }
    if placement not in placement_args:
        raise ValueError("placement must be preserve, center or assembly")
    prefix = slicer_prefix()

    # Keep Orca's incidental CLI files and app data inside this temporary run.
    help_run = subprocess.run(prefix + ["--help"], cwd=run_dir, capture_output=True,
                              text=True, timeout=30, check=False)
    version_match = re.search(
        r"(?i)orcaslicer[^\n]{0,80}?\b(v?\d+\.\d+(?:\.\d+)?(?:[-+][\w.]+)?)",
        help_run.stdout + help_run.stderr)
    slicer_version = version_match.group(1) if version_match else "unknown"
    effective_path = run_dir / "effective-settings.json"
    command = prefix + [str(model),
        "--load-settings", f"{profiles['process']};{profiles['printer']}",
        "--load-filaments", str(profiles["filament"]),
        *placement_args[placement], "--slice", "0",
        "--outputdir", str(run_dir), "--export-settings", str(effective_path)]
    (run_dir / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    with (run_dir / "slicer.log").open("w") as log:
        completed = subprocess.run(command, cwd=run_dir, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=SLICE_TIMEOUT_SECONDS, check=False)
    log_text = (run_dir / "slicer.log").read_text(errors="replace")

    result_path = run_dir / "result.json"
    if completed.returncode != 0 or not result_path.is_file():
        raise RuntimeError("OrcaSlicer CLI failed; use --slice-keep-run to retain the slicer log")
    result = json.loads(result_path.read_text())
    if result.get("return_code") != 0 or not result.get("sliced_plates"):
        raise RuntimeError("OrcaSlicer did not report a completed plate")
    if not effective_path.is_file():
        raise RuntimeError("OrcaSlicer did not export effective printer settings")
    effective = json.loads(effective_path.read_text())
    notices = _log_notices(log_text)
    for plate in result["sliced_plates"]:
        warning = plate.get("warning_message", "").strip()
        if warning:
            notices.append(f"plate {plate.get('id', '?')}: {warning}")
    if result.get("error_string") not in (None, "", "Success", "Success."):
        notices.append(str(result["error_string"]))
    try:
        support_probe = _auto_support_probe(command, run_dir, effective, result)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        support_probe = {"ok": False, "message": str(exc)}
    report = {
        "model": str(model),
        "profiles": {key: str(path) for key, path in profiles.items()},
        "slicer_version": slicer_version,
        "placement": placement,
        "effective_settings": _settings_summary(effective),
        "sliced_plates": [plate.get("id") for plate in result["sliced_plates"]],
        "support_probe": support_probe,
        "log_notices": notices,
        "review_required": bool(notices) or not support_probe["ok"] or support_probe.get("generated", False),
    }
    return report


def review(model, printer=DEFAULTS["printer"], process=DEFAULTS["process"],
           filament=DEFAULTS["filament"], placement="center", keep_run=False):
    model = Path(model).expanduser().resolve(strict=True)
    profiles = {key: _resolve_profile(value) for key, value in {
        "printer": printer, "process": process, "filament": filament}.items()}
    # Flatpak OrcaSlicer can access the user's home, but may not see host /tmp.
    run_dir = Path(tempfile.mkdtemp(prefix="orca-slicer-review-", dir=Path.home()))
    try:
        report = _review_in_directory(model, profiles, run_dir, placement)
        if keep_run:
            report["kept_run_directory"] = str(run_dir)
            (run_dir / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
        return report
    except Exception as exc:
        if keep_run:
            raise RuntimeError(f"{exc}; run artifacts kept at {run_dir}") from exc
        raise
    finally:
        if not keep_run:
            shutil.rmtree(run_dir, ignore_errors=True)


def positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Expected a finite positive number")
    return number


def positive_pixel(value):
    number = int(value)
    if not 1 <= number <= 4096:
        raise argparse.ArgumentTypeError("Expected an integer from 1 to 4096")
    return number


def add_slice_review(report, model, args):
    before = time.monotonic()
    try:
        sliced = review(model,
                        printer=args.slice_printer or DEFAULTS["printer"],
                        process=args.slice_process or DEFAULTS["process"],
                        filament=args.slice_filament or DEFAULTS["filament"],
                        placement=args.slice_placement,
                        keep_run=args.slice_keep_run)
        report["slice"] = {"ok": True, **sliced}
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report["slice"] = {"ok": False, "message": str(exc)}
        report["errors"].append({"stage": "slice", "message": str(exc)})
        report["ok"] = False
    report.setdefault("timings_seconds", {})["slice"] = time.monotonic() - before


def emit_report(report, args):
    """Retain native evidence and optionally shorten console output, without rerunning stages."""
    if args.report:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            # A failed write must not truncate an earlier useful report.
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.report.parent,
                                             delete=False) as saved:
                temporary = Path(saved.name)
                try:
                    saved.write(json.dumps(report, indent=2) + "\n")
                    saved.close()
                    temporary.replace(args.report)
                finally:
                    temporary.unlink(missing_ok=True)
        except OSError as exc:
            report["ok"] = False
            report.setdefault("errors", []).append({"stage": "report", "message": str(exc)})
    output = report
    if args.summary:
        output = {key: report[key] for key in
                  ("ok", "file_path", "geometry", "views", "exports", "errors",
                   "timings_seconds", "versions", "diagnostics") if key in report}
        if "slice" in report:
            output["slice"] = {key: report["slice"][key] for key in
                               ("ok", "message", "review_required", "support_probe", "log_notices")
                               if key in report["slice"]}
        if not any(error.get("stage") == "report" for error in report.get("errors", [])):
            output["report_path"] = str(args.report)
    print(json.dumps(output, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=f"{__doc__}\nFor valid evaluations, stdout always contains one JSON object. "
                    "Model, view, and export paths in the report are absolute.\n"
                    f"STL exports use {STL_LINEAR_TOLERANCE_MM} mm absolute linear and "
                    f"{STL_ANGULAR_TOLERANCE_RAD} rad angular tessellation tolerances.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file_path", type=Path, nargs="?", help="Trusted CadQuery Python entry point")
    parser.add_argument("--views", default="isometric,front,top,right",
                        help=f"Comma-separated views from {', '.join(VIEWS)}, or none; "
                             "Z is upright except top/bottom, which use Y upright")
    parser.add_argument("--output-dir", default="renders/scratch",
                        help="Render output directory, relative to the model file")
    parser.add_argument("--width", type=positive_pixel, default=800,
                        help="Rendered image width in pixels (1–4096)")
    parser.add_argument("--height", type=positive_pixel, default=600,
                        help="Rendered image height in pixels (1–4096)")
    parser.add_argument("--show-hidden", action="store_true",
                        help="Include hidden edges in rendered views")
    parser.add_argument("--export", action="store_true",
                        help="Export matching STEP and STL beside the source, using its stem")
    parser.add_argument("--slice", action="store_true",
                        help="Export the pair, smoke-slice its STL and probe Orca automatic supports")
    parser.add_argument("--slice-existing", type=Path, metavar="STL_OR_3MF",
                        help="Review an existing STL or 3MF without rebuilding CAD")
    parser.add_argument("--slice-printer", type=Path,
                        help=f"Orca printer profile (default: {DEFAULTS['printer']})")
    parser.add_argument("--slice-process", type=Path,
                        help=f"Orca process profile (default: {DEFAULTS['process']})")
    parser.add_argument("--slice-filament", type=Path,
                        help=f"Orca filament profile (default: {DEFAULTS['filament']})")
    parser.add_argument("--slice-placement", choices=("preserve", "center", "assembly"),
                        default="center", help="Orca placement for --slice or --slice-existing")
    parser.add_argument("--slice-keep-run", action="store_true",
                        help="Keep Orca diagnostics and G-code for a slice review")
    parser.add_argument("--timeout", type=positive_float, default=300,
                        help="Maximum evaluation time in seconds")
    parser.add_argument("--report", type=Path, metavar="JSON",
                        help="Also save the complete native report; path relative to the current directory, "
                             "parent directories created, existing report replaced")
    parser.add_argument("--summary", action="store_true",
                        help="With --report, print a compact stage summary instead of the complete report")
    args = parser.parse_args(argv)
    if args.summary and not args.report:
        parser.error("--summary requires --report so complete evidence is retained")
    if args.report:
        args.report = args.report.resolve()
        if args.report.suffix.lower() != ".json":
            parser.error("--report must use a .json path")
        protected = [args.file_path, args.slice_existing]
        for key, default in DEFAULTS.items():
            value = getattr(args, f"slice_{key}") or default
            try:
                protected.append(_resolve_profile(value))
            except OSError:
                protected.append(Path(value).expanduser().resolve())
        if any(path and args.report == path.resolve() for path in protected):
            parser.error("Report path must be distinct from model input and slice profiles")
    if args.slice_existing and (args.file_path or args.slice or args.export):
        parser.error("--slice-existing takes an STL or 3MF instead of a CAD source or --slice/--export")
    if args.slice_existing and (args.views != "isometric,front,top,right"
                                or args.output_dir != "renders/scratch" or args.show_hidden
                                or args.width != 800 or args.height != 600):
        parser.error("CAD view options cannot be used with --slice-existing")
    if not args.slice_existing and not args.file_path:
        parser.error("Provide a CadQuery source or --slice-existing STL_OR_3MF")
    if not (args.slice or args.slice_existing) and any((args.slice_printer, args.slice_process,
                                                       args.slice_filament, args.slice_keep_run,
                                                       args.slice_placement != "center")):
        parser.error("Slice settings require --slice or --slice-existing")
    if args.slice_existing:
        existing = args.slice_existing.resolve()
        if not existing.is_file() or existing.suffix.lower() not in (".stl", ".3mf"):
            parser.error(f"Existing slice input must be an STL or 3MF file: {existing}")
        started = time.monotonic()
        report = {"ok": True, "file_path": str(existing), "errors": [],
                  "views": [], "exports": [], "timings_seconds": {}}
        add_slice_review(report, existing, args)
        report["timings_seconds"]["total"] = time.monotonic() - started
        emit_report(report, args)
        if not report["ok"]:
            return 1
        return 2 if report["slice"]["review_required"] else 0
    source = args.file_path.resolve()
    if not source.is_file():
        parser.error(f"Model source does not exist: {source}")
    views = [] if args.views == "none" else args.views.split(",")
    if len(views) != len(set(views)) or any(view not in VIEWS for view in views):
        parser.error(f"Views must be distinct names from {', '.join(VIEWS)}, or none")
    root = source.parent
    output_dir = (root / args.output_dir).resolve()
    exports = []
    paths = {source}
    if args.export or args.slice:
        for name, suffix in (("STEP", ".step"), ("STL", ".stl")):
            path = root / f"{source.stem}{suffix}"
            if path in paths:
                parser.error(f"{name} output path must be distinct from the source")
            paths.add(path)
            exports.append({"path": str(path), "format": name})
    destinations = {output_dir / f"{source.stem}_{view}.png" for view in views}
    if source in destinations or paths & destinations:
        parser.error("Source, view and export paths must be distinct")
    request = {"file_path": str(source), "views": views, "output_dir": str(output_dir),
               "width": args.width, "height": args.height,
               "show_hidden": args.show_hidden, "exports": exports}
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="cadquery-evaluate-") as directory:
        request_file, response_file = Path(directory) / "request.json", Path(directory) / "response.json"
        request_file.write_text(json.dumps(request))
        process = subprocess.Popen([sys.executable, __file__, "--worker", str(request_file), str(response_file)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   start_new_session=(os.name == "posix"))
        try:
            returncode = process.wait(timeout=args.timeout)
        except subprocess.TimeoutExpired:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()
            report = {"ok": False, "file_path": str(source), "errors": [{"stage": "timeout",
                "message": f"Evaluation exceeded {args.timeout} seconds; model side effects may remain"}]}
        else:
            if not response_file.exists():
                report = {"ok": False, "file_path": str(source), "errors": [{"stage": "worker",
                    "message": f"Worker exited {returncode} without a report"}]}
            else:
                report = json.loads(response_file.read_text())
                if returncode and report.get("ok"):
                    report["ok"] = False
                    report["errors"].append({"stage": "worker", "message": f"Worker exited {returncode}"})
    report.setdefault("timings_seconds", {})["total"] = time.monotonic() - started
    pair_ready = (len(report.get("exports", [])) == 2
                  and all(item.get("ok") for item in report["exports"]))
    if args.slice and pair_ready:
        add_slice_review(report, root / f"{source.stem}.stl", args)
        report["timings_seconds"]["total"] = time.monotonic() - started
    emit_report(report, args)
    if not report["ok"]:
        return 1
    return 2 if args.slice and pair_ready and report["slice"]["review_required"] else 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        sys.exit(worker(sys.argv[2], sys.argv[3]))
    sys.exit(main())
