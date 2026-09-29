"""Inspection only, no reference phone included in printable result."""
import cadquery as cq
from components import assembled
result=cq.Compound.makeCompound([p.val() for p in assembled().values()])
