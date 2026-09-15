"""Parametric shallow rounded-square tray, dimensions in millimetres."""

import cadquery as cq


# Primary envelope and cavity parameters.
TOP_OUTER_SIZE = 240.0
TOP_OUTER_RADIUS = 38.0
BOTTOM_OUTER_SIZE = 226.0
BOTTOM_OUTER_RADIUS = 31.0

INNER_SIZE = 220.0
INNER_RADIUS = 30.0
INTERIOR_DEPTH = 31.0
BASE_THICKNESS = 6.0
TOTAL_HEIGHT = BASE_THICKNESS + INTERIOR_DEPTH

# Edge treatment.
FLOOR_WALL_FILLET = 10.0
TOP_INNER_EDGE = 2.5
TOP_OUTER_EDGE = 2.5
BOTTOM_OUTER_FILLET = 8.0


def rounded_square_wire(size: float, radius: float, z: float = 0.0) -> cq.Wire:
    """Centered rounded-square wire with overall `size` and corner `radius`."""
    if not (0.0 < radius < size / 2.0):
        raise ValueError("Rounded-square radius must be between 0 and half its size")
    half = size / 2.0
    wire = (
        cq.Workplane("XY")
        .moveTo(-half + radius, -half)
        .lineTo(half - radius, -half)
        .radiusArc((half, -half + radius), -radius)
        .lineTo(half, half - radius)
        .radiusArc((half - radius, half), -radius)
        .lineTo(-half + radius, half)
        .radiusArc((-half, half - radius), -radius)
        .lineTo(-half, -half + radius)
        .radiusArc((-half + radius, -half), -radius)
        .close()
        .val()
    )
    return wire.translate(cq.Vector(0, 0, z))


def edges_near_z(shape: cq.Shape, z_value: float, tolerance: float = 0.05):
    """All planar perimeter edges whose complete Z span lies at `z_value`."""
    return [
        edge
        for edge in shape.Edges()
        if abs(edge.BoundingBox().zmin - z_value) <= tolerance
        and abs(edge.BoundingBox().zmax - z_value) <= tolerance
    ]


def build_tray() -> cq.Workplane:
    if BASE_THICKNESS <= 0.0 or INTERIOR_DEPTH <= 0.0:
        raise ValueError("Base thickness and interior depth must be positive")
    if TOP_OUTER_SIZE <= INNER_SIZE:
        raise ValueError("Outer profile must be larger than the cavity")
    if BOTTOM_OUTER_SIZE <= 2.0 * BOTTOM_OUTER_FILLET:
        raise ValueError("Bottom fillet is too large for the footprint")
    if FLOOR_WALL_FILLET >= INTERIOR_DEPTH:
        raise ValueError("Interior floor fillet must be smaller than the cavity depth")

    # Lofted exterior, in its intended print orientation with the underside at Z=0.
    lower_wire = rounded_square_wire(BOTTOM_OUTER_SIZE, BOTTOM_OUTER_RADIUS)
    upper_wire = rounded_square_wire(
        TOP_OUTER_SIZE, TOP_OUTER_RADIUS, z=TOTAL_HEIGHT
    )
    body = cq.Workplane(obj=cq.Solid.makeLoft([lower_wire, upper_wire]))

    # Round the lower outside transition while retaining a broad, flat bed-contact face.
    bottom_edges = edges_near_z(body.val(), 0.0)
    body = body.newObject(bottom_edges).fillet(BOTTOM_OUTER_FILLET)

    # A downward-facing rounded edge on the cutter creates the floor-to-wall fillet.
    cutter = (
        cq.Workplane("XY")
        .add(rounded_square_wire(INNER_SIZE, INNER_RADIUS, z=BASE_THICKNESS))
        .toPending()
        .extrude(INTERIOR_DEPTH - TOP_INNER_EDGE)
    )
    cavity_floor_edges = edges_near_z(cutter.val(), BASE_THICKNESS)
    cutter = cutter.newObject(cavity_floor_edges).fillet(FLOOR_WALL_FILLET)
    inner_shoulder_z = TOTAL_HEIGHT - TOP_INNER_EDGE
    inner_flare = cq.Solid.makeLoft(
        [
            rounded_square_wire(INNER_SIZE, INNER_RADIUS, z=inner_shoulder_z),
            rounded_square_wire(
                INNER_SIZE + 2.0 * TOP_INNER_EDGE,
                INNER_RADIUS + TOP_INNER_EDGE,
                z=TOTAL_HEIGHT,
            ),
        ]
    )
    upper_cutter = (
        cq.Workplane("XY")
        .add(
            rounded_square_wire(
                INNER_SIZE + 2.0 * TOP_INNER_EDGE,
                INNER_RADIUS + TOP_INNER_EDGE,
                z=TOTAL_HEIGHT,
            )
        )
        .toPending()
        .extrude(TOP_INNER_EDGE + 1.0)
    )
    cutter = cutter.union(cq.Workplane(obj=inner_flare)).union(upper_cutter)
    tray = body.cut(cutter)

    # Restrained 2.5 mm edge breaks retain a clearly defined flat rim.
    top_edges = edges_near_z(tray.val(), TOTAL_HEIGHT)
    rim_midline = (TOP_OUTER_SIZE + INNER_SIZE) / 4.0
    outer_edges = [
        edge
        for edge in top_edges
        if max(abs(edge.Center().x), abs(edge.Center().y)) > rim_midline
    ]
    if len(outer_edges) < 4:
        raise ValueError("Could not identify the outer top-rim perimeter")
    tray = tray.newObject(outer_edges).chamfer(TOP_OUTER_EDGE)
    return tray


result = build_tray()

if "show_object" in globals():
    show_object(result, name="rounded_square_tray")
