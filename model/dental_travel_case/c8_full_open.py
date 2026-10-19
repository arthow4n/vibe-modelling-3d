"""Inspection only: full-size C8 architecture opened flat; packing unqualified."""
from spine_design import build,FULL,assembly
result=assembly(build('tpu_spine',size=FULL),180)
