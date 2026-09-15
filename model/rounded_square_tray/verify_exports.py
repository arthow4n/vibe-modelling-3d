"""Independent STEP/STL consistency checks for the final tray exports."""

from pathlib import Path
import importlib.util
import json

import cadquery as cq


object_dir = Path(__file__).resolve().parent
helper_path = object_dir.parents[1] / ".codex/skills/cadquery-3d-design/scripts/check_exports.py"
spec = importlib.util.spec_from_file_location("export_checks", helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

report = helper.check_pair(
    object_dir / "rounded_square_tray.step",
    object_dir / "rounded_square_tray.stl",
    expected_solids=1,
)
(object_dir / "notes/export_checks.json").write_text(json.dumps(report, indent=2) + "\n")
result = cq.importers.importStep(str(object_dir / "rounded_square_tray.step"))
