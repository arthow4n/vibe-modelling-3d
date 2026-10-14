"""Inspection pose only; use cylinder_case.py cups-down print layout."""
from cylinder_design import build,assembly
result=assembly(build(),opening_degrees=0,loaded=False)
