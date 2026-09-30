"""Repair result extraction without remeshing or launching another native solve."""
import argparse
import hashlib
import json
from pathlib import Path
from .results import AnalysisResult
from .backends.structural import CalculixBackend,run_worker


def recover_run(directory, *, timeout_seconds=600):
    """Recheck saved native fields against byte-identical regenerated input.

    The original result survives failed recovery. This is for repository-owned
    native runs, not importing arbitrary solver files. Backend-specific guards
    and quality checks remain in their workers.
    """
    directory=Path(directory).resolve()
    old=AnalysisResult(**json.loads((directory/'result.json').read_text()))
    native_input='scene.json' if old.provenance.get('backend')=='PolyFEM-IPC-experimental' else 'analysis.inp'
    for key,name in (('input_sha256',native_input),('case_sha256','case.json')):
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=old.provenance.get(key):
            raise ValueError('Saved input/case identity differs from the original result')
    if old.provenance.get('backend','CalculiX')=='CalculiX':backend=CalculixBackend()
    elif old.provenance['backend']=='FEBio':
        from .backends.febio import FebioBackend
        backend=FebioBackend()
    elif old.provenance['backend']=='PolyFEM-IPC-experimental':
        from .backends.polyfem import PolyfemBackend
        backend=PolyfemBackend()
    else:raise ValueError('No recovery adapter for this backend')
    scratch=AnalysisResult(old.case,'recovering')
    answer=directory/'answer.json'
    # Never consume an answer left by the original worker if this one fails.
    if answer.exists():answer.unlink()
    code=run_worker(directory,backend.worker_module,backend.environment(),timeout_seconds,scratch,
                    arguments=('--postprocess-only',),log_name='recovery.log',failure_record='recovery_result.json')
    if code!=0 or not answer.exists():
        raise RuntimeError('Recovery failed; original result preserved. See recovery.log: '+str(scratch.errors))
    recovered=AnalysisResult(**json.loads(answer.read_text()))
    if not recovered.provenance.get('postprocess_only') or not recovered.metrics:
        raise RuntimeError('Recovery did not recheck complete native fields; original result preserved: '+str(recovered.errors))
    recovered.provenance['original_backend_sha256']=old.provenance.get('original_backend_sha256',old.provenance.get('backend_sha256',{}))
    recovered.artifacts.update(old.artifacts,recovery_log='recovery.log')
    recovered.write(directory/'result.json')
    return recovered


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory');p.add_argument('--timeout',type=float,default=600)
    a=p.parse_args();r=recover_run(a.directory,timeout_seconds=a.timeout)
    print(json.dumps(dict(status=r.status,completed=r.completed,errors=r.errors)))
