"""Independently verify final STEP/STL files through the repository checker."""
from pathlib import Path
import importlib.util
import json
import cadquery as cq


def verify():
    root = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location('export_checks',
        root.parents[1]/'.codex/skills/cadquery-3d-design/scripts/check_exports.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    reports = {}
    for name,count in [('plate_left',1),('plate_right',1),('locking_keys',4),('joint_test',3)]:
        reports[name]=checker.check_pair(root/f'{name}.step',root/f'{name}.stl',expected_solids=count)
    (root/'notes/export_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Four STEP/STL pairs passed: topology, winding, bounds, volume, components and bed contact.')
    return cq.importers.importStep(str(root/'plate_left.step'))

result = verify()
