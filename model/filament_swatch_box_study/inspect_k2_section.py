"""Inspection only: actual source-card bowl and K2 catch at left contact point.

The section plane is derived from source geometry and corrected nose placement.
No invented reflected card, no printable selection.
"""
import cap_k2_base_5 as v
import swatch_reference as ref
j=v.k.j
back=-j.slots.SLOT_WIDTH/2
# Tangency is on the bowl shoulder, not through the small sphere's center.
x=ref.point(ref.DOME_SOURCE,back)[0]-v.k.NOSE_CONTACT_RADIUS
cut=j.g.block(x-.02,x+.02,-4,4,0,30)
items=[v.panel().translate((0,v.k.SEATED_TRAVEL_Y,0)).intersect(cut),
       ref.card(back).intersect(cut)]
result=j.g.compound(*items)
