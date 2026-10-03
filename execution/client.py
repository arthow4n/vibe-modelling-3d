"""Automatic coordinator startup; conventional fallback before dispatch only."""
import fcntl
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from .identity import ROOT, runtime_identity, digest
from . import protocol
from .telemetry import run, child_environment, span, data_root
from .resources import thread_environment


class CoordinatorUnavailable(RuntimeError):pass


def connect():
    path=protocol.socket_path()
    def attempt():
        connection=socket.socket(socket.AF_UNIX);connection.settimeout(5)
        try:
            connection.connect(str(path))
            protocol.send(connection,{'kind':'status'})
            status=protocol.receive(connection)
            if status.get('runtime')!=runtime_identity():
                connection.close()
                stopping=socket.socket(socket.AF_UNIX);stopping.connect(str(path))
                protocol.send(stopping,{'kind':'stop'});protocol.receive(stopping);stopping.close()
                deadline=time.monotonic()+3
                while path.exists() and time.monotonic()<deadline:time.sleep(.03)
                return None
            connection.close()
            connection=socket.socket(socket.AF_UNIX);connection.settimeout(5);connection.connect(str(path))
            return connection
        except (OSError,EOFError):connection.close();return None
    connection=attempt()
    if connection:return connection
    with (path.parent/'startup.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        connection=attempt()
        if connection:return connection
        log=data_root()/'coordinator.log';log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('ab') as output:
            subprocess.Popen([sys.executable,'-m','execution.coordinator'],cwd=ROOT,
                stdin=subprocess.DEVNULL,stdout=output,stderr=output,start_new_session=True,
                env=thread_environment(os.environ,1))
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            connection=attempt()
            if connection:return connection
            time.sleep(.03)
    raise CoordinatorUnavailable('Local execution coordinator unavailable')


def submit(request, fds=(0,1,2), on_event=None):
    connection=connect()  # Only this pre-dispatch failure permits fallback.
    try:
        with span('coordinator.request'):
            request['environment']=child_environment(request.get('environment'))
            protocol.send(connection,request,fds)
            connection.settimeout(None)
            while True:
                answer=protocol.receive(connection)
                if not answer.get('event'):return answer
                if on_event:on_event(answer)
    except (EOFError,ConnectionError,OSError) as exc:
        raise RuntimeError('Coordinator connection lost after dispatch; execution was not replayed') from exc
    finally:connection.close()


def script(source, arguments=(), *, cwd=None, strategy='isolated', preload='scientific',
           timeout=None, threads=1, memory_mb=2048, profile=None, coordinator=True):
    source=Path(source).resolve(strict=True)
    if not source.is_file():raise ValueError('Script source must be a file')
    with run('script.command',source,strategy,arguments) as record:
        request=dict(kind='script',run_id=record['run_id'],source=str(source),
            source_sha256=digest(source),arguments=list(arguments),cwd=str(Path(cwd or os.getcwd()).resolve()),
            strategy=strategy,preload=preload,timeout=timeout,threads=threads,memory_mb=memory_mb,
            profile=profile,environment=thread_environment(child_environment(),threads),
            runtime=runtime_identity(),pythonpath=[str(ROOT)])
        from .resources import inherited_budget
        if inherited_budget():coordinator=False
        if coordinator:
            try:answer=submit(request)
            except CoordinatorUnavailable:answer=fallback(request)
        else:answer=fallback(request)
        record.update(answer)
        return answer


def fallback(request):
    import json
    from .lifecycle import run as run_process
    with tempfile.TemporaryDirectory(prefix='engineering-execute-') as directory:
        path=Path(directory)/'request.json';path.write_text(json.dumps(request));path.chmod(0o600)
        env=child_environment(request['environment']);env['ENGINEERING_LEASE_THREADS']=str(request['threads']);env['PYTHONPATH']=str(ROOT)+os.pathsep+env.get('PYTHONPATH','')
        try:
            code,resources=run_process([sys.executable,'-m','execution.runner',str(path)],
                cwd=request['cwd'],env=env,timeout=request['timeout'],memory_mb=request['memory_mb'])
            return dict(exit_code=code,status='completed' if code==0 else 'failed',resources=resources,
                execution_strategy='isolated-fallback')
        except subprocess.TimeoutExpired:return dict(exit_code=124,status='timeout',execution_strategy='isolated-fallback')
        except MemoryError:return dict(exit_code=1,status='memory_limit',execution_strategy='isolated-fallback')
