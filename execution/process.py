"""Conventional subprocess.run semantics with shared tracing and owned-tree cleanup."""
import subprocess
import tempfile
from .lifecycle import run as launch
from .telemetry import child_environment, span


def run(command, *, cwd=None, env=None, stdout=None, stderr=None, timeout=None,
        check=False, capture_output=False, text=False, input=None):
    with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err,tempfile.TemporaryFile() as incoming:
        if input is not None:
            incoming.write(input.encode() if isinstance(input,str) else input);incoming.seek(0)
        code,measurements=launch(command,cwd=cwd,env=child_environment(env),timeout=timeout,
            stdin=incoming if input is not None else None,
            stdout=out if capture_output else stdout,stderr=err if capture_output else stderr)
        if capture_output:
            out.seek(0);err.seek(0);output=out.read();errors=err.read()
            if text:output=output.decode(errors='replace');errors=errors.decode(errors='replace')
        else:output=errors=None
        result=subprocess.CompletedProcess(command,code,output,errors)
        if check:result.check_returncode()
        return result
