"""Five-card trial with three seated references. Inspection only."""
import cadquery as cq

from card_base_test import FLOOR, build_base, slot_y
from study import FLOOR as REFERENCE_FLOOR, card_reference

cards = [card_reference().translate((0, slot_y(index, 5), FLOOR - REFERENCE_FLOOR)).val()
         for index in (0, 2, 4)]
result = cq.Compound.makeCompound([build_base(5).val(), *cards])
