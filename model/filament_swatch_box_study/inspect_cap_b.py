"""B twenty-card closed/open comparison; withdrawn tray rests on same table."""
from cap_common import *
from cap_b_drawer_5 import drawer,housing

count=FULL_COUNT
closed=compound(drawer(count),housing(count))
shift=CAP_OUTER_X+28
pull=outer_depth(count)+14
open_housing=housing(count).translate((shift,0,0))
offset=(shift,-pull,-CAP_WALL)
open_tray=drawer(count).translate(offset)
cards=[p.translate(offset) for p in contents(count,sparse=True)]
result=compound(closed,open_housing,open_tray,*cards)
