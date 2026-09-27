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
            raise RuntimeError("Orca automatic-support probe failed; use --keep-run for its log")
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
        "reused_primary_slice": reuse_primary,
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
    try:
        support_probe = _auto_support_probe(command, run_dir, effective, result)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        support_probe = {"ok": False, "message": str(exc)}
    report = {
        "model": str(model),
        "profiles": {key: str(path) for key, path in profiles.items()},
        "slicer_help_header": version_header,
        "placement": placement,
        "effective_settings": _settings_summary(effective),
        "sliced_plates": [plate.get("id") for plate in result["sliced_plates"]],
        "support_probe": support_probe,
        "log_notices": notices,
        "review_required": bool(notices) or not support_probe["ok"] or support_probe.get("generated", False),
        "limits": "Reports Orca's slice status and effective settings under the selected profiles. The automatic-support probe enables support and permits support under bridges, then checks Orca's emitted support line types. Generated support is a prompt to inspect placement and removal, not proof it is physically necessary; no generated support does not prove every overhang or bridge will print well. The probe uses the selected profile's support threshold and maximum bridge length. Orientation and arrangement rotation are disabled. Center placement may reposition multiple independent objects; use assembly mode to translate a grouped 3MF layout while retaining its internal positions, or preserve mode for an already positioned project. This smoke slice does not inspect deposited bounds, mesh repair, clearance or physical print quality.",
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
