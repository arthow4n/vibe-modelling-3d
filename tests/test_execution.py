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


def test_percent_budgets_and_disjoint_affinity():
    from execution.resources import cores,Admission,current_affinity
    from concurrent.futures import ThreadPoolExecutor
    import threading
    assert cores('50%',16)==8 and cores('50%',3)==1 and cores('3',8)==3
    barrier=threading.Barrier(2);gate=Admission(cpus=4,memory_mb=100,jobs=2)
    def work():
        with gate.acquire(2,10):
            assigned=set(current_affinity().split(','));barrier.wait(2);return assigned
    with ThreadPoolExecutor(2) as pool:
        first=pool.submit(work);second=pool.submit(work)
        assert not first.result()&second.result()


def test_batch_dependencies_and_failed_dependency(tmp_path):
    from execution.batch import ScriptTask,run
    source=tmp_path/'work.py';source.write_text('import sys\nraise SystemExit(int(sys.argv[1]))\n')
    results=run([ScriptTask('good',source,('0',),threads=1),ScriptTask('bad',source,('3',),threads=1),
                 ScriptTask('after',source,('0',),depends_on=('good',),threads=1),
                 ScriptTask('skip',source,('0',),depends_on=('bad',),threads=1)])
    assert results['good']['exit_code']==results['after']['exit_code']==0
    assert results['bad']['exit_code']==3 and results['skip']['status']=='dependency_failed'


@pytest.mark.parametrize('strategy',['isolated','preinitialized'])
@pytest.mark.parametrize('native_child',[False,True])
def test_dead_coordinator_restarts_without_replaying_script(tmp_path,monkeypatch,strategy,native_child):
    from execution import client,protocol
    import signal,psutil,uuid
    monkeypatch.setenv('ENGINEERING_INSTANCE',uuid.uuid4().hex)
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'records'))
    source=tmp_path/'long.py';started=tmp_path/'started'
    native=f'import os,ctypes\nopen({str(started)!r},"w").write(str(os.getpid()))\nctypes.PyDLL("libc.so.6").sleep(60)\n'
    source.write_text(f'import sys\nfrom execution.lifecycle import run\nrun([sys.executable,"-c",{native!r}])\n' if native_child else native)
    command=[sys.executable,str(CLI),'--strategy',strategy,str(source)]
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    deadline=time.monotonic()+15
    while not started.exists() and time.monotonic()<deadline:time.sleep(.02)
    assert started.exists()
    connection=client.connect();protocol.send(connection,{'kind':'status'});status=protocol.receive(connection);connection.close()
    os.kill(status['pid'],signal.SIGKILL)
    out,err=proc.communicate(timeout=10)
    assert proc.returncode==1 and 'not replayed' in err
    child_pid=int(started.read_text());deadline=time.monotonic()+5
    def alive():
        try:return psutil.Process(child_pid).status()!=psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:return False
    while alive() and time.monotonic()<deadline:time.sleep(.05)
    assert not alive()
    source.write_text('print("new service")\n')
    restarted=call(source)
    assert restarted.returncode==0 and restarted.stdout=='new service\n'
    journal=list((tmp_path/'records/jobs').glob('*.json'))
    assert any(json.loads(p.read_text())['status']=='running' for p in journal)
    connection=client.connect();protocol.send(connection,{'kind':'stop'});protocol.receive(connection);connection.close()


def test_process_birth_identity_ignores_wall_clock(monkeypatch):
    from execution.lifecycle import process_identity
    import psutil
    identity=process_identity()
    monkeypatch.setattr(psutil.Process,'create_time',lambda _:0.)
    assert process_identity()==identity and identity.startswith('ticks:')


