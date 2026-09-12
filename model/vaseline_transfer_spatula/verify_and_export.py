"""Independent STEP/STL consistency check for the transfer spatula."""
from pathlib import Path
import importlib.util
import json

import cadquery as cq


OBJECT_DIR = Path(__file__).resolve().parent
HELPER_PATH = (
    OBJECT_DIR.parents[1]
    / ".codex/skills/cadquery-3d-design/scripts/check_exports.py"
)
spec = importlib.util.spec_from_file_location("export_checks", HELPER_PATH)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

report = helper.check_pair(
    OBJECT_DIR / "vaseline_transfer_spatula.step",
    OBJECT_DIR / "vaseline_transfer_spatula.stl",
    expected_solids=1,
)
(OBJECT_DIR / "notes/export_checks.json").write_text(json.dumps(report, indent=2) + "\n")

result = cq.importers.importStep(str(OBJECT_DIR / "vaseline_transfer_spatula.step"))
