"""One private local coordinator: admission, process ownership and warm infrastructure."""
import contextvars
import fcntl
import json
import multiprocessing as mp
from multiprocessing.reduction import DupFd
import os
from pathlib import Path
import select
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from . import protocol
from .identity import ROOT, runtime_identity, digest
from .lifecycle import wait, terminate
from .resources import Admission
from .telemetry import span, write_record, data_root


class CADPool:
    """At most two idle geometry owners; identity changes replace state wholesale."""
    def __init__(self,ctx):
        self.ctx=ctx;self.entries={};self.lock=threading.Lock()

    def get(self,request):
        from .identity import fingerprint
        key=fingerprint(dict(identity=request['identity'],threads=request['threads'],environment=request['environment'].get('ENGINEERING_THREADS')))
        with self.lock:
            now=time.monotonic()
            for old,(process,connection,touched,jobs) in list(self.entries.items()):
                if not process.is_alive() or now-touched>60 or jobs>=100:
                    connection.close();terminate(process);del self.entries[old]
            if key in self.entries:
                process,connection,_,jobs=self.entries.pop(key)
                return key,process,connection,jobs,True
            if len(self.entries)>=2:
                old=next(iter(self.entries));process,connection,*_=self.entries.pop(old)
                connection.close();terminate(process)
        from .cad import child
        connection,child_connection=self.ctx.Pipe()
        process=self.ctx.Process(target=child,args=(child_connection,));process.start();child_connection.close()
        return key,process,connection,0,False

    def put(self,key,process,connection,jobs):
        with self.lock:
            if len(self.entries)>=2:
                connection.close();terminate(process)
            else:self.entries[key]=(process,connection,time.monotonic(),jobs)

    def close(self):
        with self.lock:
            for process,connection,*_ in self.entries.values():
                connection.close();terminate(process)
            self.entries.clear()


