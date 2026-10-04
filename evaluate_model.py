#!/usr/bin/env python3
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

if __name__=='__main__':
    from execution.bootstrap import ensure
    ensure()

from execution.telemetry import operation, span, child_environment
from execution.process import run as run_command
from execution.resources import DEFAULT_MEMORY_MB

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


@operation("cad.validation")
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


@operation("cad.export")
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


@operation("cad.render")
def render(shape, view, width, height, show_hidden):
    from cadquery.occ_impl.exporters.svg import getSVG
    projected = shape.transformShape(view_transform(view))
    svg = getSVG(projected, opts={"width": width, "height": height,
                                 "projectionDir": (0, 0, 1), "showHidden": show_hidden,
                                 "showAxes": False}).encode("utf-8")
    import cairosvg
    return cairosvg.svg2png(bytestring=svg, output_width=width, output_height=height,
                            background_color="#ffffff")


def evaluate_request(args, cache=None, progress=None):
    dependency_started=time.monotonic()
    import cadquery as cq
    import runpy
    from execution.artifacts import ArtifactCache
    from execution.identity import digest, fingerprint
    artifacts=ArtifactCache("cad")
    path = Path(args["file_path"])
    root = path.parent
    report = {"ok": False, "file_path": str(path), "errors": [],
              "views": [], "exports": [], "timings_seconds": {},
              "versions": {"python": sys.version.split()[0], "cadquery": cq.__version__}}
    report["timings_seconds"]["dependency_initialization"] = time.monotonic()-dependency_started
    log = io.StringIO()

    def error(stage, exc, **details):
        frames = traceback.extract_tb(exc.__traceback__)
        report["errors"].append({"stage": stage, "type": type(exc).__name__,
                                 "message": str(exc), **details,
                                 "file": getattr(exc, "filename", None) or (frames[-1].filename if frames else None),
                                 "line": getattr(exc, "lineno", None) or (frames[-1].lineno if frames else None),
                                 "traceback": "".join(traceback.format_exception(exc))[-8192:]})

    previous_cwd=Path.cwd();previous_path=sys.path.copy()
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        try:
            os.chdir(root)
            sys.path.insert(0, str(root))
            from execution.source import install
            install(path)
            outputs = []
            def show_object(obj, *unused, **options):
                outputs.append(obj)
            before = time.monotonic()
            identity=args.get("identity")
            reused=cache is not None and cache.get("identity")==identity
            if reused:
                shape=cache["shape"]
                report["geometry"]=cache["geometry"].copy()
                report["reuse"]={"geometry":True,"identity":identity,
                    "origin_build_seconds":cache["build_seconds"]}
                report["timings_seconds"]["build"]=0.0
            else:
                with span("cad.construction"):
                    namespace = runpy.run_path(str(path), init_globals={"show_object": show_object}, run_name="__cqgi__")
                report["timings_seconds"]["build"] = time.monotonic() - before
                before=time.monotonic()
                with span("cad.selection"):
                    shape = selected_shape(namespace.get("result") if namespace.get("result") is not None else outputs)
                report["timings_seconds"]["selection"]=time.monotonic()-before
                before=time.monotonic()
                report["geometry"] = geometry_data(shape)
                report["timings_seconds"]["validation"]=time.monotonic()-before
                report["reuse"]={"geometry":False,"identity":identity}
                if cache is not None and report["geometry"]["valid"]:
                    cache.clear()
                    cache.update(identity=identity,shape=shape,geometry=report["geometry"].copy(),
                        build_seconds=report["timings_seconds"]["build"])
            if not report["geometry"]["valid"]:
                raise ValueError("Selected geometry is invalid; exports and views skipped")
            artifact_identity=None
            if reused:artifact_identity=cache.get('artifact_identity')
            if (args['exports'] or args['views']) and artifact_identity is None:
                # Identify actual geometry, including dynamic script inputs, after validation.
                # Exclude triangulations added by previous exports from this identity.
                from OCP.BRepTools import BRepTools
                from OCP.TopTools import TopTools_FormatVersion
                import hashlib
                with span('cad.artifact_identity'):
                    serialized=io.BytesIO()
                    BRepTools.Write_s(shape.wrapped,serialized,False,False,TopTools_FormatVersion.TopTools_FormatVersion_VERSION_3)
                    artifact_identity=fingerprint({'brep':hashlib.sha256(serialized.getvalue()).hexdigest(),
                        'runtime':args.get('runtime'),'implementation':digest(__file__)})
                if cache is not None:cache['artifact_identity']=artifact_identity
            if artifact_identity:
                report['reuse']['artifact_identity']=artifact_identity
            for item in args["exports"]:
                try:
                    before=time.monotonic()
                    key={"identity":artifact_identity,"format":item["format"],"linear":STL_LINEAR_TOLERANCE_MM,
                         "angular":STL_ANGULAR_TOLERANCE_RAD}
                    data=artifacts.read(key) if not args.get('fresh') else None
                    if data is not None:
                        atomic_bytes(Path(item["path"]),data)
                        status={"path":item["path"],"ok":True,"reused":True}
                    else:
                        status={**export(shape,item),"reused":False}
                        if not args.get('fresh'):artifacts.store(key,Path(item["path"]).read_bytes())
                    report["exports"].append(status)
                    report["timings_seconds"]["export_"+item["format"].lower()]=time.monotonic()-before
                except Exception as exc:
                    report["exports"].append({"path": item["path"], "ok": False})
                    error("export", exc, path=item["path"])
            if progress and report['exports'] and all(e['ok'] for e in report['exports']):
                progress({'event':'exports_ready','exports':report['exports']})
            for view in args["views"]:
                destination = Path(args["output_dir"]) / f'{path.stem}_{view}.png'
                try:
                    before=time.monotonic()
                    key={"identity":artifact_identity,"view":view,"width":args["width"],"height":args["height"],
                         "hidden":args["show_hidden"]}
                    data=artifacts.read(key) if not args.get('fresh') else None
                    reused_view=data is not None
                    if data is None:
                        data = render(shape, view, args["width"], args["height"], args["show_hidden"])
                        if not args.get('fresh'):artifacts.store(key,data)
                    report["timings_seconds"]["render_"+view]=time.monotonic()-before
                    atomic_bytes(destination, data)
                    report["views"].append({"view": view, "ok": True, "path": str(destination), "reused":reused_view,
                                            "camera": {"from_direction": VIEWS[view],
                                                       "up_direction": view_up(view)}})
                except Exception as exc:
                    report["views"].append({"view": view, "ok": False})
                    error("render", exc, view=view)
        except Exception as exc:
            error("build", exc)
    os.chdir(previous_cwd);sys.path[:]=previous_path
    if report["errors"] and log.getvalue():
        report["diagnostics"] = log.getvalue()[:16384]
    report["ok"] = not report["errors"]
    return report


