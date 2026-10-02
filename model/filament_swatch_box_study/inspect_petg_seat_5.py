"""Inspection only: one real-size card partly lifted above the relaxed leaves."""
import cadquery as cq
from card_base_petg_5 import build_base, slot_y, CARD_COUNT
from study import card_reference

base = build_base()
card = card_reference().translate((0, slot_y(2, CARD_COUNT)-0.4, 18))
result = cq.Compound.makeCompound([base.val(), card.val()])
