"""R2: thick horizontal, rounded-house 3D coil; TPU print experiment, mm.

The first printed circular/upright sample remains in tpu_coil_cord.py.
"""
import math
import cadquery as cq
from OCP.BRepTools import BRepTools_WireExplorer

CORD_DIAMETER = 5.2
TURN_GAP = 0.8  # sideways CAD gap; not calibrated printed clearance
TURNS = 4
HALF_LOOP_WIDTH = 7.0
SIDE_HEIGHT = 7.0
CORNER_RADIUS = 3.0
BED_FLATTENING = 0.6
END_FRAME_OFFSET = 5.5  # outboard eyes join the winding through broad foot tabs
PITCH = CORD_DIAMETER + TURN_GAP
AXIAL_RISE = TURNS * PITCH
BASE_CENTER_Z = CORD_DIAMETER / 2 - BED_FLATTENING


def loop_wire():
    """Closed planar centerline, YZ: flat feet, vertical sides, 45-degree roof."""
    h, w = BASE_CENTER_Z, HALF_LOOP_WIDTH
    vertices = [cq.Vector(0,y,z) for y,z in [
        (-w,h), (w,h), (w,h+SIDE_HEIGHT),
        (0,h+SIDE_HEIGHT+w), (-w,h+SIDE_HEIGHT),
    ]]
    wire = cq.Wire.makePolygon(vertices, close=True)
    return wire.fillet2D(CORNER_RADIUS, wire.Vertices())


def coil_spine(wire):
    """Exact straight segments and helical corner arcs, advancing X continuously."""
    explorer = BRepTools_WireExplorer(wire.wrapped)
    segments = []
    while explorer.More():
        edge = cq.Edge(explorer.Current())
        start = cq.Vertex(explorer.CurrentVertex()).Center()
        end = edge.endPoint() if (start-edge.startPoint()).Length < 1e-7 else edge.startPoint()
        segments.append((edge,start,end))
        explorer.Next()
    edges = []
    x = 0.0
    loop_length = wire.Length()
    for _ in range(TURNS):
        for edge,start,end in segments:
            dx = PITCH*edge.Length()/loop_length
            p0 = cq.Vector(x,start.y,start.z)
            p1 = cq.Vector(x+dx,end.y,end.z)
            if edge.geomType() == 'LINE':
                edges.append(cq.Edge.makeLine(p0,p1))
            elif edge.geomType() == 'CIRCLE':
                center, radius = edge.arcCenter(), edge.radius()
                a, b = start-center, end-center
                clockwise = a.y*b.z-a.z*b.y < 0
                angle = math.degrees(math.atan2(a.z,a.y))+90
                arc = (cq.Wire.makeHelix(PITCH*2*math.pi*radius/loop_length,dx,radius,
                                       lefthand=clockwise)
                       .rotate((0,0,0),(0,1,0),90)
                       .rotate((0,0,0),(1,0,0),angle)
                       .translate((x,center.y,center.z)))
                if (arc.startPoint()-p0).Length > 1e-5 or (arc.endPoint()-p1).Length > 1e-5:
                    raise ValueError('Helical corner does not meet the adjacent straight sections')
                edges.extend(arc.Edges())
            else:
                raise ValueError('Loop must contain only straight sides and circular corner rounds')
            x += dx
    return cq.Wire.assembleEdges(edges)


def attachment_eye(wire):
    """Closed end frame with the same bore; broad, rounded hook-bearing edges."""
    radius = CORD_DIAMETER/2
    outer = wire.offset2D(radius)[0]
    inner = wire.offset2D(-radius)[0]
    if cq.Face.makeFromWires(outer).Area() <= cq.Face.makeFromWires(inner).Area():
        raise ValueError('End-eye offsets reversed')
    eye = cq.Workplane(obj=cq.Solid.extrudeLinear(outer,[inner],(CORD_DIAMETER,0,0)))
    # Rounding the eye rims keeps them from presenting sharp extruded edges.
    eye = eye.edges().fillet(0.6)
    return eye.translate((-radius,0,0))


def build_sample():
    if not (0 < CORD_DIAMETER/2 < CORNER_RADIUS < HALF_LOOP_WIDTH/2):
        raise ValueError('Corner radius must clear the cord radius and fit the loop')
    if TURN_GAP <= 0 or TURNS < 3 or not (0 < BED_FLATTENING < CORD_DIAMETER/4):
        raise ValueError('Need separated turns, at least three circuits and a shallow foot')
    loop = loop_wire()
    path = coil_spine(loop)
    plane = cq.Plane(origin=path.startPoint(), normal=path.tangentAt(0))
    coil = (cq.Workplane(plane).circle(CORD_DIAMETER/2)
            .sweep(path, isFrenet=False, transition='round'))
    eye = attachment_eye(loop)
    # Keep eye faces away from coincident swept faces. Broad base tabs provide
    # the deliberate load path into each terminal foot instead of a tangent join.
    start_y = path.startPoint().y
    tab_length = END_FRAME_OFFSET + 1.4
    tab = (cq.Workplane('XY').box(tab_length,6.0,4.2,centered=(False,True,False))
           .edges('|Z').fillet(0.8).edges('>Z').fillet(0.6))
    left_tab = tab.translate((-END_FRAME_OFFSET,start_y+1.5,0))
    right_tab = tab.translate((AXIAL_RISE-1.4,start_y+1.5,0))
    whole = (coil.union(left_tab).union(right_tab)
             .union(eye.translate((-END_FRAME_OFFSET,0,0)))
             .union(eye.translate((AXIAL_RISE+END_FRAME_OFFSET,0,0))))
    # Slice a shallow flat into each round foot; all circuits contact the bed.
    extent = AXIAL_RISE + 4*HALF_LOOP_WIDTH + 4*CORD_DIAMETER
    above_bed = cq.Workplane('XY').box(2*extent,2*extent,extent,centered=(True,True,False))
    return whole.intersect(above_bed).clean()


if __name__ in ("__main__", "__cqgi__"):
    result = build_sample()
