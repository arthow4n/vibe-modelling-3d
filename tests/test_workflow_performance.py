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
from performance.sessions import request_metrics
from performance.workflow import measurement, model_latency, markdown

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
    assert summary['warm_worker']=={'reused':1,'new':1}
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


@pytest.mark.parametrize('command,expected',[
    (['./evaluate_model.py',SECRET],'cad'),
    (['bash','-lc','./execute.py '+SECRET],'script'),
    (['OrcaSlicer','--private',SECRET],'slicing'),
    (['unknown',SECRET],'shell'),
])
def test_actual_rollout_command_vectors_are_classified_without_arguments(command,expected,tmp_path):
    item={'type':'CommandExecution','id':'c','command':command,'exit_code':0}
    s=parse(write(tmp_path/'vector.jsonl',[row('event_msg',{'type':'item_completed','item':item})]))
    assert s.events[0].category==expected
    assert SECRET not in json.dumps(s.normalized())


def test_complete_option_identity_does_not_group_changed_cad_requests():
    base=dict(operation='cad.command',strategy='persistent',source_sha256='source',
              repository_python_sha256='repo',lock_sha256='lock',arguments_sha256='legacy-empty',elapsed_seconds=1.)
    rows=[{**base,'execution_inputs_sha256':'views-a'}, {**base,'execution_inputs_sha256':'views-b'}]
    s=analyze([],rows,[])
    assert s['repeated_identity_runs']==0 and s['complete_comparison_identity_runs']==2
    rows.append({**base,'execution_inputs_sha256':'views-a'})
    assert analyze([],rows,[])['repeated_identity_runs']==1


def test_admission_reason_overlap_is_labeled_as_work():
    s=analyze([], [{'admission':{'blocked_seconds':{'memory':2.,'jobs':2.},'status':'acquired'}}],[])
    assert s['admission_covered_executions']==1
    assert s['blocked_reason_work_s']=={'memory':2.,'jobs':2.}


def test_native_lease_queue_is_reported_separately_from_run_intervals():
    span={'name':'resource.admission','startTimeUnixNano':str(1_000_000_000),
          'endTimeUnixNano':str(3_000_000_000),'traceId':'a','attributes':[
              {'key':'queue_seconds','value':{'doubleValue':1.5}},
              {'key':'blocked_memory_seconds','value':{'doubleValue':1.5}},
              {'key':'blocked_jobs_seconds','value':{'doubleValue':1.5}}]}
    summary=analyze([], [{'start_unix_ns':0,'elapsed_seconds':5}], [({},span)])
    assert summary['execution_union_s']==5 and summary['lease_queue']['sum_s']==1.5
    assert summary['lease_blocked_reason_work_s']=={'memory':1.5,'jobs':1.5}


def context(turn='turn-a', model='gpt-6.1-sol', effort='high', time=T):
    return row('turn_context',dict(turn_id=turn,model=model,effort=effort,instructions=SECRET),time)


def turn_response(n=100, id='r1', turn='turn-a', time=T):
    r=response(n,id);r['payload']['turn_id']=turn;r['timestamp']=time
    return r


def turn_end(turn='turn-a', duration=10000, delay=2500, sub='task_complete'):
    return row('event_msg',dict(type=sub,turn_id=turn,started_at=T,
        completed_at='2026-10-03T08:00:10Z',duration_ms=duration,time_to_first_token_ms=delay),
        '2026-10-03T08:00:10Z')


