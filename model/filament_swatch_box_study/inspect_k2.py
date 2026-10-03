"""Inspection only: actual front-facing cards in K2 beside closed J2."""
import cap_k2_base_5 as v
import cap_j2_base_5 as j2
import swatch_reference as ref
import cap_i_grip_keys as keys
j=v.k.j
left,right=keys.module_centres()
items=[v.base().translate((0,left,0)),j2.base().translate((0,right,0)),
       j.g.cap().translate((0,right,0)),keys.seated_key(3)]
for n in (0,2,4):
    items.append(ref.card(left+j.slots.slot_y(n,j.COUNT)-j.slots.SLOT_WIDTH/2))
result=j.g.compound(*items)
