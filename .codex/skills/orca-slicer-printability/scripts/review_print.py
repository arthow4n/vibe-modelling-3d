"""Create a fresh OrcaSlicer reference review; never send a printer job.

Writes G-code and slicer logs (ignored), effective-settings and result records,
deposited-path summaries and bounds. It preserves the supplied model
arrangement and orientation.
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
from inspect_gcode import _is_support, read_paths, summarize

REPO_ROOT = Path(__file__).resolve().parents[4]
PROFILE_DIR = REPO_ROOT / ".codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg"
DEFAULTS = {
    "printer": PROFILE_DIR / "qidi-q2c-0.4-nozzle.json",
    "process": PROFILE_DIR / "qidi-q2c-0.20-standard-adaptive-cubic-7.json",
    "filament": PROFILE_DIR / "generic-petg-qidi-q2c-0.4.json",
}


def footprint(layers, bed):
    if len(bed) != 3 or not all(math.isfinite(v) and v > 0 for v in bed):
        raise ValueError("Three positive finite safe build dimensions required")
    lo, hi = [float("inf")] * 2, [-float("inf")] * 2
    support_segments = 0
    for paths in layers.values():
        for path in paths:
            support_segments += int(_is_support(path["role"]))
            width = path["width_mm"]
            if not math.isfinite(width) or width <= 0:
                raise ValueError("Invalid extrusion width")
            for point in (path["a"], path["b"]):
                if not all(math.isfinite(v) for v in point):
                    raise ValueError("Nonfinite deposition position")
                for k in (0, 1):
                    lo[k] = min(lo[k], point[k] - width / 2)
                    hi[k] = max(hi[k], point[k] + width / 2)
    zlo, zhi = min(layers), max(layers)
    fits = zlo >= 0 and zhi <= bed[2] and all(0 <= lo[k] <= hi[k] <= bed[k] for k in (0, 1))
    return {"xy_bounds_including_half_width_mm": lo + hi, "min_layer_z_mm": zlo,
            "max_layer_z_mm": zhi, "inside_safe_volume": fits,
            "support_segments": support_segments}


def slicer_prefix(command=None):
    value = command or os.environ.get("ORCASLICER_COMMAND")
    if value:
        prefix = shlex.split(value)
    elif shutil.which("orca-slicer"):
        prefix = [shutil.which("orca-slicer")]
    else:
        prefix = ["flatpak", "run", "com.orcaslicer.OrcaSlicer"]
    if not prefix or not shutil.which(prefix[0]):
        raise FileNotFoundError(f"OrcaSlicer command is unavailable: {prefix}")
    return prefix


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


def review(model, printer, process, filament, output, bed=(260, 260, 250),
           slicer=None, expect_no_supports=False, timeout=600,
           purpose="smoke", profile_scope="reference", placement="center"):
    model = Path(model).resolve(strict=True)
    profiles = {key: Path(value).resolve(strict=True) for key, value in {
        "printer": printer, "process": process, "filament": filament}.items()}
    output = Path(output).resolve()
    if len(bed) != 3 or not all(math.isfinite(v) and v > 0 for v in bed):
        raise ValueError("Invalid safe build volume")
    placement_args = {
        "preserve": ["--arrange", "0", "--orient", "0"],
        "center": ["--arrange", "1", "--orient", "0", "--allow-rotations=0"],
        "assembly": ["--assemble", "--arrange", "1", "--orient", "0", "--allow-rotations=0"],
    }
    if placement not in placement_args:
        raise ValueError("placement must be preserve, center or assembly")
    prefix = slicer_prefix(slicer)
    output.mkdir(parents=True, exist_ok=False)
    (output / ".gitignore").write_text("*.gcode\n*.log\n")

    # Keep Orca's incidental CLI files and any app data inside this fresh run.
    help_run = subprocess.run(prefix + ["--help"], cwd=output, capture_output=True,
                              text=True, timeout=30, check=False)
    version_header = (help_run.stdout + help_run.stderr).splitlines()[:8]
    effective_path = output / "effective-settings.json"
    command = prefix + [str(model),
        "--load-settings", f"{profiles['process']};{profiles['printer']}",
        "--load-filaments", str(profiles["filament"]),
        *placement_args[placement], "--slice", "0",
        "--outputdir", str(output), "--export-settings", str(effective_path)]
    (output / "command.json").write_text(json.dumps(command, indent=2) + "\n")
    with (output / "slicer.log").open("w") as log:
        completed = subprocess.run(command, cwd=output, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=timeout, check=False)
    log_text = (output / "slicer.log").read_text(errors="replace")

    result_path = output / "result.json"
    if completed.returncode != 0 or not result_path.is_file():
        raise RuntimeError(f"OrcaSlicer CLI failed; inspect {output / 'slicer.log'}")
    result = json.loads(result_path.read_text())
    if result.get("return_code") != 0 or not result.get("sliced_plates"):
        raise RuntimeError(f"OrcaSlicer did not report a completed plate; inspect {result_path}")
    if not effective_path.is_file():
        raise RuntimeError(f"OrcaSlicer did not export effective settings: {effective_path}")
    effective = json.loads(effective_path.read_text())
    gcode_files = sorted(output.glob("*.gcode"))
    if not gcode_files or any(not path.is_file() or path.stat().st_size == 0 for path in gcode_files):
        raise RuntimeError(f"OrcaSlicer did not produce fresh nonempty G-code in {output}")
    expected_plates = result["sliced_plates"]
    expected_plate_numbers = [int(plate["id"]) for plate in expected_plates]
    if len(expected_plate_numbers) != len(set(expected_plate_numbers)):
        raise RuntimeError(f"OrcaSlicer reported duplicate sliced plate IDs: {expected_plate_numbers}")
    gcode_plate_numbers = []
    for gcode in gcode_files:
        match = re.search(r"plate[_-]?(\d+)", gcode.stem, re.I)
        if not match:
            raise RuntimeError(f"Cannot match G-code file to an Orca plate ID: {gcode.name}")
        gcode_plate_numbers.append(int(match.group(1)))
    if len(gcode_plate_numbers) != len(set(gcode_plate_numbers)):
        raise RuntimeError(f"OrcaSlicer wrote duplicate G-code plate IDs: {gcode_plate_numbers}")
    if set(gcode_plate_numbers) != set(expected_plate_numbers):
        raise RuntimeError(
            f"OrcaSlicer reported plate IDs {sorted(expected_plate_numbers)} "
            f"but wrote G-code for plate IDs {sorted(gcode_plate_numbers)}"
        )

    plates, path_summaries, notices = [], {}, _log_notices(log_text)
    for gcode, plate_number in zip(gcode_files, gcode_plate_numbers):
        layers, metadata = read_paths(gcode)
        path_summary = summarize(layers, metadata)
        bounds = footprint(layers, bed)
        plates.append({"plate": plate_number, "gcode": str(gcode), **bounds,
                       "layer_count": path_summary["layer_count"], "metadata": metadata})
        path_summaries[f"plate_{plate_number}"] = path_summary

    for plate in result.get("sliced_plates", []):
        warning = plate.get("warning_message", "").strip()
        if warning:
            notices.append(f"plate {plate.get('id', '?')}: {warning}")
    if result.get("error_string") not in (None, "", "Success", "Success."):
        notices.append(str(result["error_string"]))
    inside = all(plate["inside_safe_volume"] for plate in plates)
    support_segments = sum(plate["support_segments"] for plate in plates)
    report = {
        "model": str(model), "profile_scope": profile_scope, "purpose": purpose,
        "profiles": {key: str(path) for key, path in profiles.items()},
        "slicer_help_header": version_header, "safe_build_volume_mm": list(bed),
        "placement": placement,
        "effective_settings": _settings_summary(effective),
        "effective_settings_file": str(effective_path), "result_file": str(result_path),
        "plates": plates, "inside_safe_volume": inside,
        "support_segments": support_segments, "log_notices": notices,
        "review_required": bool(notices) or not inside or (expect_no_supports and support_segments > 0),
        "limits": "Generic reference/actual-profile paths only. Orientation and arrangement rotation are disabled. Center placement may reposition multiple independent objects; use assembly mode to translate a grouped 3MF layout while retaining its internal positions, or preserve mode for an already positioned project. Bounds include half line width, brim and generated support paths, but exclude travel, start/end machine motion and physical flow spread. Linear ASCII extrusion paths only; role labels and segment lengths do not establish anchors, free-air spans, clearance or physical print quality."
    }
    (output / "paths.json").write_text(json.dumps(path_summaries, indent=2) + "\n")
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--printer", type=Path, default=DEFAULTS["printer"])
    parser.add_argument("--process", type=Path, default=DEFAULTS["process"])
    parser.add_argument("--filament", type=Path, default=DEFAULTS["filament"])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bed", type=float, nargs=3, default=(260, 260, 250), metavar=("X", "Y", "Z"))
    parser.add_argument("--slicer", help="Executable command; defaults to orca-slicer or Flatpak OrcaSlicer")
    parser.add_argument("--placement", choices=("preserve", "center", "assembly"), default="center")
    parser.add_argument("--expect-no-supports", action="store_true")
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--purpose", choices=("smoke", "investigation"), default="smoke")
    parser.add_argument("--profile-scope", choices=("reference", "actual"), default="reference")
    args = parser.parse_args()
    report = review(args.model, args.printer, args.process, args.filament, args.out,
                    bed=args.bed, slicer=args.slicer,
                    expect_no_supports=args.expect_no_supports, timeout=args.timeout,
                    purpose=args.purpose, profile_scope=args.profile_scope,
                    placement=args.placement)
    print(json.dumps({"report": str(args.out.resolve() / "summary.json"),
                      "effective_settings": report["effective_settings"],
                      "plates": report["plates"], "review_required": report["review_required"]}))
    raise SystemExit(2 if report["review_required"] else 0)


if __name__ == "__main__":
    main()
