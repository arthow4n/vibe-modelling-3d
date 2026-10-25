"""R8: accepted R5 octagonal coil with recessed, rounded exterior ridges; mm."""
import math
import cadquery as cq
import coil_r5_octagonal as baseline

EXTERIOR_RADIUS = 0.5
# Preserve the R5 nominal winding, section, spacing and terminal-loop construction.
OUTSIDE_ACROSS_FLATS = baseline.OUTSIDE_ACROSS_FLATS
AXIAL_WIDTH = baseline.AXIAL_WIDTH
RADIAL_WIDTH = baseline.RADIAL_WIDTH
PITCH = baseline.PITCH
TURNS = baseline.TURNS
OVERALL_LENGTH = baseline.OVERALL_LENGTH
AXIS_HEIGHT = baseline.AXIS_HEIGHT


def octagonal_offset(point):
    """Distance to the outermost of the eight facet-normal coordinate planes."""
    return max(point.y * math.sin(i * math.pi / 4)
               + (point.z - AXIS_HEIGHT) * math.cos(i * math.pi / 4) for i in range(8))


def exterior_edges(shape):
    """Convex exterior-only ridges; do not blend the bore, roof or inner half."""
    threshold = baseline.MEAN_APOTHEM + RADIAL_WIDTH / 2 - baseline.CORD_CHAMFER
    solids = shape.Solids()
    selected = []
    for edge in shape.Edges():
        if edge.geomType() != 'LINE':
            continue
        points = [v.Center() for v in edge.Vertices()]
        if not points or min(octagonal_offset(p) for p in points) < threshold - 1e-5:
            continue
        faces = edge.ancestors(shape, 'Face').Faces()
        if len(faces) != 2:
            continue
        n1, n2 = (face.normalAt() for face in faces)
        if abs(n1.dot(n2)) > .99999:
            continue
        # Cross-wedge offsets are outside at a convex ridge, inside at a
        # concave junction. Exclude concave terminal unions that could add material.
        transverse = (n1 - n2).normalized() * .03
        point = edge.positionAt(.5)
        if any(s.isInside(p, 1e-6) for s in solids for p in (point + transverse, point - transverse)):
            continue
        selected.append(edge)
    if not selected:
        raise ValueError('No exterior convex ridges selected')
    return selected


def soften_exterior(original):
    """Apply the local edge treatment to the unchanged accepted baseline geometry."""
    if not 0 < EXTERIOR_RADIUS < baseline.CORD_CHAMFER:
        raise ValueError('Exterior rounds must retain the original section flats')
    edges = exterior_edges(original)
    result = cq.Workplane(obj=original).newObject(edges).fillet(EXTERIOR_RADIUS)
    anchors = [cq.Vector(x, y, z + AXIS_HEIGHT)
               for x in (AXIAL_WIDTH / 2, AXIAL_WIDTH / 2 + baseline.RISE)
               for y, z in baseline.transverse_points()[:-1]]
    anchors.append(cq.Vector(AXIAL_WIDTH / 2 + 2 * PITCH, 0,
                            AXIS_HEIGHT - baseline.MEAN_APOTHEM))
    if not any(all(s.isInside(p, 1e-6) for p in anchors) for s in result.val().Solids()):
        raise ValueError('Edge blending lost connected winding or terminal material')
    return result


def build_sample():
    return soften_exterior(baseline.build_sample().val())


def corner_inspection():
    """Compare the real terminal-section silhouette with the accepted sharp control."""
    from cad_inspection import Camera, Frame, Inspection, Label, Region, Section, View
    original = baseline.build_sample().val()
    rounded = soften_exterior(original).val()
    scene = cq.Assembly(name='comparison').add(original, name='R5').add(rounded, name='R8')
    y = OUTSIDE_ACROSS_FLATS / 2 * math.tan(math.pi / 8)
    x = AXIAL_WIDTH / 2
    return Inspection(scene, View(
        Camera((1, 0, 0), up=(0, 0, 1)),
        section=Section((x, 0, 0), (1, 0, 0), mode='planar'),
        frame=Frame(Region.around((x, y, 2 * AXIS_HEIGHT), (1, 2.4, 2.4)), margin_mm=.15),
        colors=(('R5', '#a7adb5'), ('R8', '#16768e')),
        annotations=(Label((x, y, 2 * AXIS_HEIGHT), 'Original corner', offset_px=(30, -65)),)),
        title='R8 exterior corner relief',
        purpose='Gray: original R5; teal: R8, with the ridge recessed by a tangent round.')


inspections = {'outer-corner': corner_inspection}


if __name__ in ('__main__', '__cqgi__'):
    result = build_sample()
