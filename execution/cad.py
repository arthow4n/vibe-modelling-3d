"""Controlled CAD process ownership; immutable shape retained only by declaration."""
import copy
import json
import os
from pathlib import Path
import sys
import time
from .identity import cad_identity
from .telemetry import span, data_root


def child(connection):
    os.setsid()
    cache={};jobs=0
    while True:
        try:request=connection.recv()
        except EOFError:break
        os.environ.clear();os.environ.update(request['environment'])
        source=Path(request['source']);os.chdir(source.parent)
        sys.path.insert(0,str(source.parent))
        sys.dont_write_bytecode=True;sys.pycache_prefix=str(data_root()/'bytecode-disabled'/request['run_id'])
        from threadpoolctl import threadpool_limits
        from OCP.OSD import OSD_ThreadPool
        OSD_ThreadPool.DefaultPool_s(request['threads']).Init(request['threads'])
        before=time.monotonic()
        with span('cad.worker'),threadpool_limits(limits=request['threads']):
            import evaluate_model
            answer=evaluate_model.evaluate_request(request['cad'],cache if request.get('reuse') else None)
        answer.setdefault('timings_seconds',{})['worker']=time.monotonic()-before
        connection.send(answer);jobs+=1
        if not request.get('reuse') or jobs>=100:break
        sys.path.pop(0)
    connection.close()


def execute(request, *, coordinator=True):
    from .client import submit, CoordinatorUnavailable
    request.update(kind='cad',strategy='persistent' if request.get('reuse') else 'preinitialized',
        cwd=str(Path(request['source']).parent))
    if coordinator:
        try:
            response=submit(request)
            if 'report' not in response:raise RuntimeError(response.get('error','CAD execution failed'))
            return response['report']
        except CoordinatorUnavailable:pass
    # Conventional process fallback retains the same artifact publication rules.
    from .coordinator import run_cad
    return run_cad(request,None,lambda:False,time.monotonic()+request['timeout'],isolated=True)['report']
