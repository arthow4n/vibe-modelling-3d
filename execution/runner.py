"""Ordinary script semantics in an isolated or freshly forkserver-created child."""
import cProfile
import json
import os
from pathlib import Path
import runpy
import sys
import time
import traceback
from .telemetry import span, data_root


def execute(request):
    os.environ.clear();os.environ.update(request['environment'])
    from .resources import apply_affinity
    apply_affinity()
    from .lifecycle import watch_owner
    watch_owner()
    os.chdir(request['cwd'])
    source=Path(request['source'])
    sys.argv=[str(source),*request.get('arguments',[])]
    sys.path[:]=[str(source.parent),*request.get('pythonpath',[]),*sys.path]
    # Content edits within filesystem timestamp resolution must never load old pyc.
    sys.dont_write_bytecode=True
    sys.pycache_prefix=str(data_root()/'bytecode-disabled'/request['run_id'])
    profiler=cProfile.Profile() if request.get('profile')=='cpu' else None
    if request.get('profile')=='allocations':
        import tracemalloc;tracemalloc.start()
    try:
        with span('script.execute', source_sha256=request['source_sha256']):
            if profiler:profiler.enable()
            # Audit hook observes subprocess starts only; it does not invent completion timings.
            def audit(event, values):
                if event=='subprocess.Popen':
                    try:
                        from opentelemetry import trace
                        trace.get_current_span().add_event('subprocess.start',{'executable':os.path.basename(str(values[0]))})
                    except Exception:pass
            sys.addaudithook(audit)
            runpy.run_path(str(source),run_name='__main__')
        return 0
    except SystemExit as exc:
        if exc.code is None:return 0
        if isinstance(exc.code,int):return exc.code
        print(exc.code,file=sys.stderr);return 1
    except KeyboardInterrupt:
        return 130
    except BaseException:
        traceback.print_exc();return 1
    finally:
        if profiler:
            profiler.disable()
            try:
                folder=data_root()/'profiles';folder.mkdir(parents=True,exist_ok=True)
                profiler.dump_stats(str(folder/f'{request["run_id"]}.pstats'))
            except OSError:pass
        if request.get('profile')=='allocations':
            try:
                folder=data_root()/'profiles';folder.mkdir(parents=True,exist_ok=True)
                tracemalloc.take_snapshot().dump(str(folder/f'{request["run_id"]}.allocations'))
            except OSError:pass
            finally:tracemalloc.stop()


def child(request, descriptors):
    os.setsid()
    for target,descriptor in enumerate(descriptors):
        fd=descriptor.detach();os.dup2(fd,target)
        if fd>2:os.close(fd)
    # multiprocessing closes stdin separately; restore the actual forwarded stream.
    sys.stdin=os.fdopen(os.dup(0),'r')
    if request.get('strategy')=='preinitialized':
        from OCP.OSD import OSD_ThreadPool
        OSD_ThreadPool.DefaultPool_s(request['threads']).Init(request['threads'])
    # Native pools must fit the admitted CPU budget, even when inherited from preload.
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=request['threads']):
        code=execute(request)
    sys.stdout.flush();sys.stderr.flush()
    raise SystemExit(code)


def main():
    request=json.loads(Path(sys.argv[1]).read_text())
    raise SystemExit(execute(request))
if __name__=='__main__':main()
