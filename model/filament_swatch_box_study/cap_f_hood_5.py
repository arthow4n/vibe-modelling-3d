"""F flush exterior hood only; compatible with cap_e_base_5, roof down."""
from cap_f_flat_5 import *
result=hood_print(cap()).translate((PRINT_ANCHOR[0]+hood_shift(),PRINT_ANCHOR[1],0))