def test_replacement_reaps_detached_arbitrary_script_children(tmp_path,monkeypatch):
    from execution import client,protocol
    import signal,psutil,uuid
    monkeypatch.setenv('ENGINEERING_INSTANCE',uuid.uuid4().hex)
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'records'))
    source=tmp_path/'spawn.py';pidfile=tmp_path/'child'
    source.write_text(f'import subprocess,sys,ctypes\np=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"],start_new_session=True)\nopen({str(pidfile)!r},"w").write(str(p.pid))\nctypes.PyDLL("libc.so.6").sleep(60)\n')
    proc=subprocess.Popen([sys.executable,str(CLI),str(source)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    deadline=time.monotonic()+10
    while not pidfile.exists() and time.monotonic()<deadline:time.sleep(.02)
    assert pidfile.exists()
    c=client.connect();protocol.send(c,{'kind':'status'});status=protocol.receive(c);c.close()
    os.kill(status['pid'],signal.SIGKILL);proc.wait(timeout=10)
    pid=int(pidfile.read_text())
    source.write_text('print("replacement")\n')
    assert call(source).stdout=='replacement\n'
    try:assert psutil.Process(pid).status()==psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:pass
    c=client.connect();protocol.send(c,{'kind':'stop'});protocol.receive(c);c.close()


def test_memory_limit_and_invalid_resource_request(tmp_path):
    source=tmp_path/'memory.py'
    source.write_text('import time\ndata=bytearray(80*1024**2)\ntime.sleep(5)\n')
    assert call(source,'--memory-mb','40').returncode==1
    assert call(source,'--threads','0').returncode==2


@pytest.mark.parametrize('strategy',['isolated','preinitialized'])
def test_immediate_exit_does_not_abandon_detached_child(tmp_path,strategy):
    import psutil
    source=tmp_path/'spawn.py';pidfile=tmp_path/'child'
    source.write_text(f'import subprocess,sys\np=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"],start_new_session=True)\nopen({str(pidfile)!r},"w").write(str(p.pid))\n')
    assert call(source,'--strategy',strategy).returncode==0
    pid=int(pidfile.read_text())
    try:assert psutil.Process(pid).status()==psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:pass


def test_unavailable_trace_storage_preserves_execution(tmp_path,monkeypatch):
    target=tmp_path/'not_directory';target.write_text('occupied')
    monkeypatch.setenv('ENGINEERING_DATA',str(target))
    source=tmp_path/'ok.py';source.write_text('print("calculated")\n')
    assert call(source).stdout=='calculated\n'


def test_incompatible_preload_selects_clean_spawn(monkeypatch):
    from execution import coordinator,qualification
    monkeypatch.setenv('ENGINEERING_OWNER_PID',str(os.getpid()))
    monkeypatch.setenv('ENGINEERING_OWNER_ID','')
    service=coordinator.Coordinator()
    service.preload_ready.set()  # Native qualification is mocked; no server loop.
    monkeypatch.setattr(qualification,'qualify',lambda *args:False)
    service.initialize({},lambda:False,None)
    assert service.qualified and service.ctx.get_start_method()=='spawn'


def test_native_and_watchdog_threads_use_allocated_cpu_set(tmp_path):
    source=tmp_path/'affinity.py'
    source.write_text('import os,psutil,numpy as np\na=np.ones((256,256));a@a\nexpected={int(v) for v in os.environ["ENGINEERING_AFFINITY"].split(",")}\nassert all(os.sched_getaffinity(t.id)==expected for t in psutil.Process().threads())\n')
    assert call(source,'--strategy','preinitialized','--threads','2').returncode==0


def test_external_editable_imports_are_fresh_and_trace_disable_is_per_request(tmp_path,monkeypatch):
    from execution import client,protocol
    import uuid
    monkeypatch.setenv('ENGINEERING_INSTANCE',uuid.uuid4().hex)
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'records'))
    external=tmp_path/'external';external.mkdir()
    module=external/'outside.py';module.write_text('VALUE=31\n')
    folder=tmp_path/'scripts';folder.mkdir()
    source=folder/'work.py';source.write_text(f'import sys\nsys.path.insert(0,{str(external)!r})\nimport outside\nprint(outside.VALUE)\n')
    assert call(source).stdout=='31\n'
    module.write_text('VALUE=32\n')
    monkeypatch.setenv('ENGINEERING_TRACE','0')
    assert call(source).stdout=='32\n'
    records=sorted((tmp_path/'records/runs').glob('*.json'),key=lambda p:p.stat().st_mtime)
    last=json.loads(records[-1].read_text())
    assert not list((tmp_path/'records/traces').glob(last['run_id']+'*'))
    c=client.connect();protocol.send(c,{'kind':'stop'});protocol.receive(c);c.close()


