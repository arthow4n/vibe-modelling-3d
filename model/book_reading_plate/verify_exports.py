"""Independent verification of the final two panels and two-piece rail coupon."""
from pathlib import Path
import importlib.util
import json
import cadquery as cq


def verify():
    root=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('export_checks',
        root.parents[1]/'.codex/skills/cadquery-3d-design/scripts/check_exports.py')
    checker=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    reports={name:checker.check_pair(root/f'{name}.step',root/f'{name}.stl',expected_solids=count)
             for name,count in [('plate_left',1),('plate_right',1),('joint_test',2)]}
    assembly=cq.importers.importStep(str(root/'book_reading_plate_assembled.step'))
    assert len(assembly.solids().vals())==2
    (root/'notes/export_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Three STEP/STL pairs passed; assembly and coupon each contain exactly two solids.')
    return cq.importers.importStep(str(root/'joint_test.step'))

result=verify()
