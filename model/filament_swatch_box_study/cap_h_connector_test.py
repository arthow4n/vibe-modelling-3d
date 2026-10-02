"""H actual-end fit sample; floor down and key flat. No hoods in this sample."""
from cap_h_module_5 import *
result=compound(end_fixture(1).translate((80,110,0)),
                end_fixture(-1).translate((80,120,0)),
                key_print().translate((150,115,0)))
