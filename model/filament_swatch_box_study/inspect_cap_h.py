"""H full product inspection; one closed module and one open with three cards."""
from cap_h_module_5 import *
b=base()
items=[]
for i,y in enumerate(module_centres(2)):
    items.append(b.translate((0,y,0)))
    items.extend(c.translate((0,y,0)) for c in contents(COUNT,sparse=i==0))
    if i==1: items.append(cap().translate((0,y,0)))
result=compound(*items,connector())
