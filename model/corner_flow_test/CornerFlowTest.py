"""Parametric Orca Slicer corner-flow calibration prism.

The printable result is one solid made by extruding one constant, closed 2D
profile.  It intentionally contains no slicer settings or toolpath logic.
"""

from math import cos, isclose, pi, radians, sin

import cadquery as cq


# User-editable dimensions, millimetres.
model_height = 50.0
r_small = 2.0
r_medium = 5.0
r_large = 10.0


def _point_on_arc(center, radius, degrees):
    angle = radians(degrees)
    return cq.Vector(
        center[0] + radius * cos(angle),
        center[1] + radius * sin(angle),
        0,
    )


def build_model():
    """Build the one-body calibration solid in its specified XY coordinates."""
    if model_height <= 0:
        raise ValueError("model_height must be greater than zero")
    if not 0.5 <= r_small < 8.0:
        raise ValueError("r_small must be in [0.5, 8.0) mm")
    if not 0.5 <= r_medium < 12.0:
        raise ValueError("r_medium must be in [0.5, 12.0) mm")
    if not 0.5 <= r_large < 22.0:
        raise ValueError("r_large must be in [0.5, 22.0) mm")

    top_y = 70.0 + r_large

    p0 = cq.Vector(10, 10, 0)
    p1 = cq.Vector(110, 10, 0)
    p2 = cq.Vector(110, 70, 0)
    p3 = cq.Vector(110 - r_large, top_y, 0)
    p4 = cq.Vector(88, top_y, 0)
    p5 = cq.Vector(88, 52, 0)
    p6 = cq.Vector(88 - 2 * r_medium, 52, 0)
    p7 = cq.Vector(p6.x, top_y, 0)
    p8 = cq.Vector(64, top_y, 0)
    p9 = cq.Vector(64, 46, 0)
    p10 = cq.Vector(64 - 2 * r_small, 46, 0)
    p11 = cq.Vector(p10.x, top_y, 0)
    p12 = cq.Vector(48, top_y, 0)
    p13 = cq.Vector(48, 62, 0)
    p14 = cq.Vector(38, 62, 0)
    p15 = cq.Vector(38, top_y, 0)
    p16 = cq.Vector(20, top_y, 0)
    p17 = cq.Vector(10, 70, 0)

    c1 = (110 - r_large, 70)
    c2 = (88 - r_medium, 52)
    c3 = (64 - r_small, 46)

    edges = [
        cq.Edge.makeLine(p0, p1),
        cq.Edge.makeLine(p1, p2),
        cq.Edge.makeThreePointArc(p2, _point_on_arc(c1, r_large, 45), p3),
        cq.Edge.makeLine(p3, p4),
        cq.Edge.makeLine(p4, p5),
        cq.Edge.makeThreePointArc(p5, _point_on_arc(c2, r_medium, -90), p6),
        cq.Edge.makeLine(p6, p7),
        cq.Edge.makeLine(p7, p8),
        cq.Edge.makeLine(p8, p9),
        cq.Edge.makeThreePointArc(p9, _point_on_arc(c3, r_small, -90), p10),
        cq.Edge.makeLine(p10, p11),
        cq.Edge.makeLine(p11, p12),
        cq.Edge.makeLine(p12, p13),
        cq.Edge.makeLine(p13, p14),
        cq.Edge.makeLine(p14, p15),
        cq.Edge.makeLine(p15, p16),
        cq.Edge.makeLine(p16, p17),
        cq.Edge.makeLine(p17, p0),
    ]

    profile = cq.Wire.assembleEdges(edges)
    if not profile.IsClosed():
        raise ValueError("Profile did not form a closed wire")

    face = cq.Face.makeFromWires(profile)
    solid = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, model_height))
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise ValueError("Extruded calibration solid is invalid")

    bounds = solid.BoundingBox()
    expected_bounds = (10, 10, 0, 110, top_y, model_height)
    actual_bounds = (
        bounds.xmin, bounds.ymin, bounds.zmin,
        bounds.xmax, bounds.ymax, bounds.zmax,
    )
    if not all(isclose(a, b, abs_tol=1e-8) for a, b in zip(actual_bounds, expected_bounds)):
        raise ValueError("Unexpected model bounds")

    bottom_edges = [
        edge for edge in solid.Edges()
        if all(isclose(vertex.Z, 0.0, abs_tol=1e-8) for vertex in edge.Vertices())
    ]
    if len(bottom_edges) != 18:
        raise ValueError("Profile must contain exactly 18 analytic edges")
    if sum(edge.geomType() == "LINE" for edge in bottom_edges) != 15:
        raise ValueError("Profile must contain exactly 15 straight edges")
    arc_lengths = sorted(edge.Length() for edge in bottom_edges if edge.geomType() == "CIRCLE")
    expected_arc_lengths = sorted([pi * r_small, pi * r_medium, pi * r_large / 2])
    if len(arc_lengths) != 3 or not all(
        isclose(a, b, abs_tol=1e-8) for a, b in zip(arc_lengths, expected_arc_lengths)
    ):
        raise ValueError("Profile arcs do not match the requested radii and sweeps")
    return solid


result = build_model()
if "show_object" in globals():
    show_object(result, name="CornerFlowTest")
