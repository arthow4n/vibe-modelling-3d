"""Five-card PETG locating-seat trial. Flat floor down; units millimetres.

The previous free-clearance prototype remains in card_base_test_5.py.
Leaves are printed relaxed; real cards bend them against the locating surfaces.
"""
import cadquery as cq

from card_base_test import (
    FLOOR, INNER_WIDTH, OUTER_WIDTH, TOP_Z, THROAT_Z,
    SLOT_WIDTH, MOUTH_WIDTH, SIDE_LEAD, CORNER_RADIUS, BED_CHAMFER,
    CREST_RADIUS, outer_depth, slot_y,
)

CARD_COUNT = 5
END_DATUM_X = -25.0  # At the square bed/back edge of the swatch's bevel.
FREE_RIGHT_X = 27.0
FRONT_LEAF_THICKNESS = 1.0
SIDE_LEAF_THICKNESS = 0.8
FRONT_PAD_X = 7.0
FRONT_LEAF_WIDTH = 28.0
FRONT_PAD_WIDTH = 4.0  # Original swatch Y=16..20: outside text/dome/windows.
FRONT_ROOT_Y = SLOT_WIDTH / 2
FRONT_FREE_Y = 0.25  # Nominal seated front face is +0.6: 0.35 mm preload.
FRONT_RELIEF_BACK_Y = 3.6
SIDE_ROOT_X = 26.0
SIDE_FREE_X = 24.45  # Nominal square back edge at X=25: 0.55 mm preload.
SIDE_LEAF_BACK_Y = -1.2
SIDE_LEAF_WIDTH = 1.0  # Contact near flat back; front edge is rounded.
SIDE_RELIEF_OUTER_X = 28.0
RAMP_START = 10.0
PAD_HEIGHT = 13.0
LEAF_HEIGHT = 16.0
ROOT_OVERLAP = 0.1
RELIEF_SIDE_GAP = 0.8


def block(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0,
                                    centered=(False, False, False))
            .translate((x0, y0, z0)))


def slot_cutter(index, count):
    y = slot_y(index, count)
    width = FREE_RIGHT_X - END_DATUM_X
    centre = (FREE_RIGHT_X + END_DATUM_X) / 2
    lower = block(END_DATUM_X, FREE_RIGHT_X, y-SLOT_WIDTH/2, y+SLOT_WIDTH/2,
                  FLOOR, THROAT_Z)
    # Both end faces and both broad faces open outward, retaining the old mouth.
    funnel = (cq.Workplane("XY", origin=(centre, y, THROAT_Z))
              .rect(width, SLOT_WIDTH)
              .workplane(offset=TOP_Z-THROAT_Z)
              .center(-centre, 0).rect(INNER_WIDTH+2*SIDE_LEAD, MOUTH_WIDTH)
              .workplane(offset=0.2).rect(INNER_WIDTH+2*SIDE_LEAD, MOUTH_WIDTH)
              .loft(ruled=True))
    return lower.union(funnel)


def front_leaf(y):
    z = FLOOR
    # No suspended horizontal arm: grows from the floor, then a gradual pad.
    stem = block(FRONT_PAD_X-FRONT_LEAF_WIDTH/2,
                 FRONT_PAD_X+FRONT_LEAF_WIDTH/2,
                 y+FRONT_ROOT_Y, y+FRONT_ROOT_Y+FRONT_LEAF_THICKNESS,
                 z-ROOT_OVERLAP, z+LEAF_HEIGHT)
    profile = [(FRONT_ROOT_Y, z+RAMP_START),
               (FRONT_ROOT_Y, z+LEAF_HEIGHT), (FRONT_FREE_Y, z+PAD_HEIGHT)]
    pad = (cq.Workplane("YZ", origin=(FRONT_PAD_X-FRONT_PAD_WIDTH/2, y, 0))
           .polyline(profile).close().extrude(FRONT_PAD_WIDTH))
    leaf = stem.union(pad)
    return leaf.edges(cq.selectors.NearestToPointSelector(
        (FRONT_PAD_X, y+FRONT_FREE_Y, z+PAD_HEIGHT))).fillet(0.25)


def side_leaf(y):
    z = FLOOR
    profile = [(SIDE_ROOT_X, z-ROOT_OVERLAP),
               (SIDE_ROOT_X+SIDE_LEAF_THICKNESS, z-ROOT_OVERLAP),
               (SIDE_ROOT_X+SIDE_LEAF_THICKNESS, z+LEAF_HEIGHT),
               (SIDE_ROOT_X, z+LEAF_HEIGHT),
               (SIDE_FREE_X, z+PAD_HEIGHT),
               (SIDE_ROOT_X, z+RAMP_START)]
    # XZ normal points toward -Y; grow back from the higher-Y end.
    leaf = (cq.Workplane("XZ", origin=(0, y+SIDE_LEAF_BACK_Y+SIDE_LEAF_WIDTH, 0))
            .polyline(profile).close().extrude(SIDE_LEAF_WIDTH))
    return leaf.edges(cq.selectors.NearestToPointSelector(
        (SIDE_FREE_X, y+SIDE_LEAF_BACK_Y+SIDE_LEAF_WIDTH/2,
         z+PAD_HEIGHT))).fillet(0.25)


def build_base(count=CARD_COUNT, include_leaves=True):
    assert count >= 1
    base = (cq.Workplane("XY").box(OUTER_WIDTH, outer_depth(count), TOP_Z,
                                   centered=(True, True, False))
            .edges("|Z").fillet(CORNER_RADIUS)
            .faces("<Z").edges().chamfer(BED_CHAMFER))
    for index in range(count):
        base = base.cut(slot_cutter(index, count))
    base = base.edges(">Z").fillet(CREST_RADIUS)
    for index in range(count):
        y = slot_y(index, count)
        front_relief = block(
            FRONT_PAD_X-FRONT_LEAF_WIDTH/2-RELIEF_SIDE_GAP,
            FRONT_PAD_X+FRONT_LEAF_WIDTH/2+RELIEF_SIDE_GAP,
            y+FRONT_ROOT_Y-0.05, y+FRONT_RELIEF_BACK_Y,
            FLOOR, TOP_Z+0.2)
        side_relief = block(SIDE_ROOT_X-0.25, SIDE_RELIEF_OUTER_X,
                            y+SIDE_LEAF_BACK_Y-RELIEF_SIDE_GAP,
                            y+SIDE_LEAF_BACK_Y+SIDE_LEAF_WIDTH+RELIEF_SIDE_GAP,
                            FLOOR, TOP_Z+0.2)
        base = base.cut(front_relief).cut(side_relief)
        if include_leaves:
            base = base.union(front_leaf(y)).union(side_leaf(y))
    return base


if __name__ in ("__main__", "__cqgi__"):
    result = build_base()
