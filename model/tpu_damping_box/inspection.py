"""Inspection only: section through C, with a removed cup and lifted pad."""
import cadquery as cq
from design import assembled, block, cup, pad_print, FLOOR
# Rear half-section makes the floor, all lining layers and mating seam visible.
a = assembled('C')
mask = block(60, 30, 60).translate((0,15,0))
scene = cq.Assembly(name='inspection')
for name in ('body','cup','pad','lid'):
    part = a.objects[name].obj
    if name == 'cup':
        part = part.translate((0,0,FLOOR))
    scene.add(part.intersect(mask), name=name)
# Beside it, the complete cup and lifted roof pad show removal and channels.
scene.add(cup('C').translate((58,0,0)), name='removed_cup')
scene.add(pad_print('C').rotate((0,0,0),(1,0,0),180).translate((58,0,46)), name='lifted_pad')
result = scene
