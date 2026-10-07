"""Validate the locked environment once per content change, then use its Python."""
import fcntl
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys


def _uv_binary():
    candidate = shutil.which('uv')
    if candidate:
        return candidate
    for extra in (Path.home()/'.local/bin/uv', Path.home()/'.cargo/bin/uv'):
        if extra.is_file() and os.access(extra, os.X_OK):
            return str(extra)
    return 'uv'


def ensure():
    root=Path(__file__).resolve().parents[1]
    python=root/'.venv/bin/python'
    identity=hashlib.sha256((root/'uv.lock').read_bytes()+(root/'pyproject.toml').read_bytes()).hexdigest()
    state=root/'.execution';state.mkdir(exist_ok=True,mode=0o700)
    with (state/'environment.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        marker=state/'environment.identity'
        if not python.exists() or not marker.exists() or marker.read_text()!=identity:
            with (state/'environment-sync.log').open('w') as log:
                result=subprocess.run([_uv_binary(),'sync','--locked'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError('uv sync failed; inspect .execution/environment-sync.log')
            marker.write_text(identity)
    if Path(sys.prefix).resolve()!= (root/'.venv').resolve():
        os.execv(str(python),[str(python),*sys.argv])
