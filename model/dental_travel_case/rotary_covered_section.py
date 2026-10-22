"""Inspection only: section through a keyed pocket at X=7.0 mm."""
import cadquery as cq
import m1_design as base
from rotary_covered_design import covered_case,KEY_X
p=covered_case();d=p['dimensions'];result=cq.Assembly(name='keyed_cover_section')
window=base.box(KEY_X-12,-29,d.pivot,24,40,45)
for name in ('body','rotor','facecap','pivot_axle','pivot_nut'):
    result.add(p[name].intersect(window),name=name)
