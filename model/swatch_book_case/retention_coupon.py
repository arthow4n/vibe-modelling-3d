"""One sample of the production catch, seat, keeper and adjacent front wall.

Preserves all local geometry and print orientations. Slide cap down vertically
onto its shoulder; this conservative local closing path omits the real hinge
arc. Tests feel/fit/recovery, not full-shell stiffness, hinges or card handling.
"""
import cadquery as cq
from swatch_book_case import body,lid,latch_print,block,FRONT_Y,TOTAL_Z

def coupon_parts():
    clip=block(-30,FRONT_Y-4,0,60,16,TOTAL_Z+1)
    base=body().intersect(clip)
    cap=lid().intersect(clip)
    # Source bed orientation for every local feature, including lid keeper.
    base=base.translate((30,-FRONT_Y+4,0))
    cap=cap.rotate((0,0,0),(1,0,0),180).translate((30,FRONT_Y+35,TOTAL_Z))
    catch=latch_print().translate((5,55,0))
    return base,cap,catch

result=cq.Compound.makeCompound([s.val() for s in coupon_parts()])
