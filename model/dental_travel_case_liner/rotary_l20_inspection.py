"""Inspection only: half-section of the lined rotary case, in installed poses."""
import cadquery as cq
from rotary_l20_design import rigid,installed,block
p=rigid();result=cq.Assembly(name='rotary_L20_installed_section')
window=block(110,45,280,y=-22.5,z=-1)
for name in ('body','cap'):
    # Turn the open section toward the standard isometric camera.
    result.add(p[name].intersect(window).rotate((0,0,0),(0,0,1),180),name='rigid_'+name)
    result.add(installed(name).intersect(window).rotate((0,0,0),(0,0,1),180),name='TPU_'+name)
