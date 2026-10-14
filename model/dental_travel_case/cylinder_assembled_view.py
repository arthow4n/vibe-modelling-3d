"""Inspection only: loaded plain cylinder; content proxies are not printable."""
from cylinder_design import build,assembly
result=assembly(build(),opening_degrees=0,loaded=True)
