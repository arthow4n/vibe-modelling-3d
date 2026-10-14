"""Inspection pose only; use separate print layouts for manufacturing."""
from r2_design import build,assembly
from r2_geometry import CLOSED_LINK_ANGLE
result=assembly(build(),phi=0,theta=CLOSED_LINK_ANGLE,loaded=False)
