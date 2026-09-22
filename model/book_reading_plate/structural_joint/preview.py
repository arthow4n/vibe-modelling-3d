"""Inspection poses only; never used as print layouts."""
from pathlib import Path
import cadquery as cq
from joint import P,halves,screw,posed
root=Path(__file__).resolve().parent
a,b=halves(threaded=True);bolt=screw()
# Separate the mating L layers normally to expose both lip and back interfaces.
parts=[a,b.translate((8,12,12))]
parts += [posed(bolt,x,-14,z,True) for x in [-P.hole_x,P.hole_x] for z in P.hole_z]
parts += [posed(bolt,x,P.back_hole_y,-14) for x in [-P.hole_x,P.hole_x]]
result=cq.Compound.makeCompound([p.val() for p in parts]).rotate((0,0,0),(1,0,0),180)
