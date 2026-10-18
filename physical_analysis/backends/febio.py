"""Experimental FEBio contact route, driven by the swatch release failure.

Not a replacement for the default backend. Peak Green strain is recovered from
nodal kinematics and checked against native element-mean principal strains.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
from .structural import CalculixBackend, runtime_environment


@dataclass(frozen=True)
class FgmresILUT:
    """Explicit bounded-memory native solve controls; no acceptance relaxation.

    Restart bounds the Krylov workspace independently of the iteration limit.
    ILUT fill bounds its factor allocation; neither guarantees convergence.
    """
    max_iterations: int
    restart_iterations: int
    relative_tolerance: float
    absolute_tolerance: float
    max_fill: int
    fill_tolerance: float
    restart_correction_plugin: Path | None = None

    def __post_init__(self):
        for name in ('max_iterations', 'restart_iterations', 'max_fill'):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f'{name} must be a positive integer')
        if self.restart_iterations > self.max_iterations:
            raise ValueError('restart_iterations must not exceed max_iterations')
        for name in ('relative_tolerance', 'absolute_tolerance', 'fill_tolerance'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be finite and positive')
        if self.restart_correction_plugin is not None and not isinstance(self.restart_correction_plugin, Path):
            raise TypeError('restart_correction_plugin must be a pathlib.Path')


class FebioBackend(CalculixBackend):
    backend_name = 'FEBio'
    worker_module = 'physical_analysis.backends.febio_worker'

    def __init__(self, *, augmented_lagrange=True, search_radius_mm=1.0, two_pass=False, force_residual_tolerance_N=1e-6,
                 linear_solver: FgmresILUT | None = None):
        from ..case import positive
        positive(search_radius_mm, 'Contact search radius')
        positive(force_residual_tolerance_N, 'Absolute residual force tolerance')
        self.augmented_lagrange = bool(augmented_lagrange)
        self.search_radius_mm = search_radius_mm
        self.two_pass = bool(two_pass)
        self.force_residual_tolerance_N = force_residual_tolerance_N
        if linear_solver is not None and not isinstance(linear_solver, FgmresILUT):
            raise TypeError('linear_solver must be FgmresILUT or None for the native default')
        self.linear_solver = linear_solver

    def configure_request(self, request):
        if request['loads'] or not request['nonlinear']:
            raise ValueError('Experimental FEBio route supports nonlinear prescribed motions only')
        if any(c['discretization']!='surface_to_surface' for c in request['contacts']):
            raise ValueError('FEBio route requires surface_to_surface contact intent')
        request['febio'] = dict(augmented_lagrange=self.augmented_lagrange,
                               search_radius_mm=self.search_radius_mm,two_pass=self.two_pass,
                               force_residual_tolerance_N=self.force_residual_tolerance_N)
        if self.linear_solver is not None:
            controls = asdict(self.linear_solver)
            plugin = controls.pop('restart_correction_plugin')
            request['febio']['linear_solver'] = dict(type='fgmres', preconditioner='ilut',
                **controls, fail_max_iters=True,
                replace_zero_diagonal=False, print_level=2)
            if plugin is not None:
                plugin = plugin.resolve()
                manifest_path = plugin.parent/'build_manifest.json'
                manifest = json.loads(manifest_path.read_text())
                sha = hashlib.sha256(plugin.read_bytes()).hexdigest()
                if sha != manifest['plugin_sha256']:
                    raise ValueError('FEBio restart plugin differs from its build manifest')
                from ..experiments.febio_fgmres.build import COMMIT, SDK_HEADER_TREE_SHA256, RUNTIME_HASHES
                if (manifest.get('commit')!=COMMIT or
                    manifest.get('sdk_header_tree_sha256')!=SDK_HEADER_TREE_SHA256 or
                    manifest.get('runtime_hashes')!=RUNTIME_HASHES):
                    raise ValueError('FEBio restart plugin requires the reviewed SDK and runtime build')
                request['febio']['linear_solver']['plugin'] = dict(path=str(plugin),sha256=sha,
                    build_manifest=manifest,manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest())

    def environment(self):
        env=runtime_environment()
        # FEBio/PARDISO supports OpenMP. Use the already admitted budget,
        # rather than inheriting CalculiX's deliberately serial environment.
        from execution.resources import inherited_budget,thread_environment
        env=thread_environment(env,inherited_budget() or 1)
        prefix=Path(os.environ.get('FEBIO_RUNTIME','~/.local/opt/febio-exploration/FEBio4')).expanduser()
        env['FEBIO_COMMAND']=os.environ.get('FEBIO_COMMAND',str(prefix/'bin/febio4'))
        env['LD_LIBRARY_PATH']=str(prefix/'lib')+os.pathsep+env.get('LD_LIBRARY_PATH','')
        return env


def evidence_files(directory):
    from .structural import evidence_files as mesh_evidence
    files,_=mesh_evidence(directory)
    files.update(native_input=('analysis.feb',True),native_log=('analysis.log',True),
                 native_plugin_manifest=('native_plugin_manifest.json',False))
    command = ('use the exact recorded provenance command including -import. If that plugin is unavailable, '
               'rebuild it using physical_analysis/experiments/febio_fgmres and the retained native_plugin_manifest; '
               'verify the recorded runtime/build identities and record any new build identity instead of '
               'silently substituting it' if (directory/'native_plugin_manifest.json').is_file() else
               'run the recorded FEBio executable with -i analysis.feb')
    return files, ('Decompress analysis.feb.gz in a new directory and '+command+'. '
                   'analysis.inp is the shared mesh deck, not the native FEBio solve input. '
                   'Peak Green strain uses recorded tet10 G8 kinematic recovery.')
