"""Inspection only: source-derived cards and J2 opposing rails."""
import cap_j2_base_5 as v
import swatch_reference as ref

items=[v.base()]
for n in (0,2,4):
    y=v.j.slots.slot_y(n,v.j.COUNT)
    items.append(ref.card(y+v.j.slots.SLOT_WIDTH/2-ref.THICKNESS))
result=v.j.g.compound(*items)
