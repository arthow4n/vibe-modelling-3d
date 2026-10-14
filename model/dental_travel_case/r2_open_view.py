"""Inspection-only flat-open pose; held item proxies are not printable."""
from r2_design import build,assembly
result=assembly(build(),phi=180,theta=0,loaded=True)
