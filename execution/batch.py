"""Dependency-aware ordinary-script batches through the single execution interface."""
from dataclasses import dataclass,field
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import contextvars
from pathlib import Path
from .client import script
from .resources import cpu_capacity,cores,inherited_budget,_budget,_affinity,current_affinity
from .artifacts import destinations
from .telemetry import operation


@dataclass(frozen=True)
class ScriptTask:
    name:str
    source:str|Path
    arguments:tuple=()
    depends_on:tuple=()
    outputs:tuple=()
    threads:int|str='50%'
    timeout:float|None=None


@operation('execution.batch')
def run(tasks, *, max_concurrent=None):
    tasks=list(tasks);by_name={t.name:t for t in tasks}
    if len(by_name)!=len(tasks):raise ValueError('Task names must be unique')
    if any(set(t.depends_on)-by_name.keys() for t in tasks):raise ValueError('Unknown task dependency')
    parent=inherited_budget();capacity=parent or cpu_capacity()
    concurrency=max_concurrent or min(4,capacity)
    if concurrency<1:raise ValueError('Concurrency must be positive')
    results={};pending=by_name.copy();running={};used=set()
    affinity=[int(x) for x in current_affinity().split(',')] if current_affinity() else []
    def execute(task,allocated):
        token=_budget.set(len(allocated)) if parent else None
        affinity_token=_affinity.set(','.join(map(str,allocated))) if parent and affinity else None
        try:
            with destinations(task.outputs):
                return script(task.source,task.arguments,threads=len(allocated),timeout=task.timeout)
        finally:
            if token is not None:_budget.reset(token)
            if affinity_token is not None:_affinity.reset(affinity_token)
    with ThreadPoolExecutor(concurrency) as executor:
        while pending or running:
            for name,task in list(pending.items()):
                if not all(d in results for d in task.depends_on):continue
                if any(results[d]['exit_code']!=0 for d in task.depends_on):
                    results[name]=dict(exit_code=1,status='dependency_failed');del pending[name];continue
                count=cores(task.threads,capacity)
                available=[c for c in (affinity or list(range(capacity))) if c not in used]
                if len(running)>=concurrency or len(available)<count:continue
                allocated=available[:count];used.update(allocated);del pending[name]
                context=contextvars.copy_context()
                running[executor.submit(context.run,execute,task,allocated)]=(name,allocated)
            if not running:
                if pending:raise ValueError('Dependency cycle or unsatisfiable resource plan')
                break
            done,_=wait(running,return_when=FIRST_COMPLETED)
            for future in done:
                name,allocated=running.pop(future);used.difference_update(allocated)
                try:results[name]=future.result()
                except Exception as exc:results[name]=dict(exit_code=1,status='failed',error=str(exc))
    return results
