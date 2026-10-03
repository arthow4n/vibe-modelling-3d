"""Validate the locked environment once per content change, then use its Python."""
import fcntl
import hashlib
import os
from pathlib import Path
import subprocess
import sys


def ensure():
    root=Path(__file__).resolve().parents[1]
    python=root/'.venv/bin/python'
    identity=hashlib.sha256((root/'uv.lock').read_bytes()+(root/'pyproject.toml').read_bytes()).hexdigest()
    state=root/'.execution';state.mkdir(exist_ok=True,mode=0o700)
    with (state/'environment.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        marker=state/'environment.identity'
        if not python.exists() or not marker.exists() or marker.read_text()!=identity:
            subprocess.run(['uv','sync','--locked'],cwd=root,check=True,stdout=sys.stderr)
            marker.write_text(identity)
    if Path(sys.prefix).resolve()!= (root/'.venv').resolve():
        os.execv(str(python),[str(python),*sys.argv])
