"""Isolated Gmsh/CalculiX static solid backend; no solver state in the CAD process."""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
from ..results import AnalysisResult
from execution.telemetry import operation, child_environment
from execution.resources import lease as resource_lease
from execution.lifecycle import wait as wait_owned, terminate, process_identity


def runtime_environment():
    env = os.environ.copy()
    # Optional unprivileged Ubuntu installation, documented in physical_analysis/README.md.
    prefix = Path(env.get('PHYSICAL_ANALYSIS_RUNTIME', '~/.local/opt/physical-analysis')).expanduser()
    lib = prefix/'usr/lib/x86_64-linux-gnu'
    if lib.is_dir():
        env['LD_LIBRARY_PATH'] = ':'.join(map(str, (lib, lib/'blas', lib/'lapack'))) + (
            ':'+env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
    env['OMP_NUM_THREADS'] = '1'
    env['OPENBLAS_NUM_THREADS'] = '1'
    executable = env.get('CALCULIX_COMMAND') or shutil.which('ccx')
    if not executable and (prefix/'usr/bin/ccx').is_file():
        executable = str(prefix/'usr/bin/ccx')
    env['CALCULIX_COMMAND'] = executable or 'ccx'
    root = str(Path(__file__).resolve().parents[2])
    env['PYTHONPATH'] = root + (os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    return env


def evidence_files(directory):
    """Compact replay files for this backend; absent files are allowed on failure.

    Values are (relative path, compress) pairs, or lists of those pairs. Keeping
    this policy here avoids solver filenames and replay commands in model code.
    Raw fields remain in the source run for extraction/recovery.
    """
    files = dict(case=('case.json', False), input=('analysis.inp', True),
                 run_metadata=('run_metadata.json',False),
                 rigid_driver_clearance=('rigid_driver_clearance.json',False),
                 solver_log=('solver.log', True), worker_log=('worker.log', True),
                 recovery_log=('recovery.log',True),
                 increments=('analysis.sta', False), regions=('regions.json', True),
                 mesh_source_input=('mesh_source.inp',True), mesh_source_case=('mesh_source_case.json',False),
                 fixture_geometry=[(p.name, True) for p in sorted(directory.glob('part_*.brep'))])
    replay = ('Decompress analysis.inp.gz in a new directory and run ccx -i analysis '
              'in the configured native environment to regenerate raw solver fields. '
              'Use the model analysis source to rebuild the current case; retained fixtures may be historical.')
    return files, replay


@operation("analysis.worker")
def run_worker(directory, module, environment, timeout_seconds, result, *,
               arguments=(), log_name='worker.log', failure_record='result.json'):
    """One process-group lifecycle for solves and saved-field recovery."""
    with resource_lease(int(environment.get('OMP_NUM_THREADS',1))), (directory/log_name).open('w') as log:
        import psutil
        environment=child_environment(environment)
        environment['ENGINEERING_OWNER_PID']=str(os.getpid())
        environment['ENGINEERING_OWNER_ID']=process_identity()
        process=subprocess.Popen([sys.executable,'-m','execution.runner','--module',module,str(directory),*arguments],
            cwd=directory,env=child_environment(environment),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            if not hasattr(process,'poll'):return process.wait(timeout=timeout_seconds)
            code,measurements=wait_owned(process,timeout_seconds)
            result.provenance['execution_resources']=measurements
            return code
        except subprocess.TimeoutExpired:
            terminate(process)
            result.status='timeout'
            result.errors.append(f'Analysis exceeded {timeout_seconds:g} seconds; worker and solver stopped')
            return None
        except KeyboardInterrupt:
            terminate(process);result.status='interrupted'
            result.errors.append('Caller interrupted analysis; worker and solver stopped')
            metadata=directory/'run_metadata.json'
            if metadata.is_file():result.provenance.update(json.loads(metadata.read_text()))
            result.artifacts['worker_log']=log_name
            result.write(directory/failure_record)
            raise


class CalculixBackend:
    backend_name = 'CalculiX'
    worker_module = 'physical_analysis.backends.worker'
    meshing_assumption = 'Quadratic tetrahedra; backend identifies strain measure and extraction; no stress singularity removal.'

    def environment(self):
        return runtime_environment()

    def configure_request(self, request):
        pass

    def reuse_mesh(self, request, directory, source):
        """Backend-owned input identity; stable route keeps its existing deck guard."""
        previous=json.loads((source/'case.json').read_text())
        provenance=json.loads((source/'result.json').read_text())['provenance']
        identity={key:hashlib.sha256((source/name).read_bytes()).hexdigest()
            for key,name in (('input_sha256','analysis.inp'),('case_sha256','case.json'))}
        if any(provenance.get(key)!=value for key,value in identity.items()):
            raise ValueError('Mesh source identity differs from its result provenance')
        signature=lambda parts:[(p['name'],p['sha256'],p['mesh_size_mm']) for p in parts]
        if signature(previous['parts'])!=signature(request['parts']):
            raise ValueError('Mesh source geometry or mesh settings differ from the new case')
        shutil.copyfile(source/'analysis.inp',directory/'mesh_source.inp')
        shutil.copyfile(source/'case.json',directory/'mesh_source_case.json')
        if hashlib.sha256((directory/'mesh_source.inp').read_bytes()).hexdigest()!=identity['input_sha256'] or hashlib.sha256((directory/'mesh_source_case.json').read_bytes()).hexdigest()!=identity['case_sha256']:
            raise ValueError('Mesh source changed during snapshot')
        request['mesh_reuse']=dict(**identity,input='mesh_source.inp',case='mesh_source_case.json',
                                  mesh=provenance.get('mesh',{}))

    def mesh_identity(self,request):
        from execution.identity import runtime_identity,digest
        # Reuse the existing backend snapshot/guard rather than storing another mesh format.
        return dict(backend=self.backend_name,runtime=runtime_identity(),
            implementation={p.name:digest(p) for p in Path(__file__).parent.glob('*.py')},
            parts=[(p['name'],p['sha256'],p['mesh_size_mm']) for p in request['parts']],
            ipc=request.get('ipc'),contacts=request['contacts'] if request.get('ipc') else None)

    @operation("analysis.prepare")
    def prepare_request(self, case, directory):
        """Canonical physical intent and geometry snapshots, shared with evidence checks."""
        import cadquery as cq
        request = {key: getattr(case, key) for key in ('name', 'nonlinear', 'max_increment')}
        request.update(parts=[], constraints=[asdict(x) for x in case.constraints],
                       loads=[asdict(x) for x in case.loads], contacts=[asdict(x) for x in case.contacts],
                       observations=[dict(name=k, selection=asdict(v)) for k, v in case.observations.items()])
        for group in ('constraints', 'loads', 'contacts', 'observations'):
            for item in request[group]:
                for key in ('selection', 'slave', 'master'):
                    if key in item:
                        values = item[key] if isinstance(item[key], (list, tuple)) else (item[key],)
                        for selection in values:
                            reg = selection['region']
                            for side in ('lower', 'upper'):
                                reg[side] = [v if abs(v) != float('inf') else None for v in reg[side]]
        for i, part in enumerate(case.parts.values()):
            shape = part.shape.val() if isinstance(part.shape, cq.Workplane) else part.shape
            if not isinstance(shape, cq.Shape) or not shape.isValid() or len(shape.Solids()) != 1:
                raise ValueError(f'{part.name}: provide one valid connected solid per part')
            path = directory/f'part_{i}.brep'
            shape.exportBrep(str(path))
            request['parts'].append(dict(name=part.name, geometry=path.name,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                material=asdict(part.material), mesh_size_mm=part.mesh_size_mm))
        self.configure_request(request)
        return request

    def run(self, case, directory, *, mesh_from=None):
        if not case.parts or not case.constraints:
            raise ValueError('An analysis needs parts and explicit constraints')
        directory = directory.resolve()
        directory.mkdir(parents=True, exist_ok=False)
        result = AnalysisResult(case.name, 'preparing', assumptions=[
            'mm, N, MPa; static loads ramp over time 0..1; motions may use recorded piecewise-linear progress.',
            'Homogeneous isotropic elastic solids; no infill, creep, plasticity, fatigue or layer failure model.',
            self.meshing_assumption,
            'Frictionless contact; enforcement and pairing depend on backend/formulation.',
            'Numerical completion is not physical validation or a load rating.'])
        result.artifacts = {'directory': str(directory), 'result': 'result.json'}
        result.provenance = dict(backend=self.backend_name)
        try:
            request = self.prepare_request(case, directory)
            from execution.artifacts import ArtifactCache
            from execution.telemetry import span
            mesh_cache=ArtifactCache('meshes');mesh_key=self.mesh_identity(request)
            if mesh_from is not None:
                self.reuse_mesh(request,directory,Path(mesh_from).resolve())
            elif os.environ.get('ENGINEERING_REUSE_MESH')!='0':
                with span('analysis.mesh_lookup'):
                    saved=mesh_cache.read(mesh_key)
                    if saved:
                        try:
                            self.reuse_mesh(request,directory,Path(saved.decode()))
                            request['mesh_reuse']['automatic']=True
                        except (OSError,ValueError,KeyError):
                            request.pop('mesh_reuse',None)  # Unknown/stale sources compute freshly.
                            for leftover in directory.glob('mesh_source*'):leftover.unlink(missing_ok=True)
            (directory/'case.json').write_text(json.dumps(request, indent=2, allow_nan=False)+'\n')
            result.artifacts['case'] = 'case.json'
            from ..motion import rigid_driver_clearance
            clearance=rigid_driver_clearance(case)
            if clearance['pairs']:
                (directory/'rigid_driver_clearance.json').write_text(json.dumps(clearance,indent=2)+'\n')
                result.artifacts['rigid_driver_clearance']='rigid_driver_clearance.json'
            if not clearance['ok']:
                result.status='invalid_rigid_motion'
                result.errors.append('Prescribed rigid drivers overlap at sampled poses; revise their physical path before solving')
                result.write(directory/'result.json')
                return result
            code=run_worker(directory,self.worker_module,self.environment(),case.timeout_seconds,result)
            answer = directory/'answer.json'
            if code!=0 and (directory/'run_metadata.json').is_file():
                result.provenance.update(json.loads((directory/'run_metadata.json').read_text()))
            if code == 0 and answer.exists():
                payload = json.loads(answer.read_text())
                payload.setdefault('provenance',{}).update(result.provenance)
                result = AnalysisResult(**payload)
            elif code is not None:
                result.status = 'failed'
                detail=(directory/'worker.log').read_text()[-4000:]
                result.errors.append(f'Analysis worker exited with code {code}'+(f': {detail}' if detail else '; worker log is empty'))
            result.artifacts.update(directory=str(directory), result='result.json', worker_log='worker.log')
            if clearance['pairs']:
                result.artifacts['rigid_driver_clearance']='rigid_driver_clearance.json'
        except Exception as exc:
            result.status = 'failed'
            result.errors.append(f'{type(exc).__name__}: {exc}')
        result.write(directory/'result.json')
        if result.completed and self.mesh_identity(request)==mesh_key:
            mesh_cache.store(mesh_key,str(directory).encode())
        return result
