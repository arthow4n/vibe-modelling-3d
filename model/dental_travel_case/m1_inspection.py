"""Inspection only: cap removed; measured-item proxies are not printable parts."""
from m1_design import build, configuration
parts = build()
result = configuration(parts, cap_lift=106, contents=True, releases=(0, 0))
