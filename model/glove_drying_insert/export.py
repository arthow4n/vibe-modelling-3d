"""Evaluate with CadQuery MCP to export and verify the production print layout."""
import sys, importlib, importlib.util, json, hashlib
from pathlib import Path
HERE=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/export.py')).resolve().parent
sys.path.insert(0,str(HERE))
import glove_drying_insert as m
importlib.reload(m)
import cadquery as cq
spec=importlib.util.spec_from_file_location('checks',HERE.parents[1]/'.codex/skills/cadquery-3d-design/scripts/check_exports.py')
checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)

def export_pair(shape,name,count):
    step=HERE/(name+'.step');stl=HERE/(name+'.stl')
    cq.exporters.export(shape,str(step))
    cq.exporters.export(shape,str(stl),tolerance=.015,angularTolerance=.1)
    return checks.check_pair(step,stl,count)

result=m.compound(m.print_parts())
report={'production':export_pair(result,'glove_drying_insert',4)}
# Optional reduced hinge-fit print reuses the full production hinge and axle.
clip=m.box(150,22,15,(0,5,0))
a=m.frame(True).intersect(clip)
b=m.frame(False).intersect(clip).translate((55,0,0))
pin=m.axle().translate((20,-17,0))
coupon=m.compound([a,b,pin])
report['hinge_sample']=export_pair(coupon,'hinge_fit_sample',3)
cq.exporters.export(m.compound(m.assembled()),str(HERE/'glove_drying_insert_assembled.step'))
report['source_sha256']=hashlib.sha256((HERE/'glove_drying_insert.py').read_bytes()).hexdigest()
(HERE/'notes/export_checks.json').write_text(json.dumps(report,indent=2)+'\n')
