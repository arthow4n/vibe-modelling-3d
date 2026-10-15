"""Inspection only: front half removed to expose both actual end catches."""
import cadquery as cq
from m1_design import build, box
parts = build()
d = parts['dimensions']
lo, hi = d.beam_root-12, d.seam+30
section = box(0, d.depth/4, (lo+hi)/2, d.width+2, d.depth/2, hi-lo)
result = cq.Assembly(name='m1_joint_section')
result.add(parts['body'].intersect(section), name='sectioned_body')
result.add(parts['cap'].intersect(section), name='sectioned_cap')