@pytest.mark.parametrize('request_count',[1,3])
def test_native_turn_timing_does_not_manufacture_request_timing(tmp_path,request_count):
    rows=[context(),row('event_msg',dict(type='task_started',turn_id='turn-a',started_at=T))]
    for i in range(request_count):
        rows += [turn_response(id=f'r{i}'),row('response_item',dict(type='function_call',call_id=f'c{i}',name='exec_command')),
                 row('response_item',dict(type='function_call_output',call_id=f'c{i}',output=SECRET),'2026-10-03T08:00:01Z')]
    rows.append(turn_end())
    s=parse(write(tmp_path/'synthetic.jsonl',rows));m=model_latency([s])
    assert m['response_count']==request_count
    assert m['native_turn_duration']['median']==10
    assert m['native_turn_first_token_delay']['median']==2.5
    for key in ('request_duration','request_first_token_delay','end_to_end_output_throughput','approx_generation_throughput'):
        assert m[key]['eligible']==request_count and m[key]['measured']==0
        assert m[key]['quality']=='unavailable' and m[key]['median'] is None
    assert all(r.turn_model=='gpt-6.1-sol' and r.configuration_scope=='initial_turn_snapshot' for r in s.responses)
    assert SECRET not in json.dumps(s.normalized())


def test_configuration_changes_unknown_models_and_compaction(tmp_path):
    rows=[context(),turn_response(),turn_end(),context('turn-b','gpt-6-astra','medium'),
          turn_response(id='r2',turn='turn-b'),context('turn-c',SECRET,SECRET),turn_response(id='r3',turn='turn-c'),
          turn_response(id='compaction',turn='turn-b'),row('compacted',dict(compaction_response_id='compaction',summary=SECRET))]
    s=parse(write(tmp_path/'synthetic.jsonl',rows))
    assert [(r.turn_model,r.turn_effort) for r in s.responses]==[('gpt-6.1-sol','high'),('gpt-6-astra','medium'),('unknown','unknown'),('unknown','unknown')]
    m=model_latency([s]);assert m['configuration_changes']==2
    assert m['compactions']==1 and m['request_model']=='unavailable'
    assert SECRET not in json.dumps(s.normalized()) and SECRET not in json.dumps(m)


def test_effort_change_and_conflicting_same_turn_snapshots(tmp_path):
    s=parse(write(tmp_path/'synthetic.jsonl',[context(),turn_response(),context(effort='low'),turn_response(id='r2'),turn_end(),
        context('next',effort='low'),turn_response(id='r3',turn='next')]))
    assert [r.turn_model for r in s.responses]==['unknown','unknown','gpt-6.1-sol']
    assert s.responses[-1].turn_effort=='low'
    assert s.quality['ambiguous_turn_configuration']==1


def test_missing_turn_key_cannot_borrow_configuration(tmp_path):
    s=parse(write(tmp_path/'synthetic.jsonl',[context(),response(100),turn_response(id='r2',turn='unrelated')]))
    assert all(r.configuration_scope=='unavailable' for r in s.responses)


def test_thread_settings_changed_inside_turn_make_response_configuration_unknown(tmp_path):
    s=parse(write(tmp_path/'synthetic.jsonl',[row('event_msg',dict(type='task_started',turn_id='turn-a')),context(),
        row('event_msg',dict(type='thread_settings_applied',thread_settings=dict(model='gpt-6-astra',reasoning_effort='medium',private=SECRET))),
        turn_response(),turn_end()]))
    assert s.responses[0].turn_model=='unknown'
    assert SECRET not in json.dumps(s.normalized())


@pytest.mark.parametrize('missing',['started_at','completed_at','duration_ms','time_to_first_token_ms'])
def test_missing_native_fields_remain_missing(tmp_path,missing):
    r=turn_end();r['payload'].pop(missing)
    s=parse(write(tmp_path/'synthetic.jsonl',[r,turn_response()]))
    m=model_latency([s])
    assert m['request_duration']['median'] is None
    if missing=='duration_ms':
        assert m['native_turn_duration']['measured']==0
        assert m['timestamp_turn_duration']['median']==10
    if missing=='time_to_first_token_ms':
        assert m['native_turn_first_token_delay']['median'] is None
    # Native duration can exist without a wall-clock boundary; it is its own observation.
    if missing=='started_at':assert s.events[0].start is None


