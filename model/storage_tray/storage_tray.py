"""Rounded storage tray, millimetres; underside on Z=0."""
import cadquery as cq
from math import cos, sin, radians

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
CORNER_FACET_SHIFT = 10.0  # degrees: stagger shoulder vertices for triangular facets


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
    assert 0 <= CORNER_FACET_SHIFT <= 12
    assert (INNER_RADIUS + RIM_WALL)*cos(radians(15)) - INNER_RADIUS > 2*RIM_FILLET
    assert RIM_WALL > 2 * RIM_FILLET
    rim_radius = INNER_RADIUS + RIM_WALL
    # Explicit planar faces preserve the triangular corner detail (a smooth
    # loft would erase it). Straight sides remain single broad planes.
    def ring(radius, z, angles):
        points = []
        centre = INTERIOR_WIDTH / 2 - INNER_RADIUS
        for quadrant in range(4):
            rotation = radians(90 * quadrant)
            for angle in angles:
                x = centre + radius*cos(radians(angle))
                y = centre + radius*sin(radians(angle))
                points.append(cq.Vector(x*cos(rotation)-y*sin(rotation),
                                        x*sin(rotation)+y*cos(rotation), z))
        return points

    top = ring(rim_radius, HEIGHT, [0, 30, 60, 90])
    shoulder_angles = [0, 30-CORNER_FACET_SHIFT, 60+CORNER_FACET_SHIFT, 90]
    middle = ring(rim_radius+OUTER_BULGE, SHOULDER_HEIGHT, shoulder_angles)
    bottom = ring(rim_radius+OUTER_BULGE-LOWER_INSET, 0, shoulder_angles)
    faces = []

    def face(points):
        faces.append(cq.Face.makeFromWires(cq.Wire.makePolygon(points, close=True)))

    face(list(reversed(bottom)))
    face(top)
    for i in range(len(top)):
        j = (i+1) % len(top)
        face([bottom[i], bottom[j], middle[j], middle[i]])
        if i % 4 in (1, 3):  # symmetric centre facet or straight side
            face([middle[i], middle[j], top[j], top[i]])
        elif i % 4 == 2:  # mirror the first corner panel
            face([middle[i], middle[j], top[j]])
            face([middle[i], top[j], top[i]])
        else:
            face([middle[i], middle[j], top[i]])
            face([middle[j], top[j], top[i]])
    outer = cq.Workplane('XY').add(cq.Solid.makeSolid(cq.Shell.makeShell(faces)))
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
