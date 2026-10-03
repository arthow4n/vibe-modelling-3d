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
    return fingerprint({k: v for k, v in (env or os.environ).items()
        if not k.startswith(('ENGINEERING_', 'OTEL_')) and k not in ('_', 'SHLVL')})


def runtime_identity():
    files = [ROOT/'pyproject.toml', ROOT/'uv.lock', ROOT/'.venv/pyvenv.cfg']
    files += sorted((ROOT/'execution').glob('*.py'))
    # Installed metadata detects environment edits outside uv as well as lock changes.
    import sysconfig
    files += sorted(Path(sysconfig.get_path('purelib')).glob('*.dist-info/METADATA'))
    return fingerprint(dict(python=sys.version, executable=str(Path(sys.executable).resolve()),prefix=str(Path(sys.prefix).resolve()),
        files={str(p): digest(p) for p in files if p.is_file()}))


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
