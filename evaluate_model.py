#!/usr/bin/env -S uv run --locked
"""Evaluate a trusted CadQuery source file without an MCP server.

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
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    def measure(item):
        box = Bnd_Box()
        BRepBndLib.AddOptimal_s(item.wrapped, box, False, False)
        bounds = list(box.Get())
        return {"valid": item.isValid(), "bounds_mm": bounds,
                "size_mm": [bounds[i + 3] - bounds[i] for i in range(3)],
                "volume_mm3": item.Volume(), "surface_area_mm2": item.Area(),
                "center_of_mass_mm": list(item.Center().toTuple())}

    data = measure(shape)
    data["topology"] = {name: len(getattr(shape, method)()) for name, method in
                        (("solids", "Solids"), ("faces", "Faces"),
                         ("edges", "Edges"), ("vertices", "Vertices"))}
    data["components"] = [measure(part) for part in shape.Solids()]
    return data


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
        data = temporary.read_bytes()
        temporary.replace(path)
        result = {key: value for key, value in item.items() if key != "format"}
        return {**result, "ok": True, "bytes": len(data)}
    finally:
        temporary.unlink(missing_ok=True)


def render(shape, view, width, height, show_hidden):
    from cadquery.occ_impl.exporters.svg import getSVG
    svg = getSVG(shape, opts={"width": width, "height": height,
                              "projectionDir": VIEWS[view], "showHidden": show_hidden,
                              "showAxes": view.startswith("isometric")}).encode("utf-8")
    import cairosvg
    return cairosvg.svg2png(bytestring=svg, output_width=width, output_height=height,
                            background_color="#ffffff")


def worker(request, response):
    import cadquery as cq
    from cadquery import cqgi
    import runpy

    args = json.loads(Path(request).read_text())
    path = Path(args["file_path"])
    root = path.parent
    report = {"ok": False, "file_path": str(path), "units": "mm", "errors": [],
              "views": [], "exports": [], "timings_seconds": {},
              "versions": {"python": sys.version.split()[0], "cadquery": cq.__version__}}
    log = io.StringIO()
    started = time.monotonic()

    def error(stage, exc, **details):
        frames = traceback.extract_tb(exc.__traceback__)
        report["errors"].append({"stage": stage, "type": type(exc).__name__,
                                 "message": str(exc), **details,
                                 "file": getattr(exc, "filename", None) or (frames[-1].filename if frames else None),
                                 "line": getattr(exc, "lineno", None) or (frames[-1].lineno if frames else None),
                                 "traceback": "".join(traceback.format_exception(exc))[-8192:]})

    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        try:
            source = path.read_bytes()
            # CQGI supplies parameter metadata, while run_path preserves __file__
            # and normal sibling imports. Both use the same top-level source.
            try:
                parsed = cqgi.parse(source.decode("utf-8"))
                report["parameters"] = {name: {"value": param.default_value,
                    "type": param.varType.__name__ if param.varType else "unknown",
                    "description": param.desc} for name, param in parsed.metadata.parameters.items()}
            except Exception as exc:
                report["parameter_note"] = f"CQGI metadata unavailable: {exc}"
                report["parameters"] = {}
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
            before = time.monotonic()
            for item in args["exports"]:
                try:
                    report["exports"].append(export(shape, item))
                except Exception as exc:
                    result = {key: value for key, value in item.items() if key != "format"}
                    report["exports"].append({**result, "ok": False})
                    error("export", exc, path=item["path"])
            report["timings_seconds"]["export"] = time.monotonic() - before
            before = time.monotonic()
            for view in args["views"]:
                destination = Path(args["output_dir"]) / f'{path.stem}_{view}.png'
                try:
                    data = render(shape, view, args["width"], args["height"],
                                  args["show_hidden"])
                    atomic_bytes(destination, data)
                    report["views"].append({"view": view, "ok": True, "path": str(destination)})
                except Exception as exc:
                    report["views"].append({"view": view, "ok": False})
                    error("render", exc, view=view)
            report["timings_seconds"]["render"] = time.monotonic() - before
        except Exception as exc:
            error("build", exc)
    report["diagnostics"] = log.getvalue()[:16384]
    report["timings_seconds"]["worker"] = time.monotonic() - started
    report["ok"] = not report["errors"]
    Path(response).write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["ok"] else 1


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


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=f"{__doc__}\nFor valid evaluations, stdout always contains one JSON object. "
                    "Model, view, and export paths in the report are absolute.\n"
                    f"STL exports use {STL_LINEAR_TOLERANCE_MM} mm absolute linear and "
                    f"{STL_ANGULAR_TOLERANCE_RAD} rad angular tessellation tolerances.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("file_path", type=Path, help="Trusted CadQuery Python entry point")
    parser.add_argument("--views", default="isometric,front,top,right",
                        help=f"Comma-separated views from {', '.join(VIEWS)}, or none")
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
                        help="Export the pair and smoke-slice its STL with OrcaSlicer")
    parser.add_argument("--slice-printer", type=Path,
                        help="Orca printer profile; use with --slice")
    parser.add_argument("--slice-process", type=Path,
                        help="Orca process profile; use with --slice")
    parser.add_argument("--slice-filament", type=Path,
                        help="Orca filament profile; use with --slice")
    parser.add_argument("--slice-placement", choices=("preserve", "center", "assembly"),
                        default="center", help="Orca placement; use with --slice")
    parser.add_argument("--slice-expect-no-supports", action="store_true",
                        help="Flag generated supports for review; use with --slice")
    parser.add_argument("--slice-keep-run", action="store_true",
                        help="Keep Orca diagnostics and G-code; use with --slice")
    parser.add_argument("--timeout", type=positive_float, default=300,
                        help="Maximum evaluation time in seconds")
    args = parser.parse_args(argv)
    if not args.slice and any((args.slice_printer, args.slice_process,
                               args.slice_filament, args.slice_expect_no_supports,
                               args.slice_keep_run, args.slice_placement != "center")):
        parser.error("Slice settings require --slice")
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
            item = {"path": str(path), "format": name}
            if name == "STL":
                item.update(tolerance_mm=STL_LINEAR_TOLERANCE_MM,
                            angular_tolerance_rad=STL_ANGULAR_TOLERANCE_RAD,
                            linear_tolerance_mode="absolute")
            exports.append(item)
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
        slicer = Path(__file__).resolve().parent / ".codex/skills/orca-slicer-printability/scripts/review_print.py"
        command = [sys.executable, str(slicer), "--model", str(root / f"{source.stem}.stl"),
                   "--placement", args.slice_placement]
        for option, value in (("--printer", args.slice_printer),
                              ("--process", args.slice_process),
                              ("--filament", args.slice_filament)):
            if value is not None:
                command.extend((option, str(value)))
        if args.slice_expect_no_supports:
            command.append("--expect-no-supports")
        if args.slice_keep_run:
            command.append("--keep-run")
        before = time.monotonic()
        try:
            sliced = subprocess.run(command, cwd=Path(__file__).resolve().parent,
                                    capture_output=True, text=True, timeout=SLICE_TIMEOUT_SECONDS + 60,
                                    check=False)
            if sliced.returncode not in (0, 2):
                raise RuntimeError(sliced.stderr.strip() or "OrcaSlicer review failed")
            report["slice"] = {"ok": True, **json.loads(sliced.stdout)}
        except (OSError, ValueError, subprocess.TimeoutExpired, RuntimeError) as exc:
            report["slice"] = {"ok": False, "message": str(exc)}
            report["errors"].append({"stage": "slice", "message": str(exc)})
            report["ok"] = False
        report["timings_seconds"]["slice"] = time.monotonic() - before
        report["timings_seconds"]["total"] = time.monotonic() - started
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        return 1
    return 2 if args.slice and report["slice"]["review_required"] else 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        sys.exit(worker(sys.argv[2], sys.argv[3]))
    sys.exit(main())
