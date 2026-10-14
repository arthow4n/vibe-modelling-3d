"""Inspection only: closed M1 exterior, assembled rather than print placement."""
from m1_design import build, configuration
result = configuration(build(), cap_lift=0, contents=False, releases=(0, 0))
