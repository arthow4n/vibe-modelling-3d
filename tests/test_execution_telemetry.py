import json
from execution.telemetry import run, span, child_environment
from execution.history import main


def _delayed_record_update(root,field,ready):
    import os
    from pathlib import Path
    import time
    from execution.telemetry import write_record
    os.environ['ENGINEERING_DATA']=str(root)
    target=root/'runs'/'shared.json'
    original=Path.read_text
    def delayed_read(path,*args,**kwargs):
        text=original(path,*args,**kwargs)
        if path==target:time.sleep(.15)
        return text
    Path.read_text=delayed_read
    ready.wait(5);write_record('shared',{field:True})


def test_concurrent_process_record_updates_preserve_both_writers(tmp_path,monkeypatch):
    import multiprocessing
    from execution.telemetry import write_record
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path))
    target=tmp_path/'runs'/'shared.json'
    write_record('shared',{'operation':'command'})
    context=multiprocessing.get_context('spawn');ready=context.Barrier(2)
    writers=[context.Process(target=_delayed_record_update,args=(tmp_path,field,ready)) for field in ('caller','coordinator')]
    for writer in writers:writer.start()
    try:
        for writer in writers:
            writer.join(5)
            assert writer.exitcode==0
    finally:
        for writer in writers:
            if writer.is_alive():writer.kill();writer.join()
    assert json.loads(target.read_text())=={'schema_version':1,'operation':'command','caller':True,'coordinator':True}


def test_otlp_hierarchy_context_and_perfetto(tmp_path, monkeypatch):
    monkeypatch.setenv('ENGINEERING_DATA', str(tmp_path))
    with run('command') as record:
        with span('construction'):
            assert child_environment()['ENGINEERING_TRACEPARENT'].startswith('00-')
    saved=json.loads((tmp_path/'runs'/f'{record["run_id"]}.json').read_text())
    assert saved['status']=='completed' and saved['elapsed_seconds']>0
    spans=[]
    for line in next((tmp_path/'traces').glob('*')).read_text().splitlines():
        spans += json.loads(line)['resourceSpans'][0]['scopeSpans'][0]['spans']
    assert spans[0]['parentSpanId']==spans[1]['spanId']
    assert len(spans[0]['traceId'])==32
    timeline=tmp_path/'perfetto.json'
    assert main(['--perfetto',str(timeline),'--run',record['run_id']])==0
    assert len(json.loads(timeline.read_text())['traceEvents'])==2


def test_telemetry_failure_does_not_fail_computation(tmp_path, monkeypatch):
    target=tmp_path/'file';target.write_text('not a directory')
    monkeypatch.setenv('ENGINEERING_DATA', str(target))
    with run('command'):
        with span('work'):
            assert 1+1==2


def test_perfetto_includes_nested_runs_in_shared_trace(tmp_path,monkeypatch):
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path))
    with run('parent') as parent:
        with run('nested') as nested:
            with span('work'):pass
    output=tmp_path/'trace.json'
    main(['--perfetto',str(output),'--run',parent['run_id']])
    assert {s['name'] for s in json.loads(output.read_text())['traceEvents']}=={'parent','nested','work'}
