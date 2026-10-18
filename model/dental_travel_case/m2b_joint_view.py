"""Inspection only: actual central section of M2B guide, catches and controls."""
import cadquery as cq
from m1_design import box
from m2b_design import build
parts=build()
d=parts['dimensions']
lo,hi=d.beam_root-10,d.seam+d.lap+10
section=box(0,d.depth/4,(lo+hi)/2,d.width+4,d.depth/2,hi-lo)
result=cq.Assembly(name='m2b_section')
result.add(parts['body'].intersect(section),name='sectioned_body')
result.add(parts['cap'].intersect(section),name='sectioned_cap')
