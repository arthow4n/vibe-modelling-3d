"""Content identities; timestamps are never evidence keys."""
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def environment_identity(env=None):
    # Values influence compatibility but are never retained in diagnostics.
    reserved={'ENGINEERING_RUN_ID','ENGINEERING_TRACEPARENT','ENGINEERING_OWNER_PID','ENGINEERING_OWNER_ID',
        'ENGINEERING_LEASE_THREADS','ENGINEERING_AFFINITY','ENGINEERING_THREADS','ENGINEERING_INSTANCE',
        'ENGINEERING_DATA','ENGINEERING_TRACE','ENGINEERING_CPUS','ENGINEERING_JOBS',
        'ENGINEERING_REUSE_MESH','ENGINEERING_EXEC_OWNER_PID','ENGINEERING_EXEC_OWNER_ID','ENGINEERING_REPOSITORY'}
    return fingerprint({k: v for k, v in (env or os.environ).items()
        if k not in reserved and not k.startswith('OTEL_') and k not in ('_', 'SHLVL')})


def runtime_identity():
    files = [ROOT/'pyproject.toml', ROOT/'uv.lock', ROOT/'.venv/pyvenv.cfg']
    files += sorted((ROOT/'execution').glob('*.py'))
    # Installed metadata detects environment edits outside uv as well as lock changes.
    import sysconfig
    files += sorted(Path(sysconfig.get_path('purelib')).glob('*.dist-info/METADATA'))
    return fingerprint(dict(python=sys.version, executable=str(Path(sys.executable).resolve()),prefix=str(Path(sys.prefix).resolve()),
        coordinator={k:os.environ.get(k) for k in ('ENGINEERING_CPUS','ENGINEERING_JOBS','ENGINEERING_DATA')},
        files={str(p): digest(p) for p in files if p.is_file()}))


def execution_inputs_identity(request):
    """Comparison identity for actual options and budgets, not an output cache.

    Exclude per-dispatch IDs; hash paths/arguments/environment without retaining
    their values. CAD view/export/fresh options are consequential inputs too.
    """
    cad=request.get('cad')
    return fingerprint(dict(kind=request.get('kind'), source=request.get('source_sha256'),
        runtime=request.get('runtime'), strategy=request.get('strategy'),
        threads=request.get('threads'),
        timeout=request.get('timeout'), preload=request.get('preload'),profile=request.get('profile'),
        cwd=request.get('cwd'), arguments=request.get('arguments'),
        environment=environment_identity(request.get('environment')),
        cad={k:v for k,v in cad.items() if k!='run_id'} if isinstance(cad,dict) else None))


def repository_revision():
    """Read Git identity without launching a process on each engineering command."""
    folder=ROOT/'.git'
    if folder.is_file():folder=(ROOT/folder.read_text().removeprefix('gitdir:').strip()).resolve()
    head=(folder/'HEAD').read_text().strip()
    if not head.startswith('ref: '):return head
    reference=head[5:]
    if (folder/'commondir').exists():folder=(folder/(folder/'commondir').read_text().strip()).resolve()
    if (folder/reference).exists():return (folder/reference).read_text().strip()
    for line in (folder/'packed-refs').read_text().splitlines():
        if line.endswith(' '+reference):return line.split()[0]
    return None


def python_sources(folder):
    excluded={'.git','.venv','.execution','__pycache__','.pytest_cache','node_modules','venv','env'}
    for directory,children,files in os.walk(folder):
        children[:]=[name for name in children if name not in excluded]
        for name in files:
            if name.endswith('.py'):yield Path(directory)/name


def cad_identity(source, dependencies=(), environment=None):
    """Closed-input declaration: repo/sibling Python plus explicitly declared data."""
    source = Path(source).resolve()
    files = set()
    # Avoid virtual environments, caches and generated evidence trees.
    files.update(python_sources(ROOT))
    files.update(python_sources(source.parent))
    files.add(source)
    for dependency in dependencies:
        path = Path(dependency).resolve(strict=True)
        files.update(p for p in path.rglob('*') if p.is_file()) if path.is_dir() else files.add(path)
    return fingerprint(dict(runtime=runtime_identity(), environment=environment_identity(environment),
        files={str(p): digest(p) for p in sorted(files) if '__pycache__' not in p.parts}))
