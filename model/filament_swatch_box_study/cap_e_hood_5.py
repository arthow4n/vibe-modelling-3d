"""E thin hood only, roof down; print in translucent PETG with the E base."""
from cap_e_thin_5 import *
result=hood_print(cap()).translate((PRINT_ANCHOR[0]+hood_shift(),PRINT_ANCHOR[1],0))
