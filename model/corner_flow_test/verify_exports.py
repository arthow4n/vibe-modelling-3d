"""Verify the final STEP/STL pair with the repository export checker."""

from pathlib import Path
import importlib.util
import json

import cadquery as cq


OBJECT_DIR = Path(__file__).resolve().parent
REPO = OBJECT_DIR.parents[1]
HELPER = REPO / ".codex/skills/cadquery-3d-design/scripts/check_exports.py"

spec = importlib.util.spec_from_file_location("check_exports", HELPER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

report = checker.check_pair(
    OBJECT_DIR / "CornerFlowTest.step",
    OBJECT_DIR / "CornerFlowTest.stl",
    expected_solids=1,
)
(OBJECT_DIR / "notes/export_checks.json").write_text(
    json.dumps(report, indent=2) + "\n"
)

result = cq.importers.importStep(str(OBJECT_DIR / "CornerFlowTest.step"))
