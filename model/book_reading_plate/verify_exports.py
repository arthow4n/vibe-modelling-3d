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
    assembly=cq.importers.importStep(str(root/'book_reading_plate_assembled.step')).solids().vals()
    male=next(s for s in assembly if s.BoundingBox().xmin < -100)
    keys=[s for s in assembly if s.BoundingBox().xlen<30]
    assert len(keys)==4
    stop=[]
    for key in keys:
        seated_to_stop=0.2
        at_stop=key.translate((0,0,seated_to_stop))
        beyond=key.translate((0,0,seated_to_stop+0.05))
        assert at_stop.BoundingBox().zmax<=10.00001
        assert beyond.intersect(male).Volume()>0.01
        stop.append({'tip_z_at_stop_mm':at_stop.BoundingBox().zmax,
                     'overtravel_0_05_mm_contact_volume_mm3':beyond.intersect(male).Volume()})
    reports['assembled_depth_stop']=stop
    (root/'notes/export_checks.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Four STEP/STL pairs passed: topology, winding, bounds, volume, components, bed contact and assembled depth stops.')
    return cq.importers.importStep(str(root/'plate_left.step'))

result = verify()