def test_delayed_interrupted_failed_and_incomplete_turns(tmp_path):
    aborted=turn_end('a',sub='turn_aborted');aborted['payload'].pop('time_to_first_token_ms')
    failed=turn_end('b',delay=9000);failed['payload']['error']={'message':SECRET}
    s=parse(write(tmp_path/'synthetic.jsonl',[aborted,failed,row('event_msg',dict(type='task_started',turn_id='c')),
        row('event_msg',dict(type='error',message=SECRET)),row('event_msg',dict(type='stream_error',message=SECRET))]))
    m=model_latency([s])
    assert m['turn_outcomes']==dict(interrupted=1,failed=1,incomplete=1)
    assert m['native_turn_first_token_delay']['measured']==1 and m['native_turn_first_token_delay']['eligible']==3
    assert m['observed_stream_error_notices']==1 and m['retries'].startswith('unavailable')
    assert m['observed_error_events']==1 and SECRET not in json.dumps(s.normalized())


@pytest.mark.parametrize('duration,delay,expected,generation',[(10,2,10,12.5),(10,None,10,None),(None,2,None,None),(0,0,None,None),(2,2,50,None),(2,3,50,None),(-1,0,None,None),(float('nan'),0,None,None)])
def test_qualified_throughput_arithmetic(duration,delay,expected,generation):
    m=request_metrics(duration,delay,dict(output_tokens=100,reasoning_output_tokens=60))
    assert m['output_tokens_per_s']==expected
    assert m['approx_generation_tokens_per_s']==generation
    assert request_metrics(duration,delay,{})['output_tokens_per_s'] is None


def test_duplicate_usage_and_uncached_input_coverage(tmp_path):
    a=turn_response();b=turn_response(id='r2');b['payload']['usage'].pop('cached_input_tokens')
    s=parse(write(tmp_path/'synthetic.jsonl',[context(),a,a,b]))
    m=model_latency([s]);assert m['response_count']==2
    assert m['tokens']['output_tokens']==20 and m['tokens']['reasoning_output_tokens']==10
    assert m['tokens']['uncached_input_tokens'] is None
    assert m['token_measurements']['uncached_input_tokens']['measured']==1
    single=model_latency([parse(write(tmp_path/'single.jsonl',[a]))])
    assert single['tokens']['uncached_input_tokens']==50
    assert single['token_measurements']['uncached_input_tokens']['quality']=='derived'


def test_invalid_token_subsets_and_native_timing(tmp_path):
    r=turn_response();r['payload']['usage']['cached_input_tokens']=200
    s=parse(write(tmp_path/'synthetic.jsonl',[r,turn_end(delay=11000),turn_end('b',duration=-2,delay=float('inf'))]))
    assert s.quality['invalid_token_subsets']==1 and s.quality['invalid_native_first_token_delay']==1
    assert s.quality['invalid_native_timing_fields']==2
    assert model_latency([s])['tokens']['uncached_input_tokens'] is None


def test_replayed_resume_configuration_and_usage_warnings(tmp_path):
    s=parse(write(tmp_path/'synthetic.jsonl',[row('session_meta',dict(cli_version='0.160.0',forked_from_id=SECRET)),
        context(),turn_response(),row('compacted',{}),row('session_meta',dict(cli_version='0.160.0')),
        context(),turn_response()]))
    assert s.quality['duplicate_response_usage']==1 and s.quality['repeated_session_metadata_inherited_history_possible']==1
    m=analyze([s,s],[],[])['model_latency']
    assert m['response_count'] is None and all(v is None for v in m['tokens'].values())


def test_unexpected_order_and_unsupported_response_fields(tmp_path):
    r=turn_response(time='2026-10-03T08:00:01Z')
    r['payload'].update(request_started_at=T,time_to_first_token_ms=12,duration_ms=1000)
    s=parse(write(tmp_path/'synthetic.jsonl',[turn_end(),r,context()]))
    assert s.quality['out_of_order_timestamps']
    assert s.responses[0].turn_model=='gpt-6.1-sol'  # exact turn key, not record order
    m=model_latency([s]);assert m['request_duration']['measured']==0


def test_small_sample_statistics_and_coverage():
    m=measurement([None,1,3],80,'derived')
    assert m['eligible']==80 and m['measured']==2 and m['median']==2 and m['p90'] is None
    assert measurement(list(range(1,11)),20,'observed')['p90']==9
    assert measurement([],20,'observed')['quality']=='unavailable'


