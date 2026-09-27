"""Slice one model with OrcaSlicer and print a compact path-review JSON report.

G-code, slicer output and intermediate reports live in a temporary directory
that is removed when the command finishes. ``--keep-run`` preserves them.
This command never sends a printer job.
"""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

from inspect_gcode import _is_support, read_paths, summarize

REPO_ROOT = Path(__file__).resolve().parents[4]
PROFILE_DIR = Path(".codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg")
DEFAULTS = {
    "printer": PROFILE_DIR / "qidi-q2c-0.4-nozzle.json",
    "process": PROFILE_DIR / "qidi-q2c-0.20-standard-adaptive-cubic-7.json",
    "filament": PROFILE_DIR / "generic-petg-qidi-q2c-0.4.json",
}
SLICE_TIMEOUT_SECONDS = 600
_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_AREA_POINT = re.compile(rf"^\s*({_NUMBER})x({_NUMBER})\s*$", re.I)


def printer_volume(settings):
    """Read an axis-aligned rectangular volume from Orca's effective settings."""
    area = settings.get("printable_area")
    if not isinstance(area, list) or len(area) != 4:
        raise ValueError("Effective printer profile must define four rectangular printable_area points")
    points = []
    for item in area:
        match = _AREA_POINT.fullmatch(str(item))
        if not match:
            raise ValueError(f"Cannot parse printer printable_area point: {item!r}")
        point = tuple(float(value) for value in match.groups())
        if not all(math.isfinite(value) for value in point):
            raise ValueError("Printer printable_area contains a nonfinite coordinate")
        points.append(point)

    xs = sorted({point[0] for point in points})
    ys = sorted({point[1] for point in points})
    expected_corners = {(x, y) for x in xs for y in ys}
    if len(xs) != 2 or len(ys) != 2 or set(points) != expected_corners:
        raise ValueError("Only axis-aligned rectangular printer printable_area profiles are supported")

    height_value = settings.get("printable_height")
    try:
        height = float(height_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Effective printer profile must define a numeric printable_height") from exc
    if not math.isfinite(height) or height <= 0 or xs[0] >= xs[1] or ys[0] >= ys[1]:
        raise ValueError("Printer profile has invalid printable dimensions")
    return {
        "xy_bounds_mm": [xs[0], ys[0], xs[1], ys[1]],
        "height_mm": height,
        "dimensions_mm": [xs[1] - xs[0], ys[1] - ys[0], height],
    }


def footprint(layers, volume):
    """Bound deposited paths, including half-width, against the printer profile."""
    if not isinstance(volume, dict) or not all(
            key in volume for key in ("xy_bounds_mm", "height_mm")):
        raise ValueError("A printer volume derived from effective settings is required")
    xmin, ymin, xmax, ymax = volume["xy_bounds_mm"]
    height = volume["height_mm"]
    machine = (xmin, ymin, xmax, ymax, height)
    if not all(math.isfinite(value) for value in machine) or xmin >= xmax or ymin >= ymax or height <= 0:
        raise ValueError("Invalid printer volume")

    lo, hi = [float("inf")] * 2, [-float("inf")] * 2
    support_segments = 0
    for paths in layers.values():
        for path in paths:
            support_segments += int(_is_support(path["role"]))
            width = path["width_mm"]
            if not math.isfinite(width) or width <= 0:
                raise ValueError("Invalid extrusion width")
            for point in (path["a"], path["b"]):
                if not all(math.isfinite(value) for value in point):
                    raise ValueError("Nonfinite deposition position")
                lo[0] = min(lo[0], point[0] - width / 2)
                hi[0] = max(hi[0], point[0] + width / 2)
                lo[1] = min(lo[1], point[1] - width / 2)
                hi[1] = max(hi[1], point[1] + width / 2)
    if not layers:
        raise ValueError("No deposited layers found")
    zlo, zhi = min(layers), max(layers)
    fits = (zlo >= 0 and zhi <= height and xmin <= lo[0] <= hi[0] <= xmax
            and ymin <= lo[1] <= hi[1] <= ymax)
    return {
        "xy_bounds_including_half_width_mm": lo + hi,
        "min_layer_z_mm": zlo,
        "max_layer_z_mm": zhi,
        "inside_printer_volume": fits,
        "support_segments": support_segments,
    }


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
            "printable_height", "filament_type", "filament_settings_id",
            "nozzle_temperature", "nozzle_temperature_initial_layer", "hot_plate_temp",
            "hot_plate_temp_initial_layer", "print_settings_id", "layer_height",
            "sparse_infill_density", "sparse_infill_pattern")
    return {key: settings[key] for key in keys if key in settings}


def _log_notices(text):
    return [line.strip() for line in text.splitlines() if re.search(
        r"warning|error|detected print stability|long bridging|loose extrusions|consider enabling supports",
        line, re.I)]


