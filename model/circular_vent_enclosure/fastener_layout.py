"""Inspection only: exploded rear view with nominal metal hardware. Not printable."""
from vent_parameters import Parameters
from assembly import configuration

if __name__ in ('__main__','__cqgi__'):
    p=Parameters()
    result=configuration(p,p.clamp_free_diameter,18,include_hardware=True).assembly().toCompound()
    result=result.rotate((0,0,0),(1,0,0),180).translate((0,0,p.depth+18))
