"""One process lifecycle for coordinator jobs, native solvers and fallback."""
import os
import signal
import subprocess
import time
import contextvars
from .telemetry import child_environment, span

_cancellation=contextvars.ContextVar('engineering_cancellation',default=lambda:False)
_watching_pid=None


def arm_parent_death():
    """Linux delivers SIGKILL even when native code holds the Python GIL."""
    import sys
    if sys.platform.startswith('linux'):
        import ctypes
        parent=os.getppid()
        ctypes.CDLL(None).prctl(1,signal.SIGKILL,0,0,0)  # PR_SET_PDEATHSIG
        if os.getppid()!=parent:os.kill(os.getpid(),signal.SIGKILL)


def enable_reaper():
    """Adopt detached grandchildren on Linux so rapid exits cannot abandon them."""
    import sys
    if sys.platform.startswith('linux'):
        import ctypes
        ctypes.CDLL(None).prctl(36,1,0,0,0)  # PR_SET_CHILD_SUBREAPER


def cleanup_orphans(run_id):
    if not run_id:return
    import psutil
    try:children=psutil.Process().children()
    except psutil.Error:return
    for child in children:
        try:
            if child.environ().get('ENGINEERING_RUN_ID')==run_id:
                child.kill();child.wait(timeout=2)
        except psutil.Error:pass


def cleanup_abandoned():
    """A replacement service reaps tagged work whose supervisor birth identity died.

    Covers arbitrary subprocesses inherited from scripts, including detached
    children surviving a supervisor SIGKILL. Never select by executable/name.
    """
    import psutil
    from .identity import ROOT,fingerprint
    repository=fingerprint(str(ROOT))
    for process in psutil.process_iter():
        try:
            env=process.environ()
            if env.get('ENGINEERING_REPOSITORY')!=repository or not env.get('ENGINEERING_RUN_ID'):continue
            owner=env.get('ENGINEERING_OWNER_PID');expected=env.get('ENGINEERING_OWNER_ID')
            if not owner or not expected:continue
            try:alive=process_identity(int(owner))==expected and psutil.Process(int(owner)).status()!=psutil.STATUS_ZOMBIE
            except (ProcessLookupError,psutil.Error):alive=False
            if not alive:process.kill()
        except (psutil.Error,ValueError):pass


def process_identity(pid=None):
    """PID birth identity unaffected by wall-clock corrections on Linux/WSL."""
    from pathlib import Path
    pid=pid or os.getpid()
    import sys
    try:
        # Field 22 is monotonic boot ticks; comm may contain spaces and parentheses.
        return 'ticks:'+Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
    except FileNotFoundError:
        if sys.platform.startswith('linux'):raise ProcessLookupError(pid)
        import psutil
        return 'time:'+str(psutil.Process(pid).create_time())
    except OSError:
        import psutil
        return 'time:'+str(psutil.Process(pid).create_time())


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


def wait(process, timeout=None, cancelled=lambda: False, memory_mb=None, sample=None,run_id=None):
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
            try:os.killpg(process.pid,signal.SIGKILL)
            except (ProcessLookupError,PermissionError):pass
            cleanup_orphans(run_id)
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
        cancelled=None, memory_mb=None):
    with span('subprocess', executable=os.path.basename(str(command[0]))):
        enable_reaper()
        import shutil
        environment=child_environment(env)
        affinity=environment.get('ENGINEERING_AFFINITY')
        if affinity and shutil.which('taskset'):
            command=['taskset','--cpu-list',affinity,*command]
        import sys
        from .identity import ROOT
        environment['PYTHONPATH']=str(ROOT)+os.pathsep+environment.get('PYTHONPATH','')
        environment['ENGINEERING_EXEC_OWNER_PID']=str(os.getpid())
        environment['ENGINEERING_EXEC_OWNER_ID']=process_identity()
        command=[sys.executable,'-m','execution.native',*map(str,command)]
        process=subprocess.Popen(command,cwd=cwd,env=environment,stdin=stdin,
            stdout=stdout,stderr=stderr,start_new_session=(os.name=='posix'))
        try:
            code, measurements=wait(process,timeout,cancelled or _cancellation.get(),memory_mb,run_id=environment.get('ENGINEERING_RUN_ID'))
        except BaseException:
            terminate(process)
            raise
        finally:cleanup_orphans(environment.get('ENGINEERING_RUN_ID'))
        return code,measurements


def watch_owner(environment=None):
    """Stop orphan work after abrupt supervisor death, even during native calls."""
    import threading
    import psutil
    env=environment or os.environ
    owner=env.get('ENGINEERING_OWNER_PID')
    if not owner:return
    global _watching_pid
    if _watching_pid==os.getpid():return
    arm_parent_death()
    _watching_pid=os.getpid()
    expected=env.get('ENGINEERING_OWNER_ID')
    children={}
    def watchdog():
        while True:
            try:
                parent=psutil.Process(int(owner))
                alive=parent.is_running() and parent.status()!=psutil.STATUS_ZOMBIE
                if expected:alive &= process_identity(int(owner))==expected
            except (psutil.Error,ProcessLookupError):alive=False
            try:
                own=psutil.Process()
                children.update({p.pid:p for p in own.children(recursive=True)})
            except psutil.Error:pass
            if not alive:
                for p in children.values():
                    try:p.kill()
                    except psutil.Error:pass
                try:os.killpg(os.getpgrp(),signal.SIGKILL)
                finally:os._exit(130)
            time.sleep(.1)
    threading.Thread(target=watchdog,name='engineering-owner-watchdog',daemon=True).start()
