"""V1 section: thin waist on an existing closure leaf, relaxed overlap shown.

This is geometry explanation, not a solved deformed contact pose. No exports.
"""
import cadquery as cq
import cap_v1_vase_hood_5 as v

y=v.g.detent_centres(v.g.COUNT)[0]
window=cq.Workplane('XY').box(8,.08,21).translate((v.g.OUTSIDE_X/2-2,y,15.5))
result=v.g.compound(v.nominal_shell().intersect(window),v.g.leaf(y).intersect(window))
