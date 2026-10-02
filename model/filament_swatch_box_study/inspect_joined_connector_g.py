"""Inspection only: joined end crops from above, exposing the seated G key."""
from cap_g_module_5 import *

result=compound(end_fixture(1).translate((0,-MODULE_GAP/2,0)),
                end_fixture(-1).translate((0,MODULE_GAP/2,0)), connector())
