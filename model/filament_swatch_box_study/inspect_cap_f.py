"""F whole-form inspection: smooth closed hood, open sparse box, hood interior."""
from cap_f_flat_5 import *
lower=base();hood=cap()
shift=FOOT_X+15
result=compound(lower,hood,*contents(COUNT),lower.translate((shift,0,0)),
                *[c.translate((shift,0,0)) for c in contents(COUNT,sparse=True)],
                hood_print(hood).translate((2*shift,0,0)))
