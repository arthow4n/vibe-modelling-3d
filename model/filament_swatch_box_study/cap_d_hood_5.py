"""D cap only; requires the matching grooved base, not earlier ungrooved bases."""
from cap_d_snap_5 import *
shift=OUTER_WIDTH/2+OUTSIDE_X/2+10
result=hood_print(cap()).translate((PRINT_ANCHOR[0]+shift,PRINT_ANCHOR[1],0))
