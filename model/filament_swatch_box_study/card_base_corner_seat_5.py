"""Five-card trial: rigid bottom-corner seats and a firmer front clip.

Print flat floor down in PETG, 0.4 mm nozzle / 0.2 mm layers. Units mm.
Earlier printed sources remain unchanged. No side spring, cover or reference card.
"""
import cadquery as cq
from study import UPRIGHT_WIDTH, swatch_dimension
from card_base_test import (
    FLOOR, INNER_WIDTH, OUTER_WIDTH, TOP_Z, SLOT_WIDTH, CORNER_RADIUS,
    BED_CHAMFER, CREST_RADIUS, outer_depth, slot_y, slot_cutter,
)
from card_base_petg_5 import (
    block, FRONT_PAD_X, FRONT_PAD_WIDTH, FRONT_LEAF_WIDTH, FRONT_ROOT_Y,
    FRONT_FREE_Y, FRONT_RELIEF_BACK_Y, RAMP_START, PAD_HEIGHT,
    LEAF_HEIGHT, ROOT_OVERLAP, RELIEF_SIDE_GAP,
)

CARD_COUNT = 5
FRONT_LEAF_THICKNESS = 1.2  # Previous good-grip stem was 1.0 mm.
BOTTOM_CORNER_CHAMFER = swatch_dimension('left_chamfer_size')
SEAT_HALF_SPAN = UPRIGHT_WIDTH/2 - BOTTOM_CORNER_CHAMFER
FLOOR_RELIEF_DEPTH = 0.6  # Leaves 1.8 mm of floor under central card edge.
PAD_RADIUS = 0.25

assert 0 < FLOOR_RELIEF_DEPTH < FLOOR
assert SEAT_HALF_SPAN > 0
assert FRONT_RELIEF_BACK_Y-FRONT_ROOT_Y-FRONT_LEAF_THICKNESS >= 1.0-1e-9


def corner_seat(y, side):
    """45-degree support for a card's bottom chamfer; grows from the floor."""
    inner = SEAT_HALF_SPAN
    outer = INNER_WIDTH/2
    bottom = FLOOR-FLOOR_RELIEF_DEPTH-ROOT_OVERLAP
    points = [(side*inner, bottom), (side*outer, bottom),
              (side*outer, FLOOR+outer-inner), (side*inner, FLOOR)]
    return (cq.Workplane('XZ', origin=(0, y+SLOT_WIDTH/2, 0))
            .polyline(points).close().extrude(SLOT_WIDTH))


def front_leaf(y):
    stem = block(FRONT_PAD_X-FRONT_LEAF_WIDTH/2, FRONT_PAD_X+FRONT_LEAF_WIDTH/2,
                 y+FRONT_ROOT_Y, y+FRONT_ROOT_Y+FRONT_LEAF_THICKNESS,
                 FLOOR-ROOT_OVERLAP, FLOOR+LEAF_HEIGHT)
    points = [(FRONT_ROOT_Y, FLOOR+RAMP_START),
              (FRONT_ROOT_Y, FLOOR+LEAF_HEIGHT),
              (FRONT_FREE_Y, FLOOR+PAD_HEIGHT)]
    pad = (cq.Workplane('YZ', origin=(FRONT_PAD_X-FRONT_PAD_WIDTH/2, y, 0))
           .polyline(points).close().extrude(FRONT_PAD_WIDTH))
    return stem.union(pad).edges(cq.selectors.NearestToPointSelector(
        (FRONT_PAD_X, y+FRONT_FREE_Y, FLOOR+PAD_HEIGHT))).fillet(PAD_RADIUS)


def build_base(count=CARD_COUNT, include_leaves=True):
    assert count >= 1
    base = (cq.Workplane('XY').box(OUTER_WIDTH, outer_depth(count), TOP_Z,
                                   centered=(True,True,False))
            .edges('|Z').fillet(CORNER_RADIUS)
            .faces('<Z').edges().chamfer(BED_CHAMFER))
    for index in range(count):
        base = base.cut(slot_cutter(index, count))
    base = base.edges('>Z').fillet(CREST_RADIUS)
    for index in range(count):
        y = slot_y(index, count)
        # Small central depth relief permits narrower cards to reach both ramps.
        base = base.cut(block(-INNER_WIDTH/2, INNER_WIDTH/2,
                              y-SLOT_WIDTH/2, y+SLOT_WIDTH/2,
                              FLOOR-FLOOR_RELIEF_DEPTH, FLOOR+0.05))
        base = base.union(corner_seat(y,-1)).union(corner_seat(y,1))
        relief = block(FRONT_PAD_X-FRONT_LEAF_WIDTH/2-RELIEF_SIDE_GAP,
                       FRONT_PAD_X+FRONT_LEAF_WIDTH/2+RELIEF_SIDE_GAP,
                       y+FRONT_ROOT_Y-0.05, y+FRONT_RELIEF_BACK_Y,
                       FLOOR, TOP_Z+0.2)
        base = base.cut(relief)
        if include_leaves:
            base = base.union(front_leaf(y))
    return base


if __name__ in ('__main__','__cqgi__'):
    result = build_base()
