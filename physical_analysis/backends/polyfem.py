"""Optional IPC experiment. Deliberately absent from engineering questions.

Uses an external native CLI, explicit units, and the existing isolated lifecycle.
No solver termination is promoted to passage without independent geometry checks.
"""
from dataclasses import dataclass, asdict
import hashlib
import json
import os
import shutil
from .structural import CalculixBackend, runtime_environment
from ..case import positive


@dataclass(frozen=True)
class IPCSettings:
    activation_distance_mm: float = .001
    obstacle_mesh_size_mm: float | None = None
    gradient_tolerance_N: float = 1e-6
    max_iterations: int = 200
    initial_offset_mm: tuple = (0., 0., 0.)
    unit_system: str = 'mm_N_MPa'
    ccd_tolerance_mm: float = 1e-6
    constraint_initial_weight: float = 1e12
    convergent_barrier: bool = False
    projected_newton: bool = False
    bounded_feasibility_search: bool = False

    def __post_init__(self):
        for value in (self.activation_distance_mm, self.gradient_tolerance_N,self.ccd_tolerance_mm,
                      self.constraint_initial_weight):
            positive(value, 'IPC numerical setting')
        if self.obstacle_mesh_size_mm is not None:
            positive(self.obstacle_mesh_size_mm, 'Obstacle mesh size')
        if type(self.max_iterations) is not int or self.max_iterations < 1:
            raise ValueError('IPC iteration limit must be a positive integer')
        from ..case import vector
        vector(self.initial_offset_mm)
        if self.unit_system not in ('SI', 'mm_N_MPa'):
            raise ValueError('IPC unit system must be SI or mm_N_MPa')
        if not all(isinstance(v,bool) for v in (self.convergent_barrier,self.projected_newton,self.bounded_feasibility_search)):
            raise ValueError('IPC barrier and Newton options must be boolean')


class PolyfemBackend(CalculixBackend):
    backend_name = 'PolyFEM-IPC-experimental'
    worker_module = 'physical_analysis.backends.polyfem_worker'
    meshing_assumption = 'Experimental P1 tetrahedra and straight collision triangles; Green strain; no stress singularity removal.'

    def __init__(self, settings=None):
        self.settings = settings or IPCSettings()

    def reuse_mesh(self, request, directory, source):
        if not all((source/file).is_file() for file in ('case.json','result.json','mesh.json','scene.json')):
            raise ValueError('IPC mesh source is incomplete')
        previous=json.loads((source/'case.json').read_text())
        provenance=json.loads((source/'result.json').read_text())['provenance']
        if provenance.get('backend')!=self.backend_name:
            raise ValueError('IPC mesh reuse requires an IPC source scene')
        identity={key:hashlib.sha256((source/name).read_bytes()).hexdigest()
            for key,name in (('input_sha256','scene.json'),('mesh_sha256','mesh.json'),('case_sha256','case.json'))}
        if any(provenance.get(key)!=value for key,value in identity.items()):
            raise ValueError('IPC mesh source identity differs from result provenance')
        signature=lambda c: json.dumps(([ (p['name'],p['sha256'],p['mesh_size_mm']) for p in c['parts']],
            [(p['slave'],p['master']) for p in c['contacts']],
            c['ipc']['initial_offset_mm'],c['ipc']['obstacle_mesh_size_mm']),sort_keys=True)
        if signature(previous)!=signature(request):
            raise ValueError('IPC mesh source geometry, surface selection or mesh settings differ')
        shutil.copyfile(source/'mesh.json',directory/'mesh_source.json')
        shutil.copyfile(source/'case.json',directory/'mesh_source_case.json')
        request['mesh_reuse']=dict(**identity,input='mesh_source.json',case='mesh_source_case.json')

    def configure_request(self, request):
        if request['loads'] or not request['nonlinear'] or not request['contacts']:
            raise ValueError('IPC experiment requires nonlinear prescribed-motion contact; force loading unsupported')
        if any(c['discretization'] == 'mortar' for c in request['contacts']):
            raise ValueError('IPC is not a Mortar discretization')
        slaves = {c['slave']['part'] for c in request['contacts']}
        if len(slaves) != 1:
            raise ValueError('IPC experiment requires exactly one deformable contact solid')
        deformable = next(iter(slaves))
        rigid = {p['name'] for p in request['parts']} - slaves
        for name in rigid:
            constraints = [c for c in request['constraints'] if c['selection']['part'] == name]
            if len(constraints) != 1 or any(v is None for v in constraints[0]['displacement_mm']):
                raise ValueError('IPC obstacles require one whole-part prescribed translation')
            r = constraints[0]['selection']['region']
            if any(v is not None for side in ('lower', 'upper') for v in r[side]):
                raise ValueError('IPC obstacle partial-region motion unsupported')
        masters = {s['part'] for c in request['contacts'] for s in
                   (c['master'] if isinstance(c['master'], (list, tuple)) else [c['master']])}
        if masters != rigid:
            raise ValueError('Every rigid part must be a collision obstacle')
        request['ipc'] = dict(asdict(self.settings), deformable=deformable)

    def environment(self):
        env = runtime_environment()
        env['POLYFEM_COMMAND'] = os.environ.get('POLYFEM_COMMAND', 'PolyFEM_bin')
        return env


def evidence_files(directory):
    from .structural import evidence_files as base
    files, _ = base(directory)
    files.update(input=('scene.json', True), mesh=('mesh.json', True),
                 native_statistics=('native.json', True),
                 geometry_witness=('geometry_witness.json', True),
                 initial_geometry_witness=('initial_geometry_witness.json',True),
                 investigation_stop=('investigation_stop.json',False),
                 prefix_diagnostics=('prefix_diagnostics.json',True),
                 early_witness=('early_witness.json',False),
                 mapping_witness=('mapping_witness.json',False),
                 mesh_source=('mesh_source.json',True),
                 numerical_meshes=[(p.name, True) for p in sorted(directory.glob('*.mesh'))] +
                                  [(p.name, True) for p in sorted(directory.glob('*.obj'))])
    return files, ('Decompress scene.json, *.mesh and *.obj into a new directory; '
                   'run the recorded POLYFEM_COMMAND --json scene.json --max_threads 1. '
                   'Use the recorded scene units; quasi-static, frictionless SaintVenant elasticity. '
                   'Native VTU fields are required for independent recovery/inspection.')
