"""R8 comparison to working R5: exterior recession, retained facets/feet and paths.

Run with ./execute.py model/tpu_coil_cord/notes/review_r8.py RETAINED_ORCA_RUN.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq

OBJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OBJECT))
import coil_r8_soft_octagon as m
from gcode_paths import extrusions, plot_coil_review


def review(run):
    original = m.baseline.build_sample().val()
    shape = m.soften_exterior(original).val()
    solids, old_solids = shape.Solids(), original.Solids()

    def occupied(point, bodies=solids, tolerance=1e-6):
        return any(s.isInside(cq.Vector(*point), tolerance) for s in bodies)

    path = m.baseline.winding_path()
    witnesses = []
    for turn in (1, 2, 3):
        for fraction in (.05, .15, .25, .35, .45, .55, .65, .75):
            point = path.positionAt((turn + fraction) / m.TURNS)
            gap = point + cq.Vector(m.PITCH / 2, 0, 0)
            witnesses.append(dict(turn=turn, fraction=fraction, material=occupied(point.toTuple()),
                gap_clear=all(not occupied((gap + cq.Vector(dx, 0, 0)).toTuple()) for dx in (-.3, 0, .3))))
    if not all(w['material'] and w['gap_clear'] for w in witnesses):
        raise ValueError('Middle winding or turn gap witness failed')

    terminals = []
    for x in (m.AXIAL_WIDTH / 2, m.AXIAL_WIDTH / 2 + m.baseline.RISE):
        for y, z in m.baseline.transverse_points()[:-1]:
            terminals.append(occupied((x, y, z + m.AXIS_HEIGHT)))
        if occupied((x, 0, m.AXIS_HEIGHT)):
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
                    and abs(p.y * ny + (p.z - m.AXIS_HEIGHT) * nz
                            - (m.baseline.MEAN_APOTHEM - m.RADIAL_WIDTH / 2)) < 1e-5):
                found = True
        inner_facets.append(dict(degrees=i * 45, unchanged_plane_present=found))
    if not all(f['unchanged_plane_present'] for f in inner_facets):
        raise ValueError('Lost one of the original eight inner facet planes')

    bed = [f for f in faces if f.geomType() == 'PLANE' and abs(f.Center().z) < 1e-5
           and abs(f.normalAt().z) > .999999]
    contacts = []
    for turn in (1, 2, 3, 4):
        x = m.AXIAL_WIDTH / 2 + turn * m.PITCH
        area = sum(f.Area() for f in bed if abs(f.Center().x - x) < m.PITCH / 2)
        contacts.append(dict(turn=turn, area_mm2=area, retained_trial_screen_mm2=5.0))
    if not all(c['area_mm2'] >= c['retained_trial_screen_mm2'] for c in contacts):
        raise ValueError('Exterior rounding reduced a foot below the retained 5 mm² screen')

    recession = []
    # Actual original outer miter ridges, sampled just inside their sharp peaks.
    for x, y, z in m.baseline.winding_stations()[9:36]:
        if abs(y) < 1e-8:
            continue
        factor = (m.OUTSIDE_ACROSS_FLATS / 2) / m.baseline.MEAN_APOTHEM
        length = math.hypot(y, z)
        point = (x, y * factor - .01 * y / length,
                 m.AXIS_HEIGHT + z * factor - .01 * z / length)
        recession.append(dict(point=point, original_material=occupied(point, old_solids),
                              rounded_material=occupied(point)))
    if not all(w['original_material'] and not w['rounded_material'] for w in recession):
        raise ValueError('Exterior ridge recession not present in all sampled octagonal corners')

    point = path.positionAt(2.25 / m.TURNS)
    crops = []
    for dx in (0, m.PITCH):
        box = cq.Workplane('XY').box(m.PITCH, .5, .5).translate((point.x + dx, point.y, point.z)).val()
        crop = shape.intersect(box)
        if not crop.Faces():
            raise ValueError('Empty turn-gap crop')
        crops.append(crop)
    gap = crops[0].distance(crops[1])
    if gap < 1.0:
        raise ValueError('Turn gap below retained 1 mm screen')

    files = dict(primary=run / 'plate_1.gcode', probe=run / 'support_probe/plate_1.gcode')
    paths = {key: list(extrusions(file)) for key, file in files.items()}
    if not any(abs(s['z'] - .2) < 1e-5 for s in paths['primary']):
        raise ValueError('No expected first-layer paths')
    bridges = [s for s in paths['primary'] if s['role'] == 'Bridge']
    outside = []
    for s in bridges:
        point = (sum(s['x']) / 2 - (135 - m.OVERALL_LENGTH / 2), sum(s['y']) / 2 - 135, s['z'] - .1)
        if not occupied(point, tolerance=.005):
            outside.append(point)
    plot_coil_review(paths['primary'], paths['probe'], axis_height=m.AXIS_HEIGHT,
                     name='R8', destination=OBJECT / 'notes/r8_actual_paths.png')
    answer = dict(scope='CAD comparison to accepted R5 and supplied-profile paths; not physical finish/adhesion qualification.',
        material_gap_witnesses=witnesses, terminal_material_witnesses=terminals, terminal_bores_open=True,
        inner_facets=inner_facets, planar_bed_contact_samples=contacts,
        total_planar_bed_contact_mm2=sum(f.Area() for f in bed), local_turn_gap_mm=gap, gap_screen_mm=1.0,
        exterior_recession_witnesses=recession,
        source_sha256=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
        baseline_source_sha256=hashlib.sha256(Path(m.baseline.__file__).read_bytes()).hexdigest(),
        gcode_sha256={key: hashlib.sha256(file.read_bytes()).hexdigest() for key, file in files.items()},
        bridge_midpoint_check=dict(checked=len(bridges), outside=outside, tolerance_mm=.005,
            scope='Midpoints at representative layer mid-height only, not all paths or bead widths.'),
        primary_bridge_layers_mm=sorted({s['z'] for s in bridges}),
        support_layers_mm=sorted({s['z'] for s in paths['probe'] if s['role'] in ('Support', 'Support interface')}))
    (OBJECT / 'notes/r8_targeted_checks.json').write_text(json.dumps(answer, indent=2) + '\n')
    print(json.dumps({k: v for k, v in answer.items() if not k.endswith('_witnesses') and k != 'support_layers_mm'}))
    if outside:
        raise ValueError('Bridge midpoint outside sampled current-layer material; review required')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError('Supply the retained Orca run directory')
    review(Path(sys.argv[1]))
