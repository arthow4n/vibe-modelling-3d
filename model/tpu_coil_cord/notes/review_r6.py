"""Targeted R6 flat-contact, open-turn and roof-path review.

Run: ./execute.py model/tpu_coil_cord/notes/review_r6.py RETAINED_ORCA_RUN_DIRECTORY
Writes the local check record and a selected-path image; imports do not run CAD.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

OBJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OBJECT))
import coil_r6_round_flats as m
from gcode_paths import extrusions


def review(run):
    shape = m.build_sample().val()
    solids = shape.Solids()

    def occupied(point, tolerance=1e-6):
        return any(s.isInside(cq.Vector(*point), tolerance) for s in solids)

    def center(turn, angle):
        theta = math.radians(angle)
        return (m.CORD_DIAMETER / 2 + (turn + angle / 360) * m.PITCH,
                m.MEAN_RADIUS * math.sin(theta),
                m.AXIS_HEIGHT - m.MEAN_RADIUS * math.cos(theta))

    witnesses = []
    for turn in (1, 2, 3):
        for angle in range(0, 360, 30):
            point = center(turn, angle)
            gap = (point[0] + m.PITCH / 2, point[1], point[2])
            theta = math.radians(angle)
            bore = (point[0], 4.0 * math.sin(theta), m.AXIS_HEIGHT - 4.0 * math.cos(theta))
            witnesses.append(dict(turn=turn, degrees=angle, material=occupied(point),
                gap_clear=all(not occupied((gap[0] + dx, gap[1], gap[2])) for dx in (-.3, 0, .3)),
                bore_clear=not occupied(bore)))
    if not all(w['material'] and w['gap_clear'] and w['bore_clear'] for w in witnesses):
        raise ValueError('Winding, circular bore or separated-turn witness failed')

    flats = {key: [] for key in ('bottom', 'top')}
    for face in shape.Faces():
        if face.geomType() != 'PLANE' or abs(face.normalAt().z) < .999999:
            continue
        for key, height in [('bottom', 0), ('top', m.FLAT_HEIGHT)]:
            if abs(face.Center().z - height) < 1e-5:
                flats[key].append(face)
    if not all(flats.values()):
        raise ValueError('Opposing flat-contact faces missing')
    contacts = []
    for turn in (1, 2, 3, 4):
        x = center(turn, 0)[0]
        area = sum(f.Area() for f in flats['bottom'] if abs(f.Center().x - x) < m.PITCH / 2)
        contacts.append(dict(turn=turn, area_mm2=area, trial_screen_mm2=5.0))
    if not all(c['area_mm2'] >= c['trial_screen_mm2'] for c in contacts):
        raise ValueError('Flat contact below the retained local 5 mm² trial screen')

    point = center(2, 90)
    crops = []
    for dx in (0, m.PITCH):
        box = cq.Workplane('XY').box(m.PITCH, .5, .5).translate((point[0] + dx, point[1], point[2])).val()
        crop = shape.intersect(box)
        if not crop.Faces():
            raise ValueError('Adjacent-turn witness crop is empty')
        crops.append(crop)
    gap = crops[0].distance(crops[1])
    if gap < 1.0:
        raise ValueError('Local turn gap below retained 1 mm geometric screen')
    for turn in (0, m.TURNS):
        if occupied((center(turn, 0)[0], 0, m.AXIS_HEIGHT)):
            raise ValueError('Closed terminal turn has lost its open bore')

    files = dict(primary=run / 'plate_1.gcode', probe=run / 'support_probe/plate_1.gcode')
    paths = {name: list(extrusions(file)) for name, file in files.items()}
    bridges = [s for s in paths['primary'] if s['role'] == 'Bridge']
    support = [s for s in paths['probe'] if s['role'] in ('Support', 'Support interface')]
    first = [s for s in paths['primary'] if abs(s['z'] - .2) < 1e-5]
    if not first:
        raise ValueError('Expected 0.2 mm first-layer paths missing')
    outside = []
    # The native slice uses center placement, with the model axial envelope 0..25.2.
    for s in bridges:
        point = (sum(s['x']) / 2 - (135 - m.OVERALL_LENGTH / 2),
                 sum(s['y']) / 2 - 135, s['z'] - .1)
        if not occupied(point, tolerance=.005):
            outside.append(point)
    roof = min((s['z'] for s in bridges if s['z'] > m.AXIS_HEIGHT), default=11.0)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')

    def draw(ax, segments, color, *, xz=False, width=.65):
        lines = [[(s['x'][0], s['z'] if xz else s['y'][0]),
                  (s['x'][1], s['z'] if xz else s['y'][1])] for s in segments]
        if lines:
            ax.add_collection(LineCollection(lines, colors=color, linewidths=width))
            ax.autoscale_view()

    draw(axes[0, 0], first, '#286a9e')
    draw(axes[0, 1], [s for s in paths['primary'] if abs(s['z'] - 7) < 1e-5], '#286a9e')
    draw(axes[1, 0], support, '#b35c2a', xz=True)
    draw(axes[1, 1], [s for s in paths['primary'] if abs(s['z'] - (roof - .2)) < 1e-5], '#b9c1c7', width=1.8)
    draw(axes[1, 1], [s for s in paths['primary'] if abs(s['z'] - roof) < 1e-5 and s['role'] != 'Bridge'], '#286a9e')
    draw(axes[1, 1], [s for s in bridges if abs(s['z'] - roof) < 1e-5], '#b35c2a')
    for ax, title in zip(axes.flat, ['R6 bed contact Z0.2', 'R6 side walls Z7',
                                    'R6 support probe: X vs Z', f'R6 roof Z{roof:g}: bridge orange, prior gray']):
        ax.set(title=title, xlabel='Bed X (mm)', ylabel='Z (mm)' if ax == axes[1, 0] else 'Bed Y (mm)')
        if ax != axes[1, 0]:
            ax.set_aspect('equal')
    fig.savefig(OBJECT / 'notes/r6_actual_paths.png', dpi=150)
    plt.close(fig)
    result = dict(scope='Local CAD/contact and selected-profile path evidence, not physical print qualification.',
        material_gap_bore_witnesses=witnesses, contact_samples=contacts,
        total_planar_bed_contact_mm2=sum(f.Area() for f in flats['bottom']),
        native_local_turn_gap_mm=gap, geometric_gap_screen_mm=1.0,
        terminal_bores_open=True,
        source_sha256=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
        gcode_sha256={name: hashlib.sha256(file.read_bytes()).hexdigest() for name, file in files.items()},
        primary_bridge_layers_mm=sorted({s['z'] for s in bridges}),
        bridge_midpoint_check=dict(checked=len(bridges), outside=outside, tolerance_mm=.005,
            scope='Midpoint only at layer mid-height; not a bead-width or full deposition audit.'),
        support_layers_mm=sorted({s['z'] for s in support}), selected_roof_layer_mm=roof)
    (OBJECT / 'notes/r6_targeted_checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    if outside:
        raise ValueError('Bridge midpoints fall outside sampled current-layer CAD material; review required')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError('Supply the retained Orca run directory')
    review(Path(sys.argv[1]))
