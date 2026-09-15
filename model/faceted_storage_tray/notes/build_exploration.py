"""Evaluate through CadQuery MCP to build/export/check all eight alternatives."""
from pathlib import Path
import sys
import json
import runpy
import hashlib
import importlib.util
import cadquery as cq

root = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root))
helper_path = root.parents[1]/'.codex/skills/cadquery-3d-design/scripts/check_exports.py'
spec = importlib.util.spec_from_file_location('export_checks',helper_path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
reports = []
for config in json.loads((root/'notes/variants.json').read_text()):
    name = config['name']
    folder = root/'variants'/name
    source = folder/(name+'.py')
    shape = runpy.run_path(str(source))['result']
    step, stl = folder/(name+'.step'), folder/(name+'.stl')
    cq.exporters.export(shape,str(step))
    cq.exporters.export(shape,str(stl),tolerance=0.02,angularTolerance=0.1)
    report = helper.check_pair(step,stl,expected_solids=1)
    final = cq.importers.importStep(str(step)).val()
    symmetry = {}
    for label, transformed in [('rotate_90',final.rotate((0,0,0),(0,0,1),90)),
                                ('mirror_diagonal',final.mirror((1,-1,0)))]:
        diff = final.cut(transformed).Volume()+transformed.cut(final).Volume()
        assert diff < 0.01,(name,label,diff)
        symmetry[label] = diff
    gaps = {}
    for z in [9.,20.,30.,37.]:
        wires = cq.Workplane('XY').add(final).section(z).wires().vals()
        assert len(wires)==2
        gap = wires[0].distance(wires[1])
        assert gap > 2.8,(name,z,gap)
        gaps[str(z)] = gap
    walls = [f for f in final.Faces() if f.geomType()=='PLANE'
             and abs(f.Center().z-22.6)<1
             and (abs(abs(f.Center().x)-110)<1e-5 or abs(abs(f.Center().y)-110)<1e-5)]
    assert len(walls)==4,(name,len(walls))
    report.update(config=config,symmetry_difference_mm3=symmetry,
                  sampled_horizontal_wall_minimum_mm=gaps,
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  builder_sha256=hashlib.sha256((root/'faceted_storage_tray.py').read_bytes()).hexdigest())
    (folder/'checks.json').write_text(json.dumps(report,indent=2))
    box = final.BoundingBox()
    reports.append(dict(name=name,size_mm=[box.xlen,box.ylen,box.zlen],passed=True))
(root/'notes/exploration_build.json').write_text(json.dumps(reports,indent=2))
from faceted_storage_tray import result
print(json.dumps(reports))
