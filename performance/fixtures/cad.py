"""Deterministic tool benchmark fixture; not a printable product."""
import cadquery as cq
result = cq.Workplane('XY').box(30, 20, 8).edges('|Z').fillet(2).faces('>Z').workplane().hole(5)
