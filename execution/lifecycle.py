"""One process lifecycle for coordinator jobs, native solvers and fallback."""
import os
import signal
import subprocess
import time
from .telemetry import child_environment, span


def terminate(process, descendants=()):
    """Kill known descendants, including children that made a new session."""
    try:
        import psutil
        children = psutil.Process(process.pid).children(recursive=True)
    except Exception:
        children = []
    for child in [*descendants, *children]:
        try:
            child.kill()
        except Exception:
            pass
    try:
        if os.name == 'posix':
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5) if hasattr(process, 'wait') else process.join(5)
    except Exception:
        pass


def wait(process, timeout=None, cancelled=lambda: False, memory_mb=None, sample=None):
    """Observe actual process tree use; unavailable data stays null, never zero."""
    import psutil
    started=time.monotonic();seen={};peak=None;cpu=None
    while True:
        done=process.poll() is not None if hasattr(process, 'poll') else not process.is_alive()
        if done:
            # All repository jobs own subprocesses; detached leftovers cannot outlive a job.
            for child in seen.values():
                try: child.kill()
                except psutil.Error: pass
            return process.returncode if hasattr(process, 'poll') else process.exitcode, dict(
                peak_tree_rss_bytes=peak, sampled_tree_cpu_seconds=cpu, measurement='sampled process tree',
                elapsed_seconds=time.monotonic()-started)
        try:
            root=psutil.Process(process.pid);children=root.children(recursive=True)
            seen.update({p.pid:p for p in children})
            processes=[root,*children];rss=sum(p.memory_info().rss for p in processes)
            # Includes live processes only: sampling can miss short-lived subprocesses.
            times=[p.cpu_times() for p in processes];now_cpu=sum(t.user+t.system for t in times)
            peak=max(peak or 0,rss);cpu=max(cpu or 0,now_cpu)
            if sample: sample(time.time_ns(),rss,now_cpu)
            if memory_mb and rss>memory_mb*1024**2:
                terminate(process,seen.values());raise MemoryError('Execution exceeded its process-tree memory budget')
        except psutil.Error:
            pass
        if cancelled():
            terminate(process,seen.values());raise InterruptedError('Execution client disconnected or cancelled')
        if timeout is not None and time.monotonic()-started>timeout:
            terminate(process,seen.values());raise subprocess.TimeoutExpired('engineering execution',timeout)
        time.sleep(.02)


def run(command, *, timeout=None, cwd=None, env=None, stdin=None, stdout=None, stderr=None,
        cancelled=lambda: False, memory_mb=None):
    with span('subprocess', executable=os.path.basename(str(command[0]))):
        process=subprocess.Popen(command,cwd=cwd,env=child_environment(env),stdin=stdin,
            stdout=stdout,stderr=stderr,start_new_session=(os.name=='posix'))
        try:
            code, measurements=wait(process,timeout,cancelled,memory_mb)
        except BaseException:
            terminate(process)
            raise
        return code,measurements
