"""Inspect the delivered STEP/STL pair through the repository checker."""
from pathlib import Path
import importlib.util
import json
import cadquery as cq

root = Path(__file__).resolve().parent
helper_path = root.parents[1] / '.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec = importlib.util.spec_from_file_location('export_checks', helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
step = root / 'rounded_square_tray.step'
stl = root / 'rounded_square_tray.stl'
report = helper.check_pair(step, stl, expected_solids=1)
(root / 'notes/export_checks.json').write_text(json.dumps(report, indent=2) + '\n')
result = cq.importers.importStep(str(step))
