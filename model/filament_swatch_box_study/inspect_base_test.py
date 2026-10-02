"""Six real-size, notch-up card references; inspection only, never export."""
import cadquery as cq

from card_base_test import FLOOR, build_base, slot_y
from study import FLOOR as REFERENCE_FLOOR, card_reference

cards = [card_reference().translate((0, slot_y(index), FLOOR - REFERENCE_FLOOR)).val()
         for index in (0, 3, 5, 9, 11, 14)]
result = cq.Compound.makeCompound([build_base().val(), *cards])
