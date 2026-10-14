"""Inspection only, loaded rounded case; reference items are not printable."""
from r2_design import build,assembly
from r2_geometry import CLOSED_LINK_ANGLE
result=assembly(build(),phi=0,theta=CLOSED_LINK_ANGLE,loaded=True)
