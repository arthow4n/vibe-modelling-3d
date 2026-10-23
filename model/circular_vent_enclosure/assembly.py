"""Installed poses: wall Z=0, room +Z. Hardware/valve are inspection references."""
from functools import cache
import cadquery as cq
from assembly_geometry import Configuration
from vent_parameters import Parameters
from circular_vent_enclosure import build
from mounting_clamp import build_clamp, bolt_position


@cache
def hood_component(p):
    return build(p)


@cache
def components(p, diameter):
    return hood_component(p), build_clamp(p,diameter)


def configuration(p, diameter, withdrawal):
    base_hood, clamp = components(p,diameter)
    hood=base_hood.rotate((0,0,0),(1,0,0),180).translate((0,0,p.depth+withdrawal))
    assembly=(cq.Assembly(name='vent').add(hood,name='hood',color=cq.Color(0.25,0.5,0.8))
              .add(clamp,name='clamp',color=cq.Color(0.9,0.55,0.2)))
    return Configuration.explicit(assembly,name=f'diameter-{diameter}-withdrawal-{withdrawal}',
        kind='operating' if withdrawal==0 else 'intermediate',
        parameters={'diameter_mm':diameter,'withdrawal_mm':withdrawal})


if __name__ in ('__main__','__cqgi__'):
    p=Parameters()
    result=configuration(p,p.valve_diameter,0).assembly()
