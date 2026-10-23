"""Inspection only: actual half-section through M3 head, clamp, hood and nut.

Displayed wall side is upward, room/front side downward. Not printable geometry.
"""
import cadquery as cq
from vent_parameters import Parameters
from assembly import configuration

if __name__ in ('__main__','__cqgi__'):
    p=Parameters()
    pose=configuration(p,p.clamp_free_diameter,0,include_hardware=True)
    window=(cq.Workplane('XY',origin=(p.mount_radius,-6,18)).box(35,12,26).val())
    pieces=[]
    for name in ('hood','clamp','M3_head_1','M3_nut_1'):
        shape=pose.shape(name).rotate((0,0,0),(0,0,1),p.mount_angles[0])
        pieces.append(shape.intersect(window))
    result=cq.Compound.makeCompound(pieces).rotate((0,0,0),(1,0,0),180).translate((0,0,35))
