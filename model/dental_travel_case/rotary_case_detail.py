"""Inspection only: full-size mechanism and its surrounding cap/body wall."""
import cadquery as cq
import m1_design as base
from rotary_case_design import case

p=case();d=p['dimensions']
window=base.box(0,-25,d.pivot+5,48,36,55)
result=cq.Assembly(name='full_rotary_detail')
for name in ('body','cap','rotor','pivot_axle','pivot_nut'):
    result.add(p[name].intersect(window),name=name)
