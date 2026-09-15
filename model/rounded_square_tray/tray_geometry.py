"""Parametric tray construction; all lengths are millimetres."""

import cadquery as cq


def rounded_square(size, radius, z):
    """One planar wire with tangent straight sides and circular corners."""
    wire = cq.Workplane("XY", origin=(0, 0, z)).rect(size, size).val()
    return wire.fillet2D(radius, wire.Vertices())


def edges_at_height(shape, z, tolerance=1e-5):
    return [
        edge for edge in shape.Edges()
        if abs(edge.BoundingBox().zmin - z) < tolerance
        and abs(edge.BoundingBox().zmax - z) < tolerance
    ]


def build_tray(cavity_size, inner_corner_radius, depth, base_thickness,
               rim_wall, taper_inset, floor_fillet, inner_rim_fillet,
               outer_rim_fillet, bottom_fillet):
    """Build upright, XY-centred, with underside on Z=0.

    cavity_size measures the vertical walls before their edge blends;
    the completely flat floor is smaller by twice floor_fillet.
    rim_wall measures the unrounded top profiles, not the remaining flat land.
    """
    height = base_thickness + depth
    top_size = cavity_size + 2 * rim_wall
    top_radius = inner_corner_radius + rim_wall
    bottom_size = top_size - 2 * taper_inset
    bottom_radius = top_radius - taper_inset
    assert 0 < floor_fillet < inner_corner_radius < cavity_size / 2
    assert min(depth, base_thickness, rim_wall, bottom_radius) > 0
    assert floor_fillet + inner_rim_fillet < depth
    assert inner_rim_fillet + outer_rim_fillet < rim_wall
    assert taper_inset < rim_wall

    body = cq.Solid.makeLoft([
        rounded_square(bottom_size, bottom_radius, 0),
        rounded_square(top_size, top_radius, height),
    ], ruled=True)
    body = body.fillet(bottom_fillet, edges_at_height(body, 0))

    cavity_wire = rounded_square(cavity_size, inner_corner_radius, base_thickness)
    cavity = cq.Solid.extrudeLinear(cavity_wire, [], cq.Vector(0, 0, depth + 1))
    # Rounding the cutter's lower edges leaves a concave interior fillet.
    cavity = cavity.fillet(floor_fillet, edges_at_height(cavity, base_thickness))
    tray = body.cut(cavity)

    top_edges = edges_at_height(tray, height)
    inner_edges = [e for e in top_edges
                   if max(abs(e.BoundingBox().xmin), abs(e.BoundingBox().xmax),
                          abs(e.BoundingBox().ymin), abs(e.BoundingBox().ymax))
                   < cavity_size / 2 + 1e-5]
    tray = tray.fillet(inner_rim_fillet, inner_edges)
    outer_edges = [e for e in edges_at_height(tray, height)
                   if max(abs(e.BoundingBox().xmin), abs(e.BoundingBox().xmax),
                          abs(e.BoundingBox().ymin), abs(e.BoundingBox().ymax))
                   > cavity_size / 2 + inner_rim_fillet + 1e-5]
    tray = tray.fillet(outer_rim_fillet, outer_edges)
    assert tray.isValid() and len(tray.Solids()) == 1
    return tray
