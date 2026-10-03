#!/usr/bin/env python3
"""Matched resource-budget study using existing coordinator/history primitives.

Run through execute.py with an outer budget covering this study's private
coordinator. No exports, slicing, changed geometry, global defaults or solvers.
All observations are local; this helper never publishes or commits evidence.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from execution.history import iter_records, iter_spans
from execution.identity import digest, repository_revision
from execution.resources import inherited_budget
from performance.benchmark import stop_coordinator


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeats',type=int,default=3)
    args=p.parse_args()
    if not 1<=args.repeats<=5:p.error('Use 1..5 matched pairs per budget')
    source=args.model.resolve(strict=True); output=args.output.resolve()
    if output.is_relative_to(ROOT/'.execution') is False:p.error('This study writes only ignored local evidence')
    outer=inherited_budget()
    if not outer or outer<4:p.error('Run through execute.py with at least four CPU threads')
    # Private admission lies entirely inside the outer CPU allocation. This
    # benchmark explicitly owns four cores and <=2560 MiB; children still obtain
    # leases normally. It is not a normal nested engineering operation.
    env=os.environ.copy()
    for key in ('ENGINEERING_LEASE_THREADS','ENGINEERING_RUN_ID','ENGINEERING_TRACEPARENT'):
        env.pop(key,None)
    env.update(ENGINEERING_INSTANCE=uuid.uuid4().hex,ENGINEERING_CPUS='4',
               ENGINEERING_MEMORY_MB='2560',ENGINEERING_JOBS='4')
    env['ENGINEERING_DATA']=str(output.parent/'budget-study-records')
    output.parent.mkdir(parents=True,exist_ok=True)
    rows=[]; initial=digest(source); identities=set()
    def evaluate(memory):
        before=time.monotonic()
        answer=subprocess.run([str(ROOT/'evaluate_model.py'),str(source),'--views','none','--fresh',
            '--threads','2','--memory-mb',str(memory)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
        elapsed=time.monotonic()-before
        if answer.returncode:
            (output.parent/'budget-study-failure.log').write_text(answer.stdout+answer.stderr)
            raise RuntimeError('Study evaluation failed; inspect local diagnostic log')
        report=json.loads(answer.stdout)
        if not report.get('ok'):raise RuntimeError('Study geometry did not validate')
        identities.add(report.get('reuse',{}).get('identity'))
        return elapsed
    try:
        study_started=time.time_ns()
        cold=evaluate(2048)  # Qualified import host is cold only for this run.
        for repeat in range(args.repeats):
            for memory in ((2048,1024) if repeat%2==0 else (1024,2048)):
                before=time.time_ns();clock=time.monotonic()
                # Independent conventional evaluator subprocesses, existing
                # coordinator admission; no substitute scheduler or worker pool.
                with ThreadPoolExecutor(2) as pool:
                    calls=list(pool.map(evaluate,[memory,memory]))
                wall=time.monotonic()-clock
                records=[r for r in iter_records(Path(env['ENGINEERING_DATA']))
                         if r.get('operation')=='cad.command' and r.get('start_unix_ns',0)>=before]
                if len(records)!=2:raise RuntimeError('Expected two retained CAD run summaries')
                if any(r.get('status')!='completed' for r in records):raise RuntimeError('Study execution failed')
                peaks=[r['resources']['peak_worker_rss_bytes']/1024**2 for r in records]
                rows.append(dict(memory_mb=memory,pair_wall_seconds=wall,call_seconds=calls,
                    queue_seconds=[r.get('queue_seconds') for r in records],peak_worker_rss_mb=peaks,
                    blocked_seconds=[r.get('admission',{}).get('blocked_seconds',{}) for r in records]))
        if digest(source)!=initial or len(identities)!=1:raise RuntimeError('Inputs changed during matched study')
        spans=list(iter_spans(Path(env['ENGINEERING_DATA'])))
        initializations=[s for _,s in spans if s.get('name')=='worker.initialization' and int(s.get('startTimeUnixNano',0))>=study_started]
        record=dict(schema_version=1,revision=repository_revision(),source_sha256=initial,
            input_identity=next(iter(identities)),python=sys.version.split()[0],cadquery=version('cadquery'),
            capacity_cpus=4,capacity_memory_mb=2560,capacity_jobs=4,per_call_cpus=2,
            cold_call_seconds=cold,initialization_spans=len(initializations),rows=rows,
            scope='Fresh geometry only, identical source and closed-input identity, interleaved budgets; no physical/product validation')
        output.write_text(json.dumps(record,indent=2)+'\n');output.chmod(0o600)
        print(json.dumps({'output':str(output),'initialization_spans':len(initializations),
            'summary':{str(memory):{'median_pair_wall_s':statistics.median(r['pair_wall_seconds'] for r in rows if r['memory_mb']==memory),
                'max_queue_s':max(q for r in rows if r['memory_mb']==memory for q in r['queue_seconds']),
                'max_worker_rss_mb':max(q for r in rows if r['memory_mb']==memory for q in r['peak_worker_rss_mb'])} for memory in (2048,1024)}},indent=2))
    finally:
        stop_coordinator(env)


if __name__=='__main__':main()
