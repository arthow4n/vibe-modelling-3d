"""Smoke-slice one model with OrcaSlicer and print a compact JSON report.

G-code, slicer output and intermediate reports live in a temporary directory
that is removed when the command finishes. ``--keep-run`` preserves them.
This command never sends a printer job.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[4]
PROFILE_DIR = Path(".codex/skills/orca-slicer-printability/profiles/qidi-q2c-petg")
DEFAULTS = {
    "printer": PROFILE_DIR / "qidi-q2c-0.4-nozzle.json",
    "process": PROFILE_DIR / "qidi-q2c-0.20-standard-adaptive-cubic-7.json",
    "filament": PROFILE_DIR / "generic-petg-qidi-q2c-0.4.json",
}
SLICE_TIMEOUT_SECONDS = 600


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
            "enable_support", "support_type", "filament_flow_ratio", "enable_arc_fitting",
            "sparse_infill_density", "sparse_infill_pattern")
    return {key: settings[key] for key in keys if key in settings}


def _log_notices(text):
    return [line.strip() for line in text.splitlines() if re.search(
        r"warning|error|detected print stability|long bridging|loose extrusions|consider enabling supports",
        line, re.I)]


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
    notices = _log_notices(log_text)
    for plate in result["sliced_plates"]:
        warning = plate.get("warning_message", "").strip()
        if warning:
            notices.append(f"plate {plate.get('id', '?')}: {warning}")
    if result.get("error_string") not in (None, "", "Success", "Success."):
        notices.append(str(result["error_string"]))
    report = {
        "model": str(model),
        "profiles": {key: str(path) for key, path in profiles.items()},
        "slicer_help_header": version_header,
        "placement": placement,
        "effective_settings": _settings_summary(effective),
        "sliced_plates": [plate.get("id") for plate in result["sliced_plates"]],
        "log_notices": notices,
        "review_required": bool(notices),
        "limits": "Reports Orca's slice status and effective settings under the selected profiles. Orientation and arrangement rotation are disabled. Center placement may reposition multiple independent objects; use assembly mode to translate a grouped 3MF layout while retaining its internal positions, or preserve mode for an already positioned project. This smoke slice does not inspect deposited paths, support presence, mesh repair, clearance or physical print quality.",
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


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="Orca is inferred from ORCASLICER_COMMAND, then orca-slicer, then Flatpak."
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
    parser.add_argument("--keep-run", action="store_true",
                        help="keep temporary G-code and slicer diagnostics (default: false)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        report = review(args.model, args.printer, args.process, args.filament,
                        placement=args.placement, keep_run=args.keep_run)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 2 if report["review_required"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
