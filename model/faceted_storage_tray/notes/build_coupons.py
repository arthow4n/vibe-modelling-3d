"""Evaluate through the shared CadQuery command to build and export all exterior coupons."""
from pathlib import Path
import hashlib
import importlib.util
import json
import runpy
import sys

import cadquery as cq

root = Path(__file__).resolve().parent.parent
repo = root.parents[1]
sys.path.insert(0, str(root))
helper_path = repo / '.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec = importlib.util.spec_from_file_location('export_checks', helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

reports = []
for config in json.loads((root / 'notes/variants.json').read_text()):
    name = config['name']
    folder = root / 'test_pieces' / name
    source = folder / f'{name}_coupon.py'
    shape = runpy.run_path(str(source))['result']
    step = folder / f'{name}_coupon.step'
    stl = folder / f'{name}_coupon.stl'
    cq.exporters.export(shape, str(step))
    cq.exporters.export(shape, str(stl), tolerance=0.02, angularTolerance=0.1)
    report = helper.check_pair(step, stl, expected_solids=1)
    solid = cq.importers.importStep(str(step)).val()
    box = solid.BoundingBox()
    assert abs(box.xlen - 50.0) < 0.035
    assert abs(box.zlen - 38.0) < 0.035
    assert box.ylen <= 40.035
    report.update(
        config=config,
        size_mm=[box.xlen, box.ylen, box.zlen],
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        builder_sha256=hashlib.sha256((root / 'faceted_storage_tray.py').read_bytes()).hexdigest(),
    )
    (folder / 'checks.json').write_text(json.dumps(report, indent=2))
    reports.append({'name': name, 'size_mm': report['size_mm'], 'passed': True})

(root / 'notes/coupon_build.json').write_text(json.dumps(reports, indent=2))
print(json.dumps(reports))
from faceted_storage_tray import result
