#!/usr/bin/env python3
"""Focused tracing, thread and scheduling policies; ordinary files, shared scheduler."""
import argparse
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

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    from performance.benchmark import stop_coordinator
    from execution.batch import ScriptTask,run
    from evaluate_model import review,DEFAULTS
    from execution.telemetry import run as observed
    from execution.resources import Admission
    from execution.identity import digest
    import platform
    from importlib.metadata import version
    capacity=Admission()
    record={'schema_version':1,'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'platform':platform.platform(),'python':sys.version,'lock_sha256':digest(ROOT/'uv.lock'),
        'available_cpus':len(os.sched_getaffinity(0)),'shared_cpu_capacity':capacity.cpus,
        'numpy':version('numpy'),'policies':{}}
    with tempfile.TemporaryDirectory(prefix='engineering-policy-',dir=Path.home()) as folder:
        temp=Path(folder);os.environ['ENGINEERING_DATA']=str(temp/'records')
        os.environ['ENGINEERING_INSTANCE']=uuid.uuid4().hex
        short=temp/'short.py';short.write_text('print(42)\n')
        matrix=temp/'matrix.py'
        matrix.write_text('import numpy as np,sys\na=np.ones((2400,2400));b=a.copy()\nfor i in range(3):c=a@b\nopen(sys.argv[1],"w").write(str(float(c[0,0])))\n')
        def command(source,*options,argument=None):
            before=time.perf_counter()
            result=subprocess.run([str(ROOT/'execute.py'),*options,str(source),*([str(argument)] if argument else [])],capture_output=True,text=True,cwd=ROOT,timeout=120)
            if result.returncode:raise RuntimeError(result.stderr+result.stdout)
            return time.perf_counter()-before
        def measure(fn,count=5):
            samples=[fn() for _ in range(count)]
            return {'samples_seconds':samples,'median_seconds':statistics.median(samples)}
        command(short) # Coordinator initialization is excluded from this overhead experiment.
        for enabled in ('0','1'):
            os.environ['ENGINEERING_TRACE']=enabled
            record['policies']['tracing_'+enabled]=measure(lambda:command(short))
        os.environ['ENGINEERING_TRACE']='1'
        for threads in (1,2,4,8):
            if threads>capacity.cpus:continue
            command(matrix,'--threads',str(threads),argument=temp/'matrix.txt')
            record['policies'][f'matrix_threads_{threads}']=measure(lambda:command(matrix,'--threads',str(threads),argument=temp/'matrix.txt'),3)
            assert (temp/'matrix.txt').read_text()=='2400.0'
        tasks=[ScriptTask(str(i),matrix,(str(temp/f'{i}.txt'),),outputs=(temp/f'{i}.txt',),threads=min(4,max(1,capacity.cpus//2))) for i in range(2)]
        for concurrent in (1,2):
            def batch():
                before=time.perf_counter();answers=run(tasks,max_concurrent=concurrent)
                assert all(a['exit_code']==0 for a in answers.values()),answers
                assert all((temp/f'{i}.txt').read_text()=='2400.0' for i in range(2))
                return time.perf_counter()-before
            record['policies'][f'batch_concurrency_{concurrent}']=measure(batch,3)
        cad=temp/'cad.py';cad.write_bytes((ROOT/'performance/fixtures/cad.py').read_bytes())
        completed=subprocess.run([str(ROOT/'evaluate_model.py'),str(cad),'--export'],capture_output=True,text=True,cwd=ROOT,timeout=60)
        assert completed.returncode==0,completed.stdout+completed.stderr
        # --fresh slices: both lanes repeat identical engineering evidence, not cache hits.
        for threads in sorted({1,min(4,capacity.cpus)}):
            def slice_pair():
                with observed('benchmark.slice',source=cad.with_suffix('.stl')):
                    before=time.perf_counter()
                    result=review(cad.with_suffix('.stl'),**DEFAULTS,threads=threads,reuse=False)
                    assert result['support_probe']['ok']
                    return time.perf_counter()-before
            record['policies'][f'slice_threads_{threads}']=measure(slice_pair,3)
        stop_coordinator(os.environ.copy())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v['median_seconds'] for k,v in record['policies'].items()},indent=2))
if __name__=='__main__':main()
