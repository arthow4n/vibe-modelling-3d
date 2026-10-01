"""Private controlled-study runner: replay identity-checked retained native scenes.

No remeshing, geometry redesign or engineering-question backend selection.
Edits must be recorded explicitly by the study caller; all accepted states still
go through the normal extractor/witness. Timing excludes Python extraction.
"""
import gzip
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time
from physical_analysis.backends.polyfem_worker import digest, write_json, implementation_identity
from physical_analysis.backends.polyfem_output import extract
from physical_analysis.backends.structural import runtime_environment
from physical_analysis.results import AnalysisResult


def prepare(source, directory, threads):
    source=Path(source);directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    original=json.loads((source/'result.json').read_text())
    for p in source.iterdir():
        name=p.name.removesuffix('.gz')
        if name in ('case.json','scene.json','mesh.json') or name.startswith('part_'):
            (directory/name).write_bytes(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
    provenance=original['provenance']
    for key,file in (('case_sha256','case.json'),('input_sha256','scene.json'),('mesh_sha256','mesh.json')):
        if digest(directory/file)!=provenance[key]:raise ValueError('Retained scene identity differs')
    for file,sha in provenance['mesh_files_sha256'].items():
        if digest(directory/file)!=sha:raise ValueError('Retained numerical mesh identity differs')
    case=json.loads((directory/'case.json').read_text())
    for part in case['parts']:
        if digest(directory/part['geometry'])!=part['sha256']:raise ValueError('Retained CAD identity differs')
    case['ipc']['threads']=threads
    return directory,case,json.loads((directory/'scene.json').read_text()),json.loads((directory/'mesh.json').read_text()),provenance


def run(prepared, *, changes, timeout=180, retain=None):
    directory,case,scene,mesh,old=prepared
    if type(case['ipc']['threads']) is not int or case['ipc']['threads']<1:raise ValueError('Invalid thread count')
    for name,data in (('case.json',case),('scene.json',scene),('mesh.json',mesh)):write_json(directory/name,data)
    env=runtime_environment();threads=case['ipc']['threads']
    env.update(OMP_NUM_THREADS=str(threads),OPENBLAS_NUM_THREADS=str(threads))
    exe=shutil.which(os.environ.get('POLYFEM_COMMAND',old['executable']))
    if not exe or digest(exe)!=old['executable_sha256']:raise ValueError('Fixed study requires recorded executable')
    command=[exe,'--json','scene.json','--max_threads',str(threads)]
    r=AnalysisResult(case['name'],'running',assumptions=['Controlled native-scene replay; changes recorded explicitly; numerical evidence only.'])
    r.provenance=dict(old,backend_sha256=implementation_identity(),case_sha256=digest(directory/'case.json'),
        input_sha256=digest(directory/'scene.json'),mesh_sha256=digest(directory/'mesh.json'),
        command=command,thread_environment={k:env[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS')},
        study_changes=changes,source_input_sha256=old['input_sha256'],source_backend_sha256=old['backend_sha256'],
        ipc_settings=case['ipc'],study_runner_sha256=digest(__file__))
    write_json(directory/'run_metadata.json',r.provenance)
    before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.perf_counter()
    with (directory/'solver.log').open('w') as log:
        process=subprocess.Popen(command,cwd=directory,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired,KeyboardInterrupt) as exc:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            process.wait();code=None
            r.status='timeout' if isinstance(exc,subprocess.TimeoutExpired) else 'interrupted'
            r.errors.append('Controlled study stopped; native process group terminated')
    elapsed=time.perf_counter()-started;after=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
    r.provenance.update(native_exit_code=code,native_timing=dict(wall_seconds=elapsed,cpu_seconds=cpu,cpu_percent=100*cpu/elapsed))
    write_json(directory/'run_metadata.json',r.provenance)
    if code:r.status='solver_failed'
    if list(directory.glob('step_*.vtu')):
        try:extract(directory,case,mesh['parts'],mesh['selections'],scene,r,partial=code!=0)
        except Exception as exc:
            if code==0:r.status='extraction_failed'
            r.errors.append(f'{type(exc).__name__}: {exc}')
    elif code==0:r.status='extraction_failed';r.errors.append('No native accepted fields')
    r.write(directory/'result.json')
    if retain:
        from physical_analysis.evidence import retain_run
        retain_run(directory,retain)
    print(json.dumps(dict(directory=str(directory),status=r.status,completed=r.completed,timing=r.provenance['native_timing'],metrics=r.metrics)),flush=True)
    if r.status=='interrupted':raise KeyboardInterrupt
    return r
