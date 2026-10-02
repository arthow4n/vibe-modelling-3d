"""H joined end pockets and wider key, with no external arm."""
from cap_h_module_5 import *
result=compound(end_fixture(1).translate((0,-MODULE_GAP/2,0)),
                end_fixture(-1).translate((0,MODULE_GAP/2,0)),connector())
