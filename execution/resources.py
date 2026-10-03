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
    def acquire(self, cpus, memory_mb, cancelled=lambda:False, deadline=None):
        if cpus<1 or cpus>self.cpus or memory_mb<1 or memory_mb>self.memory_mb:
            raise ValueError('Requested resources exceed coordinator capacity')
        started=time.monotonic()
        with self.condition:
            while True:
                ready=(self.used_cpus+cpus<=self.cpus and self.used_memory+memory_mb<=self.memory_mb and self.active<self.jobs)
                if ready:
                    available=self.memory_mb-self.used_memory-memory_mb
                    if self.resident_usage()>available:self.reclaim_resident(available)
                    if self.resident_usage()<=available:break
                if cancelled():raise InterruptedError('Cancelled while waiting for resources')
                if deadline and time.monotonic()>deadline:raise TimeoutError('Deadline expired waiting for resources')
                self.condition.wait(.05)
            allocated=self.free_cores[:cpus];del self.free_cores[:cpus]
            self.used_cpus+=cpus;self.used_memory+=memory_mb;self.active+=1
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
            connection=connect();protocol.send(connection,dict(kind='lease',threads=threads,memory_mb=memory_mb))
            import select
            from .lifecycle import _cancellation
            while not select.select([connection],[],[],.05)[0]:
                if _cancellation.get()():raise InterruptedError('Cancelled during resource admission')
            response=protocol.receive(connection)
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