def _review_in_directory(model, profiles, run_dir, expect_no_supports, placement):
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
    version_header = (help_run.stdout + help_run.stderr).splitlines()[:8]
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
        raise RuntimeError("OrcaSlicer CLI failed; use --keep-run to retain the slicer log")
    result = json.loads(result_path.read_text())
    if result.get("return_code") != 0 or not result.get("sliced_plates"):
        raise RuntimeError("OrcaSlicer did not report a completed plate")
    if not effective_path.is_file():
        raise RuntimeError("OrcaSlicer did not export effective printer settings")
    effective = json.loads(effective_path.read_text())
    volume = printer_volume(effective)
    gcode_files = sorted(run_dir.glob("*.gcode"))
    if not gcode_files or any(not path.is_file() or path.stat().st_size == 0 for path in gcode_files):
        raise RuntimeError("OrcaSlicer did not produce fresh nonempty G-code")
    expected_plates = result["sliced_plates"]
    expected_ids = [int(plate["id"]) for plate in expected_plates]
    if len(expected_ids) != len(set(expected_ids)):
        raise RuntimeError(f"OrcaSlicer reported duplicate sliced plate IDs: {expected_ids}")
    gcode_ids = []
    for gcode in gcode_files:
        match = re.search(r"plate[_-]?(\d+)", gcode.stem, re.I)
        if not match:
            raise RuntimeError(f"Cannot match G-code file to an Orca plate ID: {gcode.name}")
        gcode_ids.append(int(match.group(1)))
    if len(gcode_ids) != len(set(gcode_ids)):
        raise RuntimeError(f"OrcaSlicer wrote duplicate G-code plate IDs: {gcode_ids}")
    if set(gcode_ids) != set(expected_ids):
        raise RuntimeError(
            f"OrcaSlicer reported plate IDs {sorted(expected_ids)} "
            f"but wrote G-code for plate IDs {sorted(gcode_ids)}")

    plates, notices = [], _log_notices(log_text)
    for gcode, plate_number in zip(gcode_files, gcode_ids):
        layers, metadata = read_paths(gcode)
        path_summary = summarize(layers, metadata)
        bounds = footprint(layers, volume)
        plates.append({
            "plate": plate_number,
            **bounds,
            "layer_count": path_summary["layer_count"],
            "path_roles": path_summary["roles"],
            "longest_bridge_segments": path_summary["longest_bridge_segments"],
            "metadata": metadata,
        })

    for plate in expected_plates:
        warning = plate.get("warning_message", "").strip()
        if warning:
            notices.append(f"plate {plate.get('id', '?')}: {warning}")
    if result.get("error_string") not in (None, "", "Success", "Success."):
        notices.append(str(result["error_string"]))
    inside = all(plate["inside_printer_volume"] for plate in plates)
    support_segments = sum(plate["support_segments"] for plate in plates)
    report = {
        "model": str(model),
        "profiles": {key: str(path) for key, path in profiles.items()},
        "slicer_help_header": version_header,
        "printer_volume": volume,
        "placement": placement,
        "effective_settings": _settings_summary(effective),
        "plates": plates,
        "inside_printer_volume": inside,
        "support_segments": support_segments,
        "log_notices": notices,
        "review_required": bool(notices) or not inside or (expect_no_supports and support_segments > 0),
        "limits": "Reports Orca's exported paths under the selected profiles. Orientation and arrangement rotation are disabled. Center placement may reposition multiple independent objects; use assembly mode to translate a grouped 3MF layout while retaining its internal positions, or preserve mode for an already positioned project. Bounds include half line width, brim and generated support paths, but exclude travel, start/end machine motion and physical flow spread. Linear ASCII extrusion paths only; role labels and segment lengths do not establish anchors, free-air spans, clearance or physical print quality.",
    }
    return report


def review(model, printer=DEFAULTS["printer"], process=DEFAULTS["process"],
           filament=DEFAULTS["filament"], placement="center",
           expect_no_supports=False, keep_run=False):
    model = Path(model).expanduser().resolve(strict=True)
    profiles = {key: _resolve_profile(value) for key, value in {
        "printer": printer, "process": process, "filament": filament}.items()}
    # Flatpak OrcaSlicer can access the user's home, but may not see host /tmp.
    run_dir = Path(tempfile.mkdtemp(prefix="orca-slicer-review-", dir=Path.home()))
    try:
        report = _review_in_directory(model, profiles, run_dir, expect_no_supports, placement)
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


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=("Printer bounds come from Orca's effective printable_area and printable_height. "
                "The inferred Orca command uses ORCASLICER_COMMAND, then orca-slicer, then Flatpak.")
    )
    parser.add_argument("--model", type=Path, required=True,
                        help="STL or 3MF model to slice")
    parser.add_argument("--printer", type=Path, default=DEFAULTS["printer"],
                        help=f"Orca printer profile (default: {DEFAULTS['printer'].as_posix()})")
    parser.add_argument("--process", type=Path, default=DEFAULTS["process"],
                        help=f"Orca process profile (default: {DEFAULTS['process'].as_posix()})")
    parser.add_argument("--filament", type=Path, default=DEFAULTS["filament"],
                        help=f"Orca filament profile (default: {DEFAULTS['filament'].as_posix()})")
    parser.add_argument("--placement", choices=("preserve", "center", "assembly"), default="center",
                        help="preserve coordinates, center layout, or center a grouped assembly (default: center)")
    parser.add_argument("--expect-no-supports", action="store_true",
                        help="request review if Orca generates any support paths (default: false)")
    parser.add_argument("--keep-run", action="store_true",
                        help="keep temporary G-code and slicer diagnostics (default: false)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        report = review(args.model, args.printer, args.process, args.filament,
                        placement=args.placement,
                        expect_no_supports=args.expect_no_supports,
                        keep_run=args.keep_run)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 2 if report["review_required"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
