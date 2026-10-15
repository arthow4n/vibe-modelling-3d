"""Inspection only: H and I half-sections reveal their hidden webs."""
import cadquery as cq
from design import cup, pad_closed, block, FLOOR
result=cq.Assembly(name='selected_sections')
for i,name in enumerate(('H','I')):
    mask=block(40,20,45).translate((0,10,0))
    result.add(cup(name).intersect(mask),name=f'cup_{name}',loc=cq.Location((45*i,0,0)))
    result.add(pad_closed(name).translate((0,0,-FLOOR)).intersect(mask),name=f'pad_{name}',loc=cq.Location((45*i,0,0)))
