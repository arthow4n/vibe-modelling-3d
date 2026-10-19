"""Captive mini box, open 90 degrees in a V; broad panels slope 45 degrees.

The mirrored R4 exterior corners have equal lowest tangencies. Their analytical
bed translation avoids lifting either disconnected moving part above the bed.
"""
import math
import cadquery as cq
from internal_hinge_design import build, MINI, rotate, closure


def layout():
    p=build('internal_cone',size=MINI)
    rise=MINI.depth/2/math.sqrt(2)-4*math.sqrt(2)+4
    a=cq.Assembly(name='C7_captive_V_trial')
    for name in ('body','lid'):
        part=p[name] if name=='body' else rotate(p,p[name],90)
        part=part.rotate((0,0,0),(1,0,0),-45).translate((0,0,rise))
        a.add(part,name=name)
    keeper=closure.keeper().rotate((0,0,0),(0,1,0),-90).translate((70,10,5.5))
    a.add(keeper,name='keeper')
    return a


result=layout()