def run_cad(request,pool,cancelled,deadline,isolated=False,progress=None):
    """Stage outputs, check final source identity, then publish with exclusive ownership."""
    import copy
    from .artifacts import destinations
    from .identity import cad_identity
    from .telemetry import child_environment
    managed=request['cad']
    output_paths=[item['path'] for item in managed['exports']]
    output_paths += [str(Path(managed['output_dir'])/f"{Path(request['source']).stem}_{view}.png") for view in managed['views']]
    if request.get('reuse'):output_paths.append(str(data_root()/'geometry-ownership'/request['identity']))
    started=time.monotonic()
    with destinations(output_paths,cancelled,deadline),tempfile.TemporaryDirectory(prefix='engineering-cad-',dir=data_root()) as directory:
        original=copy.deepcopy(request);request=copy.deepcopy(request)
        request['environment']=child_environment(request['environment'])
        request['environment']['ENGINEERING_LEASE_THREADS']=str(request['threads'])
        remap={}
        for i,item in enumerate(request['cad']['exports']):
            staged=str(Path(directory)/f"export-{i}{Path(item['path']).suffix}")
            remap[staged]=item['path'];item['path']=staged
        request['cad']['output_dir']=directory
        for view in managed['views']:
            name=f"{Path(request['source']).stem}_{view}.png"
            remap[str(Path(directory)/name)]=str(Path(managed['output_dir'])/name)
        if cad_identity(request['source'],request['dependencies'],request['environment'])!=request['identity']:
            raise RuntimeError('CAD inputs changed while queued; run the current source')
        persistent=pool is not None and request.get('reuse') and not isolated
        if isolated:
            request_path=Path(directory)/'request.json';response=Path(directory)/'response.json'
            request_path.write_text(json.dumps(request['cad']))
            process=subprocess.Popen([sys.executable,str(ROOT/'evaluate_model.py'),'--worker',str(request_path),str(response)],
                cwd=ROOT,env=request['environment'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            connection=None;warm=False
        else:
            if persistent:key,process,connection,jobs,warm=pool.get(request)
            else:
                from .cad import child
                ctx=pool.ctx if pool else mp.get_context('forkserver')
                connection,other=ctx.Pipe();process=ctx.Process(target=child,args=(other,));process.start();other.close();warm=False
            connection.send(request)
        try:
            if isolated:
                code,resources=wait(process,max(.001,deadline-time.monotonic()),cancelled,request['memory_mb'])
                if not response.is_file():raise RuntimeError(f'CAD worker exited {code} without report')
                report=json.loads(response.read_text())
            else:
                import psutil
                peak=None
                while True:
                    if connection.poll(.02):
                        message=connection.recv()
                        if message.get('event'):
                            if progress:progress(message)
                            continue
                        report=message;break
                    if not process.is_alive():raise RuntimeError(f'CAD worker exited {process.exitcode} without report')
                    if cancelled():raise InterruptedError('CAD request cancelled')
                    if time.monotonic()>deadline:raise TimeoutError('CAD evaluation exceeded deadline')
                    try:
                        rss=psutil.Process(process.pid).memory_info().rss;peak=max(peak or 0,rss)
                        if rss>request['memory_mb']*1024**2:raise MemoryError('CAD worker memory budget exceeded')
                    except psutil.Error:pass
                resources=dict(peak_worker_rss_bytes=peak)
            if cancelled():raise InterruptedError('CAD request cancelled before publication')
            if cad_identity(request['source'],request['dependencies'],request['environment'])!=request['identity']:
                raise RuntimeError('CAD inputs changed during execution; managed artifacts were not published')
            for item in [*report.get('exports',[]),*report.get('views',[])]:
                if item.get('ok'):
                    staged=Path(item['path']);target=Path(remap[str(staged)]);target.parent.mkdir(parents=True,exist_ok=True)
                    # Cross-device atomic publication uses the established writer.
                    from evaluate_model import atomic_bytes
                    atomic_bytes(target,staged.read_bytes());item['path']=str(target)
            if persistent and report.get('ok'):
                pool.put(key,process,connection,jobs+1);connection=None
            return dict(report=report,exit_code=0 if report['ok'] else 1,resources=resources,
                warm_worker=warm,worker_seconds=time.monotonic()-started)
        finally:
            if connection is not None:connection.close();terminate(process)
            if isolated:terminate(process)


class Coordinator:
    def __init__(self):
        self.runtime=runtime_identity()
        self.admission=Admission()
        self.ctx=mp.get_context('forkserver')
        mp.set_forkserver_preload(['execution.preload'])
        self.cad_pool=CADPool(self.ctx)
        self.last_request=time.monotonic();self.stopping=threading.Event()
        self.jobs=set();self.lock=threading.Lock()

    def handle(self, connection):
        fds=[]
        try:
            request,fds=protocol.receive(connection,descriptors=True)
            if request.get('kind')=='status':
                protocol.send(connection,dict(cpus=self.admission.cpus,memory_mb=self.admission.memory_mb,
                    active=self.admission.active,pid=os.getpid(),runtime=self.runtime));return
            if request.get('kind')=='stop':
                self.stopping.set();protocol.send(connection,dict(stopping=True));return
            if request.get('kind')=='lease':
                def abandoned():
                    return self.stopping.is_set() or (bool(select.select([connection],[],[],0)[0]) and connection.recv(1,socket.MSG_PEEK)==b'')
                with self.admission.acquire(request['threads'],request['memory_mb'],abandoned) as queued:
                    from .resources import current_affinity
                    protocol.send(connection,dict(acquired=True,queue_seconds=queued,affinity=current_affinity()))
                    while not abandoned():time.sleep(.05)
                return
            if len(fds)!=3:raise ValueError('Expected stdin, stdout and stderr descriptors')
            if request['kind'] not in ('script','cad'):raise ValueError('Unsupported execution operation')
            from .journal import update as journal
            journal(request,"queued")
            self.last_request=time.monotonic()
            import psutil
            request["environment"]["ENGINEERING_OWNER_PID"]=str(os.getpid())
            request["environment"]["ENGINEERING_OWNER_STARTED"]=str(psutil.Process().create_time())
            def cancelled():
                if self.stopping.is_set():return True
                if select.select([connection],[],[],0)[0]:
                    return connection.recv(1,socket.MSG_PEEK)==b''
                return False
            deadline=time.monotonic()+request['timeout'] if request.get('timeout') else None
            # Explicit trace context enters this handler without global environment mutation.
            from opentelemetry.context import attach,detach
            from opentelemetry.propagate import extract
            from .telemetry import _active
            token=_active.set(request['run_id']);parent=attach(extract({'traceparent':request['environment'].get('ENGINEERING_TRACEPARENT','')}))
            try:
                with span('coordinator.admission'):
                    with self.admission.acquire(request['threads'],request['memory_mb'],cancelled,deadline) as queued:
                        journal(request,'running')
                        answer=run_cad(request,self.cad_pool,cancelled,deadline,progress=lambda event:protocol.send(connection,event)) if request['kind']=='cad' else self.execute(request,fds,cancelled,deadline)
                        answer['queue_seconds']=queued
                        journal(request,'completed' if answer['exit_code']==0 else 'failed')
                        write_record(request['run_id'],dict(run_id=request['run_id'],source=request['source'],source_sha256=request['source_sha256'],**answer))
                protocol.send(connection,answer)
            finally:detach(parent);_active.reset(token)
        except BaseException as exc:
            if 'request' in locals() and request.get('run_id'):
                from .journal import update as journal
                journal(request,'timeout' if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else 'interrupted' if isinstance(exc,InterruptedError) else 'failed')
                write_record(request['run_id'],dict(run_id=request['run_id'],status='timeout' if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else 'interrupted' if isinstance(exc,InterruptedError) else 'failed',failure_type=type(exc).__name__))
            try:protocol.send(connection,dict(exit_code=124 if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else 1,
                status='timeout' if isinstance(exc,(TimeoutError,subprocess.TimeoutExpired)) else 'failed',
                error=f'{type(exc).__name__}: {exc}'))
            except (OSError,EOFError):pass
        finally:
            for fd in fds:
                os.close(fd)
            connection.close()

    def execute(self,request,fds,cancelled,deadline):
        started=time.monotonic()
        remaining=max(.001,deadline-time.monotonic()) if deadline else None
        samples=[]
        def sample(t,rss,cpu):
            # Bound resource history, not script output.
            if len(samples)<2000:samples.append([t,rss,cpu])
        if digest(request['source'])!=request['source_sha256']:
            raise RuntimeError('Script changed while queued; request a fresh execution')
        with span('worker.lifecycle',strategy=request['strategy']):
            from .telemetry import child_environment
            request['environment']=child_environment(request['environment'])
            request['environment']['ENGINEERING_LEASE_THREADS']=str(request['threads'])
            if request['strategy']=='preinitialized':
                from .runner import child
                process=self.ctx.Process(target=child,args=(request,[DupFd(fd) for fd in fds]))
                before=time.monotonic();process.start();startup=time.monotonic()-before
            else:
                directory=tempfile.TemporaryDirectory(prefix='engineering-job-')
                path=Path(directory.name)/'request.json';path.write_text(json.dumps(request));path.chmod(0o600)
                env=dict(request['environment']);env['PYTHONPATH']=str(ROOT)+os.pathsep+env.get('PYTHONPATH','')
                before=time.monotonic()
                process=subprocess.Popen([sys.executable,'-m','execution.runner',str(path)],cwd=request['cwd'],
                    env=env,stdin=fds[0],stdout=fds[1],stderr=fds[2],start_new_session=True)
                startup=time.monotonic()-before
            try:
                code,resources=wait(process,remaining,cancelled,request['memory_mb'],sample)
            except BaseException:
                terminate(process);raise
            finally:
                if request['strategy']=='isolated':directory.cleanup()
                try:
                    folder=data_root()/'resources';folder.mkdir(parents=True,exist_ok=True)
                    (folder/f'{request["run_id"]}.json').write_text(json.dumps(dict(schema_version=1,
                        columns=['unix_ns','tree_rss_bytes','live_tree_cpu_seconds'],samples=samples)))
                except OSError:pass
        return dict(exit_code=code,status='completed' if code==0 else 'failed',
            resources=resources,startup_dispatch_seconds=startup,worker_seconds=time.monotonic()-started,
            execution_strategy=request['strategy'])

    def serve(self):
        path=protocol.socket_path()
        with (path.parent/'daemon.lock').open('a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return
            path.unlink(missing_ok=True)
            server=socket.socket(socket.AF_UNIX);server.bind(str(path));path.chmod(0o600);server.listen(32);server.settimeout(.5)
            def stop(*unused):self.stopping.set()
            signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
            try:
                while not self.stopping.is_set():
                    if not self.admission.active and time.monotonic()-self.last_request>120:break
                    try:connection,_=server.accept()
                    except socket.timeout:continue
                    thread=threading.Thread(target=self.handle,args=(connection,))
                    thread.start()
                    self.jobs.add(thread)
                    self.jobs={t for t in self.jobs if t.is_alive()}
            finally:
                self.stopping.set();server.close();path.unlink(missing_ok=True)
                for job in self.jobs:job.join(10)
                self.cad_pool.close()
if __name__=='__main__':Coordinator().serve()
