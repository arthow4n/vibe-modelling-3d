"""Synthetic fixtures only; never copy private rollouts into these tests."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

import pytest
from execution.history import iter_records, iter_spans
from performance.sessions import Event, Session, discover, parse, timestamp
from performance.workflow import analyze, associate, local_directory, main, save_local, union
from performance.publication import create_review, validate

T='2026-10-03T08:00:00Z'
SECRET='private prompt alice@example.test /home/synthetic-user/private sk-secret123456789'


def row(typ,payload,time=T):
    return {'type':typ,'timestamp':time,'payload':payload}


def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r)+'\n' if not isinstance(r,str) else r+'\n' for r in rows))
    return path


def usage(n):
    return dict(input_tokens=n,output_tokens=n//10,cached_input_tokens=n//2,reasoning_output_tokens=n//20)


def response(n,id='r1',thread='t1',total=None):
    return row('token_usage_record',dict(thread_id=thread,response_id=id,usage=usage(n),thread_token_usage=usage(n if total is None else total)))


def test_discovery_headers_and_explicit_private_metadata(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();sessions=tmp_path/'sessions'
    a=write(sessions/'a.jsonl',[row('session_meta',{'cwd':str(repo),'timestamp':T,'id':SECRET,'base_instructions':SECRET}),response(100)])
    write(sessions/'b.jsonl',[row('session_meta',{'cwd':str(tmp_path/'repository-other'),'timestamp':T}),row('response_item',{'content':SECRET})])
    write(sessions/'c.jsonl',[row('session_meta',{'workspace_roots':[str(repo)],'timestamp':T})])
    assert discover(repo,sessions,20)==[a]
    normalized=json.dumps(parse(a).normalized())
    assert SECRET not in normalized and 'synthetic-user' not in normalized and 'response_id' not in normalized
    assert discover(repo,tmp_path/'missing')==[]


def test_response_accounting_not_legacy_or_turn_sums(tmp_path):
    p=write(tmp_path/'s.jsonl',[response(100),response(100),response(200,'r2',total=300),
        row('event_msg',{'type':'token_count','info':{'total_token_usage':usage(99999),'last_token_usage':usage(200)}}),
        row('compacted',{'message':SECRET}),response(100,'r3',total=400)])
    s=parse(p)
    assert s.tokens==usage(400)
    assert s.quality['duplicate_response_usage']==1 and s.quality['compactions']==1
    assert not s.quality['response_thread_total_mismatch']


def test_cumulative_baseline_reset_and_resume(tmp_path):
    rows=[row('event_msg',{'type':'token_count','info':{'total_token_usage':usage(n)}}) for n in (100,100,300,50,150)]
    s=parse(write(tmp_path/'s.jsonl',rows))
    assert s.tokens==usage(300)
    assert s.quality['counter_resets']==1
    assert s.quality['reset_baseline_fields_excluded']==4
    assert 'incomplete' in s.usage_method


def test_missing_fields_conflicts_and_inherited_thread(tmp_path):
    rows=[response(100),response(200),response(200,'r2',total=999)]
    rows[-1]['payload']['usage'].pop('reasoning_output_tokens')
    s=parse(write(tmp_path/'s.jsonl',rows))
    assert s.tokens['reasoning_output_tokens'] is None
    assert s.quality['conflicting_response_usage']==1
    assert s.quality['response_thread_total_mismatch']==1
    assert 'incomplete' in s.usage_method


def test_turns_tools_items_compaction_subagents_and_private_outputs(tmp_path):
    rows=[row('event_msg',{'type':'task_started','turn_id':'t','started_at':T}),
          row('response_item',{'type':'custom_tool_call','call_id':'c','name':'functions.exec','input':SECRET}),
          row('response_item',{'type':'custom_tool_call_output','call_id':'c','output':SECRET},'2026-10-03T08:00:05Z'),
          row('response_item',{'type':'function_call','call_id':'incomplete','name':'exec_command','arguments':SECRET}),
          row('event_msg',{'type':'turn_aborted','turn_id':'t','started_at':T,'completed_at':'2026-10-03T08:00:10Z','reason':SECRET}),
          row('event_msg',{'type':'item_completed','item':{'type':'CommandExecution','id':'item','command':'./evaluate_model.py '+SECRET,'status':'failed','exit_code':1},'started_at_ms':1791014400000,'completed_at_ms':1791014403000}),
          row('inter_agent_communication_metadata',{'trigger_turn':SECRET}),
          row('session_meta',{'source':{'subagent':{'parent_thread_id':SECRET}}})]
    s=parse(write(tmp_path/'s.jsonl',rows))
    assert SECRET not in json.dumps(s.normalized())
    assert s.subagent and s.quality['subagent_activity']==1
    assert s.quality['incomplete_tools']==1
    assert [(e.category,e.outcome) for e in s.events if e.kind=='item']==[('cad','failed')]
    assert next(e for e in s.events if e.kind=='turn').outcome=='interrupted'


def test_malformed_unknown_missing_time_and_inaccessible(tmp_path):
    s=parse(write(tmp_path/'s.jsonl',['bad json',[],{'type':'unexpected','payload':{}},row('event_msg',[]) ]))
    assert s.quality['malformed_lines']==2
    assert s.quality['missing_timestamps']==1 and s.quality['unknown_record_types']==1
    assert s.quality['malformed_payloads']==1
    assert parse(tmp_path/'missing').quality['inaccessible_records']==1
    assert timestamp('2026-10-03T08:00:00') is None


def test_per_turn_usage_not_summed_without_response_identity(tmp_path):
    s=parse(write(tmp_path/'s.jsonl',[row('token_usage_record',{'turn_token_usage':usage(100),'usage':usage(100)}),row('token_usage_record',{'turn_token_usage':usage(200),'usage':usage(200)})]))
    assert all(v is None for v in s.tokens.values())
    assert s.quality['unkeyed_response_usage']==2


def test_overlaps_and_correlation_strength():
    s=Session(start=0,end=20,events=[Event('turn',0,20,'turn'),Event('tool',2,12,'orchestration'),Event('tool',8,15,'shell')])
    r={'start_unix_ns':3e9,'elapsed_seconds':4,'run_id':'a'*32,'operation':'cad.command','warm_worker':True}
    assert associate(r,[s])=='plausible_time'
    s.events[-1].start=2
    assert associate(r,[s])=='ambiguous_time'
    s.events[1].run_refs=['a'*32]
    assert associate(r,[s])=='confident_run_id'
    assert associate({'start_unix_ns':30e9,'elapsed_seconds':1},[s])=='unassociated'
    summary=analyze([s],[r,{'start_unix_ns':5e9,'elapsed_seconds':5,'warm_worker':False}],[])
    assert summary['tool_union_s']==13 and summary['execution_union_s']==7
    assert summary['turn_without_observed_tool_s']==7
    assert summary['warm_worker']=={'warm':1,'cold':1}
    assert union([(1,8),(2,3),(6,10),(12,14)])==11


def test_existing_execution_history_reuse_and_missing(tmp_path):
    r={'start_unix_ns':100e9,'elapsed_seconds':10,'operation':'cad.command','trace_id':'a','warm_worker':True,'queue_seconds':2,
       'source':SECRET,'arguments':SECRET,'status':'completed'}
    write(tmp_path/'runs'/'good.json',[])  # Replace with existing schema JSON.
    (tmp_path/'runs'/'good.json').write_text(json.dumps(r))
    (tmp_path/'runs'/'bad.json').write_text('malformed')
    span={'traceId':'a','spanId':'s','name':'cad.render','startTimeUnixNano':100e9,'endTimeUnixNano':101e9,'attributes':[{'key':'strategy','value':{'stringValue':'reused'}}]}
    write(tmp_path/'traces'/'a.otlp.jsonl',[{'resourceSpans':[{'resource':{},'scopeSpans':[{'spans':[span]}]}]}])
    records=list(iter_records(tmp_path));spans=list(iter_spans(tmp_path,{'a'}))
    s=analyze([],records,spans,inventory_count=2)
    assert s['reuse']=={'cad.render:reused':1}
    assert s['unreadable_execution_records']==1
    assert s['trace_covered_executions']==1 and s['tokens']['input_tokens'] is None
    assert SECRET not in json.dumps(s)
    assert len(list(iter_spans(tmp_path,{'missing'})))==0


def review():
    return '\n'.join(s+': Synthetic measured baseline.' for s in ('Scope','Measurements','Findings','Implications','Changes or recommendations','Verification and limitations'))+'\n'


@pytest.mark.parametrize('secret',[SECRET,'session_id: secret','{"payload": {}}','ghp_123456789secret','password=synthetic','https://private.internal/test','Traceback (most recent call last)','a'*32])
def test_publication_rejects_sensitive(secret):
    assert validate(review()+secret)


def test_publication_structure_filename_and_collision(tmp_path):
    assert validate('No sections')
    assert not validate(review())
    now=datetime(2026,10,3,12,30,0,tzinfo=timezone.utc)
    a=create_review(tmp_path,'baseline',review(),now);b=create_review(tmp_path,'baseline',review(),now)
    assert a.name=='2026-10-03-123000-baseline.md' and a!=b
    assert a.read_text()==review()
    with pytest.raises(ValueError):
        create_review(tmp_path,'../../escape',review(),now)


def test_cli_execution_only_agent_only_and_no_records(tmp_path,monkeypatch,capsys):
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path.parent/(tmp_path.name+'-data')))
    assert main(['--execution-only','--repo',str(tmp_path)])==0
    result=json.loads(capsys.readouterr().out)
    assert result['summary']['sessions']==0 and result['summary']['executions']==0
    p=write(tmp_path/'s.jsonl',[response(100)])
    before=p.read_bytes()
    assert main(['--session',str(p),'--agent-only','--timeline','--repo',str(tmp_path)])==0
    result=json.loads(capsys.readouterr().out)
    assert result['summary']['tokens']==usage(100) and p.read_bytes()==before
    report=Path(result['local_report'])
    assert report.exists() and report.with_suffix('.perfetto.json').exists()


def test_ignored_local_storage_and_raw_defaults():
    repo=Path(__file__).resolve().parents[1]
    for path in ('.execution/workflow-analysis/probe.md','.execution/probe.otlp.jsonl'):
        assert subprocess.run(['git','check-ignore','--quiet',path],cwd=repo).returncode==0
    assert not list((repo/'tests').glob('**/rollout-*.jsonl'))


def test_local_output_deduplicated(tmp_path):
    summary=analyze([],[],[])
    a=save_local(tmp_path,summary,[],[],True)
    mtime=a.stat().st_mtime_ns
    assert save_local(tmp_path,summary,[],[],True)==a
    assert a.stat().st_mtime_ns==mtime


def test_cross_session_inherited_usage_cannot_double_count(tmp_path):
    a=parse(write(tmp_path/'a.jsonl',[response(100)]))
    b=parse(write(tmp_path/'b.jsonl',[response(100)]))
    result=analyze([a,b],[],[])
    assert result['quality']['overlapping_session_response_scopes']==1
    assert all(v is None for v in result['tokens'].values())


def test_malformed_identifier_fields_do_not_crash(tmp_path):
    rows=[row('token_usage_record',{'thread_id':[],'response_id':{},'usage':usage(100)}),
          row('event_msg',{'type':'task_started','turn_id':[]}),
          row('response_item',{'type':'function_call','call_id':{}}),
          row('response_item',{'type':'function_call_output','call_id':[]}),
          row('event_msg',{'type':'item_completed','item':{'id':[]}})]
    s=parse(write(tmp_path/'s.jsonl',rows))
    assert s.quality['unkeyed_response_usage']==1 and s.quality['malformed_item_ids']==1


def test_reuse_summary_copies_only_observed_decisions():
    from execution.telemetry import artifact_reuse_summary
    report={'reuse':{'geometry':True,'identity':SECRET},'views':[{'ok':True,'reused':True,'path':SECRET},{'ok':False,'reused':False}],
            'exports':[{'ok':True,'reused':False,'path':SECRET}],'diagnostics':SECRET,'reused':False}
    s=artifact_reuse_summary(report)
    assert s=={'geometry':'reused','views':{'fresh':0,'reused':1},'exports':{'fresh':1,'reused':0},'slice':'fresh'}
    assert artifact_reuse_summary({})=={}
    r=analyze([], [{'artifact_reuse':s}],[])
    assert r['reuse_covered_executions']==1 and r['artifact_reuse']['geometry:reused']==1
    assert SECRET not in json.dumps(r)


def test_oversized_line_is_bounded_and_next_record_parsed(tmp_path,monkeypatch):
    import performance.sessions as adapter
    monkeypatch.setattr(adapter,'MAX_LINE',256)
    s=parse(write(tmp_path/'s.jsonl',['x'*500,row('session_meta',{'cli_version':'0.160.0'})]))
    assert s.version=='0.160.0' and s.quality['oversized_lines']==1


def test_unsupported_exec_stream_is_not_rollout(tmp_path):
    s=parse(write(tmp_path/'s.jsonl',[{'type':'turn.completed','usage':usage(100)}]))
    assert all(v is None for v in s.tokens.values())
    assert s.quality['unknown_record_types']==1


def test_run_id_relationship_requires_structured_output():
    from performance.sessions import run_references
    identifier='b'*32
    assert run_references(json.dumps({'output':json.dumps({'run_id':identifier,'private':SECRET})}))=={identifier}
    assert not run_references('Private prose quoting "run_id": "'+identifier+'"')


def test_output_retention_excludes_deliberate_follow_up(tmp_path):
    follow_up=tmp_path/'analysis-0000000000000000.follow-up.md'
    follow_up.write_text('Retained local interpretation')
    for i in range(22):
        summary=analyze([],[],[]);summary['sessions']=i
        save_local(tmp_path,summary,[],[])
    assert follow_up.exists()
    assert len(list(tmp_path.glob('analysis-*.md')))==21


def test_missing_thread_crosscheck_is_explicit(tmp_path):
    r=response(100);r['payload'].pop('thread_token_usage')
    s=parse(write(tmp_path/'s.jsonl',[r]))
    assert s.tokens==usage(100)
    assert s.quality['missing_thread_usage_crosscheck']==1
    assert 'cross-check unavailable' in s.usage_method


def test_history_orphan_run_timeline_keeps_filename_fallback(tmp_path,monkeypatch):
    from execution.history import main as history_main
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path))
    span={'traceId':'a','spanId':'b','name':'cad.command','startTimeUnixNano':'1000000000','endTimeUnixNano':'2000000000'}
    write(tmp_path/'traces'/'orphan-1.otlp.jsonl',[{'resourceSpans':[{'resource':{},'scopeSpans':[{'spans':[span]}]}]}])
    write(tmp_path/'traces'/'other-1.otlp.jsonl',[{'resourceSpans':[{'resource':{},'scopeSpans':[{'spans':[span]}]}]}])
    target=tmp_path/'timeline.json'
    assert history_main(['--run','orphan','--perfetto',str(target)])==0
    assert len(json.loads(target.read_text())['traceEvents'])==1
