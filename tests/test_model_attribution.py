"""Synthetic task ownership; no private session content or fixtures."""
from pathlib import Path
import json

import pytest
from performance.attribution import attribute, select_turns
from performance.sessions import parse
from performance.workflow import union


def source(repo, name='session', legacy=False, overlap=False, subagent=False):
    path = repo/f'{name}.jsonl'
    rows = []
    def row(typ, payload, second):
        rows.append({'type':typ, 'payload':payload, 'timestamp':f'2026-10-04T08:00:{second:02d}Z'})
    row('session_meta', {'id':name, 'cwd':str(repo), 'cli_version':'0.160.0',
                        'source':{'subagent':{}} if subagent else 'cli'}, 0)
    for i, (start, end) in enumerate(((1, 10), (5 if overlap else 11, 20)), 1):
        row('turn_context', {'turn_id':f'private-turn-{i}', 'model':'gpt-6.1-sol','effort':'high'}, start)
        row('event_msg', {'type':'task_started','turn_id':f'private-turn-{i}'}, start)
        values = dict(input_tokens=100*i, cached_input_tokens=30*i, output_tokens=10*i, reasoning_output_tokens=4*i)
        if legacy:
            row('event_msg', {'type':'token_count','info':{'total_token_usage':values}}, end)
        else:
            row('token_usage_record', {'thread_id':'private-thread', 'response_id':f'private-response-{i}',
                                      'turn_id':f'private-turn-{i}', 'usage':values}, end+1)
        row('event_msg', {'type':'task_complete','turn_id':f'private-turn-{i}'}, end)
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    return path


def setup(tmp_path):
    for obj in ('one', 'two'):
        p=tmp_path/'model'/obj; p.mkdir(parents=True); (p/'README.md').write_text('Digital checks; physical fit unknown.')
    return tmp_path


def entry(path, turns, obj='one', scope='direct'):
    return dict(object=obj, scope=scope, milestone='Checked geometry', outcome='Digital only; physical use unknown',
                evidence=[f'model/{obj}/README.md'], selections=[dict(session=str(path),turns=turns,basis='Reviewed task boundary')])


def test_turn_ownership_not_usage_timestamp_and_private_keys(tmp_path):
    repo=setup(tmp_path); session=parse(source(repo))
    chosen, _=select_turns(session, [1])
    assert chosen.tokens == dict(input_tokens=100,cached_input_tokens=30,output_tokens=10,reasoning_output_tokens=4)
    assert chosen.responses[0].recorded_at > chosen.events[0].end
    normalized=json.dumps(session.normalized())
    assert 'private-turn' not in normalized and 'private-response' not in normalized and 'private-thread' not in normalized
    assert session.normalized()['responses'][0]['turn_index']==1


def test_mixed_turns_partition_without_proration(tmp_path):
    repo=setup(tmp_path); path=source(repo)
    result=attribute({'schema':1,'entries':[entry(path,[1]),entry(path,[2],scope='mixed')]},repo)
    assert [r['tokens']['output_tokens'] for r in result['entries']]==[10,20]
    assert result['entries'][0]['uncached_input_tokens']==70
    assert result['sources'][0]['unassigned_response_count']==0
    assert len(result['sources'][0]['sha256'])==64


@pytest.mark.parametrize('first,second', [([1],[1]),('all',[2]),([1],'all')])
def test_rejects_double_charged_turns(tmp_path, first, second):
    repo=setup(tmp_path); path=source(repo)
    with pytest.raises(ValueError,match='overlap|multiple'):
        attribute({'schema':1,'entries':[entry(path,first),entry(path,second,'two')]},repo)


def test_cross_file_inherited_usage_not_charged_twice(tmp_path):
    repo=setup(tmp_path); a=source(repo,'a'); b=source(repo,'b')
    with pytest.raises(ValueError,match='Shared response histories'):
        attribute({'schema':1,'entries':[entry(a,[1]),entry(b,[1],'two')]},repo)


def test_partial_legacy_counters_unavailable_and_unassigned_retained(tmp_path):
    repo=setup(tmp_path); legacy=parse(source(repo,legacy=True))
    chosen,_=select_turns(legacy,[1])
    assert all(v is None for v in chosen.tokens.values())
    assert select_turns(legacy,'all')[0].tokens['output_tokens']==10
    path=source(repo,'modern')
    result=attribute({'schema':1,'entries':[entry(path,[1])]},repo)
    assert result['sources'][0]['unassigned_tokens']['output_tokens']==20


