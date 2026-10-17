"""Review the delivered coupon slice: local voids/ribs/roof paths and probe locations."""
import json
import re
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
from review_thin_paths import require_multiple_tracks
import surface_design as d

ROOT = Path(__file__).resolve().parent


def main():
    receipt = json.loads((ROOT/'notes/surface_final.json').read_text())
    association = json.loads((ROOT/'notes/verification_sources.json').read_text())['surface_publication']
    assert all(digest(ROOT/n) == h for n, h in association['source_sha256'].items()), 'Stale source/export association: republish and review changed builders/profiles'
    assert receipt['reuse']['artifact_identity'] == association['artifact_identity']
    assert all(digest(ROOT/n) == h for n, h in association['export_sha256'].items())
    assert receipt['slice']['input_sha256'] == digest(ROOT/'surface_samples.stl')
    run = Path(receipt['slice']['kept_run_directory'])
    settings = json.loads((run/'effective-settings.json').read_text())
    for k, value in {'layer_height': '0.2', 'initial_layer_print_height': '0.2',
                     'thick_bridges': '0', 'thick_internal_bridges': '0',
                     'enable_support': '0', 'ironing_type': 'top',
                     'ironing_flow': '50%', 'bridge_angle': '180',
                     'internal_bridge_angle': '180'}.items():
        assert settings[k] == value, (k, settings[k])
    paths = list(orca_linear_paths(run/'plate_1.gcode'))
    assert not any(p[-1].startswith('Support') for p in paths)
    support = [p for p in orca_linear_paths(run/'support_probe/plate_1.gcode')
               if p[-1].startswith('Support')]
    # Centered 138 x 66 mm planned layout; the G-code header declares center 135,135.
    shift = (63., 99.)
    rows = []
    fig, axes = plt.subplots(2, 4, figsize=(13, 6))
    for (name, pos), ax in zip(d.placements(), axes.flat):
        v = d.variant_named(name)
        x, y = pos[0]+shift[0], pos[1]+shift[1]
        cy = y+d.FIELD_CY
        local = [p for p in paths if abs((p[0]+p[2])/2-x)<14.9
                 and abs((p[1]+p[3])/2-y)<14.9]
        local_support = [p for p in support if abs((p[0]+p[2])/2-x)<15
                         and abs((p[1]+p[3])/2-y)<15]
        # The thin-core support probe may suggest trapped internal interfaces.
        # Require every proposal to lie within the roof/core region, not outside.
        assert all(.4-1e-5 <= p[4] <= 1.4+1e-5 for p in local_support)
        assert all(abs((p[0]+p[2])/2-x)<d.FIELD_X/2+.3
                   and abs((p[1]+p[3])/2-cy)<d.FIELD_Y/2+.3 for p in local_support)
        channels = []
        tracks = []
        for z in (.6, .8, 1., 1.2):
            if v.pattern != 'solid':
                air = section_coverage(local, x_mm=x+v.pitch/2, z_mm=z,
                    span_mm=(cy+v.pitch/2-.5, cy+v.pitch/2+.5))
                assert air['filled_width_mm']<.01, (name, z, air)
                channels.append({'z_mm': z, 'coverage': air})
                tracks.append(require_multiple_tracks(local,
                    (x-.7, cy+v.pitch/2), (x+.7, cy+v.pitch/2), z, name, 'coupon'))
            else:
                solid = section_coverage(local, x_mm=x+v.pitch/2, z_mm=z,
                    span_mm=(cy+v.pitch/2-.5, cy+v.pitch/2+.5))
                assert solid['uncovered_width_mm']<.01, (name, z, solid)
        roof = [p for p in local if abs(p[4]-1.4)<1e-5
                and abs((p[0]+p[2])/2-x)<10 and abs((p[1]+p[3])/2-cy)<6
                and 'bridge' in p[-1].lower()]
        if v.pattern != 'solid':
            assert roof, f'{name}: no first-skin bridge paths found'
            assert all(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in roof), name
        ironing = [p for p in local if p[-1]=='Ironing']
        assert ironing, f'{name}: missing ironing paths'
        ax.add_patch(Rectangle((x-15,y-15),30,30,fill=False,color='#475569'))
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in local
                          if abs(p[4]-1.)<1e-5],colors='#477a98',linewidths=.6))
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in roof],
                          colors='#a85d9a',linewidths=.4,alpha=.6))
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in local_support],
                          colors='#d88621',linewidths=.5))
        ax.set_xlim(x-16,x+16); ax.set_ylim(y-16,y+16)
        ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f'{name}: {v.pattern}, skin {v.skin:g} mm')
        rows.append({'variant': name, 'channels': channels, 'rib_tracks': tracks,
                     'first_skin_bridge_segments': len(roof),
                     'ironing_segments': len(ironing),
                     'support_probe_segments': len(local_support),
                     'support_probe_z_range_mm': [min(p[4] for p in local_support),
                         max(p[4] for p in local_support)] if local_support else None})
    # Inspect bridge-height metadata only on real extrusion, accepting E.123 syntax.
    heights = set()
    role = ''; height = None
    for line in (run/'plate_1.gcode').open():
        if line.startswith(';TYPE:'): role = line[6:].strip()
        if line.startswith(';HEIGHT:'): height = float(line[8:])
        e = re.search(r'\bE(-?(?:\d+(?:\.\d*)?|\.\d+))', line)
        if line.startswith('G1 ') and e and float(e[1])>0 and 'bridge' in role.lower():
            assert height is not None
            heights.add(height)
    assert heights and max(heights)<=.20001, heights
    fig.suptitle('Core paths blue; first roof bridges purple; trapped probe proposals orange')
    fig.tight_layout()
    fig.savefig(ROOT/'renders/surface_path_review.png',dpi=150)
    out = {'category': 'local-sliced-manufacturing-evidence',
           'limits': 'Path metadata only: no deposited-gap, finish, stiffness, or damping qualification.',
           'source_sha256': {n: digest(ROOT/n) for n in
               ('surface_design.py','surface_samples.py','review_surface_paths.py','surface_samples.stl')},
           'gcode_sha256': digest(run/'plate_1.gcode'),
           'bridge_heights_mm': sorted(heights), 'center_translation_mm': shift,
           'results': rows}
    (ROOT/'notes/surface_path_review.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))


if __name__ == '__main__':
    main()