def test_modeling_mode_multiple_sessions_and_reviewed_evidence(tmp_path,monkeypatch,capsys):
    monkeypatch.setenv('ENGINEERING_DATA',str(tmp_path.parent/(tmp_path.name+'-data')))
    (tmp_path/'notes.md').write_text('Existing geometry checks; physical testing pending.')
    paths=[write(tmp_path/f's{i}.jsonl',[context(),turn_response(id=f'r{i}'),turn_end()]) for i in range(2)]
    args=['--repo',str(tmp_path),'--mode','modeling','--since',T,'--until','2026-10-03T08:00:20Z',
        '--milestone','Checked geometry','--outcome','CAD checked; physical use remains untested',
        '--evidence','notes.md','--association-basis','Selected sessions implement the documented geometry change','--agent-only']
    for p in paths:args += ['--session',str(p)]
    assert main(args)==0
    result=json.loads(capsys.readouterr().out);s=result['summary']
    assert s['sessions']==2 and s['executions']==0 and s['model_latency']['response_count']==2
    assert s['investigation']['evidence'][0]['path']=='notes.md'
    assert 'not automated engineering acceptance' in Path(result['local_report']).read_text()
    with pytest.raises(SystemExit):main(['--mode','modeling'])
    with pytest.raises(SystemExit):main(args+['--evidence','../escape'])


@pytest.mark.parametrize('secret',['resp_private12345','req_private12345','2026-10-03T08:00:01.123Z'])
def test_publication_excludes_raw_request_identifiers_and_timestamps(secret):
    assert validate(review()+secret)


def test_local_report_states_latency_limits_without_executions(tmp_path):
    s=parse(write(tmp_path/'synthetic.jsonl',[context(),turn_response(),turn_end()]))
    report=markdown(analyze([s],[],[]))
    assert '0/1' in report and 'neither request TTFT nor visible-text streaming speed' in report
    assert 'P90 uses nearest rank' in report and SECRET not in report


def test_disjoint_model_item_tool_compaction_attribution():
    s=Session(start=0,end=20,events=[Event('turn',0,20,'turn'),Event('tool',0,5,'shell'),
        Event('item',3,10,'reasoning_item'),Event('item',8,12,'message_item'),Event('item',9,15,'compaction')])
    a=analyze([s],[],[])['turn_attribution']
    assert a==dict(tool_s=5,model_items_outside_tools_s=7,compaction_outside_tools_and_model_items_s=3,unattributed_s=5)
    assert sum(a.values())==20


def test_conflicting_response_turn_key_is_not_attributed(tmp_path):
    s=parse(write(tmp_path/'synthetic.jsonl',[context(),context('turn-b','gpt-6-astra'),turn_response(),turn_response(turn='turn-b')]))
    assert s.quality['conflicting_response_turn']==1
    assert s.responses[0].configuration_scope=='unavailable'


def test_comparable_turn_groups_preserve_per_metric_coverage():
    events=[Event('turn',None,None,'turn',duration_s=10+i,native_first_token_delay_s=2 if i<3 else None,
                  model='gpt-6.1-sol',effort='high') for i in range(10)]
    m=model_latency([Session(events=events)])
    group=m['turn_configuration_groups'][0]
    assert group['native_duration']['measured']==10 and group['native_duration']['p90']==18
    assert group['native_first_token_delay']['eligible']==10 and group['native_first_token_delay']['measured']==3
    assert group['native_first_token_delay']['p90'] is None
    assert not model_latency([Session(events=events[:3])])['turn_configuration_groups']


def test_overlapping_turn_history_suppresses_native_distributions(tmp_path):
    s=parse(write(tmp_path/'synthetic.jsonl',[context(),turn_end()]))
    summary=analyze([s,s],[],[])
    assert summary['active_turn_union_s']==10
    assert summary['quality']['overlapping_session_turn_scopes']==1
    assert summary['model_latency']['native_turn_duration']['quality']=='unavailable'
    assert 'turn-a' not in json.dumps(s.normalized())
