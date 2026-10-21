"""Fast L20+L18 cup-only plate; reuse the physically approved T08 lid pad."""
import cadquery as cq
from thin_gap_design import cup
result=cq.Assembly(name='L20_L18_cups_reuse_T08_pad')
result.add(cup('L20'),name='cup_L20',loc=cq.Location((60,60,0)))
result.add(cup('L18'),name='cup_L18',loc=cq.Location((102,60,0)))
