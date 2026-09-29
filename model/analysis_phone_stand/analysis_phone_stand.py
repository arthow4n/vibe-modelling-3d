"""Final shared print layout, mm. See README for solid PETG and hardware."""
import cadquery as cq
from components import printable_parts
parts=printable_parts()
placements={'base':(45,5,0),'arm':(115,35,0),'cradle':(185,40,0),'latch':(115,180,0)}
result=cq.Compound.makeCompound([part.translate(placements[name]).val() for name,part in parts.items()])
