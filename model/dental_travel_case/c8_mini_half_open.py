"""Inspection: intermediate 90-degree fold with connection outside storage."""
from spine_design import build,MINI,assembly
result=assembly(build('tpu_spine',size=MINI),90)
