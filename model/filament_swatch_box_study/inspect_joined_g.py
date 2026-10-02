"""Inspection only: two closed G modules joined in the actual assembled pose."""
from cap_g_module_5 import *

b=base()
h=cap()
result=compound(*[part.translate((0,y,0))
                  for y in module_centres(2) for part in (b,h)], connector())
