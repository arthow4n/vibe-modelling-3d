"""Small runtime diagnostic, intentionally separate from modelling commands."""
import json
import subprocess
import sys
from .backends.structural import runtime_environment

from execution.telemetry import operation
from execution.process import run as run_command
from execution.resources import lease


@operation('analysis.doctor')
def main():
    if sys.argv[1:] != ['doctor']:
        raise SystemExit('Usage: python -m physical_analysis doctor')
    env=runtime_environment()
    checks={}
    with lease(1):
        for name,command in (
            ('gmsh',[sys.executable,'-c','import gmsh; print(gmsh.__version__)']),
            ('calculix',[env['CALCULIX_COMMAND'],'-v']),
        ):
            try:
                r=run_command(command,env=env,capture_output=True,text=True)
                output=(r.stdout+r.stderr).strip()
                # CalculiX 2.21 returns 201 for its version flag.
                ok=r.returncode==0 if name=='gmsh' else 'This is Version' in output
                checks[name]=dict(ok=ok,output=output,exit_code=r.returncode)
            except (OSError,subprocess.TimeoutExpired) as exc:
                checks[name]=dict(ok=False,error=str(exc))
    print(json.dumps(checks,indent=2))
    return 0 if all(c['ok'] for c in checks.values()) else 1

if __name__=='__main__':raise SystemExit(main())
