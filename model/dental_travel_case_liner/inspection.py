"""Inspection only: cutaway inserts, omitting the existing rigid box."""
import cadquery as cq
from design import print_part, box

result=cq.Assembly(name='liner_cutaway')
for name in ('body','cap'):
    part=print_part(name)
    # Expose the entire end/core section and the stepped guard region.
    result.add(part.intersect(box(40,-25,0,170,50,200)),name=name)
