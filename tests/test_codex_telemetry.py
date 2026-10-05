"""Synthetic native OTLP fixtures only; no real sessions or private trace bodies."""
import json
from pathlib import Path
import subprocess
import threading
import tomllib
import urllib.request
import urllib.error

import pytest

from performance.sessions import Event, Session, native_capture
from performance.telemetry import Capture, MAX_BODY, approved, decode, install, normalize, pseudonym
from performance.workflow import analyze, native_latency, timeline

SECRET = 'private prompt sk-private123 alice@example.test /home/private/session'
KEY = b'x'*32


def bundle(tmp_path, rows):
    p = tmp_path/'otel-synthetic'; p.mkdir()
    (p/'capture.json').write_text(json.dumps(dict(schema=1,source='codex-native-otel',key=KEY.hex(),counts={})))
    (p/'records.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    return p


def native_rows(offset=0, model='gpt-6.1-sol', effort='high', identity=1,version='0.160.0'):
    def s(n,parent,name,a,b,**kwargs):
        return dict(type='span',trace_key='a'*32,span_key=f'{identity*10+n:032x}',
                    parent_key=f'{identity*10+parent:032x}',name=name,start=a+offset,end=b+offset,**kwargs)
    return [s(0,9,'try_run_sampling_request',0,20,model=model,version=version,
              session_key=pseudonym(SECRET,KEY,'session')),
            s(1,0,'stream_request',1,2),s(2,0,'receiving_stream',2,20),
            s(3,2,'handle_responses',5,6.9,**{
                'gen_ai.usage.input_tokens':100,'gen_ai.usage.cache_read.input_tokens':40,
                'gen_ai.usage.output_tokens':100,'codex.usage.reasoning_output_tokens':50,
                'codex.request.reasoning_effort':effort}),s(4,3,'receiving',5,6)]


def test_native_structural_boundary_and_throughput(tmp_path):
    rows=native_rows()+native_rows(offset=30,model='gpt-6-sol',effort='low',identity=2)
    data=native_capture([bundle(tmp_path,list(reversed(rows)))],explicit_scope=True)
    s=native_latency(data)
    assert s['completed']==2 and s['duration']['median']==5
    assert s['throughput']['median']==20 and s['duration']['p90'] is None
    assert s['tokens']['output_tokens']==200 and s['tokens']['reasoning_output_tokens']==100
    assert len(s['configuration_groups'])==2
    assert SECRET not in json.dumps(s)
    events=timeline([],[],data)['traceEvents']
    assert len(events)==2 and all(e['dur']==5e6 and 'args' not in e for e in events)


@pytest.mark.parametrize('change', ['missing_start','missing_end','zero','negative','missing_usage','unknown_version','ambiguous'])
@pytest.mark.parametrize('version', ['0.160.0','0.160.1','0.160.99'])
def test_native_missing_and_invalid_observations(tmp_path,change,version):
    rows=native_rows(version=version)
    if change=='missing_start':rows[1].pop('start')
    if change=='missing_end':rows[4].pop('end')
    if change=='zero':rows[4]['end']=1
    if change=='negative':rows[4]['end']=.5
    if change=='missing_usage':rows[3].pop('gen_ai.usage.output_tokens')
    if change=='unknown_version':rows[0]['version']='0.161.0'
    if change=='ambiguous':rows.append(dict(rows[3],span_key='b'*32))
    s=native_latency(native_capture([bundle(tmp_path,rows)],explicit_scope=True))
    assert s['requests']==1 and s['throughput']['median'] is None
    if change in ('missing_usage','zero'):assert s['duration']['measured']==1
    else:assert s['duration']['measured']==0


@pytest.mark.parametrize('version,qualification', [('0.160.0','source_checked'),
    ('0.160.1','source_checked'),('0.160.2','compatible_patch_structure'),
    ('0.160.99','compatible_patch_structure'),('0.161.0',None),('unknown',None),
    ('1.160.0',None),(None,None)])
def test_native_patch_compatibility_preserves_quality_and_scope(tmp_path,version,qualification):
    rows=native_rows(version=version)
    rows.append(dict(type='log',event_name='codex.sse_event',event_kind='response.completed',
        version=version,at=6,ttft_ms=3000,output_token_count=100))
    data=native_capture([bundle(tmp_path,rows)],explicit_scope=True)
    request=data['requests'][0]
    assert request['version_qualification']==(qualification or 'unsupported')
    measured=native_latency(data)
    assert measured['producer_qualification']=={qualification or 'unsupported':1}
    assert measured['duration']['measured']==(1 if qualification else 0)
    assert measured['throughput']['median']==(20 if qualification else None)
    assert measured['stream_first_item_delay']['measured']==(1 if qualification else 0)
    assert data['quality'].get('patch_compatible_native_requests',0)==(1 if qualification=='compatible_patch_structure' else 0)
    assert request['first_observable_delta_delay_s'] is None


def test_native_scope_duplicate_conflict_and_overlap(tmp_path):
    rows=native_rows(); rows.append(dict(rows[3]))
    p=bundle(tmp_path,rows)
    session=Session(source_ids={SECRET},events=[Event('turn',0,20,'turn'),Event('tool',3,4,'shell')])
    data=native_capture([p],[session])
    assert len(data['requests'])==1 and data['quality']['duplicate_native_spans']==1
    s=analyze([session],[],[],native=data)
    assert s['turn_attribution']['native_request_outside_tools_s']==4
    assert s['turn_attribution']['tool_s']==1 and s['turn_attribution']['unattributed_s']==15
    assert s['native_request_union_s']==5
    assert native_capture([p],[Session(source_ids={'unrelated'})])['requests']==[]
    assert native_capture([p])['requests']==[]
    with (p/'records.jsonl').open('a') as f:f.write(json.dumps(dict(rows[0],end=99))+'\n')
    data=native_capture([p],explicit_scope=True)
    assert not data['requests'] and data['quality']['conflicting_native_spans']==1


def test_native_first_item_scope_retries_and_log_duplicates(tmp_path):
    row=dict(type='log',event_name='codex.sse_event',event_kind='response.completed',
             version='0.160.0',at=6,ttft_ms=3000,output_token_count=100)
    retry=dict(type='log',event_name='codex.api_request',attempt=1,duration_ms=40,has_error=True)
    rows=native_rows()+[row,row,retry,dict(row,at=7,ttft_ms=None)]
    s=native_latency(native_capture([bundle(tmp_path,rows)],explicit_scope=True))
    assert s['stream_first_item_delay']['median']==3
    assert s['stream_first_item_delay']['measured']==1 and s['stream_first_item_delay']['eligible']==2
    assert s['explicit_transport_retries']==1 and s['error_notices']==1
    # The different TTFT scope cannot become a generation-throughput denominator.
    assert s['throughput']['median']==20


def av(key,value):
    return dict(key=key,value={'boolValue':value} if isinstance(value,bool) else {'stringValue':str(value)})


def test_receiver_allowlist_drops_payloads_and_private_attributes():
    attrs=[av('model','gpt-6.1-sol'),av('app.version','0.160.0'),av('event.name','codex.sse_event'),
           av('event.timestamp','2026-10-03T08:00:00Z'),av('event.kind','response.completed'),
           av('output_token_count','100'),av('error.message',SECRET),av('conversation.id',SECRET),
           av('prompt',SECRET),av('user.email',SECRET),av('tool.output',SECRET)]
    payload={'resourceLogs':[{'resource':{'attributes':[av('host.name',SECRET)]},'scopeLogs':[
        {'logRecords':[{'body':{'stringValue':SECRET},'attributes':attrs}]}]}]}
    rows=list(normalize(payload,'logs',KEY))
    assert rows[0]['output_token_count']==100 and rows[0]['has_error'] is True
    assert rows[0]['at']==1791014400
    assert SECRET not in json.dumps(rows) and 'user.email' not in rows[0]
    assert rows[0]['session_key']==pseudonym(SECRET,KEY,'session')
    assert approved({'output_token_count':True,'duration_ms':'nan'},KEY)=={}
    span={'resourceSpans':[{'resource':{},'scopeSpans':[{'spans':[dict(name=SECRET,
        traceId=SECRET,spanId=SECRET,attributes=attrs,events=[{'name':SECRET,'attributes':attrs}])]}]}]}
    assert SECRET not in json.dumps(list(normalize(span,'traces',KEY)))


def test_binary_otlp_decode_and_http_capture(tmp_path):
    from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
    message=ExportLogsServiceRequest()
    log=message.resource_logs.add().scope_logs.add().log_records.add()
    attr=log.attributes.add();attr.key='event.name';attr.value.string_value='codex.api_request'
    attr=log.attributes.add();attr.key='duration_ms';attr.value.int_value=12
    log.body.string_value=SECRET
    body=message.SerializeToString()
    assert SECRET not in json.dumps(list(normalize(decode(body,'logs','application/x-protobuf'),'logs',KEY)))
    server=Capture(tmp_path/'capture')
    worker=threading.Thread(target=server.handle_request);worker.start()
    request=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/v1/logs',data=body,
        headers={'Content-Type':'application/x-protobuf','x-workflow-capture':server.token})
    try:
        with urllib.request.urlopen(request) as response:assert response.status==200
        worker.join(timeout=5)
        assert server.counts['records']==1
        assert SECRET not in (tmp_path/'capture/records.jsonl').read_text()
    finally:server.server_close();server.output.close()


