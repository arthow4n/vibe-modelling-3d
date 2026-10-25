"""Shared local geometric checks for the R5-derived faceted cord experiments.

Checks take the actual selected shape and explicit trial screens. They neither
build a model nor publish files, and do not qualify printed material behavior.
"""
import math
import cadquery as cq


def check_faceted_geometry(shape, *, baseline, contact_screen_mm2, gap_screen_mm):
    solids = shape.Solids()

    def occupied(point):
        return any(s.isInside(cq.Vector(*point), 1e-6) for s in solids)

    path = baseline.winding_path()
    witnesses = []
    for turn in (1, 2, 3):
        for fraction in (.05, .15, .25, .35, .45, .55, .65, .75):
            point = path.positionAt((turn + fraction) / baseline.TURNS)
            gap = point + cq.Vector(baseline.PITCH / 2, 0, 0)
            witnesses.append(dict(turn=turn, fraction=fraction, material=occupied(point.toTuple()),
                gap_clear=all(not occupied((gap + cq.Vector(dx, 0, 0)).toTuple()) for dx in (-.3, 0, .3))))
    if not all(w['material'] and w['gap_clear'] for w in witnesses):
        raise ValueError('Middle winding or turn gap witness failed')

    terminals = []
    for x in (baseline.AXIAL_WIDTH / 2, baseline.AXIAL_WIDTH / 2 + baseline.RISE):
        for y, z in baseline.transverse_points()[:-1]:
            terminals.append(occupied((x, y, z + baseline.AXIS_HEIGHT)))
        if occupied((x, 0, baseline.AXIS_HEIGHT)):
            raise ValueError('Terminal bore obstructed')
    if not all(terminals):
        raise ValueError('Incomplete integrated terminal loop')

    faces = shape.Faces()
    inner_facets = []
    for i in range(8):
        ny, nz = math.sin(i * math.pi / 4), math.cos(i * math.pi / 4)
        found = False
        for face in faces:
            if face.geomType() != 'PLANE':
                continue
            n, p = face.normalAt(), face.Center()
            if (abs(n.x) < 1e-5 and abs(abs(n.y * ny + n.z * nz) - 1) < 1e-5
                    and abs(p.y * ny + (p.z - baseline.AXIS_HEIGHT) * nz
                            - (baseline.MEAN_APOTHEM - baseline.RADIAL_WIDTH / 2)) < 1e-5):
                found = True
        inner_facets.append(dict(degrees=i * 45, unchanged_plane_present=found))
    if not all(f['unchanged_plane_present'] for f in inner_facets):
        raise ValueError('Lost one of the original eight inner facet planes')

    bed = [f for f in faces if f.geomType() == 'PLANE' and abs(f.Center().z) < 1e-5
           and abs(f.normalAt().z) > .999999]
    contacts = []
    for turn in (1, 2, 3, 4):
        x = baseline.AXIAL_WIDTH / 2 + turn * baseline.PITCH
        area = sum(f.Area() for f in bed if abs(f.Center().x - x) < baseline.PITCH / 2)
        contacts.append(dict(turn=turn, area_mm2=area, retained_trial_screen_mm2=contact_screen_mm2))
    if not all(c['area_mm2'] >= contact_screen_mm2 for c in contacts):
        raise ValueError('A flat foot is below the declared geometric contact screen')

    point = path.positionAt(2.25 / baseline.TURNS)
    crops = []
    for dx in (0, baseline.PITCH):
        box = cq.Workplane('XY').box(baseline.PITCH, .5, .5).translate((point.x + dx, point.y, point.z)).val()
        crop = shape.intersect(box)
        if not crop.Faces():
            raise ValueError('Empty turn-gap crop')
        crops.append(crop)
    gap = crops[0].distance(crops[1])
    if gap < gap_screen_mm:
        raise ValueError('Turn gap below the declared geometric screen')
    return dict(material_gap_witnesses=witnesses, terminal_material_witnesses=terminals,
        terminal_bores_open=True, inner_facets=inner_facets, planar_bed_contact_samples=contacts,
        total_planar_bed_contact_mm2=sum(f.Area() for f in bed), local_turn_gap_mm=gap,
        gap_screen_mm=gap_screen_mm)


def bridge_midpoint_review(shape, bridges, *, offset_x, offset_y, layer_midplane_offset_mm, tolerance_mm):
    """Bounded material witnesses at bridge midpoints, not a bead-width audit."""
    solids = shape.Solids()
    outside = []
    for s in bridges:
        point = cq.Vector(sum(s['x']) / 2 - offset_x, sum(s['y']) / 2 - offset_y,
                          s['z'] - layer_midplane_offset_mm)
        if not any(body.isInside(point, tolerance_mm) for body in solids):
            outside.append(point.toTuple())
    return dict(checked=len(bridges), outside=outside, tolerance_mm=tolerance_mm,
                scope='Midpoints at representative layer mid-height only, not all paths or bead widths.')
