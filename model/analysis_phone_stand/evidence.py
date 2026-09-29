"""Retain compact, replayable solver evidence from a completed/failed run.

Usage: uv run --locked python model/analysis_phone_stand/evidence.py RUN LABEL
Raw large result fields stay in RUN; compressed input can be replayed with ccx.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent

def retain(run,label):
    run=Path(run)
    target=ROOT/'notes'/'analysis'/label
    target.mkdir(parents=True,exist_ok=False)
    result=json.loads((run/'result.json').read_text())
    result['artifacts']={
        'case':'case.json','input':'analysis.inp.gz','solver_log':'solver.log.gz',
        'increments':'analysis.sta','raw_fields_retained_in_git':False,
        'reproduce':'Decompress analysis.inp.gz into a fresh run directory; run ccx -i analysis. '
                    'Use analyze.py to rebuild geometry, mesh and compact result.'}
    (target/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    shutil.copyfile(run/'case.json',target/'case.json')
    for name in ('analysis.inp','solver.log'):
        source=run/name
        if source.exists():
            (target/(name+'.gz')).write_bytes(gzip.compress(source.read_bytes(),mtime=0))
    if (run/'analysis.sta').exists(): shutil.copyfile(run/'analysis.sta',target/'analysis.sta')
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);p.add_argument('label')
    a=p.parse_args()
    if not a.label.replace('_','').isalnum(): raise SystemExit('Label must be a short identifier')
    print(retain(a.run,a.label))