def test_native_sample_uses_own_usage_and_unique_turn_containment(tmp_path, monkeypatch):
    from performance.sessions import timestamp
    import performance.attribution as api
    repo=setup(tmp_path); path=source(repo)
    start=timestamp('2026-10-04T08:00:02Z')
    def native(*args):
        return {'requests':[dict(start=start,end=start+5,duration_s=5,output_tokens_per_s=9,
                                 tokens={'output_tokens':45},model='gpt-6.1-sol',effort='high'),
                            dict(start=None,end=None,duration_s=None,output_tokens_per_s=None,tokens={})], 'quality':{}}
    monkeypatch.setattr(api,'native_capture',native)
    row=attribute({'schema':1,'entries':[entry(path,[1])]},repo,[repo])['entries'][0]
    assert row['tokens']['output_tokens']==10
    assert row['native']['tokens']['output_tokens']==45
    assert row['native']['throughput']['median']==9
    assert row['native']['operation_union_s']==5
    assert row['selections'][0]['source_native_candidates']==2
    assert union([(start,start+5)])==5
    # A request contained by two overlapping turns must stay unassigned.
    path=source(repo,'overlap',overlap=True)
    start=timestamp('2026-10-04T08:00:06Z')
    monkeypatch.setattr(api,'native_capture',lambda *a: {'requests':[dict(start=start,end=start+2,duration_s=2,
        output_tokens_per_s=1,tokens={},model='unknown',effort='unknown')],'quality':{}})
    assert attribute({'schema':1,'entries':[entry(path,'all')]},repo,[repo])['entries'][0]['native']['request_count']==0


def test_subagent_scope_requires_review_and_missing_capture_is_unknown(tmp_path):
    repo=setup(tmp_path); path=source(repo,subagent=True)
    with pytest.raises(ValueError,match='subagents'):
        attribute({'schema':1,'entries':[entry(path,'all')]},repo)
    path=source(repo,'plain')
    native=attribute({'schema':1,'entries':[entry(path,'all')]},repo)['entries'][0]['native']
    assert native['operation_union_s'] is None
    assert native['throughput']['quality']=='unavailable'


def test_contextless_start_indices_and_review_fingerprint(tmp_path):
    from performance.attribution import digest
    repo=setup(tmp_path); path=source(repo)
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    rows.insert(1,{'type':'event_msg','timestamp':'2026-10-04T08:00:00Z',
                   'payload':{'type':'task_started','turn_id':'contextless'}})
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    session=parse(path)
    assert session.turn_order == ['contextless','private-turn-1','private-turn-2']
    assert select_turns(session,[2])[0].tokens['output_tokens']==10
    e=entry(path,[2]);e['selections'][0]['source_sha256_at_selection']=digest(path)
    attribute({'schema':1,'entries':[e]},repo)
    path.write_text(path.read_text()+'{}\n')
    with pytest.raises(ValueError,match='fingerprint'):
        attribute({'schema':1,'entries':[e]},repo)


def test_conflicting_response_turn_not_assigned_and_missing_categories_unknown(tmp_path):
    repo=setup(tmp_path); path=source(repo)
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    usage=next(r for r in rows if r['type']=='token_usage_record')
    duplicate=json.loads(json.dumps(usage));duplicate['payload']['turn_id']='private-turn-2'
    rows.append(duplicate)
    for r in rows:
        if r['type']=='token_usage_record':r['payload']['usage'].pop('reasoning_output_tokens',None)
    path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    report=attribute({'schema':1,'entries':[entry(path,[1,2])]},repo)
    assert report['entries'][0]['tokens']['output_tokens']==20
    assert report['entries'][0]['tokens']['reasoning_output_tokens'] is None
    assert report['sources'][0]['unassigned_tokens']['output_tokens']==10


def test_explicit_source_capture_selection(tmp_path,monkeypatch):
    import performance.attribution as api
    repo=setup(tmp_path);path=source(repo);capture=repo/'chosen-capture';received=[]
    def native(captures,sessions):
        received.extend(captures);return {'requests':[],'quality':{}}
    monkeypatch.setattr(api,'native_capture',native)
    manifest={'schema':1,'entries':[entry(path,[1])],'telemetry':{str(path.resolve()):[str(capture)]}}
    api.attribute(manifest,repo,[repo/'unrelated-new-capture'])
    assert received == [capture]


def test_whole_legacy_coverage_remains_incomplete_and_shared_turns_rejected(tmp_path):
    repo=setup(tmp_path);a=source(repo,'legacy-a',legacy=True)
    row=attribute({'schema':1,'entries':[entry(a,'all')]},repo)['entries'][0]
    assert row['tokens']['output_tokens']==10 and row['response_count'] is None
    assert row['token_coverage']['output_tokens']==dict(value=10,quality='derived incomplete',eligible=None,measured=None,
        scope='includes legacy cumulative differences; response coverage unavailable')
    b=source(repo,'legacy-b',legacy=True)
    with pytest.raises(ValueError,match='Shared turn histories'):
        attribute({'schema':1,'entries':[entry(a,'all'),entry(b,'all','two')]},repo)
