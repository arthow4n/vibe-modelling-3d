"""Check continuous flat-section lands, round winding and first-layer geometry.

Run with ./execute.py model/tpu_coil_cord/notes/review_r7.py RETAINED_ORCA_RUN.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq

OBJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OBJECT))
import coil_r7_flat_section as m
import coil_r6_round_flats as rejected
from gcode_paths import extrusions, plot_coil_review


def review(run):
    shape = m.build_sample().val()
    solids = shape.Solids()
    old_solids = rejected.build_sample().val().Solids()

    def occupied(point, bodies=solids, tolerance=1e-6):
        return any(s.isInside(cq.Vector(*point), tolerance) for s in bodies)

    def position(turn, angle, radial_offset=0, axial_offset=0):
        theta = math.radians(angle)
        return (m.AXIAL_WIDTH / 2 + (turn + angle / 360) * m.PITCH + axial_offset,
                (m.MEAN_RADIUS + radial_offset) * math.sin(theta),
                m.AXIS_HEIGHT - (m.MEAN_RADIUS + radial_offset) * math.cos(theta))

    witnesses = []
    lands = []
    negative_hits = 0
    for turn in (1, 2, 3):
        for angle in range(0, 360, 45):
            center = position(turn, angle)
            gap = position(turn, angle, axial_offset=m.PITCH / 2)
            witnesses.append(dict(turn=turn, degrees=angle, material=occupied(center),
                gap_clear=all(not occupied((gap[0] + dx, gap[1], gap[2])) for dx in (-.3, 0, .3)),
                bore_clear=not occupied(position(turn, angle, radial_offset=-m.MEAN_RADIUS))))
            # 0.05 mm inside each radial face, at ±0.8 mm along its 2 mm land.
            # A round profile cannot occupy these near-corner samples.
            for radial in (-m.RADIAL_WIDTH / 2 + .05, m.RADIAL_WIDTH / 2 - .05):
                for axial in (-.8, .8):
                    point = position(turn, angle, radial, axial)
                    inside = occupied(point)
                    old_point = (point[0], point[1], point[2] - m.AXIS_HEIGHT + rejected.AXIS_HEIGHT)
                    negative_hits += occupied(old_point, old_solids)
                    lands.append(dict(turn=turn, degrees=angle, radial_offset=radial,
                                      axial_offset=axial, material=inside))
    if not all(w['material'] and w['gap_clear'] and w['bore_clear'] for w in witnesses):
        raise ValueError('Round winding, bore or gap witnesses failed')
    if not all(w['material'] for w in lands) or negative_hits:
        raise ValueError('Flat-section witnesses failed to distinguish R7 from rejected round-section R6')

    terminal_witnesses = []
    for turn in (0, m.TURNS):
        x = m.AXIAL_WIDTH / 2 + turn * m.PITCH
        for degrees in range(0, 360, 30):
            theta = math.radians(degrees)
            for radial, axial in ((0, 0), (-1.55, -.8), (-1.55, .8), (1.55, -.8), (1.55, .8)):
                r = m.MEAN_RADIUS + radial
                point = (x + axial, r * math.sin(theta), m.AXIS_HEIGHT - r * math.cos(theta))
                terminal_witnesses.append(dict(end=turn, degrees=degrees, radial_offset=radial,
                                               axial_offset=axial, material=occupied(point)))
        if occupied((x, 0, m.AXIS_HEIGHT)):
            raise ValueError('Terminal eye bore is obstructed')
    if not all(w['material'] for w in terminal_witnesses):
        raise ValueError('Terminal eye or its flat section is incomplete')

    # A circular winding has tangent bed contact. Check actual layer-midplane
    # sections instead of misreporting an isolated shaved planar face as required.
    section = cq.Workplane(obj=shape).section(.1).val()
    footprints = [cq.Face.makeFromWires(w) for w in section.Wires()]
    feet = []
    for turn in (1, 2, 3, 4):
        x = position(turn, 0)[0]
        area = sum(f.Area() for f in footprints if abs(f.Center().x - x) < m.PITCH / 2)
        flat_width = all(occupied((x + dx, 0, .1)) for dx in (-.8, 0, .8))
        feet.append(dict(turn=turn, layer_midplane_area_mm2=area, axial_1p6_mm_land_retained=flat_width))
    if not all(f['layer_midplane_area_mm2'] > 0 and f['axial_1p6_mm_land_retained'] for f in feet):
        raise ValueError('First-layer section does not retain the expected flat-section width')

    point = position(2, 90)
    crops = []
    for dx in (0, m.PITCH):
        box = cq.Workplane('XY').box(m.PITCH, .5, .5).translate((point[0] + dx, point[1], point[2])).val()
        crop = shape.intersect(box)
        if not crop.Faces():
            raise ValueError('Empty local turn-gap crop')
        crops.append(crop)
    gap = crops[0].distance(crops[1])
    if gap < 1.0:
        raise ValueError('Local gap below retained 1 mm screen')

    files = dict(primary=run / 'plate_1.gcode', probe=run / 'support_probe/plate_1.gcode')
    paths = {name: list(extrusions(file)) for name, file in files.items()}
    if not any(abs(s['z'] - .2) < 1e-5 for s in paths['primary']):
        raise ValueError('Expected first-layer paths missing')
    bridges = [s for s in paths['primary'] if s['role'] == 'Bridge']
    outside = []
    for segment in bridges:
        point = (sum(segment['x']) / 2 - (135 - m.OVERALL_LENGTH / 2),
                 sum(segment['y']) / 2 - 135, segment['z'] - .1)
        if not occupied(point, tolerance=.005):
            outside.append(point)
    plot_coil_review(paths['primary'], paths['probe'], axis_height=m.AXIS_HEIGHT,
                     name='R7', destination=OBJECT / 'notes/r7_actual_paths.png')
    report = dict(scope='Local CAD and supplied-profile paths; not physical print qualification.',
        round_winding_gap_witnesses=witnesses, continuous_flat_land_witnesses=lands,
        terminal_flat_section_witnesses=terminal_witnesses,
        rejected_r6_material_hits=negative_hits, first_layer_midplane_z_mm=.1,
        first_layer_sections=feet, local_turn_gap_mm=gap, gap_screen_mm=1.0,
        source_sha256=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
        rejected_source_sha256=hashlib.sha256(Path(rejected.__file__).read_bytes()).hexdigest(),
        gcode_sha256={key: hashlib.sha256(file.read_bytes()).hexdigest() for key, file in files.items()},
        bridge_midpoint_check=dict(checked=len(bridges), outside=outside, tolerance_mm=.005,
            scope='Midpoints at layer mid-height only, not bead-width or complete path verification.'),
        primary_bridge_layers_mm=sorted({s['z'] for s in bridges}),
        support_layers_mm=sorted({s['z'] for s in paths['probe'] if s['role'] in ('Support', 'Support interface')}))
    (OBJECT / 'notes/r7_targeted_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    if outside:
        raise ValueError('Bridge midpoint outside current-layer CAD material; review required')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError('Supply the retained Orca run directory')
    review(Path(sys.argv[1]))
