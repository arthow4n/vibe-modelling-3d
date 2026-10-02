"""Inspection only: thin section through one rigid seat, leaf omitted.

Lower 28 mm of the card shown. No loaded-flexure simulation.
"""
import cadquery as cq
from card_base_corner_seat_5 import build_base, OUTER_WIDTH, TOP_Z, block
from check_corner_seat import placed_card

base=build_base(include_leaves=False)
# Isolate the middle seat: front rows would otherwise conceal its corners.
keep=block(-OUTER_WIDTH/2-1,OUTER_WIDTH/2+1,-1.3,-.9,0,TOP_Z+.1)
section=base.intersect(keep)
card=placed_card(2,50,2,4).intersect(
    block(-26,26,-2,2,0,28).val())
result=cq.Compound.makeCompound([section.val(),card])
