"""Execution contracts: scripts, streams, fresh imports, faults and resource ownership."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest

ROOT=Path(__file__).resolve().parents[1]
CLI=ROOT/'execute.py'


def call(source,*options,input=None):
    return subprocess.run([sys.executable,str(CLI),*options,str(source),'arg'],
        capture_output=True,text=True,input=input,timeout=30)


@pytest.mark.parametrize('strategy',['isolated','preinitialized'])
def test_script_semantics_and_fresh_modules(tmp_path,strategy):
    sibling=tmp_path/'sibling.py';sibling.write_text('VALUE=42\n')
    source=tmp_path/'work.py';source.write_text(
        'import sys,os,sibling\nassert __name__=="__main__"\n'
        'print(sibling.VALUE,sys.argv[1],os.getcwd(),input())\nprint("stderr",file=sys.stderr)\n')
    first=call(source,'--strategy',strategy,'--cwd',str(tmp_path),input='hello\n')
    assert first.returncode==0,first.stderr
    assert first.stdout==f'42 arg {tmp_path} hello\n' and first.stderr=='stderr\n'
    sibling.write_text('VALUE=43\n')  # same size, potentially same second
    second=call(source,'--strategy',strategy,'--cwd',str(tmp_path),input='again\n')
    assert second.returncode==0 and second.stdout.startswith('43 arg ')


@pytest.mark.parametrize('strategy',['isolated','preinitialized'])
def test_state_is_not_shared(tmp_path,strategy):
    source=tmp_path/'work.py';source.write_text('import builtins\nassert not hasattr(builtins,"polluted")\nbuiltins.polluted=True\n')
    assert call(source,'--strategy',strategy).returncode==0
    assert call(source,'--strategy',strategy).returncode==0


@pytest.mark.parametrize('strategy',['isolated','preinitialized'])
def test_timeout_crash_and_recovery(tmp_path,strategy):
    source=tmp_path/'work.py';source.write_text('import time\ntime.sleep(30)\n')
    assert call(source,'--strategy',strategy,'--timeout','.3').returncode==124
    source.write_text('import os\nos._exit(7)\n')
    assert call(source,'--strategy',strategy).returncode==7
    source.write_text('print("recovered")\n')
    answer=call(source,'--strategy',strategy)
    assert answer.returncode==0 and answer.stdout=='recovered\n'


def test_fallback_and_profile(tmp_path):
    source=tmp_path/'work.py';source.write_text('print(sum(range(1000)))\n')
    assert call(source,'--isolated','--profile','cpu').stdout=='499500\n'
    assert list((ROOT/'.execution/profiles').glob('*.pstats'))


def test_descendant_cleanup(tmp_path):
    import psutil
    source=tmp_path/'work.py';pid_file=tmp_path/'child.pid'
    source.write_text(f'import subprocess,sys,time\np=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"],start_new_session=True)\nopen({str(pid_file)!r},"w").write(str(p.pid))\ntime.sleep(60)\n')
    run=call(source,'--timeout','.5')
    assert run.returncode==124
    pid=int(pid_file.read_text())
    assert not psutil.pid_exists(pid) or psutil.Process(pid).status()==psutil.STATUS_ZOMBIE


def test_admission_and_release():
    from execution.resources import Admission
    from concurrent.futures import ThreadPoolExecutor
    gate=Admission(cpus=2,memory_mb=100,jobs=2)
    def task():
        with gate.acquire(1,40):
            time.sleep(.05)
            return gate.active
    with ThreadPoolExecutor(2) as pool:
        results=list(pool.map(lambda _:task(),range(2)))
    assert max(results)==2 and gate.active==0
    with pytest.raises(ValueError):
        with gate.acquire(3,1):pass
