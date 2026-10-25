"""R6 short circular TPU coil with two shallow opposite printing flats; mm.

The winding and cord section are circular, not polygonal. Only the outer
bottom/top caps are trimmed; the bore and curved side walls remain round.
"""
import cadquery as cq

OUTSIDE_DIAMETER = 15.0
CORD_DIAMETER = 3.2
TURN_GAP = 1.2
TURNS = 5
FLAT_TRIM = 0.5
MEAN_RADIUS = (OUTSIDE_DIAMETER - CORD_DIAMETER) / 2
PITCH = CORD_DIAMETER + TURN_GAP
RISE = TURNS * PITCH
OVERALL_LENGTH = RISE + CORD_DIAMETER
FLAT_HEIGHT = OUTSIDE_DIAMETER - 2 * FLAT_TRIM
AXIS_HEIGHT = FLAT_HEIGHT / 2


def section(axial_position):
    """Radial/axial circular section, using the proven R3/R4 sweep convention."""
    return cq.Workplane('XZ').moveTo(MEAN_RADIUS, axial_position).circle(CORD_DIAMETER / 2)


def build_axial():
    if not (0 < CORD_DIAMETER < 2 * MEAN_RADIUS):
        raise ValueError('Round cord must leave an open bore')
    if TURN_GAP <= 0 or not isinstance(TURNS, int) or TURNS < 3:
        raise ValueError('Need separated turns and at least three full circuits')
    if not 0 < FLAT_TRIM < CORD_DIAMETER / 2:
        raise ValueError('Printing flats must retain the winding centerline and bore')
    start = CORD_DIAMETER / 2
    edges = []
    for turn in range(TURNS):
        edges.extend(cq.Wire.makeHelix(PITCH, PITCH, MEAN_RADIUS)
                     .translate((0, 0, start + turn * PITCH)).Edges())
    coil = section(start).sweep(cq.Wire.assembleEdges(edges), isFrenet=True)
    first = section(start).revolve(360, (0, 0), (0, 1))
    last = (section(start + RISE).revolve(360, (0, 0), (0, 1))
            .rotate((0, 0, 0), (0, 0, 1), 90))
    # Fuse at once: sequential periodic unions previously lost middle turns.
    return coil.val().fuse(first.val(), last.val())


def build_sample():
    horizontal = build_axial().rotate((0, 0, 0), (0, 1, 0), 90)
    slab = (cq.Workplane('XY')
            .box(OVERALL_LENGTH + 2, OUTSIDE_DIAMETER + 2, FLAT_HEIGHT)
            .translate((OVERALL_LENGTH / 2, 0, 0)).val())
    shape = horizontal.intersect(slab).translate((0, 0, AXIS_HEIGHT))
    # Retain closed in-envelope terminal turns and the complete intervening cord.
    anchors = [cq.Vector(CORD_DIAMETER / 2 + t * PITCH, 0, AXIS_HEIGHT - MEAN_RADIUS)
               for t in (0, 2, TURNS)]
    if not any(all(s.isInside(p, 1e-6) for p in anchors) for s in shape.Solids()):
        raise ValueError('Terminal fusion or flat trimming lost winding material')
    return cq.Workplane(obj=shape)


if __name__ in ('__main__', '__cqgi__'):
    result = build_sample()
