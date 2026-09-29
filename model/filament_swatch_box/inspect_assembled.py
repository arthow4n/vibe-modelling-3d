"""Closed inspection pose only; print the main entry point's separate flat parts."""
import cadquery as cq
from components import body, lid, LID_Z
result = cq.Compound.makeCompound([body().val(), lid().translate((0, 0, LID_Z)).val()])
