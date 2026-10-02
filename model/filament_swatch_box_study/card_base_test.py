"""Printable 15-card base trial; flat underside on the bed, millimetres.

Funnel entrances correct small placement errors before the straight guides.
No cover, latch or reference cards are selected for export.
"""
import cadquery as cq

from study import UPRIGHT_WIDTH, CARD_THICKNESS

CARD_COUNT = 15
SLOT_PITCH = 7.0
SLOT_WIDTH = CARD_THICKNESS + 0.8  # Total lower-slot clearance, not per side.
MOUTH_WIDTH = 5.6  # Before the small rounding at the divider crests.
STRAIGHT_DEPTH = 14.0
FUNNEL_DEPTH = 4.0
SIDE_CLEARANCE = 2.0
SIDE_LEAD = 1.2
END_MARGIN = 4.0
FLOOR = 2.4
WALL = 2.8
CORNER_RADIUS = 3.0
CREST_RADIUS = 0.4
BED_CHAMFER = 0.4

INNER_WIDTH = UPRIGHT_WIDTH + 2 * SIDE_CLEARANCE
OUTER_WIDTH = INNER_WIDTH + 2 * WALL
THROAT_Z = FLOOR + STRAIGHT_DEPTH
TOP_Z = THROAT_Z + FUNNEL_DEPTH

assert SLOT_WIDTH > CARD_THICKNESS
assert SLOT_WIDTH < MOUTH_WIDTH < SLOT_PITCH
assert SLOT_PITCH - MOUTH_WIDTH > 2 * CREST_RADIUS
assert WALL > SIDE_LEAD + CREST_RADIUS


def slot_y(index, card_count=CARD_COUNT):
    return (index - (card_count - 1) / 2) * SLOT_PITCH


def outer_depth(card_count=CARD_COUNT):
    return (card_count - 1) * SLOT_PITCH + SLOT_WIDTH + 2 * END_MARGIN + 2 * WALL


def slot_cutter(index, card_count=CARD_COUNT):
    lower = (cq.Workplane("XY", origin=(0, slot_y(index, card_count), FLOOR))
             .rect(INNER_WIDTH, SLOT_WIDTH).extrude(STRAIGHT_DEPTH))
    funnel = (cq.Workplane("XY", origin=(0, slot_y(index, card_count), THROAT_Z))
              .rect(INNER_WIDTH, SLOT_WIDTH)
              .workplane(offset=FUNNEL_DEPTH).rect(INNER_WIDTH + 2 * SIDE_LEAD, MOUTH_WIDTH)
              .workplane(offset=0.2).rect(INNER_WIDTH + 2 * SIDE_LEAD, MOUTH_WIDTH)
              .loft(ruled=True))
    return lower.union(funnel)


def build_base(card_count=CARD_COUNT):
    assert card_count >= 1
    base = (cq.Workplane("XY").box(OUTER_WIDTH, outer_depth(card_count), TOP_Z,
                                   centered=(True, True, False))
            .edges("|Z").fillet(CORNER_RADIUS)
            .faces("<Z").edges().chamfer(BED_CHAMFER))
    for index in range(card_count):
        base = base.cut(slot_cutter(index, card_count))
    # Round both sides of every divider crest rather than leaving a sharp lip.
    # X edges run across the card width; Y edges are the side-rim entrances.
    return base.edges(">Z").fillet(CREST_RADIUS)


if __name__ in ("__main__", "__cqgi__"):
    result = build_base()
