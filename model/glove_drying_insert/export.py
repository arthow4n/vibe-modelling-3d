"""Export the production print layout and optional hinge-fit sample."""
import sys, importlib
from pathlib import Path
HERE=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/export.py')).resolve().parent
sys.path.insert(0,str(HERE))
import glove_drying_insert as m
importlib.reload(m)
import cadquery as cq

def export_pair(shape,name):
    step=HERE/(name+'.step');stl=HERE/(name+'.stl')
    cq.exporters.export(shape,str(step))
    cq.exporters.export(shape,str(stl),tolerance=.015,angularTolerance=.1)

result=m.compound(m.print_parts())
export_pair(result,'glove_drying_insert')
# Optional reduced hinge-fit print reuses the full production hinge and axle.
clip=m.box(150,22,15,(0,5,0))
a=m.frame(True).intersect(clip)
b=m.frame(False).intersect(clip).translate((55,0,0))
pin=m.axle().translate((20,-17,0))
coupon=m.compound([a,b,pin])
export_pair(coupon,'hinge_fit_sample')
cq.exporters.export(m.compound(m.assembled()),str(HERE/'glove_drying_insert_assembled.step'))
