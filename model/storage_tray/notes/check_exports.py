from pathlib import Path
import importlib.util
import json
import cadquery as cq

object_dir = Path(__file__).resolve().parent.parent
helper_path = object_dir.parents[1] / '.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec = importlib.util.spec_from_file_location('export_checks', helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
step = object_dir / 'storage_tray.step'
stl = object_dir / 'storage_tray.stl'
report = helper.check_pair(step, stl, expected_solids=1)
(object_dir / 'notes/export_checks.json').write_text(json.dumps(report, indent=2))
result = cq.importers.importStep(str(step))
# Inspect opposing planar inner walls in the exported CAD, above the floor blend.
walls = [f for f in result.val().Faces() if f.geomType() == 'PLANE'
         and abs(f.Center().z - 22.6) < 1.0
         and (abs(abs(f.Center().x)-110) < 1e-5
              or abs(abs(f.Center().y)-110) < 1e-5)]
assert len(walls) == 4, [(f.Center().toTuple()) for f in walls]
print('Verified four interior wall planes at X/Y = +/-110 mm (220 mm clearance).')
