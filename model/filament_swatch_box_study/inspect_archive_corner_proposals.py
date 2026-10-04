"""Inspection-only comparison: continuous, L corners, continuous side guides."""
import archive_corner_proposals as p
import swatch_reference as ref

parts = []
for i,name in enumerate(('continuous','corner','side_guides')):
    shift = i*86.
    parts.append(p.base(name).translate((shift,0,0)))
    for n in range(3):
        parts.append(ref.card((n-1)*ref.THICKNESS-ref.THICKNESS/2)
                     .translate((shift,0,0)))
result = p.r1.g.compound(*parts)
