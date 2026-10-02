"""Inspection only: closed thin hood and open sparse five-card box."""
from cap_e_thin_5 import *

lower=base();hood=cap()
shift=FOOT_X+15
closed=compound(lower,hood,*contents(COUNT))
opened=compound(lower.translate((shift,0,0)),
                *[c.translate((shift,0,0)) for c in contents(COUNT,sparse=True)],
                hood_print(hood).translate((2*shift,0,0)))
result=compound(closed,opened)
