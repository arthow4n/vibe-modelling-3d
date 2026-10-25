"""R7: circular TPU winding swept from a flat-sided rounded-square section.

Millimetres. Flat inner/outer lands are part of the swept profile everywhere;
no trimming, shaved contact patches or polygonal winding are used.
"""
import math
import cadquery as cq

OUTSIDE_DIAMETER = 15.0
RADIAL_WIDTH = 3.2
AXIAL_WIDTH = 3.2
CORNER_RADIUS = 0.6
TURN_GAP = 1.2
TURNS = 5
MEAN_RADIUS = (OUTSIDE_DIAMETER - RADIAL_WIDTH) / 2
PITCH = AXIAL_WIDTH + TURN_GAP
RISE = TURNS * PITCH
OVERALL_LENGTH = RISE + AXIAL_WIDTH
AXIS_HEIGHT = OUTSIDE_DIAMETER / 2


def section(axial_position):
    """Flat inner, outer and axial lands joined by tangent quarter-circle corners."""
    r, z = MEAN_RADIUS, axial_position
    a, b, c = RADIAL_WIDTH / 2, AXIAL_WIDTH / 2, CORNER_RADIUS
    q = c / math.sqrt(2)
    return (cq.Workplane('XZ').moveTo(r - a + c, z - b)
            .lineTo(r + a - c, z - b)
            .threePointArc((r + a - c + q, z - b + c - q), (r + a, z - b + c))
            .lineTo(r + a, z + b - c)
            .threePointArc((r + a - c + q, z + b - c + q), (r + a - c, z + b))
            .lineTo(r - a + c, z + b)
            .threePointArc((r - a + c - q, z + b - c + q), (r - a, z + b - c))
            .lineTo(r - a, z - b + c)
            .threePointArc((r - a + c - q, z - b + c - q), (r - a + c, z - b))
            .close())


def build_terminal_half():
    """Construct the right half with a complete integral terminal eye."""
    if not 0 < CORNER_RADIUS < min(RADIAL_WIDTH, AXIAL_WIDTH) / 2:
        raise ValueError('Corner rounds must leave straight lands on all four sides')
    if MEAN_RADIUS <= RADIAL_WIDTH / 2 or TURN_GAP <= 0 or not isinstance(TURNS, int) or TURNS < 3:
        raise ValueError('Need an open bore, separated turns and at least three circuits')
    start = AXIAL_WIDTH / 2
    edges = []
    for turn in range(TURNS):
        edges.extend(cq.Wire.makeHelix(PITCH, PITCH, MEAN_RADIUS)
                     .translate((0, 0, start + turn * PITCH)).Edges())
    coil = section(start).sweep(cq.Wire.assembleEdges(edges), isFrenet=True)
    first = section(start).revolve(360, (0, 0), (0, 1))
    eye = (section(start + RISE).revolve(360, (0, 0), (0, 1))
           .rotate((0, 0, 0), (0, 0, 1), 90))
    # Remove duplicate overlap before union of coincident radial faces.
    winding = coil.val()
    end = winding.fuse(first.val().cut(winding), eye.val().cut(winding))
    horizontal = (end.rotate((0, 0, 0), (0, 1, 0), 90)
                  .translate((0, 0, AXIS_HEIGHT)))
    mid = OVERALL_LENGTH / 2
    length = OVERALL_LENGTH + 2
    half_space = (cq.Workplane('XY').box(length, OUTSIDE_DIAMETER + 2, OUTSIDE_DIAMETER + 2)
                  .translate((mid + length / 2, 0, AXIS_HEIGHT)).val())
    return horizontal.intersect(half_space)


def build_sample():
    # Rotating the right half reproduces the same circular helix with its other
    # closed eye. Join on the shared axial midplane, avoiding the failed periodic
    # first-eye union. The section and exterior are never shaved or flattened.
    half = build_terminal_half()
    mid = OVERALL_LENGTH / 2
    shape = half.fuse(half.rotate((mid, 0, 0), (mid, 0, 1), 180))
    anchors = []
    for turn in (0, TURNS):
        for degrees in range(0, 360, 30):
            theta = math.radians(degrees)
            anchors.append(cq.Vector(AXIAL_WIDTH / 2 + turn * PITCH,
                MEAN_RADIUS * math.sin(theta), AXIS_HEIGHT - MEAN_RADIUS * math.cos(theta)))
    anchors.append(cq.Vector(AXIAL_WIDTH / 2 + 2 * PITCH, 0, AXIS_HEIGHT - MEAN_RADIUS))
    if not any(all(s.isInside(p, 1e-6) for p in anchors) for s in shape.Solids()):
        raise ValueError('Missing connected winding material or incomplete terminal eye')
    return cq.Workplane(obj=shape)



def profile_inspection():
    """Actual middle-turn radial/axial section, showing the swept flat lands."""
    from cad_inspection import Camera, Frame, Inspection, Label, Region, Section, View
    x = AXIAL_WIDTH / 2 + 2 * PITCH
    z = AXIS_HEIGHT - MEAN_RADIUS
    return Inspection(build_sample(), View(
        Camera((0, -1, 0), up=(0, 0, 1)),
        frame=Frame(Region.around((x, 0, z), (6, 1, 5)), margin_mm=1),
        section=Section((0, 0, 0), (0, 1, 0), mode='planar'),
        annotations=(Label((x, 0, z - RADIAL_WIDTH / 2), 'Outer flat land', offset_px=(35, 45)),
                     Label((x, 0, z + RADIAL_WIDTH / 2), 'Inner flat land', offset_px=(35, -40))),
    ), title='R7 swept cord section',
        purpose='Verify flat inner and outer lands with rounded corners on a real middle turn.')


inspections = {'cord-section': profile_inspection}

if __name__ in ('__main__', '__cqgi__'):
    result = build_sample()
