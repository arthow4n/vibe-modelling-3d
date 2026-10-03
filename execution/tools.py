"""Verified executable/configuration identities and cached version discovery."""
import json
from pathlib import Path
import shutil
import subprocess
from .identity import digest, fingerprint, runtime_identity, environment_identity
from .process import run as run_command
from .artifacts import ArtifactCache, destinations


def tool_identity(prefix):
    executable=shutil.which(prefix[0])
    if not executable:return None  # mocked/unavailable tools cannot seed caches
    identity={'prefix':prefix,'launcher_sha256':digest(executable)}
    if Path(executable).name=='flatpak':
        apps=[p for p in prefix if p.startswith('com.orcaslicer.')]
        if not apps:return None
        run=run_command([executable,'info','--show-commit',apps[0]],capture_output=True,text=True,timeout=10)
        if run.returncode:return None
        identity['deployment_commit']=run.stdout.strip()
    # Local Orca presets may participate in inherited profiles.
    roots=[Path.home()/'.var/app/com.orcaslicer.OrcaSlicer/config',Path.home()/'.config/OrcaSlicer']
    files={str(p):digest(p) for root in roots if root.is_dir() for p in root.rglob('*.json') if p.is_file()}
    identity['configuration']=files
    identity['environment']=environment_identity()
    return fingerprint(identity)


def version(prefix,cwd,discover):
    identity=tool_identity(prefix)
    if not identity:return discover()
    cache=ArtifactCache('versions');key={'tool':identity}
    with destinations([cache.folder/fingerprint(key)]):
        saved=cache.read(key)
        if saved is not None:return saved.decode()
        value=discover();cache.store(key,value.encode());return value
