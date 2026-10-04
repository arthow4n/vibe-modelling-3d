"""Private admission experiment; never an ordinary coordinator policy.

The admission ledger charges one MiB per active job, effectively omitting job
memory reservations. Request RSS watchdogs, CPU/job admission, idle-worker
reclamation and the enclosing benchmark's aggregate RSS watchdog remain active.
This tests concurrency, not automatic memory growth or a production safety policy.
"""
import os
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from execution import coordinator
from execution.resources import Admission


class UnreservedAdmission(Admission):
    def acquire(self,cpus,memory_mb,cancelled=lambda:False,deadline=None,observation=None):
        return super().acquire(cpus,1,cancelled,deadline,observation)


if __name__=='__main__':
    if os.environ.get('ENGINEERING_BENCHMARK_UNRESERVED')!='1':
        raise SystemExit('Use only the bounded admission benchmark')
    coordinator.Admission=UnreservedAdmission
    coordinator.Coordinator().serve()
