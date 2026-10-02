"""Five-card whole-object review; relaxed snaps overlap intentionally when closed."""
from cap_d_snap_5 import *

count=5
lower=base(count);hood=cap(count)
shift=OUTSIDE_X+15
closed=compound(lower,hood,*contents(count))
open_box=compound(lower.translate((shift,0,0)),
                  *[c.translate((shift,0,0)) for c in contents(count,sparse=True)],
                  hood_print(hood).translate((2*shift,0,0)))
result=compound(closed,open_box)
