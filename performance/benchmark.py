#!/usr/bin/env python3
"""Reproducible subprocess latency baseline/final comparison; writes bounded evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--label', required=True)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--repeats', type=int, default=3)
    p.add_argument('--final', action='store_true')
    args = p.parse_args()
    record = dict(schema_version=1, label=args.label, platform=platform.platform(),
                  python=sys.version, cpus=os.cpu_count(),
                  revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  dirty_diff_sha256=hashlib.sha256(subprocess.check_output(['git','diff'],cwd=ROOT)).hexdigest(),
                  lock_sha256=hashlib.sha256((ROOT/'uv.lock').read_bytes()).hexdigest(), workflows={})
    with tempfile.TemporaryDirectory(prefix='engineering-benchmark-') as folder:
        temp = Path(folder)
        cad = temp/'cad.py'; shutil.copyfile(ROOT/'performance/fixtures/cad.py', cad)
        python = str(ROOT/'.venv/bin/python')
        evaluator = str(ROOT/'evaluate_model.py')
        script = str(ROOT/'performance/fixtures/script.py')
        ordinary = [str(ROOT/'execute.py'), script] if args.final else ['uv','run','--locked','python', script]
        jobs = {'script': ordinary,
                'cad_geometry': [python,evaluator,str(cad),'--views','none'],
                'cad_default': [python,evaluator,str(cad)],
                'cad_render_export': [python,evaluator,str(cad),'--views','isometric,front','--export'],
                'cad_slice': [python,evaluator,str(cad),'--views','none','--slice']}
        if args.final:
            jobs['cad_reuse'] = [python,evaluator,str(cad),'--reuse']
            jobs['script_preinitialized'] = [str(ROOT/'execute.py'),'--strategy','preinitialized','--preload','scientific',script]
        for name, command in jobs.items():
            samples=[]
            for i in range(args.repeats):
                started=time.perf_counter()
                r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=900)
                elapsed=time.perf_counter()-started
                samples.append(dict(seconds=elapsed,exit_code=r.returncode,
                    stage_timings=(json.loads(r.stdout).get('timings_seconds') if name.startswith('cad') and r.stdout else None),
                    error=(r.stderr+r.stdout)[-1500:] if r.returncode not in (0,2) else None))
                print(f'{name} [{i}]: {elapsed:.3f}s exit={r.returncode}', flush=True)
            record['workflows'][name]=dict(first_seconds=samples[0]['seconds'],
                subsequent_median_seconds=statistics.median(x['seconds'] for x in samples[1:] or samples), samples=samples)
        samples=[]
        for i in range(args.repeats):
            solve=str(ROOT/'performance/fixtures/solve.py')
            command=[str(ROOT/'execute.py'),solve,str(temp/f'solve{i}')] if args.final else [python,solve,str(temp/f'solve{i}')]
            env=os.environ.copy();env['PYTHONPATH']=str(ROOT)
            started=time.perf_counter();r=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
            samples.append(dict(seconds=time.perf_counter()-started,exit_code=r.returncode,
                displacement_mm=float(r.stdout.strip()) if r.returncode==0 else None,
                error=(r.stdout+r.stderr)[-1500:] if r.returncode else None))
        record['workflows']['physical_solve']=dict(first_seconds=samples[0]['seconds'],
            subsequent_median_seconds=statistics.median(x['seconds'] for x in samples[1:] or samples),samples=samples)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__': main()