def test_receiver_rejects_bad_auth_and_malformed_body_without_retention(tmp_path):
    server=Capture(tmp_path/'capture')
    try:
        for auth,body,code in [('wrong',b'{}',403),(server.token,SECRET.encode(),400)]:
            worker=threading.Thread(target=server.handle_request);worker.start()
            request=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/v1/logs',data=body,
                headers={'Content-Type':'application/json','x-workflow-capture':auth})
            with pytest.raises(urllib.error.HTTPError) as error:urllib.request.urlopen(request)
            assert error.value.code==code
            worker.join(timeout=5)
        assert not (tmp_path/'capture/records.jsonl').read_text()
        assert server.counts['rejected_batches']==1
    finally:server.server_close();server.output.close()


def test_capture_size_bound_and_incomplete_response(tmp_path,monkeypatch):
    import performance.telemetry as module
    monkeypatch.setattr(module,'MAX_BYTES',10)
    server=Capture(tmp_path/'capture')
    try:
        server.append([{'duration_ms':1}])
        assert server.counts['limit_reached']==1 and server.written==0
    finally:server.server_close();server.output.close()
    rows=native_rows()[:3];rows[0]['error_status']=True
    data=native_capture([bundle(tmp_path,rows)],explicit_scope=True)
    assert data['requests'][0]['outcome']=='failed'
    assert data['requests'][0]['duration_s'] is None


