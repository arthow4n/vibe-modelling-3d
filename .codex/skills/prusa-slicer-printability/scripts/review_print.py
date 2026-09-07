"""Create a fresh diagnostic PrusaSlicer review directory; never send a print job.

Writes raw G-code/log (ignored), hashes, role/footprint summary and optional SVGs.
Requires the caller's profile and safe build volume; no rotation or splitting.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
from inspect_gcode import read_paths, summarize, draw_layers


def footprint(layers, bed):
    if len(bed) != 3 or not all(math.isfinite(v) and v > 0 for v in bed):
        raise ValueError('Three positive finite safe build dimensions required')
    lo, hi = [float('inf')]*2, [-float('inf')]*2
    support_segments = 0
    for paths in layers.values():
        for path in paths:
            support_segments += int(path['role'].startswith('Support material'))
            width = path['width_mm']
            if not math.isfinite(width) or width <= 0:
                raise ValueError('Invalid extrusion width')
            for point in (path['a'], path['b']):
                if not all(math.isfinite(v) for v in point):
                    raise ValueError('Nonfinite deposition position')
                for k in (0, 1):
                    lo[k] = min(lo[k], point[k]-width/2)
                    hi[k] = max(hi[k], point[k]+width/2)
    zlo, zhi = min(layers), max(layers)
    fits = zlo >= 0 and zhi <= bed[2] and all(0 <= lo[k] <= hi[k] <= bed[k] for k in (0, 1))
    return {'xy_bounds_including_half_width_mm': lo+hi, 'max_layer_z_mm': zhi,
            'inside_safe_volume': fits, 'support_segments': support_segments}


def review(model, profile, output, bed, slicer='prusa-slicer', windows=None,
           expect_no_supports=False, timeout=600):
    model, profile, output = Path(model).resolve(), Path(profile).resolve(), Path(output).resolve()
    # Verify inputs before reserving a new directory. Existing output is never reused.
    hashes = {key: hashlib.sha256(path.read_bytes()).hexdigest()
              for key, path in [('model', model), ('profile', profile)]}
    if len(bed) != 3 or not all(math.isfinite(v) and v > 0 for v in bed):
        raise ValueError('Invalid safe build volume')
    windows = windows or []
    names = set()
    for item in windows:
        name = item['name']
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', name) or name in names:
            raise ValueError('Window names must be unique lowercase filename stems')
        names.add(name)
        if not item['layers'] or not all(math.isfinite(v) for v in item['layers']):
            raise ValueError('Window layers must be finite and nonempty')
        box = item['window']
        if len(box) != 4 or not all(math.isfinite(v) for v in box) or box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError('Invalid layer window')
    output.mkdir(parents=True, exist_ok=False)
    (output/'.gitignore').write_text('*.gcode\n*.log\n')
    help_result = subprocess.run([slicer, '--help'], capture_output=True, text=True,
                                 timeout=30, check=False)
    version_header = (help_result.stdout + help_result.stderr).splitlines()[:8]
    command = [slicer, '--load', str(profile), '--center', f'{bed[0]/2:g},{bed[1]/2:g}',
               '--export-gcode', '--output', str(output/'slice.gcode'), str(model)]
    (output/'command.json').write_text(json.dumps(command, indent=2)+'\n')
    with (output/'slice.log').open('w') as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=timeout, check=False)
    log_text = (output/'slice.log').read_text(errors='replace')
    gcode = output/'slice.gcode'
    if completed.returncode != 0 or not gcode.exists() or gcode.stat().st_size == 0:
        raise RuntimeError(f'Slicing did not produce fresh G-code; inspect {output / "slice.log"}')
    # A fresh file is parsed as well: a zero process exit alone is insufficient.
    layers, metadata = read_paths(gcode)
    paths = summarize(layers, metadata)
    bounds = footprint(layers, bed)
    notices = [line for line in log_text.splitlines() if re.search(
        r'warning|error|detected print stability|long bridging|loose extrusions|consider enabling supports', line, re.I)]
    for item in windows:
        draw_layers(layers, item['layers'], item['window'], output/(item['name']+'.svg'))
    # Catch changed inputs rather than assigning the wrong hashes to a slice.
    if any(hashlib.sha256(path.read_bytes()).hexdigest() != hashes[key]
           for key, path in [('model', model), ('profile', profile)]):
        raise RuntimeError('Input changed during slicing; repeat in a fresh directory')
    report = {'model': str(model), 'profile': str(profile), 'input_sha256': hashes,
              'slicer_help_header': version_header,
              'gcode_sha256': hashlib.sha256(gcode.read_bytes()).hexdigest(),
              'safe_build_volume_mm': list(bed), 'metadata': metadata, **bounds,
              'log_notices': notices, 'windows': windows,
              'review_required': bool(notices) or not bounds['inside_safe_volume'] or
                  (expect_no_supports and bounds['support_segments'] > 0),
              'limits': 'Generic diagnostic job, not sent to a printer. Linear ASCII paths; width fallback is 0.45 mm if no WIDTH comment. Bounds exclude travel/start/end motion and flow spread. Role labels do not establish anchors or free-air spans. Profile includes are not resolved or independently hashed.'}
    (output/'paths.json').write_text(json.dumps(paths, indent=2)+'\n')
    (output/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--bed', type=float, nargs=3, required=True, metavar=('X', 'Y', 'Z'))
    parser.add_argument('--slicer', default='prusa-slicer')
    parser.add_argument('--windows', type=Path, help='JSON list of {name,layers,window} in sliced bed coordinates')
    parser.add_argument('--expect-no-supports', action='store_true')
    parser.add_argument('--timeout', type=float, default=600)
    args = parser.parse_args()
    windows = json.loads(args.windows.read_text()) if args.windows else None
    report = review(args.model, args.profile, args.out, args.bed, args.slicer,
                    windows, args.expect_no_supports, args.timeout)
    print(json.dumps({'report': str(args.out/'summary.json'), 'metadata': report['metadata'],
                      'review_required': report['review_required']}))
    raise SystemExit(2 if report['review_required'] else 0)


if __name__ == '__main__':
    main()
