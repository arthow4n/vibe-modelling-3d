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


def run_worker(directory, module, environment, timeout_seconds, result, *,
               arguments=(), log_name='worker.log', failure_record='result.json'):
    """One process-group lifecycle for solves and saved-field recovery."""
    with (directory/log_name).open('w') as log:
        process=subprocess.Popen([sys.executable,'-m',module,str(directory),*arguments],
            cwd=directory,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            return process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL);process.wait()
            result.status='timeout'
            result.errors.append(f'Analysis exceeded {timeout_seconds:g} seconds; worker and solver stopped')
            return None
        except KeyboardInterrupt:
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            process.wait();result.status='interrupted'
            result.errors.append('Caller interrupted analysis; worker and solver stopped')
            metadata=directory/'run_metadata.json'
            if metadata.is_file():result.provenance.update(json.loads(metadata.read_text()))
            result.artifacts['worker_log']=log_name
            result.write(directory/failure_record)
            raise


class CalculixBackend:
    backend_name = 'CalculiX'
    worker_module = 'physical_analysis.backends.worker'

    def environment(self):
        return runtime_environment()

    def configure_request(self, request):
        pass

    def run(self, case, directory, *, mesh_from=None):
        import cadquery as cq
        if not case.parts or not case.constraints:
            raise ValueError('An analysis needs parts and explicit constraints')
        directory = directory.resolve()
        directory.mkdir(parents=True, exist_ok=False)
        result = AnalysisResult(case.name, 'preparing', assumptions=[
            'mm, N, MPa; static loads ramp over time 0..1; motions may use recorded piecewise-linear progress.',
            'Homogeneous isotropic elastic solids; no infill, creep, plasticity, fatigue or layer failure model.',
            'Quadratic tetrahedra; backend identifies strain measure and extraction; no stress singularity removal.',
            'Frictionless contact; enforcement and pairing depend on backend/formulation.',
            'Numerical completion is not physical validation or a load rating.'])
        result.artifacts = {'directory': str(directory), 'result': 'result.json'}
        result.provenance = dict(backend=self.backend_name)
        try:
            request = {key: getattr(case, key) for key in ('name','nonlinear','max_increment')}
            request.update(parts=[], constraints=[asdict(x) for x in case.constraints],
                           loads=[asdict(x) for x in case.loads], contacts=[asdict(x) for x in case.contacts],
                           observations=[dict(name=k,selection=asdict(v)) for k,v in case.observations.items()])
            # JSON has no infinities. Null bounds denote an unbounded side.
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
            if mesh_from is not None:
                source=Path(mesh_from).resolve()
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
                request['mesh_reuse']=dict(**identity,input='mesh_source.inp',case='mesh_source_case.json',
                                          mesh=provenance.get('mesh',{}))
            self.configure_request(request)
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
        return result
