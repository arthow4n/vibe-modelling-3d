"""Inspection only: A6 portrait and landscape cards; never print/export this scene."""
import cadquery as cq
from postcard_display import build, BASE_HEIGHT, SLOT_GAP, LEAN_DEG


def card(width, height, thickness=0.4):
    return (cq.Workplane('XY').box(width, thickness, height)
            .translate((0,-thickness/2,height/2))
            .rotate((0,0,0),(1,0,0),-LEAN_DEG)
            .translate((0,SLOT_GAP,BASE_HEIGHT)))

holder = build()
# A fully seated rigid card must clear the holder (contact without penetration).
for w,h in [(105,148),(148,105),(100,150),(150,100)]:
    for t in [0.2,0.8]:
        assert holder.val().intersect(card(w,h,t).val()).Volume() < 1e-7, (w,h,t)

result = cq.Compound.makeCompound([
    holder.val().translate((-90,0,0)), card(105,148).val().translate((-90,0,0)),
    holder.val().translate((90,0,0)), card(148,105).val().translate((90,0,0))])