@pytest.mark.parametrize('duration',[None,5])
def test_capture_window_is_opt_in(tmp_path,monkeypatch,capsys,duration):
    import performance.telemetry as module
    import signal
    handled=[]
    class OneRequestCapture(Capture):
        def handle_request(self):
            handled.append(True)
            self.counts['limit_reached']=1
    clock=iter((0.,10000.))
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path/'records'))
    monkeypatch.setattr(module,'Capture',OneRequestCapture)
    monkeypatch.setattr(module.time,'monotonic',lambda:next(clock,20000.))
    monkeypatch.setattr(signal,'signal',lambda *args:None)
    repo=tmp_path/'repo';repo.mkdir()
    args=['--repo',str(repo)] + ([] if duration is None else ['--duration',str(duration)])
    assert module.main(args)==0
    output=json.loads(capsys.readouterr().out)
    saved=json.loads((Path(output['local_capture'])/'capture.json').read_text())
    assert output['expires_in_seconds']==duration
    assert saved['expires']==(None if duration is None else saved['started']+duration)
    assert not saved['active']
    assert len(handled)==(1 if duration is None else 0)


def test_native_coverage_percentiles_and_configuration_unknown(tmp_path):
    rows=[]
    for n in range(10):rows+=native_rows(offset=30*n,identity=n+1)
    rows[0]['model']=SECRET
    rows[3].pop('codex.request.reasoning_effort')
    data=native_capture([bundle(tmp_path,rows)],explicit_scope=True)
    s=native_latency(data)
    assert s['duration']['measured']==10 and s['duration']['p90']==5
    assert any(g['model']=='unknown' and g['effort']=='unknown' for g in s['configuration_groups'])
    assert SECRET not in json.dumps(s)


def test_machine_setup_preserves_config_and_wires_remote_control(tmp_path,monkeypatch):
    home=tmp_path/'home';home.mkdir();codex=home/'.codex';codex.mkdir()
    config=codex/'config.toml';config.write_text('model = "gpt-6.1-sol"\n')
    monkeypatch.setattr(Path,'home',classmethod(lambda cls:home))
    monkeypatch.setenv('CODEX_HOME',str(codex))
    calls=[]
    def run(args,**kwargs):
        calls.append(args);return subprocess.CompletedProcess(args,0,b'',b'')
    monkeypatch.setattr(subprocess,'run',run)
    class Response:
        status=200
        def __enter__(self):return self
        def __exit__(self,*args):pass
    monkeypatch.setattr(urllib.request,'urlopen',lambda *a,**k:Response())
    parent=tmp_path/'repo/.execution/workflow-analysis';parent.mkdir(parents=True)
    install(tmp_path/'repo',parent)
    data=tomllib.loads(config.read_text())
    assert data['model']=='gpt-6.1-sol' and data['otel']['log_user_prompt'] is False
    assert data['otel']['exporter']['otlp-http']['endpoint'].startswith('http://127.0.0.1:')
    unit=(home/'.config/systemd/user/codex-workflow-telemetry.service').read_text()
    assert '\nWorkingDirectory="' not in unit and 'Restart=always' in unit
    assert '--duration' not in unit
    assert (home/'.config/systemd/user/codex-remote-control.service.d/50-workflow-telemetry.conf').exists()
    assert not any('restart' in c and 'codex-remote-control.service' in c for c in calls)
    install(tmp_path/'repo',parent,disable=True)
    assert tomllib.loads(config.read_text())=={'model':'gpt-6.1-sol'}


def test_unmanaged_otel_is_not_overwritten(tmp_path,monkeypatch):
    home=tmp_path/'home';home.mkdir();(home/'config.toml').write_text('[otel]\nexporter="none"\n')
    monkeypatch.setenv('CODEX_HOME',str(home))
    with pytest.raises(ValueError,match='unmanaged'):install(tmp_path,tmp_path)
