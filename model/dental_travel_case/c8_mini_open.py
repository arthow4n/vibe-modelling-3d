"""Inspection: complete C8 mini box open flat, including bent TPU spines."""
from spine_design import build,MINI,assembly
result=assembly(build('tpu_spine',size=MINI),180)
