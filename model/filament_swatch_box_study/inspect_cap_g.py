"""G full product: one closed module, one open module, key in place."""
from cap_g_module_5 import *
poses=module_centres(2)
items=[]
for i,y in enumerate(poses):
    items.append(base().translate((0,y,0)))
    items.extend(c.translate((0,y,0)) for c in contents(COUNT,sparse=(i==0)))
    if i==1:
        items.append(cap().translate((0,y,0)))
items.append(connector())
items.append(hood_print(cap()).translate((FOOT_X+15,0,0)))
result=compound(*items)
