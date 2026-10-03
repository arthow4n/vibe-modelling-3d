"""J open/closed joined boxes; reference cards are inspection-only."""
import cap_j_base_5 as j
import cap_i_grip_keys as i
from study import card_reference

b=j.base()
items=[]
for number,y in enumerate(i.module_centres()):
    items.append(b.translate((0,y,0)))
    for index in ((0,2,4) if number==0 else range(j.COUNT)):
        # Plain back (-Y) to the new panel; detailed face (+Y) away from it.
        items.append(card_reference().translate((0,j.slots.slot_y(index,j.COUNT)+.4+y,0)))
    if number==1:
        items.append(j.g.cap().translate((0,y,0)))
items.append(i.seated_key(3))
result=j.g.compound(*items)