def worker(request, response):
    args=json.loads(Path(request).read_text())
    from execution.resources import apply_affinity
    from execution.lifecycle import watch_owner
    apply_affinity();watch_owner()
    from threadpoolctl import threadpool_limits
    from OCP.OSD import OSD_ThreadPool
    threads=int(os.environ.get('ENGINEERING_THREADS','1'))
    OSD_ThreadPool.DefaultPool_s(threads).Init(threads)
    with threadpool_limits(limits=threads):report=evaluate_request(args)
    Path(response).write_text(json.dumps(report,indent=2)+"\n")
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


def _auto_support_probe(command, run_dir, effective, primary_result, prepared=False):
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
        probe_dir.mkdir(exist_ok=True)
        probe_command = command.copy()
        probe_command[probe_command.index("--outputdir") + 1] = str(probe_dir)
        effective_path = probe_dir / "effective-settings.json"
        probe_command[probe_command.index("--export-settings") + 1] = str(effective_path)
        probe_command.extend(("--enable-support=1", "--bridge-no-support=0",
                              f"--support-type={auto_type}"))
        (probe_dir / "command.json").write_text(json.dumps(probe_command, indent=2) + "\n")
        if not prepared:
            with (probe_dir / "slicer.log").open("w") as log:
                completed = run_command(probe_command, cwd=probe_dir, stdout=log,
                                           stderr=subprocess.STDOUT, timeout=SLICE_TIMEOUT_SECONDS,
                                           check=False)
        else:
            completed=prepared.result()
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


