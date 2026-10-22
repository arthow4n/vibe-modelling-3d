"""Inspection only: section through matching head, shoulder and wheel."""
import cadquery as cq
import m1_design as base
from rotary_case_design import case
p=case();d=p['dimensions'];result=cq.Assembly(name='conical_head_section')
# Half-section through the pivot: exposes the taper, blind drive and solid shaft.
window=base.box(-12,-30,d.pivot,24,28,27)
for name in ('body','rotor','pivot_axle','pivot_nut'):
    result.add(p[name].intersect(window),name=name)
