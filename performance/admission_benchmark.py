#!/usr/bin/env python3
"""Matched resource-budget study using existing coordinator/history primitives.

Run through execute.py with an outer budget covering this study's private
coordinator. Optional views qualify actual rendering rather than extrapolating
geometry-only memory. No exports, slicing, changed geometry, global defaults or solvers.
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
import tempfile
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from execution.history import iter_records, iter_spans
from execution.identity import digest, repository_revision
from execution.resources import inherited_budget
from execution.telemetry import data_root
from performance.benchmark import stop_coordinator


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeats',type=int,default=3)
    p.add_argument('--views',choices=('none','isometric'),default='none',
                   help='Qualify geometry alone or the actual isometric-render workload')
    p.add_argument('--memory-budgets',type=int,nargs='+',default=[2048,1024])
    p.add_argument('--concurrent',type=int,choices=(2,4),default=2)
    p.add_argument('--coordinator-policy',choices=('reserved','unreserved'),default='reserved',
                   help='Experimental unreserved admission retains job limits and the outer RSS watchdog')
    args=p.parse_args()
    if not 1<=args.repeats<=5:p.error('Use 1..5 matched batches per budget')
    if any(b<1 or b>2560 for b in args.memory_budgets) or len(set(args.memory_budgets))!=len(args.memory_budgets):
        p.error('Use distinct positive budgets no larger than 2560 MiB')
    source=args.model.resolve(strict=True); output=args.output.resolve()
    if output.is_relative_to(ROOT/'.execution') is False:p.error('This study writes only ignored local evidence')
    outer=inherited_budget()
    study_cpus=2*args.concurrent
    if not outer or outer<study_cpus:p.error(f'Run through execute.py with at least {study_cpus} CPU threads')
    try:
        parent=json.loads((data_root()/'jobs'/f'{os.environ["ENGINEERING_RUN_ID"]}.json').read_text())
    except (KeyError,OSError,ValueError):
        p.error('This study needs a coordinator-managed outer execute job')
    if parent.get('memory_mb',0)<2560:
        p.error('Run through execute.py with at least 2560 MiB for the aggregate RSS watchdog')
    # Private admission lies entirely inside the outer CPU allocation. This
    # benchmark explicitly owns its study cores and <=2560 MiB; children still obtain
    # leases normally. It is not a normal nested engineering operation.
    env=os.environ.copy()
    for key in ('ENGINEERING_LEASE_THREADS','ENGINEERING_RUN_ID','ENGINEERING_TRACEPARENT'):
        env.pop(key,None)
    env.update(ENGINEERING_INSTANCE=uuid.uuid4().hex,ENGINEERING_CPUS=str(study_cpus),
               ENGINEERING_MEMORY_MB='2560',ENGINEERING_JOBS='4')
    if args.coordinator_policy=='unreserved':env['ENGINEERING_BENCHMARK_UNRESERVED']='1'
    env['ENGINEERING_DATA']=str(output.parent/'budget-study-records')
    output.parent.mkdir(parents=True,exist_ok=True)
    rows=[]; initial=digest(source); identities=set()
    experimental=None
    def evaluate(memory):
        before=time.monotonic()
        # Independent calls need distinct managed destinations. These benchmark
        # images are local diagnostics, never object deliverables or publication.
        with tempfile.TemporaryDirectory(prefix='budget-view-',dir=output.parent) as folder:
            answer=subprocess.run([str(ROOT/'evaluate_model.py'),str(source),'--views',args.views,'--fresh',
                '--output-dir',folder,'--threads','2','--memory-mb',str(memory)],
                cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
        elapsed=time.monotonic()-before
        if answer.returncode:
            (output.parent/'budget-study-failure.log').write_text(answer.stdout+answer.stderr)
            raise RuntimeError('Study evaluation failed; inspect local diagnostic log')
        report=json.loads(answer.stdout)
        if not report.get('ok'):raise RuntimeError('Study geometry did not validate')
        if args.views!='none' and not (len(report.get('views',[]))==1 and report['views'][0].get('ok')):
            raise RuntimeError('Study render did not complete')
        identities.add(report.get('reuse',{}).get('identity'))
        return elapsed
    try:
        # Start both policies as direct children. A daemon created by a short-
        # lived evaluator can become a sibling of this outer job after adoption,
        # escaping its process-tree RSS watchdog.
        command=([sys.executable,str(ROOT/'performance/fixtures/unreserved_coordinator.py')]
            if args.coordinator_policy=='unreserved' else [sys.executable,'-m','execution.coordinator'])
        socket_path=Path(subprocess.check_output([sys.executable,'-c',
            'from execution.protocol import socket_path; print(socket_path())'],cwd=ROOT,env=env,text=True).strip())
        with (output.parent/'private-coordinator.log').open('ab') as log:
            experimental=subprocess.Popen(command,cwd=ROOT,env=env,
                stdin=subprocess.DEVNULL,stdout=log,stderr=log)
        deadline=time.monotonic()+10
        while not socket_path.exists():
            if experimental.poll() is not None or time.monotonic()>deadline:
                raise RuntimeError('Private coordinator did not start')
            time.sleep(.03)
        study_started=time.time_ns()
        cold=evaluate(args.memory_budgets[0])  # Qualified import host is cold only for this run.
        for repeat in range(args.repeats):
            for memory in (args.memory_budgets if repeat%2==0 else reversed(args.memory_budgets)):
                before=time.time_ns();clock=time.monotonic()
                # Independent conventional evaluator subprocesses, existing
                # coordinator admission; no substitute scheduler or worker pool.
                with ThreadPoolExecutor(args.concurrent) as pool:
                    calls=list(pool.map(evaluate,[memory]*args.concurrent))
                wall=time.monotonic()-clock
                records=[r for r in iter_records(Path(env['ENGINEERING_DATA']))
                         if r.get('operation')=='cad.command' and r.get('start_unix_ns',0)>=before]
                if len(records)!=args.concurrent:raise RuntimeError('Expected one retained CAD summary per call')
                if any(r.get('status')!='completed' for r in records):raise RuntimeError('Study execution failed')
                peaks=[r['resources']['peak_worker_rss_bytes']/1024**2 for r in records]
                rows.append(dict(memory_mb=memory,batch_wall_seconds=wall,call_seconds=calls,
                    queue_seconds=[r.get('queue_seconds') for r in records],peak_worker_rss_mb=peaks,
                    blocked_seconds=[r.get('admission',{}).get('blocked_seconds',{}) for r in records]))
        if digest(source)!=initial or len(identities)!=1:raise RuntimeError('Inputs changed during matched study')
        spans=list(iter_spans(Path(env['ENGINEERING_DATA'])))
        initializations=[s for _,s in spans if s.get('name')=='worker.initialization' and int(s.get('startTimeUnixNano',0))>=study_started]
        record=dict(schema_version=1,revision=repository_revision(),source_sha256=initial,
            input_identity=next(iter(identities)),python=sys.version.split()[0],cadquery=version('cadquery'),
            capacity_cpus=study_cpus,capacity_memory_mb=2560,capacity_jobs=4,per_call_cpus=2,views=args.views,
            concurrent_calls=args.concurrent,coordinator_policy=args.coordinator_policy,
            cold_call_seconds=cold,initialization_spans=len(initializations),rows=rows,
            scope='Fresh geometry and selected views, identical source and closed-input identity within each policy, interleaved budgets; no physical/product validation')
        output.write_text(json.dumps(record,indent=2)+'\n');output.chmod(0o600)
        print(json.dumps({'output':str(output),'initialization_spans':len(initializations),
            'summary':{str(memory):{'median_batch_wall_s':statistics.median(r['batch_wall_seconds'] for r in rows if r['memory_mb']==memory),
                'max_queue_s':max(q for r in rows if r['memory_mb']==memory for q in r['queue_seconds']),
                'max_worker_rss_mb':max(q for r in rows if r['memory_mb']==memory for q in r['peak_worker_rss_mb'])} for memory in args.memory_budgets}},indent=2))
    finally:
        stop_coordinator(env)
        if experimental is not None:
            try:experimental.wait(timeout=15)
            except subprocess.TimeoutExpired:
                experimental.kill();experimental.wait()


if __name__=='__main__':main()
