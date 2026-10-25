"""R9: eight negative corner scallops on retained R8 octagonal TPU cord; mm.

Recess the winding's outward vertices, without changing the swept cord profile
on the broad faces. R5 and R8 sources and exports remain unchanged controls.
"""
import math
import cadquery as cq
import coil_r8_soft_octagon as retained

baseline = retained.baseline
CORNER_DEPTH = 0.55  # radial bite measured from the original sharp R5 vertex
RECESS_HALF_WIDTH = 1.0  # tangent coordinate on either side of each vertex
OUTSIDE_ACROSS_FLATS = baseline.OUTSIDE_ACROSS_FLATS
AXIAL_WIDTH = baseline.AXIAL_WIDTH
RADIAL_WIDTH = baseline.RADIAL_WIDTH
AXIS_HEIGHT = baseline.AXIS_HEIGHT
OVERALL_LENGTH = baseline.OVERALL_LENGTH
PITCH = baseline.PITCH
TURNS = baseline.TURNS
OUTER_APOTHEM = OUTSIDE_ACROSS_FLATS / 2
CORNER_RADIUS = OUTER_APOTHEM / math.cos(math.pi / 8)
FACET_SLOPE = math.tan(math.pi / 8)


def corner_frame(index):
    """Outward normal and transverse tangent at an actual octagon vertex."""
    if index not in range(8):
        raise ValueError('Octagon corner index must be 0..7')
    angle = math.pi / 8 + index * math.pi / 4
    return (math.sin(angle), math.cos(angle)), (math.cos(angle), -math.sin(angle))


def corner_point(index, tangent, radius, axial):
    n, t = corner_frame(index)
    return cq.Vector(axial, n[0] * radius + t[0] * tangent,
                     AXIS_HEIGHT + n[1] * radius + t[1] * tangent)


def recess_radius(tangent):
    """Cubic half-profile, mirrored at its smooth concave center."""
    u = abs(tangent) / RECESS_HALF_WIDTH
    if u > 1:
        raise ValueError('Recess profile coordinate is outside its mouth')
    k = FACET_SLOPE * RECESS_HALF_WIDTH
    return (CORNER_RADIUS - CORNER_DEPTH + (3 * CORNER_DEPTH - 2 * k) * u**2
            + (-2 * CORNER_DEPTH + k) * u**3)


def corner_cutter(index):
    """Axial negative tool with tangent shoulder joins, not a sharp circular gouge."""
    w, d, k = RECESS_HALF_WIDTH, CORNER_DEPTH, FACET_SLOPE
    x = -1.0
    r0, mouth = CORNER_RADIUS - d, CORNER_RADIUS - k * w
    local = [(-w, mouth), (-2 * w / 3, CORNER_RADIUS - 2 * k * w / 3),
             (-w / 3, r0), (0, r0), (w / 3, r0),
             (2 * w / 3, CORNER_RADIUS - 2 * k * w / 3), (w, mouth)]
    points = [corner_point(index, s, r, x) for s, r in local]
    top_right = corner_point(index, w, CORNER_RADIUS + RADIAL_WIDTH, x)
    top_left = corner_point(index, -w, CORNER_RADIUS + RADIAL_WIDTH, x)
    wire = cq.Wire.assembleEdges([
        cq.Edge.makeBezier(points[:4]), cq.Edge.makeBezier(points[3:]),
        cq.Edge.makeLine(points[-1], top_right), cq.Edge.makeLine(top_right, top_left),
        cq.Edge.makeLine(top_left, points[0])])
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(OVERALL_LENGTH + 2, 0, 0))


def recess_corners(original):
    """Apply the eight matching subtractive recesses to retained R8 geometry."""
    flat_length = 2 * OUTER_APOTHEM * math.tan(math.pi / 8)
    if not 0 < RECESS_HALF_WIDTH < flat_length * math.cos(math.pi / 8) / 2:
        raise ValueError('Recess mouths must leave broad original facets between corners')
    if not FACET_SLOPE * RECESS_HALF_WIDTH < CORNER_DEPTH < RADIAL_WIDTH / 3:
        raise ValueError('Need a concave bite with a substantial retained corner ligament')
    shape = original.cut(*(corner_cutter(i) for i in range(8)))
    anchors = [cq.Vector(x, y, z + AXIS_HEIGHT)
               for x in (AXIAL_WIDTH / 2, AXIAL_WIDTH / 2 + baseline.RISE)
               for y, z in baseline.transverse_points()[:-1]]
    anchors.append(cq.Vector(AXIAL_WIDTH / 2 + 2 * PITCH, 0, AXIS_HEIGHT - baseline.MEAN_APOTHEM))
    if not any(all(s.isInside(p, 1e-6) for p in anchors) for s in shape.Solids()):
        raise ValueError('Corner recess removed connected winding or terminal-loop material')
    return cq.Workplane(obj=shape)


def build_sample():
    return recess_corners(retained.build_sample().val())


def corner_inspection():
    """Actual end-plane cut: retained R8 outline versus the new negative corner."""
    from cad_inspection import Camera, Frame, Inspection, Label, Region, Section, View
    original = retained.build_sample().val()
    recessed = recess_corners(original).val()
    scene = cq.Assembly(name='corner_comparison').add(original, name='R8').add(recessed, name='R9')
    x = AXIAL_WIDTH / 2
    tip = corner_point(0, 0, CORNER_RADIUS, x).toTuple()
    floor = corner_point(0, 0, CORNER_RADIUS - CORNER_DEPTH, x).toTuple()
    return Inspection(scene, View(
        Camera((1, 0, 0), up=(0, 0, 1)),
        section=Section((x, 0, 0), (1, 0, 0), mode='planar'),
        frame=Frame(Region.around(floor, (1, 3.1, 2.9)), margin_mm=.1),
        colors=(('R8', '#a7adb5'), ('R9', '#16768e')),
        annotations=(Label(tip, 'Retained R8 tip', offset_px=(20, -60)),
                     Label(floor, 'R9 negative corner recess', offset_px=(-45, 80)))),
        title='R9 recesses the octagon vertex',
        purpose='Gray: retained R8. Teal: R9. The eight corner bites join the broad facets tangentially.')


inspections = {'negative-corner': corner_inspection}

if __name__ in ('__main__', '__cqgi__'):
    result = build_sample()
