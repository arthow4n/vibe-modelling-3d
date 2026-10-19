"""Inspection only: enlarged compact screw hinge, screw/nuts omitted."""
import cadquery as cq
from clamshell_design import build,base,D
p=build('screw_pin')
crop=base.box(84,41,26,22,20,25)
result=cq.Assembly(name='C6_hinge_detail')
result.add(p['body'].intersect(crop),name='base_ears')
result.add(p['lid'].intersect(crop),name='lid_ear')
