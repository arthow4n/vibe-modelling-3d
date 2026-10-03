"""Content-bound controlled artifacts and cross-process destination ownership."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import os
import tempfile
from .telemetry import data_root
from .identity import fingerprint, digest


@contextmanager
def destinations(paths, cancelled=lambda:False, deadline=None):
    locks=[]
    try:
        folder=data_root()/'locks';folder.mkdir(parents=True,exist_ok=True)
        for name in sorted({str(Path(p).resolve()) for p in paths}):
            lock=(folder/f'{fingerprint(name)}.lock').open('a')
            import time
            while True:
                try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);break
                except BlockingIOError:
                    if cancelled():lock.close();raise InterruptedError('Cancelled waiting for output ownership')
                    if deadline and time.monotonic()>deadline:lock.close();raise TimeoutError('Deadline expired waiting for output ownership')
                    time.sleep(.02)
            locks.append(lock)
        yield
    finally:
        for lock in reversed(locks):lock.close()


class ArtifactCache:
    """Cache only explicitly identified controlled artifacts; never script output."""
    def __init__(self, namespace):
        self.folder=data_root()/'cache'/namespace

    def read(self,key):
        try:
            folder=self.folder/fingerprint(key)
            record=json.loads((folder/'identity.json').read_text())
            path=folder/'artifact'
            if record['key']!=key or digest(path)!=record['sha256']:return None
            return path.read_bytes()
        except (OSError,ValueError,KeyError):return None

    def store(self,key,data):
        folder=self.folder/fingerprint(key);folder.mkdir(parents=True,exist_ok=True)
        for name,contents in [('artifact',data),('identity.json',json.dumps(dict(key=key,sha256=hashlib.sha256(data).hexdigest())).encode())]:
            with tempfile.NamedTemporaryFile(dir=folder,delete=False) as f:
                path=Path(f.name);f.write(contents)
            try:path.replace(folder/name)
            finally:path.unlink(missing_ok=True)
        self.prune()

    def prune(self,max_bytes=256*1024**2,max_entries=200):
        import shutil
        entries=[]
        for folder in self.folder.iterdir():
            if folder.is_dir():
                try:entries.append((folder.stat().st_mtime,sum(p.stat().st_size for p in folder.iterdir()),folder))
                except OSError:pass
        total=0
        for i,(_,size,folder) in enumerate(sorted(entries,reverse=True)):
            total+=size
            if i>=max_entries or total>max_bytes:shutil.rmtree(folder,ignore_errors=True)
