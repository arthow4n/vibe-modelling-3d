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


class CalculixBackend:
    def run(self, case, directory):
        import cadquery as cq
        if not case.parts or not case.constraints:
            raise ValueError('An analysis needs parts and explicit constraints')
        directory = directory.resolve()
        directory.mkdir(parents=True, exist_ok=False)
        result = AnalysisResult(case.name, 'preparing', assumptions=[
            'mm, N, MPa; static loads ramp linearly over normalized time 0..1.',
            'Homogeneous isotropic elastic solids; no infill, creep, plasticity, fatigue or layer failure model.',
            'Quadratic tetrahedra; integration-point mechanical strain; no stress singularity removal.',
            'Frictionless finite-sliding penalty contact, where explicitly requested.',
            'Numerical completion is not physical validation or a load rating.'])
        result.artifacts = {'directory': str(directory), 'result': 'result.json'}
        try:
            request = {key: getattr(case, key) for key in ('name','nonlinear','max_increment')}
            request.update(parts=[], constraints=[asdict(x) for x in case.constraints],
                           loads=[asdict(x) for x in case.loads], contacts=[asdict(x) for x in case.contacts])
            # JSON has no infinities. Null bounds denote an unbounded side.
            for group in ('constraints', 'loads', 'contacts'):
                for item in request[group]:
                    for key in ('selection', 'slave', 'master'):
                        if key in item:
                            reg = item[key]['region']
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
            (directory/'case.json').write_text(json.dumps(request, indent=2, allow_nan=False)+'\n')
            result.artifacts['case'] = 'case.json'
            with (directory/'worker.log').open('w') as log:
                process = subprocess.Popen([sys.executable, '-m', 'physical_analysis.backends.worker',
                    str(directory)], cwd=directory, env=runtime_environment(), stdout=log,
                    stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    code = process.wait(timeout=case.timeout_seconds)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    result.status = 'timeout'
                    result.errors.append(f'Analysis exceeded {case.timeout_seconds:g} seconds; worker and solver stopped')
                    code = None
            answer = directory/'answer.json'
            if code == 0 and answer.exists():
                payload = json.loads(answer.read_text())
                result = AnalysisResult(**payload)
            elif code is not None:
                result.status = 'failed'
                result.errors.append((directory/'worker.log').read_text()[-4000:])
            result.artifacts.update(directory=str(directory), result='result.json', worker_log='worker.log')
        except Exception as exc:
            result.status = 'failed'
            result.errors.append(f'{type(exc).__name__}: {exc}')
        result.write(directory/'result.json')
        return result
