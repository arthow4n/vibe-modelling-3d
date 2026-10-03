import json
from execution.telemetry import run, span, child_environment
from execution.history import main


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
