"""Inspection only: assembled M2B with the cap removed to reveal its long guide."""
from m2b_design import build,configuration
result=configuration(build(),cap_lift=48,releases=(0,0))
