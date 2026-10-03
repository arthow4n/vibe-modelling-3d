"""Owned external exec: parent-death protection survives native calls and exec."""
import os
import sys
parent=os.getppid()
if sys.platform.startswith('linux'):
    import ctypes
    import signal
    ctypes.CDLL(None).prctl(1,signal.SIGKILL,0,0,0)
    if os.getppid()!=parent:os.kill(os.getpid(),signal.SIGKILL)
    expected_parent=os.environ.get('ENGINEERING_EXEC_OWNER_PID')
    if expected_parent:
        from pathlib import Path
        try:
            identity='ticks:'+Path(f'/proc/{parent}/stat').read_text().rsplit(')',1)[1].split()[19]
        except OSError:identity=None
        if str(parent)!=expected_parent or identity!=os.environ.get('ENGINEERING_EXEC_OWNER_ID'):
            os.kill(os.getpid(),signal.SIGKILL)
os.execvpe(sys.argv[1],sys.argv[1:],os.environ)
