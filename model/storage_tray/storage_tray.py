"""Rounded storage tray, millimetres; underside on Z=0."""
import cadquery as cq

INTERIOR_WIDTH = 220.0
HEIGHT = 38.0
BASE_THICKNESS = 4.0
INNER_RADIUS = 28.0
RIM_WALL = 4.0
OUTER_BULGE = 5.0  # per side beyond the rim
LOWER_INSET = 2.0
SHOULDER_HEIGHT = 9.0
FLOOR_FILLET = 4.0
RIM_FILLET = 0.8
BED_CHAMFER = 0.6


def rounded_wire(width, radius, z):
    h = width / 2
    return (cq.Workplane('XY').workplane(offset=z)
            .moveTo(-h + radius, -h).lineTo(h - radius, -h)
            .radiusArc((h, -h + radius), -radius).lineTo(h, h - radius)
            .radiusArc((h - radius, h), -radius).lineTo(-h + radius, h)
            .radiusArc((-h, h - radius), -radius).lineTo(-h, -h + radius)
            .radiusArc((-h + radius, -h), -radius).close().val())


def build_tray():
    assert INTERIOR_WIDTH > 2 * INNER_RADIUS
    assert HEIGHT > BASE_THICKNESS + FLOOR_FILLET + RIM_FILLET
    assert RIM_WALL > 2 * RIM_FILLET
    rim_width = INTERIOR_WIDTH + 2 * RIM_WALL
    rim_radius = INNER_RADIUS + RIM_WALL
    sections = [rounded_wire(rim_width + 2*(OUTER_BULGE-LOWER_INSET),
                             rim_radius + OUTER_BULGE-LOWER_INSET, 0),
                rounded_wire(rim_width + 2*OUTER_BULGE,
                             rim_radius + OUTER_BULGE, SHOULDER_HEIGHT),
                rounded_wire(rim_width, rim_radius, HEIGHT)]
    outer = cq.Workplane('XY').add(cq.Solid.makeLoft(sections, ruled=True))
    cavity = (cq.Workplane('XY').add(rounded_wire(INTERIOR_WIDTH, INNER_RADIUS,
                                               BASE_THICKNESS)).toPending()
              .extrude(HEIGHT))
    # Rounding the cutter's bottom leaves a cleanable concave floor transition.
    cavity = cavity.edges('<Z').fillet(FLOOR_FILLET)
    tray = outer.cut(cavity).edges('>Z').fillet(RIM_FILLET)
    tray = tray.edges('<Z').chamfer(BED_CHAMFER)
    solid = tray.val()
    assert solid.isValid() and len(tray.solids().vals()) == 1
    box = solid.BoundingBox()
    assert box.xlen <= 250 and box.ylen <= 250 and box.zlen <= 250
    return tray


result = build_tray()
