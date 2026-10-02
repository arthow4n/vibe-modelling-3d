"""Inspection only: open-top end pockets and the flat drop-in key."""
from cap_g_module_5 import *
result=compound(end_fixture(1).translate((0,-5,0)),
                end_fixture(-1).translate((0,5,0)),
                key_print().translate((FOOT_X+12,0,0)))
