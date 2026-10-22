"""Inspection only: rounded corner stop and neighboring body/guide walls."""
import cadquery as cq
import m1_design as base
from rotary_quick_design import build,QUICK
p=build()
result=cq.Assembly(name='rounded_corner_stop_detail')
result.add(p['body'].intersect(base.box(33,-21,QUICK.seam+2,14,14,10)),
           name='body_corner_with_rounded_stop',color=cq.Color(.35,.55,.65))
