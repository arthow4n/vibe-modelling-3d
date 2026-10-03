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


class Coordinator:
    def __init__(self):
        self.runtime=runtime_identity()
        self.admission=Admission()
        self.ctx=mp.get_context('forkserver')
        mp.set_forkserver_preload(['execution.preload'])
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
            if len(fds)!=3:raise ValueError('Expected stdin, stdout and stderr descriptors')
            if request['kind']!='script':raise ValueError('Unsupported execution operation')
            self.last_request=time.monotonic()
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
                        answer=self.execute(request,fds,cancelled,deadline)
                        answer['queue_seconds']=queued
                        write_record(request['run_id'],dict(run_id=request['run_id'],source=request['source'],source_sha256=request['source_sha256'],**answer))
                protocol.send(connection,answer)
            finally:detach(parent);_active.reset(token)
        except BaseException as exc:
            if 'request' in locals() and request.get('run_id'):
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
if __name__=='__main__':Coordinator().serve()
