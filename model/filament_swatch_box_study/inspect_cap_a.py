"""A comparison: closed full twenty-card box and open sparse box next to it."""
from cap_common import *
from cap_a_lift_off_5 import cap

count=FULL_COUNT
closed=compound(rounded_base(count),cap(count))
shift=CAP_OUTER_X+18
open_base=rounded_base(count).translate((shift,0,0))
cards=[p.translate((shift,0,0)) for p in contents(count,sparse=True)]
lid=hood_print(cap(count)).translate((2*shift,0,0))
result=compound(closed,open_base,lid,*cards)
