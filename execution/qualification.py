"""Qualify native import cloning before dispatching any user code."""
import os
import time
from .lifecycle import terminate
from .telemetry import span,child_environment


def probe(connection,environment):
    os.setsid()
    os.environ.update(environment)
    from .resources import apply_affinity
    apply_affinity()
    from .lifecycle import watch_owner
    watch_owner()
    try:
        import cadquery as cq
        a=cq.Workplane('XY').box(4,4,4).val()
        b=cq.Workplane('XY').box(2,2,2).translate((1,0,0)).val()
        common=a.intersect(b)
        connection.send(common.isValid() and abs(common.Volume()-8)<1e-8 and a.distance(b)==0.)
    finally:connection.close()


def qualify(ctx,deadline=None,cancelled=lambda:False):
    with span('worker.preload_qualification'):
        for _ in range(2):
            incoming,outgoing=ctx.Pipe()
            process=ctx.Process(target=probe,args=(outgoing,child_environment()))
            try:
                process.start();outgoing.close()
                stop=min(deadline or float('inf'),time.monotonic()+20)
                while not incoming.poll(.02):
                    if cancelled():raise InterruptedError('Cancelled during preload qualification')
                    if time.monotonic()>stop:raise TimeoutError('Preload qualification exceeded deadline')
                    if not process.is_alive():return False
                if not incoming.recv():return False
                process.join(2)
                if process.exitcode!=0:return False
            except (EOFError,OSError,RuntimeError):return False
            finally:
                incoming.close();outgoing.close()
                if process.pid:terminate(process)
        return True
