"""Decorative faceted tray variant; millimetres, underside at Z=0."""
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
RIM_BAND_HEIGHT = 2.0  # quiet rounded border above the facet pattern
WALL_PANELS = 12  # equal diamond-like raised panels per straight side
FACET_RELIEF = 2.4  # outward distance from the tapered wall plane, mm
RIDGE_FRACTION = 0.0  # 0: point peak; >0: vertical ridge as a fraction of panel height
CORNER_FACET_SHIFT = 10.0  # degrees: stagger shoulder vertices for triangular facets


def rounded_wire(width, radius, z):
    h = width / 2
    return (cq.Workplane('XY').workplane(offset=z)
            .moveTo(-h + radius, -h).lineTo(h - radius, -h)
            .radiusArc((h, -h + radius), -radius).lineTo(h, h - radius)
            .radiusArc((h - radius, h), -radius).lineTo(-h + radius, h)
            .radiusArc((-h, h - radius), -radius).lineTo(-h, -h + radius)
            .radiusArc((-h + radius, -h), -radius).close().val())


def build_tray(wall_panels=WALL_PANELS, facet_relief=FACET_RELIEF, ridge_fraction=RIDGE_FRACTION):
    assert 0 <= ridge_fraction <= 0.5
    assert wall_panels >= 2 and wall_panels % 2 == 0
    assert 0 < facet_relief <= 3.0
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

    top = ring(rim_radius, HEIGHT-RIM_BAND_HEIGHT, [0, 30, 60, 90])
    rim = ring(rim_radius, HEIGHT, [0, 30, 60, 90])
    shoulder_angles = [0, 30-CORNER_FACET_SHIFT, 60+CORNER_FACET_SHIFT, 90]
    middle = ring(rim_radius+OUTER_BULGE, SHOULDER_HEIGHT, shoulder_angles)
    bottom = ring(rim_radius+OUTER_BULGE-LOWER_INSET, 0, shoulder_angles)
    faces = []

    def face(points):
        faces.append(cq.Face.makeFromWires(cq.Wire.makePolygon(points, close=True)))

    face(list(reversed(bottom)))
    face(rim)
    for i in range(len(top)):
        j = (i+1) % len(top)
        face([top[i], top[j], rim[j], rim[i]])
        face([bottom[i], bottom[j], middle[j], middle[i]])
        if i % 4 == 3:
            # Each shallow pyramid splits a panel into four real planar facets.
            # Shared boundary vertices make a closed CAD shell, not a mesh model.
            normal = cq.Vector(-(top[j]-top[i]).y, (top[j]-top[i]).x, 0).normalized()*-1
            for panel in range(wall_panels):
                u, v = panel/wall_panels, (panel+1)/wall_panels
                a = middle[i] + (middle[j]-middle[i])*u
                b = middle[i] + (middle[j]-middle[i])*v
                c = top[i] + (top[j]-top[i])*v
                d = top[i] + (top[j]-top[i])*u
                peak = (a+b+c+d)*0.25 + normal*facet_relief
                if ridge_fraction == 0:
                    face([a, b, peak])
                    face([b, c, peak])
                    face([c, d, peak])
                    face([d, a, peak])
                else:
                    # Follow the wall taper so both ridge ends have equal relief.
                    half_ridge = ((c+d)-(a+b))*0.25*ridge_fraction
                    low, high = peak-half_ridge, peak+half_ridge
                    face([a, b, low])
                    face([b, c, high])
                    face([b, high, low])
                    face([c, d, high])
                    face([d, a, low])
                    face([d, low, high])
        elif i % 4 == 1:  # symmetric centre corner facet
            face([middle[i], middle[j], top[j], top[i]])
        elif i % 4 == 2:  # mirror the first corner panel
            face([middle[i], middle[j], top[j]])
            face([middle[i], top[j], top[i]])
        else:
            face([middle[i], middle[j], top[i]])
            face([middle[j], top[j], top[i]])
    outer = cq.Workplane('XY').add(cq.Solid.makeSolid(cq.Shell.makeShell(faces))).clean()
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
