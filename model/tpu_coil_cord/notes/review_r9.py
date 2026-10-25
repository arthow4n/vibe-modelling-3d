"""R9 negative corner/remaining-ligament checks and shared faceted-coil review.

Run: ./execute.py model/tpu_coil_cord/notes/review_r9.py RETAINED_ORCA_RUN
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq

OBJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OBJECT))
import coil_r9_corner_recess as m
from coil_checks import check_faceted_geometry, bridge_midpoint_review
from gcode_paths import extrusions, plot_coil_review


def review(run):
    original = m.retained.build_sample().val()
    shape = m.recess_corners(original).val()
    # Qualify the shared extraction on the unchanged R8 control in this same run.
    control = check_faceted_geometry(original, baseline=m.baseline,
        contact_screen_mm2=5.0, gap_screen_mm=1.0)
    geometry = check_faceted_geometry(shape, baseline=m.baseline,
        contact_screen_mm2=5.0, gap_screen_mm=1.0)
    old = json.loads((OBJECT / 'notes/r8_targeted_checks.json').read_text())
    for key in ('local_turn_gap_mm', 'total_planar_bed_contact_mm2'):
        if abs(control[key] - old[key]) > 1e-5:
            raise ValueError('Shared check extraction changed retained R8 geometric evidence')
    if control['material_gap_witnesses'] != old['material_gap_witnesses']:
        raise ValueError('Shared winding witnesses differ from the R8 record')

    solids, original_solids = shape.Solids(), original.Solids()

    def occupied(point, bodies):
        return any(s.isInside(point, 1e-6) for s in bodies)

    corners = []
    ligaments = []
    for index in range(8):
        n, _ = m.corner_frame(index)
        fraction = (.4375 - index / 8) % 1
        x = m.AXIAL_WIDTH / 2 + (2 + fraction) * m.PITCH
        # Quarter-millimetre recession is a new intent witness, not R8's tiny edge break.
        removed = m.corner_point(index, 0, m.CORNER_RADIUS - .25, x)
        behind = m.corner_point(index, 0, m.CORNER_RADIUS - .70, x)
        corners.append(dict(index=index, original_material=occupied(removed, original_solids),
            recessed_material=occupied(removed, solids), material_behind_floor=occupied(behind, solids)))
        inner = cq.Vector(x, 0, m.AXIS_HEIGHT)
        outer = m.corner_point(index, 0, m.CORNER_RADIUS + .5, x)
        radial_section = cq.Edge.makeLine(inner, outer).intersect(shape)
        radii = [v.Center().y * n[0] + (v.Center().z - m.AXIS_HEIGHT) * n[1]
                 for v in radial_section.Vertices()]
        if len(radii) < 2:
            raise ValueError('Missing actual radial ligament section')
        depth = m.CORNER_RADIUS - max(radii)
        thickness = max(radii) - min(radii)
        ligaments.append(dict(index=index, vertex_depth_mm=depth, radial_ligament_mm=thickness,
                              geometric_ligament_screen_mm=2.8))
        if abs(depth - m.CORNER_DEPTH) > .01 or thickness < 2.8:
            raise ValueError('Actual corner depth or remaining material does not meet the local design screen')
    if not all(c['original_material'] and not c['recessed_material'] and c['material_behind_floor'] for c in corners):
        raise ValueError('Corner bite does not distinguish R9 from retained R8 with solid material behind it')

    # Inspect actual native cutter tangents rather than only rechecking its formula.
    tangent_checks = []
    n, t = m.corner_frame(0)
    for edge in m.corner_cutter(0).Edges():
        vertices = edge.Vertices()
        if edge.geomType() != 'BEZIER' or not all(abs(v.Center().x + 1) < 1e-6 for v in vertices):
            continue
        for fraction in (0, 1):
            point, tangent = edge.positionAt(fraction), edge.tangentAt(fraction)
            coordinate = point.y * t[0] + (point.z - m.AXIS_HEIGHT) * t[1]
            slope = (tangent.y * n[0] + tangent.z * n[1]) / (tangent.y * t[0] + tangent.z * t[1])
            expected = 0.0 if abs(coordinate) < 1e-6 else -math.copysign(m.FACET_SLOPE, coordinate)
            tangent_checks.append(dict(coordinate_mm=coordinate, native_slope=slope, expected_slope=expected))
            if abs(slope - expected) > 1e-6:
                raise ValueError('Native cut mouth or floor tangent does not match the intended smooth profile')
    if len(tangent_checks) != 4:
        raise ValueError('Expected two native cubic shoulder curves at the cutter base')

    files = dict(primary=run / 'plate_1.gcode', probe=run / 'support_probe/plate_1.gcode')
    paths = {key: list(extrusions(file)) for key, file in files.items()}
    if not any(abs(s['z'] - .2) < 1e-5 for s in paths['primary']):
        raise ValueError('Expected first-layer paths missing')
    bridges = [s for s in paths['primary'] if s['role'] == 'Bridge']
    bridge_check = bridge_midpoint_review(shape, bridges,
        offset_x=135 - m.OVERALL_LENGTH / 2, offset_y=135,
        layer_midplane_offset_mm=.1, tolerance_mm=.005)
    interface = [segment for segment in paths['probe'] if segment['role'] == 'Support interface']
    interface_outside_bore = []
    for segment in interface:
        y, z = sum(segment['y']) / 2 - 135, segment['z'] - .1 - m.AXIS_HEIGHT
        offset = max(y * math.sin(i * math.pi / 4) + z * math.cos(i * math.pi / 4) for i in range(8))
        if offset > m.baseline.MEAN_APOTHEM - m.RADIAL_WIDTH / 2 + .01:
            interface_outside_bore.append(dict(y_mm=y, z_mm=z + m.AXIS_HEIGHT))
    plot_coil_review(paths['primary'], paths['probe'], axis_height=m.AXIS_HEIGHT,
        name='R9', destination=OBJECT / 'notes/r9_actual_paths.png')
    report = dict(scope='Native corner relief/material and supplied-profile path evidence; not physical notch, strength or adhesion qualification.',
        **geometry, negative_corner_witnesses=corners, radial_sections=ligaments,
        profile_tangent_checks=tangent_checks,
        support_interface_location=dict(segments=len(interface), outside_nominal_bore=interface_outside_bore,
            scope='Midpoints in nominal octagonal bore projection, 0.01 mm numeric margin; not support-contact proof.'),
        retained_r8_control=dict(local_turn_gap_mm=control['local_turn_gap_mm'],
            total_planar_bed_contact_mm2=control['total_planar_bed_contact_mm2'],
            contact_fraction_retained=geometry['total_planar_bed_contact_mm2'] / control['total_planar_bed_contact_mm2'],
            shared_check_matches_r8_record=True),
        source_sha256={name: hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                       for name, module in [('r9', m), ('r8', m.retained), ('r5', m.baseline)]},
        gcode_sha256={key: hashlib.sha256(file.read_bytes()).hexdigest() for key, file in files.items()},
        bridge_midpoint_check=bridge_check,
        primary_bridge_layers_mm=sorted({s['z'] for s in bridges}),
        support_layers_mm=sorted({s['z'] for s in paths['probe'] if s['role'] in ('Support', 'Support interface')}))
    (OBJECT / 'notes/r9_targeted_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if not k.endswith('_witnesses') and k != 'support_layers_mm'}))
    if bridge_check['outside']:
        raise ValueError('Bridge midpoint outside current-layer CAD material; review required')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError('Supply the retained Orca run directory')
    review(Path(sys.argv[1]))
