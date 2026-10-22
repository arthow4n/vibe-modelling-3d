"""Inspection only: covered mechanism and neighbouring case walls."""
import cadquery as cq
import m1_design as base
from rotary_covered_design import covered_case
p=covered_case();d=p['dimensions'];result=cq.Assembly(name='keyed_cover_detail')
window=base.box(0,-28,d.pivot+5,48,40,55)
for name in ('body','cap','rotor','facecap','pivot_axle','pivot_nut'):
    result.add(p[name].intersect(window),name=name)
