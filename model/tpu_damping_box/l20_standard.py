"""Current L20 sandwich standard, shared by experiment and application builders.

All active flat damping panels use the same normal section in millimetres.
Corner lands, installation transitions and rim closures are solid boundaries.
"""
from math import floor
import cadquery as cq

SKIN = .8
CORE = .4
TOTAL = 2 * SKIN + CORE
TIE = .8
PITCH = 4.4
LAND = 4.
RIM_CAP = .4


def centres(span, *, end_margin):
    count = floor((span - 2 * end_margin - TIE) / PITCH) + 1
    if count < 1:
        raise ValueError((span, end_margin))
    return tuple((i - (count - 1) / 2) * PITCH for i in range(count))


def floor_void(width, depth):
    """Shared enclosed floor core with full posts and solid perimeter lands."""
    air = (cq.Workplane('XY').box(width - 2 * LAND, depth - 2 * LAND, CORE,
                                 centered=(True, True, False)).translate((0, 0, SKIN)))
    posts = cq.Compound.makeCompound([
        cq.Workplane('XY').box(TIE, TIE, CORE, centered=(True, True, False))
        .translate((x, y, SKIN)).val()
        for x in centres(width, end_margin=LAND)
        for y in centres(depth, end_margin=LAND)])
    return air.cut(posts)
