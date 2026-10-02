"""Economical G fit sample: two actual end crops plus one actual connector."""
from cap_g_module_5 import *
result=compound(end_fixture(1).translate((80,110,0)),
                end_fixture(-1).translate((80,120,0)),
                key_print().translate((160,115,0)))
