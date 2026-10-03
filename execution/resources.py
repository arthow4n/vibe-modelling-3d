"""Admission policy: affinity/cgroup CPU, bounded jobs, declared memory/thread use."""
from contextlib import contextmanager
import os
from pathlib import Path
import threading
import time
import math


def cores(value, available):
    """Resolve an integer or percentage without exceeding the declared capacity."""
    text=str(value)
    result=max(1,math.floor(available*float(text[:-1])/100)) if text.endswith('%') else int(text)
    if result<1 or result>available:raise ValueError(f'CPU budget must be between 1 and {available}')
    if text.endswith('%') and not 0<float(text[:-1])<=100:raise ValueError('CPU percentage must be in (0,100]')
    return result


def cpu_capacity():
    count=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count() or 1
    try:
        quota,period=Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if quota!='max':count=min(count,max(1,int(quota)//int(period)))
    except (OSError,ValueError):pass
    return cores(os.environ.get('ENGINEERING_CPUS','50%'),count)


class Admission:
    def __init__(self, cpus=None, memory_mb=None, jobs=None):
        import psutil
        self.cpus=cpus or cpu_capacity()
        self.memory_mb=memory_mb or int(os.environ.get('ENGINEERING_MEMORY_MB',psutil.virtual_memory().available*.6/1024**2))
        if memory_mb is None:
            try:
                limit=Path('/sys/fs/cgroup/memory.max').read_text().strip()
                if limit!='max':self.memory_mb=min(self.memory_mb,max(1,int(int(limit)*.6/1024**2)))
            except (OSError,ValueError):pass
        self.jobs=jobs or int(os.environ.get('ENGINEERING_JOBS',min(4,self.cpus)))
        self.used_cpus=self.used_memory=self.active=0
        self.free_cores=sorted(os.sched_getaffinity(0))[:self.cpus] if hasattr(os,"sched_getaffinity") else list(range(self.cpus))
        self.condition=threading.Condition()
        self.resident_usage=lambda:0
        self.reclaim_resident=lambda available:None

    @contextmanager
    def acquire(self, cpus, memory_mb, cancelled=lambda:False, deadline=None, observation=None):
        if cpus<1 or cpus>self.cpus or memory_mb<1 or memory_mb>self.memory_mb:
            raise ValueError('Requested resources exceed coordinator capacity')
        started=time.monotonic()
        if observation is not None:
            observation.update(requested_cpus=cpus, requested_memory_mb=memory_mb,
                capacity_cpus=self.cpus, capacity_memory_mb=self.memory_mb, capacity_jobs=self.jobs,
                blocked_seconds={}, wait_seconds=0., status='waiting')
        previous=started; reasons=[]
        def account():
            nonlocal previous
            now=time.monotonic()
            if observation is not None:
                for reason in reasons:
                    observed=observation['blocked_seconds']
                    observed[reason]=observed.get(reason,0.)+now-previous
            previous=now
        try:
            with self.condition:
                while True:
                    account()
                    # A cancelled/expired request must not dispatch just because
                    # capacity happens to be available at this instant.
                    if cancelled():raise InterruptedError('Cancelled while waiting for resources')
                    if deadline is not None and time.monotonic()>deadline:raise TimeoutError('Deadline expired waiting for resources')
                    reasons=[]
                    if self.used_cpus+cpus>self.cpus:reasons.append('cpu')
                    if self.used_memory+memory_mb>self.memory_mb:reasons.append('memory')
                    if self.active>=self.jobs:reasons.append('jobs')
                    if not reasons:
                        available=self.memory_mb-self.used_memory-memory_mb
                        if self.resident_usage()>available:self.reclaim_resident(available)
                        if self.resident_usage()<=available:break
                        reasons.append('resident_memory')
                    if observation is not None and 'first_blocked' not in observation:
                        observation['first_blocked']=dict(used_cpus=self.used_cpus,
                            used_memory_mb=self.used_memory, active_jobs=self.active)
                    self.condition.wait(.05)
                allocated=self.free_cores[:cpus];del self.free_cores[:cpus]
                self.used_cpus+=cpus;self.used_memory+=memory_mb;self.active+=1
            if observation is not None:observation['status']='acquired'
        except BaseException:
            if observation is not None:observation['status']='not_acquired'
            raise
        finally:
            if observation is not None:observation['wait_seconds']=time.monotonic()-started
        token=_affinity.set(",".join(map(str,allocated)))
        try:yield time.monotonic()-started
        finally:
            _affinity.reset(token)
            with self.condition:
                self.free_cores.extend(allocated);self.free_cores.sort()
                self.used_cpus-=cpus;self.used_memory-=memory_mb;self.active-=1
                self.condition.notify_all()


def thread_environment(env, threads):
    values=dict(env)
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
        values[key]=str(threads)
    values['ENGINEERING_THREADS']=str(threads)
    return values

# Nested repository operations borrow the admitted parent budget. Parallel children
# divide it explicitly; they do not recursively acquire capacity and deadlock.
import contextvars
_budget=contextvars.ContextVar('engineering_budget',default=None)


def inherited_budget():
    value=_budget.get() or os.environ.get('ENGINEERING_LEASE_THREADS')
    return int(value) if value else None


@contextmanager
def lease(threads=None,memory_mb=2048):
    from .client import connect,CoordinatorUnavailable
    from . import protocol
    inherited=inherited_budget()
    threads=threads or inherited or cores('50%',cpu_capacity())
    if inherited:
        if threads>inherited:raise ValueError('Nested thread request exceeds parent lease; increase the original command budget')
        token=_budget.set(threads)
        try:yield threads
        finally:_budget.reset(token)
        return
    connection=None
    try:
        try:
            from .telemetry import span
            with span('resource.admission', requested_cpus=threads, requested_memory_mb=memory_mb) as waiting:
                connection=connect();protocol.send(connection,dict(kind='lease',threads=threads,memory_mb=memory_mb))
                import select
                from .lifecycle import _cancellation
                while not select.select([connection],[],[],.05)[0]:
                    if _cancellation.get()():raise InterruptedError('Cancelled during resource admission')
                response=protocol.receive(connection)
                if waiting and response.get('acquired'):
                    try:
                        waiting.set_attribute('queue_seconds', response['queue_seconds'])
                        observed=response.get('admission',{})
                        for key in ('capacity_cpus','capacity_memory_mb','capacity_jobs'):
                            if key in observed:waiting.set_attribute(key,observed[key])
                        for reason,seconds in observed.get('blocked_seconds',{}).items():
                            waiting.set_attribute('blocked_'+reason+'_seconds',seconds)
                    except Exception:pass  # Diagnostic metadata cannot fail a calculation.
            if response.get('affinity'):affinity_token=_affinity.set(response['affinity'])
            if not response.get('acquired'):raise ValueError(response.get('error','Resource admission failed'))
        except CoordinatorUnavailable:pass
        token=_budget.set(threads)
        try:yield threads
        finally:_budget.reset(token)
    finally:
        if connection:connection.close()
        if "affinity_token" in locals():_affinity.reset(affinity_token)

_affinity=contextvars.ContextVar('engineering_affinity',default=None)


def current_affinity():
    return _affinity.get() or os.environ.get('ENGINEERING_AFFINITY')


def apply_affinity():
    value=current_affinity()
    if value and hasattr(os,'sched_setaffinity'):
        assigned={int(x) for x in value.split(',')}
        os.sched_setaffinity(0,assigned)
        # Linux affinity belongs to threads. Rebind already initialized native pools
        # when a persistent worker receives a different disjoint CPU allocation.
        for thread in Path('/proc/self/task').iterdir():
            try:os.sched_setaffinity(int(thread.name),assigned)
            except ProcessLookupError:pass


@contextmanager
def partition(start, count):
    """Divide an already admitted lease between independent native children."""
    affinity=current_affinity()
    budget=_budget.set(count)
    token=None
    if affinity:
        selected=affinity.split(',')[start:start+count]
        if len(selected)!=count:
            _budget.reset(budget)
            raise ValueError('Partition exceeds allocated CPU set')
        token=_affinity.set(','.join(selected))
    try:yield count
    finally:
        if token is not None:_affinity.reset(token)
        _budget.reset(budget)
