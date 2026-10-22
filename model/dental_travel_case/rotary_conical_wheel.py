"""Replacement wheel only: outer face down, 45-degree screw recess."""
from rotary_case_design import case
p=case();d=p['dimensions']
result=p['rotor'].rotate((0,0,0),(1,0,0),90).translate((0,d.pivot,d.wheel_front))