def _review_in_directory(model, profiles, run_dir, placement, threads=None):
    placement_args = {
        "preserve": ["--arrange", "0", "--orient", "0"],
        "center": ["--arrange", "1", "--orient", "0", "--allow-rotations=0"],
        "assembly": ["--assemble", "--arrange", "1", "--orient", "0", "--allow-rotations=0"],
    }
    if placement not in placement_args:
        raise ValueError("placement must be preserve, center or assembly")
    prefix = slicer_prefix()

    from execution.tools import version
    from execution.resources import inherited_budget, cores, cpu_capacity
    threads=threads or inherited_budget() or cores("50%",cpu_capacity())
    def discover_version():
        help_run = run_command(prefix + ["--help"], cwd=run_dir, capture_output=True,
                                  text=True, timeout=30, check=False)
        match = re.search(r"(?i)orcaslicer[^\n]{0,80}?\b(v?\d+\.\d+(?:\.\d+)?(?:[-+][\w.]+)?)",help_run.stdout+help_run.stderr)
        return match.group(1) if match else "unknown"
    slicer_version=version(prefix,run_dir,discover_version)
    effective_path = run_dir / "effective-settings.json"
    command = prefix + [str(model),
        "--load-settings", f"{profiles['process']};{profiles['printer']}",
        "--load-filaments", str(profiles["filament"]),
        *placement_args[placement], "--slice", "0",
        "--outputdir", str(run_dir), "--export-settings", str(effective_path)]
    (run_dir / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    from concurrent.futures import ThreadPoolExecutor
    from execution.telemetry import child_environment
    from execution.resources import thread_environment, partition
    # Loaded support flags are explicit in maintained resolved snapshots. Predict
    # only these flags, and verify the real exported settings before trusting probe.
    process_settings=json.loads(profiles['process'].read_text())
    support_keys=("enable_support","support_type","bridge_no_support")
    known=all(k in process_settings for k in support_keys)
    primary_auto=(str(process_settings.get("enable_support"))=="1" and
        str(process_settings.get("support_type","")).endswith("(auto)") and
        str(process_settings.get("bridge_no_support"))=="0")
    prepared=None
    executor=ThreadPoolExecutor(1)
    def probe_early():
        with span("orca.support_probe"),partition(threads//2,threads-threads//2):
            probe_dir=run_dir/'support_probe';probe_dir.mkdir(exist_ok=True)
            cmd=command.copy();cmd[cmd.index('--outputdir')+1]=str(probe_dir)
            cmd[cmd.index('--export-settings')+1]=str(probe_dir/'effective-settings.json')
            kind=str(process_settings['support_type'])
            auto_type=kind if kind.endswith('(auto)') else 'tree(auto)' if kind.startswith('tree') else 'normal(auto)'
            cmd.extend(('--enable-support=1','--bridge-no-support=0',f'--support-type={auto_type}'))
            (probe_dir/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
            with (probe_dir/'slicer.log').open('w') as log:
                return run_command(cmd,cwd=probe_dir,stdout=log,stderr=subprocess.STDOUT,
                    timeout=SLICE_TIMEOUT_SECONDS,check=False,
                    env=thread_environment(child_environment(),threads-threads//2))
    if known and not primary_auto and threads>=2:
        import contextvars
        context=contextvars.copy_context()
        prepared=executor.submit(context.run,probe_early)
    try:
        with span("orca.primary"),partition(0,threads//2 if prepared else threads), (run_dir / "slicer.log").open("w") as log:
            completed = run_command(command, cwd=run_dir, stdout=log, stderr=subprocess.STDOUT,
                                       timeout=SLICE_TIMEOUT_SECONDS, check=False,
                                       env=thread_environment(child_environment(),max(1,threads//2) if prepared else threads))
    finally:
        executor.shutdown(wait=True,cancel_futures=True)
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
        expected={k:str(process_settings[k]) for k in support_keys} if known else {}
        actual={k:str(effective.get(k)) for k in support_keys}
        if prepared and expected!=actual:
            raise RuntimeError("Effective support settings differ from the concurrent probe prediction; review the probe")
        support_probe = _auto_support_probe(command, run_dir, effective, result, prepared=prepared)
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


@operation("orca.review")
def review(model, printer=DEFAULTS["printer"], process=DEFAULTS["process"],
           filament=DEFAULTS["filament"], placement="center", keep_run=False, reuse=True, threads=None):
    model = Path(model).expanduser().resolve(strict=True)
    profiles = {key: _resolve_profile(value) for key, value in {
        "printer": printer, "process": process, "filament": filament}.items()}
    from execution.resources import lease
    from execution.tools import tool_identity
    from execution.identity import digest, fingerprint
    from execution.artifacts import ArtifactCache, destinations
    cache=ArtifactCache("slices")
    identity=tool_identity(slicer_prefix()) if reuse and not keep_run else None
    key={"model":digest(model),"profiles":{k:digest(p) for k,p in profiles.items()},
         "placement":placement,"tool":identity,"threads":threads,"implementation":digest(__file__)}
    ownership=destinations([cache.folder/fingerprint(key)]) if identity else contextlib.nullcontext()
    with ownership:
        if identity:
            saved=cache.read(key)
            if saved is not None:
                report=json.loads(saved);report.update(reused=True,identity=fingerprint(key),input_sha256=key['model'],model=str(model),
                    profiles={k:str(p) for k,p in profiles.items()})
                return report
        # Flatpak OrcaSlicer can access the user's home, but may not see host /tmp.
        run_dir = Path(tempfile.mkdtemp(prefix="orca-slicer-review-", dir=Path.home()))
        try:
            snapshot=run_dir/('input'+model.suffix)
            snapshot.write_bytes(model.read_bytes())
            snapshot_profiles={k:run_dir/(k+'.json') for k in profiles}
            for k,p in profiles.items():snapshot_profiles[k].write_bytes(p.read_bytes())
            snapshot_key={**key,'model':digest(snapshot),'profiles':{k:digest(p) for k,p in snapshot_profiles.items()}}
            if snapshot_key!=key:raise RuntimeError('Slice inputs changed during snapshot; retry current inputs')
            with lease(threads) as budget:
                report = _review_in_directory(snapshot, snapshot_profiles, run_dir, placement,budget)
            report.update(model=str(model),profiles={k:str(p) for k,p in profiles.items()})
            report.update(reused=False,identity=fingerprint(key),input_sha256=key['model'])
            if identity and report["support_probe"]["ok"] and tool_identity(slicer_prefix())==identity:
                cache.store(key,json.dumps(report).encode())
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
                        keep_run=args.slice_keep_run,reuse=not args.fresh,threads=args.threads)
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
            from execution.artifacts import destinations
            from execution.identity import cad_identity, digest
            with destinations([args.report]):
                publication=getattr(args,'_publication',None)
                if publication and cad_identity(*publication[:2],environment=publication[2])!=publication[3]:
                    raise RuntimeError('CAD inputs changed before report publication; previous report preserved')
                existing=getattr(args,'slice_existing',None)
                expected=report.get('slice',{}).get('input_sha256')
                if existing and expected and digest(existing)!=expected:
                    raise RuntimeError('Slice input changed before report publication; previous report preserved')
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
        except (OSError,RuntimeError) as exc:
            report["ok"] = False
            report.setdefault("errors", []).append({"stage": "report", "message": str(exc)})
    output = report
    if args.summary:
        output = {key: report[key] for key in
                  ("ok", "file_path", "geometry", "views", "exports", "errors",
                   "timings_seconds", "versions", "diagnostics", "reuse") if key in report}
        if "slice" in report:
            output["slice"] = {key: report["slice"][key] for key in
                               ("ok", "message", "review_required", "support_probe", "log_notices", "reused", "identity")
                               if key in report["slice"]}
        if not any(error.get("stage") == "report" for error in report.get("errors", [])):
            output["report_path"] = str(args.report)
    print(json.dumps(output, indent=2))


@operation("cad.command")
def main(argv=None):
    parser = argparse.ArgumentParser(
        description=f"{__doc__}\nFor valid evaluations, stdout always contains one JSON object. "
                    "Model, view, and export paths in the report are absolute.\n"
                    f"STL exports use {STL_LINEAR_TOLERANCE_MM} mm absolute linear and "
                    f"{STL_ANGULAR_TOLERANCE_RAD} rad angular tessellation tolerances.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file_path", type=Path, nargs="?", help="Trusted CadQuery Python entry point")
    parser.add_argument("--views", default="none",
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
    parser.add_argument("--reuse",action="store_true",help="Declare deterministic construction with closed inputs; reuse unchanged geometry")
    parser.add_argument("--fresh",action="store_true",help="Recompute controlled artifacts and ignore geometry reuse declarations")
    parser.add_argument("--dependency",type=Path,action="append",default=[],help="Additional input file/directory for --reuse and revision guards")
    parser.add_argument("--isolated",action="store_true",help="Use conventional CAD process instead of warm infrastructure")
    parser.add_argument("--threads",default="50%",help="Native CPU budget: integer or percent of shared capacity")
    parser.add_argument("--memory-mb",type=int,help=f"CAD worker memory/admission budget (default {DEFAULT_MEMORY_MB} MiB, or declared geometry-only budget)")
    parser.add_argument("--timeout", type=positive_float, default=300,
                        help="Maximum evaluation time in seconds")
    parser.add_argument("--report", type=Path, metavar="JSON",
                        help="Also save the complete native report; path relative to the current directory, "
                             "parent directories created, existing report replaced")
    parser.add_argument("--summary", action="store_true",
                        help="With --report, print a compact stage summary instead of the complete report")
    args = parser.parse_args(argv)
    from execution.resources import cores,cpu_capacity
    try:args.threads=cores(args.threads,cpu_capacity())
    except ValueError as exc:parser.error(str(exc))
    if args.memory_mb is not None and args.memory_mb<1:parser.error('Memory budget must be positive')
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
    if args.slice_existing and (args.views != "none"
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
    declaration=source.with_suffix('.execution.json')
    geometry_memory=None
    if declaration.exists():
        try:
            contract=json.loads(declaration.read_text())
            if contract.get('schema_version')!=1 or not isinstance(contract.get('deterministic'),bool):
                raise ValueError('Expected schema_version 1 and boolean deterministic')
            inputs=contract.get('inputs',[])
            if not isinstance(inputs,list) or any(not isinstance(p,str) for p in inputs):
                raise ValueError('inputs must be a list of file/directory paths')
            resources=contract.get('resources',{})
            if not isinstance(resources,dict):raise ValueError('resources must be an object')
            geometry_memory=resources.get('geometry_memory_mb')
            if geometry_memory is not None and (type(geometry_memory) is not int or geometry_memory<1):
                raise ValueError('geometry_memory_mb must be a positive integer')
            args.dependency += [declaration,*[source.parent/p for p in inputs]]
            args.reuse |= contract['deterministic']
        except (ValueError,OSError) as exc:parser.error(f'Invalid execution declaration: {exc}')
    if args.fresh:args.reuse=False
    views = [] if args.views == "none" else args.views.split(",")
    if args.memory_mb is None:
        args.memory_mb=geometry_memory if geometry_memory and not views and not (args.export or args.slice) else DEFAULT_MEMORY_MB
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
               "show_hidden": args.show_hidden, "exports": exports,"fresh":args.fresh}
    from execution.identity import cad_identity, digest, runtime_identity
    from execution.cad import execute as execute_cad
    from execution.telemetry import child_environment, _active
    from execution.resources import thread_environment
    execution_environment=thread_environment(child_environment(),args.threads)
    identity=cad_identity(source,args.dependency,execution_environment)
    args._publication=(source,args.dependency,execution_environment,identity)
    request.update(identity=identity,run_id=_active.get(),runtime=runtime_identity())
    started = time.monotonic()
    from concurrent.futures import ThreadPoolExecutor
    slice_executor=ThreadPoolExecutor(1) if args.slice and views else None
    slice_temporary=tempfile.TemporaryDirectory(prefix='engineering-slice-input-',dir=Path.home()) if slice_executor else None
    slice_future=None
    import threading
    from execution.lifecycle import _cancellation
    slice_cancelled=threading.Event()
    cancellation_token=_cancellation.set(slice_cancelled.is_set)
    def exports_ready(event):
        nonlocal slice_future
        if not slice_executor or slice_future is not None:return
        entry=next((e for e in event['exports'] if e['path'].endswith('.stl') and e['ok']),None)
        if not entry:return
        snapshot=Path(slice_temporary.name)/'input.stl';snapshot.write_bytes(Path(entry['path']).read_bytes())
        slice_report={'ok':True,'errors':[]}
        import contextvars
        context=contextvars.copy_context()
        def slice_work():
            add_slice_review(slice_report,snapshot,args)
            if 'slice' in slice_report:slice_report['slice']['model']=str(root/f'{source.stem}.stl')
            return slice_report
        slice_future=slice_executor.submit(context.run,slice_work)
    try:
        report=execute_cad(dict(source=str(source),source_sha256=digest(source),identity=identity,
            dependencies=[str(p.resolve()) for p in args.dependency],reuse=args.reuse,
            cad=request,run_id=_active.get(),environment=execution_environment,
            runtime=runtime_identity(),threads=args.threads,memory_mb=args.memory_mb,timeout=args.timeout),coordinator=not args.isolated,on_event=exports_ready)
    except KeyboardInterrupt:
        slice_cancelled.set()
        if slice_executor:slice_executor.shutdown(wait=True,cancel_futures=True)
        if slice_temporary:slice_temporary.cleanup()
        _cancellation.reset(cancellation_token)
        raise
    except Exception as exc:
        report={"ok":False,"file_path":str(source),"errors":[{"stage":"timeout" if isinstance(exc,TimeoutError) else "worker","message":str(exc)}]}
    report.setdefault("timings_seconds", {})["total"] = time.monotonic() - started
    pair_ready = (len(report.get("exports", [])) == 2
                  and all(item.get("ok") for item in report["exports"]))
    try:
        if not pair_ready:slice_cancelled.set()
        if args.slice and pair_ready:
            if slice_future:
                sliced=slice_future.result()
                report['slice']=sliced['slice'];report['errors'].extend(sliced['errors'])
                report['ok'] &= sliced['ok']
                report['timings_seconds']['slice']=sliced['timings_seconds']['slice']
            else:add_slice_review(report, root / f"{source.stem}.stl", args)
            report["timings_seconds"]["total"] = time.monotonic() - started
    finally:
        slice_cancelled.set()
        if slice_executor:slice_executor.shutdown(wait=True,cancel_futures=True)
        if slice_temporary:slice_temporary.cleanup()
        _cancellation.reset(cancellation_token)
    emit_report(report, args)
    if not report["ok"]:
        return 1
    return 2 if args.slice and pair_ready and report["slice"]["review_required"] else 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        sys.exit(worker(sys.argv[2], sys.argv[3]))
    sys.exit(main())
