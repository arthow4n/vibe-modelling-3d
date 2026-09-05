"""Read diagnostic PrusaSlicer G-code, summarize roles and plot selected layers.

Standard-library only. No CAD evaluation or modification. Requires ASCII G-code
with absolute XYZ, relative E and PrusaSlicer layer/feature comments, as generated
by review.ini. Segment lengths are toolpath lengths, not measured free-air spans.
"""
from collections import defaultdict
from pathlib import Path
import json
import math
import re

HERE = Path(__file__).resolve().parent
TOKEN = re.compile(r'([XYZEF])(-?(?:\d+(?:\.\d*)?|\.\d+))')


def read(name):
    layers = defaultdict(list)
    pos = dict(X=0.0, Y=0.0, Z=0.0)
    height, role, relative = 0.0, 'Unknown', False
    summary = {}
    with (HERE / f'{name}.gcode').open() as source:
        for number, line in enumerate(source, 1):
            if line.startswith(';TYPE:'):
                role = line.strip()[6:]
            elif line.startswith(';Z:'):
                height = round(float(line.strip()[3:]), 3)
            elif line.startswith('M83'):
                relative = True
            elif line.startswith('M82'):
                raise ValueError('This diagnostic parser requires relative E')
            elif line.startswith('G91'):
                raise ValueError('This diagnostic parser requires absolute XYZ')
            elif line.startswith('; filament used [g]') or line.startswith('; estimated printing time (normal mode)'):
                key, value = line[2:].strip().split(' = ', 1)
                summary[key] = value
            elif line.startswith(('G0 ', 'G1 ')):
                args = {key: float(value) for key, value in TOKEN.findall(line.split(';')[0])}
                end = {key: args.get(key, pos[key]) for key in pos}
                length = math.hypot(end['X']-pos['X'], end['Y']-pos['Y'])
                if args.get('E', 0) > 0 and length > .0001:
                    assert relative
                    layers[height].append(dict(role=role, a=[pos['X'], pos['Y']],
                        b=[end['X'], end['Y']], length=length, e=args['E'], line=number))
                pos = end
    feature_totals = defaultdict(lambda: dict(length_mm=0, filament_mm=0, longest_segment_mm=0))
    top_bridges = []
    for z, segments in layers.items():
        for seg in segments:
            item = feature_totals[seg['role']]
            item['length_mm'] += seg['length']
            item['filament_mm'] += seg['e']
            item['longest_segment_mm'] = max(item['longest_segment_mm'], seg['length'])
            if z > 160 and seg['role'] == 'Bridge infill':
                top_bridges.append(dict(z=z, **seg))
    top_bridges.sort(key=lambda item: item['length'], reverse=True)
    layer_summary = []
    for z, segments in sorted(layers.items()):
        if z < 166:
            continue
        roles = defaultdict(lambda: dict(length_mm=0, longest_segment_mm=0, count=0))
        for seg in segments:
            record = roles[seg['role']]
            record['count'] += 1
            record['length_mm'] += seg['length']
            record['longest_segment_mm'] = max(record['longest_segment_mm'], seg['length'])
        layer_summary.append(dict(z=z, roles=roles))
    summary['features'] = feature_totals
    summary['longest_upper_bridge_segments'] = top_bridges[:6]
    summary['upper_layers'] = layer_summary
    return layers, summary


if __name__ == '__main__':
    without, a = read('without_supports')
    supported, b = read('with_supports')
    (HERE / 'measurements.json').write_text(json.dumps(dict(without_supports=a, with_supports=b), indent=2)+'\n')
    for name, info in [('without supports', a), ('with supports', b)]:
        print(name, info['filament used [g]'], 'g;', info['estimated printing time (normal mode)'])
        print('Longest upper bridge segments:', [(s['z'], round(s['length'], 3), s['line']) for s in info['longest_upper_bridge_segments'][:3]])
    for z in [167,168,169,170,170.2,170.4,170.6,170.8,171,171.2,171.4]:
        segs=without.get(z, [])
        bridges=[s for s in segs if s['role']=='Bridge infill']
        supports=[s for s in supported.get(z, []) if s['role'].startswith('Support')]
        print(z, 'bridge', len(bridges), 'max', round(max([s['length'] for s in bridges]+[0]),2), 'support segments',len(supports))
