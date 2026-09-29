"""Compact evidence archive, following the phone-stand object's retention pattern.

Keeps replayable input, fixture geometry, history, logs and provenance. Large raw
fields remain outside Git; rerun the compressed input to recover them.
"""
import argparse
import gzip
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent


def retain(run, label):
    run = Path(run)
    target = ROOT/'notes'/'analysis'/label
    target.mkdir(parents=True, exist_ok=False)
    result = json.loads((run/'result.json').read_text())
    result['artifacts'] = dict(case='case.json', input='analysis.inp.gz',
        solver_log='solver.log.gz', worker_log='worker.log.gz', increments='analysis.sta',
        regions='regions.json.gz', fixture_geometry=['part_0.brep.gz', 'part_1.brep.gz'],
        raw_fields_retained_in_git=False,
        reproduce='Decompress analysis.inp.gz in a new directory and run ccx -i analysis. '
                  'Use analyze.py for current geometry/meshing; retained failed fixtures are historical.')
    (target/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    shutil.copyfile(run/'case.json', target/'case.json')
    for name in ('analysis.inp', 'solver.log', 'worker.log', 'regions.json', 'part_0.brep', 'part_1.brep'):
        source = run/name
        if source.exists():
            (target/(name+'.gz')).write_bytes(gzip.compress(source.read_bytes(), mtime=0))
    if (run/'analysis.sta').exists():
        shutil.copyfile(run/'analysis.sta', target/'analysis.sta')
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    parser.add_argument('label')
    args = parser.parse_args()
    if not args.label.replace('_', '').isalnum():
        raise SystemExit('Label must be a short identifier')
    print(retain(args.run, args.label))
