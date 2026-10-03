"""Admission policy: affinity/cgroup CPU, bounded jobs, declared memory/thread use."""
from contextlib import contextmanager
import os
from pathlib import Path
import threading
import time


def cpu_capacity():
    count=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count() or 1
    try:
        quota,period=Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if quota!='max':count=min(count,max(1,int(quota)//int(period)))
    except (OSError,ValueError):pass
    return max(1,int(os.environ.get('ENGINEERING_CPUS',count)))


class Admission:
    def __init__(self, cpus=None, memory_mb=None, jobs=None):
        import psutil
        self.cpus=cpus or cpu_capacity()
        self.memory_mb=memory_mb or int(os.environ.get('ENGINEERING_MEMORY_MB',psutil.virtual_memory().available*.6/1024**2))
        self.jobs=jobs or int(os.environ.get('ENGINEERING_JOBS',min(4,self.cpus)))
        self.used_cpus=self.used_memory=self.active=0
        self.condition=threading.Condition()

    @contextmanager
    def acquire(self, cpus, memory_mb, cancelled=lambda:False, deadline=None):
        if cpus<1 or cpus>self.cpus or memory_mb<1 or memory_mb>self.memory_mb:
            raise ValueError('Requested resources exceed coordinator capacity')
        started=time.monotonic()
        with self.condition:
            while (self.used_cpus+cpus>self.cpus or self.used_memory+memory_mb>self.memory_mb or self.active>=self.jobs):
                if cancelled():raise InterruptedError('Cancelled while waiting for resources')
                if deadline and time.monotonic()>deadline:raise TimeoutError('Deadline expired waiting for resources')
                self.condition.wait(.05)
            self.used_cpus+=cpus;self.used_memory+=memory_mb;self.active+=1
        try:yield time.monotonic()-started
        finally:
            with self.condition:
                self.used_cpus-=cpus;self.used_memory-=memory_mb;self.active-=1
                self.condition.notify_all()


def thread_environment(env, threads):
    values=dict(env)
    for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
        values[key]=str(threads)
    values['ENGINEERING_THREADS']=str(threads)
    return values
