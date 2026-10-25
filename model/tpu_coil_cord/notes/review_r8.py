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
from coil_checks import check_faceted_geometry, bridge_midpoint_review


def review(run):
    original = m.baseline.build_sample().val()
    shape = m.soften_exterior(original).val()
    solids, old_solids = shape.Solids(), original.Solids()

    def occupied(point, bodies=solids, tolerance=1e-6):
        return any(s.isInside(cq.Vector(*point), tolerance) for s in bodies)

    geometry = check_faceted_geometry(shape, baseline=m.baseline,
        contact_screen_mm2=5.0, gap_screen_mm=1.0)

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

    files = dict(primary=run / 'plate_1.gcode', probe=run / 'support_probe/plate_1.gcode')
    paths = {key: list(extrusions(file)) for key, file in files.items()}
    if not any(abs(s['z'] - .2) < 1e-5 for s in paths['primary']):
        raise ValueError('No expected first-layer paths')
    bridges = [s for s in paths['primary'] if s['role'] == 'Bridge']
    bridge_check = bridge_midpoint_review(shape, bridges,
        offset_x=135 - m.OVERALL_LENGTH / 2, offset_y=135,
        layer_midplane_offset_mm=.1, tolerance_mm=.005)
    plot_coil_review(paths['primary'], paths['probe'], axis_height=m.AXIS_HEIGHT,
                     name='R8', destination=OBJECT / 'notes/r8_actual_paths.png')
    answer = dict(scope='CAD comparison to accepted R5 and supplied-profile paths; not physical finish/adhesion qualification.',
        **geometry,
        exterior_recession_witnesses=recession,
        source_sha256=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
        baseline_source_sha256=hashlib.sha256(Path(m.baseline.__file__).read_bytes()).hexdigest(),
        gcode_sha256={key: hashlib.sha256(file.read_bytes()).hexdigest() for key, file in files.items()},
        bridge_midpoint_check=bridge_check,
        primary_bridge_layers_mm=sorted({s['z'] for s in bridges}),
        support_layers_mm=sorted({s['z'] for s in paths['probe'] if s['role'] in ('Support', 'Support interface')}))
    (OBJECT / 'notes/r8_targeted_checks.json').write_text(json.dumps(answer, indent=2) + '\n')
    print(json.dumps({k: v for k, v in answer.items() if not k.endswith('_witnesses') and k != 'support_layers_mm'}))
    if bridge_check['outside']:
        raise ValueError('Bridge midpoint outside sampled current-layer material; review required')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError('Supply the retained Orca run directory')
    review(Path(sys.argv[1]))