def test_idle_worker_memory_is_reclaimed_before_admission():
    from execution.resources import Admission
    gate=Admission(cpus=1,memory_mb=100,jobs=1);idle=[90];reclaimed=[]
    gate.resident_usage=lambda:idle[0]
    def reclaim(available):reclaimed.append(available);idle[0]=0
    gate.reclaim_resident=reclaim
    with gate.acquire(1,30):assert gate.used_memory+idle[0]<=100
    assert reclaimed==[70]


def test_admission_records_memory_block_and_releases_safely():
    from execution.resources import Admission
    from concurrent.futures import ThreadPoolExecutor
    import threading
    gate=Admission(cpus=2,memory_mb=100,jobs=2)
    attempted=threading.Event();observed={}
    def waiting():
        attempted.set()
        with gate.acquire(1,60,observation=observed):
            assert gate.used_memory==60
    with ThreadPoolExecutor(1) as pool:
        with gate.acquire(1,60):
            future=pool.submit(waiting)
            assert attempted.wait(1)
            deadline=time.monotonic()+1
            while 'first_blocked' not in observed and time.monotonic()<deadline:time.sleep(.001)
            assert observed['first_blocked']=={'used_cpus':1,'used_memory_mb':60,'active_jobs':1}
        future.result(timeout=2)
    assert observed['status']=='acquired' and observed['blocked_seconds']['memory']>0
    assert observed['requested_memory_mb']==60 and observed['capacity_memory_mb']==100
    assert not gate.active and not gate.used_cpus and not gate.used_memory


@pytest.mark.parametrize('expired',[True,False])
def test_admission_does_not_dispatch_expired_or_cancelled_ready_request(expired):
    from execution.resources import Admission
    gate=Admission(cpus=1,memory_mb=100,jobs=1);observed={}
    with pytest.raises(TimeoutError if expired else InterruptedError):
        with gate.acquire(1,50,cancelled=lambda:not expired,deadline=time.monotonic()-1 if expired else None,observation=observed):
            pytest.fail('Request must not dispatch')
    assert observed['status']=='not_acquired' and not gate.active
    with gate.acquire(1,50):pass


def test_execution_comparison_identity_covers_options_without_ephemeral_ids():
    from execution.identity import execution_inputs_identity
    request=dict(kind='cad',source_sha256='source',runtime='runtime',strategy='persistent',threads=2,memory_mb=512,
        environment={'ENGINEERING_RUN_ID':'a','OMP_NUM_THREADS':'2'},cad=dict(run_id='a',views=['front'],exports=[],fresh=False))
    original=execution_inputs_identity(request)
    changed={**request,'cad':{**request['cad'],'run_id':'b'},'environment':{**request['environment'],'ENGINEERING_RUN_ID':'b'}}
    assert original==execution_inputs_identity(changed)
    assert original!=execution_inputs_identity({**request,'memory_mb':1024})
    assert original!=execution_inputs_identity({**request,'cad':{**request['cad'],'views':['top']}})


def test_coordinator_does_not_expire_while_handlers_are_queued():
    from execution.coordinator import Coordinator
    service=Coordinator();service.last_request=0
    class Handler:
        def is_alive(self):return True
    service.jobs={Handler()}
    assert not service.idle_expired(now=1000)
    service.jobs.clear()
    assert service.idle_expired(now=1000)
    service.last_request=950
    assert not service.idle_expired(now=1000)


def test_completed_lease_starts_idle_timeout_at_completion(monkeypatch):
    from execution import coordinator
    from contextlib import contextmanager
    service=coordinator.Coordinator();service.last_request=0;service.stopping.set()
    class Connection:
        def close(self):pass
    @contextmanager
    def acquired(*args,**kwargs):yield 0.
    monkeypatch.setattr(service.admission,'acquire',acquired)
    monkeypatch.setattr(coordinator.protocol,'receive',lambda *a,**k:({'kind':'lease','threads':1,'memory_mb':10},[]))
    monkeypatch.setattr(coordinator.protocol,'send',lambda *a,**k:None)
    monkeypatch.setattr(coordinator.time,'monotonic',lambda:1000.)
    service.handle(Connection())
    assert service.last_request==1000.
    assert not service.idle_expired(now=1119.)
    assert service.idle_expired(now=1121.)
