#!/usr/bin/env python3
"""Local metadata-only workflow analysis; no model API or computation reruns."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
import math
from pathlib import Path
import statistics
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from execution.history import iter_records, iter_spans, perfetto_event
from performance.sessions import TOKENS, discover, parse, timestamp, session_root, native_capture

STAGES = {'cad.construction', 'cad.selection', 'cad.validation', 'cad.worker', 'cad.render',
          'cad.export', 'cad.artifact_identity', 'worker.initialization', 'worker.preload_qualification',
          'worker.lifecycle', 'script.execute', 'orca.primary', 'orca.support_probe', 'orca.review',
          'coordinator.admission', 'coordinator.request', 'analysis.prepare', 'analysis.case',
          'analysis.input', 'analysis.worker', 'analysis.mesh', 'analysis.mesh_lookup',
          'analysis.native_input', 'analysis.extraction', 'analysis.contact_diagnostics',
          'analysis.recovery', 'analysis.study', 'subprocess', 'cad.command', 'script.command', 'execution.batch', 'resource.admission'}
TOOL_ITEMS = {'shell', 'cad', 'script', 'slicing', 'edit', 'mcp', 'image', 'subagent'}


def union(intervals):
    intervals = sorted((a, b) for a, b in intervals if a is not None and b is not None and b >= a)
    total = 0; right = None
    for a, b in intervals:
        total += b - max(a, right) if right is not None and a < right < b else (b-a if right is None or a >= right else 0)
        right = max(right, b) if right is not None else b
    return total


def intersections(left, right):
    return [(max(a, c), min(b, d)) for a, b in left for c, d in right
            if a is not None and b is not None and c is not None and d is not None and max(a,c) < min(b,d)]


def safe_label(value, allowed):
    return value if isinstance(value,str) and value in allowed else 'other'


def interval(record):
    start = record.get('start_unix_ns'); elapsed = record.get('elapsed_seconds')
    if not isinstance(start, (int, float)) or not isinstance(elapsed, (int, float)) or not math.isfinite(start) or not math.isfinite(elapsed) or elapsed < 0:
        return None, None
    return start/1e9, start/1e9 + elapsed


def associate(record, sessions):
    start, end = interval(record)
    tools = [(i, e) for i, s in enumerate(sessions) for e in s.events if e.kind == 'tool' or (e.kind=='item' and e.category in ('cad','script','shell','slicing'))]
    exact = [(i, e) for i, e in tools if record.get('run_id') in e.run_refs]
    if len(exact) == 1:
        return 'confident_run_id'
    plausible = [(i, e) for i, e in tools if start is not None and e.start is not None
                 and e.end is not None and e.start-1 <= start and end <= e.end+1
                 and e.category in ('orchestration', 'shell', 'poll','cad','script','slicing')]
    return 'plausible_time' if len(plausible) == 1 else ('ambiguous_time' if plausible or exact else 'unassociated')


def measurement(values, eligible, quality, unit='s'):
    """Coverage-qualified statistics; nearest-rank p90 needs at least ten values."""
    values = sorted(v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v >= 0)
    return dict(eligible=eligible, measured=len(values), quality=quality if values else 'unavailable',
                statistics_quality='derived' if values else 'unavailable',
                unit=unit, median=statistics.median(values) if values else None,
                p90=values[math.ceil(.9*len(values))-1] if len(values) >= 10 else None,
                max=max(values) if values else None,
                p90_note='nearest rank' if len(values) >= 10 else 'unavailable: fewer than 10 measured observations')


def model_latency(sessions, overlapping=False, overlapping_turns=False):
    responses = [r for s in sessions for r in s.responses]
    turns = [(i, j, e) for i, s in enumerate(sessions, 1) for j, e in enumerate((e for e in s.events if e.kind == 'turn'), 1)]
    groups = defaultdict(list)
    for r in responses:
        groups[(r.turn_model, r.turn_effort, r.configuration_scope)].append(r)
    turn_groups = defaultdict(list)
    for _, _, e in turns:
        if e.model != 'unknown' and e.effort != 'unknown':
            turn_groups[(e.model, e.effort)].append(e)
    def tokens(rows):
        result = {k: sum(r.tokens[k] for r in rows) if rows and not overlapping and all(k in r.tokens for r in rows) else None for k in TOKENS}
        uncached = [r.tokens['input_tokens']-r.tokens['cached_input_tokens'] for r in rows
                    if 'input_tokens' in r.tokens and 'cached_input_tokens' in r.tokens and r.tokens['input_tokens'] >= r.tokens['cached_input_tokens']]
        result['uncached_input_tokens'] = sum(uncached) if rows and not overlapping and len(uncached) == len(rows) else None
        return result
    totals = tokens(responses)
    native_durations = [] if overlapping_turns else [e.duration_s for _, _, e in turns]
    elapsed = [] if overlapping_turns else [e.end-e.start for _, _, e in turns if e.duration_s is None and e.start is not None and e.end is not None]
    # No rollout field qualified as a request start, response duration or request TTFT.
    # Report absence explicitly; never divide these tokens by turn elapsed time.
    unavailable = {k: measurement([], len(responses), 'unavailable', unit) for k, unit in
                   [('request_duration', 's'), ('request_first_token_delay', 's'),
                    ('end_to_end_output_throughput', 'tokens/s'), ('approx_generation_throughput', 'tokens/s')]}
    token_measurements = {k: dict(value=totals[k], quality='observed' if totals[k] is not None else 'unavailable',
                                eligible=len(responses), measured=sum(k in r.tokens for r in responses) if not overlapping else 0) for k in TOKENS}
    uncached = totals['uncached_input_tokens']
    token_measurements['uncached_input_tokens'] = dict(value=uncached, quality='derived' if uncached is not None else 'unavailable', eligible=len(responses),
        measured=sum('input_tokens' in r.tokens and 'cached_input_tokens' in r.tokens and r.tokens['input_tokens'] >= r.tokens['cached_input_tokens'] for r in responses) if not overlapping else 0)
    return dict(response_count=len(responses) if not overlapping else None,
                response_usage_observations=len(responses),
                response_count_scope='completed unique usage records; failed/incomplete requests may be absent; overlapping scopes suppress combined count/tokens',
                **unavailable, tokens=totals,
                token_measurements=token_measurements,
                native_turn_duration=measurement(native_durations, len(turns), 'observed'),
                timestamp_turn_duration=measurement(elapsed, len(turns), 'derived'),
                native_turn_first_token_delay=measurement([] if overlapping_turns else [e.native_first_token_delay_s for _, _, e in turns], len(turns), 'observed'),
                configured_turn_groups=[dict(model=k[0], effort=k[1], scope=k[2], responses=len(v), tokens=tokens(v),
                    token_coverage={name:dict(eligible=len(v),measured=sum(name in r.tokens for r in v) if not overlapping else 0) for name in TOKENS},
                    comparable_sample='small sample' if len(v)<10 else 'configuration context only; request timing unavailable') for k,v in sorted(groups.items())],
                turn_configuration_groups=[dict(model=k[0], effort=k[1], scope='initial_turn_snapshot',
                    native_duration=measurement([e.duration_s for e in v],len(v),'observed'),
                    native_first_token_delay=measurement([e.native_first_token_delay_s for e in v],len(v),'observed'))
                    for k,v in sorted(turn_groups.items()) if not overlapping_turns and sum(e.duration_s is not None or e.native_first_token_delay_s is not None for e in v)>=10],
                configuration_changes=sum(sum((a['model'], a['effort']) != (b['model'], b['effort']) for a,b in zip(s.configurations, s.configurations[1:])) for s in sessions),
                request_model='unavailable', backend_implementation='unavailable', context_occupancy='unavailable',
                retries='unavailable: surfaced stream errors are not a complete retry count', backoff='unavailable',
                observed_stream_error_notices=sum(s.quality['observed_stream_error_events'] for s in sessions),
                observed_error_events=sum(s.quality['observed_error_events'] for s in sessions),
                turn_outcomes=dict(Counter(e.outcome for _, _, e in turns)),
                compactions=sum(s.quality['compactions'] for s in sessions),
                slowest_turns=[dict(label=f'selected-{i}-turn-{j}', duration_s=e.duration_s if e.duration_s is not None else e.end-e.start,
                    duration_quality='observed' if e.duration_s is not None else 'derived',
                    native_first_token_delay_s=e.native_first_token_delay_s, model=e.model, effort=e.effort, outcome=e.outcome)
                    for i,j,e in sorted((t for t in turns if t[2].duration_s is not None or (t[2].start is not None and t[2].end is not None)),
                        key=lambda t:t[2].duration_s if t[2].duration_s is not None else t[2].end-t[2].start, reverse=True)[:5]])


def native_latency(data):
    rows = data['requests']; n = len(rows)
    groups = defaultdict(list)
    for r in rows:
        groups[(r['model'], r['effort'])].append(r)
    return dict(requests=n, completed=sum(r['outcome']=='completed' for r in rows),
        duration=measurement([r['duration_s'] for r in rows], n, 'derived'),
        throughput=measurement([r['output_tokens_per_s'] for r in rows], n, 'derived', 'tokens/s'),
        first_observable_delta=measurement([r['first_observable_delta_delay_s'] for r in rows],n,'derived'),
        stream_first_item_delay=measurement(data['native_stream_first_item_delays'], data['native_completion_logs'], 'observed'),
        scope='client.stream operation entry to structurally associated completion receipt; includes client preparation, transport and scheduling; not backend compute',
        first_item_scope='stream-mapping start after transport setup to first OutputItemAdded; logs can include warmup completions; not request TTFT; not joined to request intervals',
        token_scope='native completion evidence, never added to rollout token totals; output already includes reasoning as a subset, never added twice. Rates use total output tokens / full client-operation seconds, including reasoning time and waiting; medians summarize per-request rates, not session totals',
        configuration_groups=[dict(model=m,effort=e,scope='configured sampling request; backend unverified',
            responses=len(v),duration=measurement([r['duration_s'] for r in v],len(v),'derived'),
            throughput=measurement([r['output_tokens_per_s'] for r in v],len(v),'derived','tokens/s')) for (m,e),v in sorted(groups.items())],
        tokens={k:sum(r['tokens'][k] for r in rows) if rows and all(k in r['tokens'] for r in rows) else None for k in TOKENS},
        token_coverage={k:sum(k in r['tokens'] for r in rows) for k in TOKENS},
        uncached_input_tokens=sum(r['tokens']['input_tokens']-r['tokens']['cached_input_tokens'] for r in rows)
            if rows and all('input_tokens' in r['tokens'] and 'cached_input_tokens' in r['tokens']
                and r['tokens']['input_tokens']>=r['tokens']['cached_input_tokens'] for r in rows) else None,
        transport_attempts=len(data['transport_attempts']),
        explicit_transport_retries=sum(r['attempt'] is not None and r['attempt']>0 for r in data['transport_attempts']),
        transport_duration=measurement([r['duration_s'] for r in data['transport_attempts']],len(data['transport_attempts']),'observed'),
        error_notices=data['error_notices'], quality=data['quality'], association_scope=data['scope'],
        producer_qualification=dict(Counter(r.get('version_qualification','unavailable') for r in rows)),
        slowest_requests=[{k:r[k] for k in ('label','duration_s','output_tokens_per_s','tokens','model','effort','version','outcome','association')}
                          for r in sorted((r for r in rows if r['duration_s'] is not None),key=lambda r:r['duration_s'],reverse=True)[:5]])


def analyze(sessions, records, spans, inventory_count=0, native=None):
    wall = [(s.start, s.end) for s in sessions]
    turns = [(e.start, e.end) for s in sessions for e in s.events if e.kind == 'turn']
    tools = [(e.start, e.end) for s in sessions for e in s.events if e.kind == 'tool' or (e.kind == 'item' and e.category in TOOL_ITEMS)]
    model_items = [(e.start, e.end) for s in sessions for e in s.events if e.kind == 'item' and e.category in ('reasoning_item', 'message_item')]
    compactions = [(e.start, e.end) for s in sessions for e in s.events if e.kind == 'item' and e.category == 'compaction']
    requests = [(r['start'],r['end']) for r in native['requests']] if native else []
    # Disjoint attribution within measured turns, with tools given precedence.
    tool_in_turn = union(intersections(tools, turns))
    tools_and_requests = union(intersections(tools+requests, turns))
    tools_and_items = union(intersections(tools+requests+model_items, turns))
    all_activity = union(intersections(tools+requests+model_items+compactions, turns))
    execution_intervals = [interval(r) for r in records]
    tools_union = union(tools); turn_union = union(turns)
    stages = defaultdict(list); stage_intervals = defaultdict(list); reuse = Counter(); covered_traces = set()
    lease_queues=[]; lease_blocked=Counter()
    for _, span in spans:
        name = safe_label(span.get('name'), STAGES)
        try:
            a = int(span['startTimeUnixNano'])/1e9; b = int(span['endTimeUnixNano'])/1e9
        except (ValueError, KeyError, TypeError):
            continue
        if b < a:
            continue
        covered_traces.add(span.get('traceId'))
        stages[name].append(b-a); stage_intervals[name].append((a,b))
        attrs = {a.get('key'): a.get('value', {}) for a in span.get('attributes', [])}
        if name=='resource.admission':
            def numeric(key):
                value=attrs.get(key,{})
                try:return float(value.get('doubleValue',value.get('intValue')))
                except (TypeError,ValueError):return None
            queue_time=numeric('queue_seconds')
            if queue_time is not None and math.isfinite(queue_time) and queue_time>=0:lease_queues.append(queue_time)
            for reason in ('cpu','memory','jobs','resident_memory'):
                seconds=numeric('blocked_'+reason+'_seconds')
                if seconds is not None and math.isfinite(seconds) and seconds>=0:lease_blocked[reason]+=seconds
        strategy = attrs.get('strategy', {}).get('stringValue')
        if strategy in ('reused', 'fresh'):
            reuse[f'{name}:{strategy}'] += 1
    recorded_reuse=Counter(); reuse_coverage=0; admission_coverage=0; blocked=Counter(); strong_comparisons=0
    run_groups = defaultdict(list); repeats = defaultdict(list); resources = []; queue=[]; dispatch=[]
    warm=Counter(); associations=Counter(); statuses=Counter(); missing=Counter()
    comparisons=defaultdict(lambda: defaultdict(list))
    for r in records:
        admission=r.get('admission')
        if isinstance(admission,dict) and admission:
            admission_coverage+=1
            for reason in ('cpu','memory','jobs','resident_memory'):
                value=admission.get('blocked_seconds',{}).get(reason)
                if isinstance(value,(int,float)) and value>=0:
                    blocked[reason]+=value
        observed=r.get('artifact_reuse')
        if isinstance(observed,dict) and observed:
            reuse_coverage+=1
            for field in ('geometry','slice'):
                if observed.get(field) in ('fresh','reused'):
                    recorded_reuse[f'{field}:{observed[field]}']+=1
            for field in ('exports','views'):
                values=observed.get(field)
                if isinstance(values,dict):
                    for status in ('fresh','reused'):
                        count=values.get(status)
                        if isinstance(count,int) and count>=0:
                            recorded_reuse[f'{field}:{status}']+=count
        op=safe_label(r.get('operation'), STAGES)
        run_groups[op].append(r.get('elapsed_seconds'))
        statuses[safe_label(r.get('status'), {'completed','failed','interrupted','timeout','running','review_required'})] += 1
        associations[associate(r,sessions)] += 1
        warm['reused' if r.get('warm_worker') is True else 'new' if r.get('warm_worker') is False else 'unreported'] += 1
        key=tuple(r.get(k) for k in ('operation','strategy','source_sha256','repository_python_sha256','lock_sha256','arguments_sha256'))
        exact_inputs=r.get('execution_inputs_sha256')
        if isinstance(exact_inputs,str):
            key+= (exact_inputs,)
            strong_comparisons+=1
        if all(isinstance(part,str) and part for part in key):
            repeats[key].append(r)
            if isinstance(r.get('warm_worker'),bool) and isinstance(r.get('elapsed_seconds'),(int,float)):
                comparisons[key]['reused' if r['warm_worker'] else 'new'].append(r['elapsed_seconds'])
        for key,target in [('queue_seconds',queue),('startup_dispatch_seconds',dispatch)]:
            if isinstance(r.get(key),(int,float)):
                target.append(r[key])
            else:
                missing[key]+=1
        res=r.get('resources') or {}
        if isinstance(res,dict):
            resources.append({k:res[k] for k in ('peak_tree_rss_bytes','peak_worker_rss_bytes','sampled_tree_cpu_seconds') if isinstance(res.get(k),(int,float))})
    quality=Counter()
    for s in sessions:
        quality.update(s.quality)
    seen_keys=set(); overlaps=0; seen_turns=set(); turn_overlaps=0
    for session in sessions:
        overlaps += len(seen_keys.intersection(session.response_keys))
        seen_keys.update(session.response_keys)
        turn_overlaps += len(seen_turns.intersection(session.turn_keys))
        seen_turns.update(session.turn_keys)
    if overlaps:
        quality['overlapping_session_response_scopes'] = overlaps
    if turn_overlaps:
        quality['overlapping_session_turn_scopes'] = turn_overlaps
    sums={k:sum(s.tokens[k] for s in sessions) if sessions and not overlaps and all(s.tokens.get(k) is not None for s in sessions) else None for k in TOKENS}
    def stats(values):
        values=[v for v in values if isinstance(v,(int,float)) and v >= 0]
        return {'count':len(values),'sum_s':sum(values),'median_s':statistics.median(values) if values else None,'max_s':max(values) if values else None}
    tool_counts=Counter(); item_counts=Counter(); outcomes=Counter(); item_outcomes=Counter(); activity=defaultdict(list)
    for s in sessions:
        for e in s.events:
            activity[f'{e.kind}:{e.category}'].append((e.start,e.end))
            if e.kind=='tool':
                tool_counts[e.category]+=1
                outcomes[e.outcome]+=1
            elif e.kind=='item':
                item_counts[e.category]+=1
                item_outcomes[e.outcome]+=1
    result = dict(schema_version=1,sessions=len(sessions),executions=len(records),
        model_latency=model_latency(sessions, bool(overlaps), bool(turn_overlaps)),
        period_start=min((a for a,b in wall+execution_intervals+requests if a is not None),default=None),
        period_end=max((b for a,b in wall+execution_intervals+requests if b is not None),default=None),
        session_wall_union_s=union(wall),active_turn_union_s=turn_union,
        tool_union_s=tools_union,tool_within_turn_union_s=union(intersections(tools,turns)),
        turn_attribution=dict(tool_s=tool_in_turn, model_items_outside_tools_s=tools_and_items-tools_and_requests,
            compaction_outside_tools_and_model_items_s=all_activity-tools_and_items,
            unattributed_s=max(0,turn_union-all_activity)),
        model_item_union_s=union(model_items),compaction_union_s=union(compactions),
        execution_union_s=union(execution_intervals),execution_within_turn_union_s=union(intersections(execution_intervals,turns)),
        turn_without_observed_tool_s=max(0,turn_union-union(intersections(tools,turns))),
        between_turns_or_missing_s=max(0,union(wall)-turn_union),
        tokens=sums,usage_methods=sorted({s.usage_method for s in sessions}),quality=dict(quality),
        versions=sorted({s.version for s in sessions}),models=sorted({m for s in sessions for m in s.models}),
        modes=sorted({m for s in sessions for m in s.modes}),subagent_sessions=sum(s.subagent for s in sessions),
        tool_calls=dict(tool_counts),completed_items=dict(item_counts),tool_outcomes=dict(outcomes),item_outcomes=dict(item_outcomes),
        activity_intervals={k:{'count':len(v),'timed':sum(a is not None and b is not None for a,b in v),'union_s':union(v),
                               'max_s':max((b-a for a,b in v if a is not None and b is not None),default=None)} for k,v in sorted(activity.items())},
        execution_groups={k:stats(v) for k,v in sorted(run_groups.items())},statuses=dict(statuses),
        queue=stats(queue),dispatch=stats(dispatch),missing_execution_fields=dict(missing),
        admission_covered_executions=admission_coverage,blocked_reason_work_s=dict(blocked),
        lease_queue=stats(lease_queues),lease_blocked_reason_work_s=dict(lease_blocked),
        complete_comparison_identity_runs=strong_comparisons,
        longest_queues=[{'operation':safe_label(r.get('operation'),STAGES),
                         **{k:r.get(k) for k in ('elapsed_seconds','queue_seconds','worker_seconds') if isinstance(r.get(k),(int,float))}}
                        for r in sorted(records,key=lambda r:r.get('queue_seconds',0) if isinstance(r.get('queue_seconds'),(int,float)) else 0,reverse=True)[:5]],
        warm_worker=dict(warm),reuse=dict(reuse),artifact_reuse=dict(recorded_reuse),reuse_covered_executions=reuse_coverage,associations=dict(associations),
        trace_covered_executions=sum(r.get('trace_id') in covered_traces for r in records),
        unreadable_execution_records=max(0,inventory_count-len(records)) if inventory_count else 0,
        stages={k:{**stats(v),'union_s':union(stage_intervals[k])} for k,v in sorted(stages.items())},
        repeated_identity_groups=sum(len(v)>1 for v in repeats.values()),
        repeated_identity_runs=sum(len(v)-1 for v in repeats.values()),
        matched_new_reused_workers=[{'operation':safe_label(key[0],STAGES),'new':stats(v['new']),'reused':stats(v['reused'])}
                           for key,v in comparisons.items() if v['new'] and v['reused']],
        sampled_resources={'cpu_lower_bound_s':sum(r.get('sampled_tree_cpu_seconds',0) for r in resources),
                           'cpu_measured_runs':sum('sampled_tree_cpu_seconds' in r for r in resources),
                           'max_sampled_rss_bytes':max((r.get('peak_tree_rss_bytes',r.get('peak_worker_rss_bytes',0)) for r in resources),default=0)})
    if native is not None:
        result['native_model_latency'] = native_latency(native)
        result['native_request_union_s'] = union(requests)
        result['turn_attribution']['native_request_outside_tools_s'] = tools_and_requests-tool_in_turn
        # Keep these client-operation measurements separate from exact provider
        # request timing and literal generated-token TTFT, which remain unavailable.
    return result


def markdown(summary):
    s=summary
    def time(value):
        return datetime.fromtimestamp(value,timezone.utc).isoformat() if value is not None else 'unavailable'
    investigation=s.get('investigation', {'mode':'latency', 'question':'Selected activity timing; task outcome has not been established.'})
    lines=['# Local workflow performance analysis','',
        f"Performance question ({investigation['mode']}): {investigation['question']}", '',
        f"Engineering result: {investigation.get('outcome', 'not assessed in latency mode')}", '',
        f"Scope: {s['sessions']} sessions; {s['executions']} retained executions. UTC period {time(s['period_start'])} to {time(s['period_end'])}.",
        '',f"Codex versions: {', '.join(s['versions']) or 'unavailable'}. Configured turn models: {', '.join(s['models']) or 'unavailable'}.",
        '', '| Timing observation | Seconds (interval union) |','| --- | ---: |']
    for key in ('session_wall_union_s','active_turn_union_s','tool_union_s','execution_union_s','execution_within_turn_union_s','turn_without_observed_tool_s','between_turns_or_missing_s'):
        lines.append(f"| {key} | {s[key]:.3f} |")
    latency=s['model_latency']
    lines += ['', f"Disjoint measured-turn attribution (tools first, then qualified native request operations when present, then recorded model items, then compaction): {s['turn_attribution']}. Model item intervals describe item activity, not full requests, inference time or first-token delays. Admission and initialization are nested execution evidence, not additional elapsed time."]
    count=str(latency['response_count']) if latency['response_count'] is not None else 'unavailable (overlapping histories)'
    lines += ['', 'Model latency: '+count+' completed unique response-usage observations. Failed or incomplete requests without usage are outside this count.', '',
              '| Measurement | Quality | Coverage | Median | P90 | Maximum |', '| --- | --- | ---: | ---: | ---: | ---: |']
    for key in ('request_duration','request_first_token_delay','end_to_end_output_throughput','approx_generation_throughput',
                'native_turn_duration','timestamp_turn_duration','native_turn_first_token_delay'):
        m=latency[key]
        def value(v): return f'{v:.3f}' if v is not None else 'unavailable'
        lines.append(f"| {key} ({m['unit']}) | {m['quality']} | {m['measured']}/{m['eligible']} | {value(m['median'])} | {value(m['p90'])} | {value(m['max'])} |")
    lines += ['', 'P90 uses nearest rank with at least ten measured observations; smaller samples retain median and maximum only. Native first-token delay is turn-start to the first recognized model event (including eligible reasoning/tool items); it is neither request TTFT nor visible-text streaming speed.', '',
              f"Token coverage: {latency['token_measurements']}.", '',
              f"Configured turn groups: {latency['configured_turn_groups']}. These are initial turn snapshots associated by turn key, not independently verified request or backend models. Changed/ambiguous snapshots and identified compaction responses retain unknown configuration.", '',
              f"Turn timing by initial configuration (at least ten timed turns; task and context are not controlled): {latency['turn_configuration_groups']}.", '',
              f"Observed turn outcomes: {latency['turn_outcomes']}; surfaced stream-error notices: {latency['observed_stream_error_notices']}; error events: {latency['observed_error_events']}; compactions: {latency['compactions']}. Full retry/backoff history and context occupancy are unavailable.", '',
              f"Slowest measured turns: {latency['slowest_turns']}. Turn intervals can contain many requests and tools; rollouts alone do not support slowest-response ranking."]
    if 'native_model_latency' in s:
        native = s['native_model_latency']
        lines += ['', f"Native OTel: {native['completed']}/{native['requests']} completed sampling request operations. Scope: {native['scope']}. Association: {native['association_scope']}.", '',
                  '| Native measurement | Quality | Coverage | Median | P90 | Maximum |', '| --- | --- | ---: | ---: | ---: | ---: |']
        for label in ('duration','throughput','first_observable_delta','stream_first_item_delay','transport_duration'):
            m=native[label]
            fmt=lambda v: f'{v:.3f}' if v is not None else 'unavailable'
            lines.append(f"| {label} ({m['unit']}) | {m['quality']} | {m['measured']}/{m['eligible']} | {fmt(m['median'])} | {fmt(m['p90'])} | {fmt(m['max'])} |")
        lines += ['', native['first_item_scope']+'. First observable text/reasoning-delta timing is unavailable: installed exports omit the required event-kind labels. Generation throughput and visible-text speed remain unavailable. '+native['token_scope']+'.', '',
                  f"Native tokens: {native['tokens']}; coverage {native['token_coverage']}; derived uncached input {native['uncached_input_tokens']}. Configuration groups: {native['configuration_groups']}.", '',
                  f"Transport attempt observations: {native['transport_attempts']}; explicit retries: {native['explicit_transport_retries']}; error notices: {native['error_notices']}. These are surfaced observations, not a complete retry/backoff ledger.", '',
                  f"Slowest qualified request operations: {native['slowest_requests']}. Quality: {native['quality']}. No backend-speed or optimization claim follows from enabling telemetry."]
    if investigation['mode']=='modeling':
        lines += ['', f"Milestone: {investigation['milestone']}. Evidence references: {investigation['evidence']}. Outcome and association basis are analyst assertions requiring evidence review, not automated engineering acceptance.", '',
                  'Association basis: '+investigation['association_basis'], '',
                  'Selection includes whole sessions and overlapping retained executions, not a task ledger. Inspect which activity belongs to the milestone; time containment alone cannot establish task ownership. Source edits/tool calls count activity, not geometry revisions or successful design changes.']
    lines+=['','Turn intervals include tools, waits and agent activity. The remainder is **unattributed**, not model reasoning time. Overlapping sessions/runs are unioned; sums in stage/group tables are work totals, not session elapsed time. Open turns/tools are excluded from duration totals.','',
            '| Reported tokens | Count |','| --- | ---: |']
    for k,v in s['tokens'].items():
        lines.append(f"| {k} | {v if v is not None else 'unavailable/incomplete'} |")
    lines+=['','Accounting: '+('; '.join(s['usage_methods']) or 'unavailable')+'. Input includes cached input; reasoning is a reported output subset, not an additional total. No cost inference.','',
        '| Response tool category | Calls |','| --- | ---: |']
    lines += [f'| {k} | {v} |' for k,v in sorted(s['tool_calls'].items())]
    lines+=['','| Recorded agent activity | Events | Timed | Union s | Maximum s |','| --- | ---: | ---: | ---: | ---: |']
    for k,v in s['activity_intervals'].items():
        lines.append(f"| {k} | {v['count']} | {v['timed']} | {v['union_s']:.3f} | {v['max_s'] or 0:.3f} |")
    lines+=['',f"Tool outcomes: {s['tool_outcomes']}. A returned tool output does not establish success.",
            '',f"Completed item categories (a separate, potentially nested activity layer): {s['completed_items']}.",'',
            '| Engineering operation | Runs | Work sum s | Median s | Maximum s |','| --- | ---: | ---: | ---: | ---: |']
    for k,v in s['execution_groups'].items():
        lines.append(f"| {k} | {v['count']} | {v['sum_s']:.3f} | {v['median_s'] or 0:.3f} | {v['max_s'] or 0:.3f} |")
    lines+=['','| Recorded stage | Spans | Work sum s | Interval union s |','| --- | ---: | ---: | ---: |']
    for k,v in sorted(s['stages'].items(),key=lambda x:x[1]['sum_s'],reverse=True):
        lines.append(f"| {k} | {v['count']} | {v['sum_s']:.3f} | {v['union_s']:.3f} |")
    lines+=['',f"Admission reason coverage: {s['admission_covered_executions']}/{s['executions']}; blocked work seconds {s['blocked_reason_work_s']}. Reasons can overlap; their sums are not elapsed time.",'',f"Longest recorded queues (not summed session time): {s['longest_queues']}.",'',f"Queue: {s['queue']}. Dispatch: {s['dispatch']} (dispatch is not complete initialization).",'',
        f"Geometry workers (new/reused): {s['warm_worker']}. New workers can inherit initialized imports; only initialization spans measure startup. Explicit stage reuse: {s['reuse']}.",'',
        f"Recorded artifact reuse: {s['artifact_reuse']}; coverage {s['reuse_covered_executions']}/{s['executions']}. Absent reuse records are unreported, not fresh.",'',
        f"Same recorded operation/strategy/source/repository/lock/argument identity: {s['repeated_identity_groups']} repeated groups; {s['repeated_identity_runs']} additional runs. These are candidates for review, not proof of unnecessary verification.",'',
        f"Matched new/reused worker groups: {s['matched_new_reused_workers']}. Complete option/budget comparison identities exist for {s['complete_comparison_identity_runs']} runs. Legacy CAD argument hashes omit view/export options; legacy groups are candidates, not verified repeats. Even complete identities do not control machine load.",'',
        f"Separate native resource leases: queue {s['lease_queue']}; blocked work seconds {s['lease_blocked_reason_work_s']}. These may occur inside run intervals and are not added to elapsed time.",'',
        f"Association strengths: {s['associations']}. Timing-only associations are inferred; ambiguous matches remain ambiguous.",'',
        f"Sampled resources: {s['sampled_resources']}. Sampled CPU is a lower bound; RSS includes shared pages.",'',
        f"Measurement quality: {s['quality']}. Trace coverage: {s['trace_covered_executions']}/{s['executions']} runs. Missing execution fields: {s['missing_execution_fields']}.",'',
        'Measured observations: compare the interval unions and coverage above; inspect the largest measurable contributor first. Qualified native request operations, when present, include client preparation, transport and scheduling. Exact provider timing remains unavailable; turn time outside observed intervals cannot distinguish generation, orchestration or unrecorded waits.', '',
        'Plausible interpretations: repeated identities, large token counts and long turns are investigation candidates. Required exploration, stronger checks and physical evidence can justify them. Engineering records must establish the result and necessity of the work.', '',
        'Recommended action: no automatic optimization. A follow-up should name the suspected change, expected benefit, required correctness/validation evidence and a matched measurement that could verify it. Route computation work to engineering execution and transferable lessons to engineering reflection.', '',
        'Limitations: retained history is bounded and may omit early operations. Session boundaries are recorded-file observations, not necessarily launch/exit times. Current files are snapshots. Forked/inherited history can overlap accounting scopes; exclude related forks for cross-session totals. Resumes without an explicit marker cannot be counted reliably. Tool outputs/arguments and prompts are not included. Missing timestamps, usage, incomplete calls and trace gaps remain missing evidence. Recorded reasoning-item intervals do not establish total model-processing latency.']
    return '\n'.join(lines)+'\n'


def timeline(sessions, spans, native=None):
    events=[]
    for i,s in enumerate(sessions):
        for e in s.events:
            if e.start is not None and e.end is not None:
                events.append(dict(name=f'{e.kind}:{e.category}',cat='agent',ph='X',pid=f'agent-{i+1}',tid=e.kind,ts=e.start*1e6,dur=(e.end-e.start)*1e6))
    for resource,span in spans:
        try:
            event=perfetto_event(resource,span)
            event['name']=safe_label(event['name'],STAGES);event.pop('args',None)
            events.append(event)
        except (KeyError,ValueError,TypeError):
            continue
    if native:
        for r in native['requests']:
            if r['start'] is not None and r['end'] is not None:
                span=dict(name='client.request_operation',startTimeUnixNano=int(r['start']*1e9),
                          endTimeUnixNano=int(r['end']*1e9),attributes=[],traceId='',spanId='')
                event=perfetto_event({},span); event.pop('args',None)
                event.update(cat='model',pid='native-model',tid='request')
                events.append(event)
    return {'traceEvents':events}


def local_directory(root, repo):
    path=root.resolve()/'workflow-analysis'
    if path.is_relative_to(repo.resolve()):
        check=subprocess.run(['git','check-ignore','--quiet',str(path/'probe.json')],cwd=repo,capture_output=True)
        if check.returncode != 0:
            raise ValueError('Analysis data root inside repository must be Git-ignored')
    path.mkdir(parents=True,exist_ok=True,mode=0o700)
    return path


def save_local(directory, summary, sessions, spans, with_timeline=False, native=None):
    payload={'summary':summary,'sessions':[s.normalized() for s in sessions]}
    encoded=json.dumps(payload,sort_keys=True)
    if len(encoded.encode())>16*1024*1024:
        raise ValueError('Normalized output exceeds 16 MiB bound; select fewer sessions')
    key=hashlib.sha256(encoded.encode()).hexdigest()[:16]
    base=directory/f'analysis-{key}'
    for suffix,content in [('.json',encoded),('.md',markdown(summary))]:
        target=base.with_suffix(suffix)
        if not target.exists():
            with target.open('x') as output:
                output.write(content)
            target.chmod(0o600)
    if with_timeline:
        content=json.dumps(timeline(sessions,spans,native))
        if len(content)>16*1024*1024:
            raise ValueError('Timeline exceeds 16 MiB bound; narrow scope')
        target=base.with_suffix('.perfetto.json')
        if not target.exists():
            with target.open('x') as output:
                output.write(content)
            target.chmod(0o600)
    # Keep at most 20 immutable analyses; only this tool's outputs are pruned.
    reports=sorted((p for p in directory.glob('analysis-*.md') if re.fullmatch(r'analysis-[0-9a-f]{16}\.md',p.name)),key=lambda p:p.stat().st_mtime,reverse=True)
    for report in reports[20:]:
        for suffix in ('.md','.json','.perfetto.json'):
            report.with_suffix(suffix).unlink(missing_ok=True)
    return base.with_suffix('.md')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=ROOT)
    parser.add_argument('--codex-home',type=Path,help='Read sessions beneath this local Codex home')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--session',type=Path,action='append',help='Explicit local rollout; may repeat; ownership override')
    mode.add_argument('--recent',type=int,default=3,help='At most N repository sessions by recorded creation time (1..20)')
    mode.add_argument('--execution-only',action='store_true')
    parser.add_argument('--agent-only',action='store_true')
    parser.add_argument('--telemetry',type=Path,action='append',help='Explicit normalized local native capture directory; may repeat')
    parser.add_argument('--telemetry-only',action='store_true',help='Analyze explicitly selected native captures without rollouts/executions')
    parser.add_argument('--last-runs',type=int,default=500,help='Retained execution bound (1..500)')
    parser.add_argument('--since',help='ISO timestamp with timezone')
    parser.add_argument('--until',help='ISO timestamp with timezone')
    parser.add_argument('--timeline',action='store_true')
    parser.add_argument('--mode',choices=('latency','modeling'),default='latency')
    parser.add_argument('--question',default='Selected activity timing; task outcome has not been established.')
    parser.add_argument('--milestone',help='Established engineering milestone; modeling mode only')
    parser.add_argument('--outcome',help='Evidence-backed result, including limitations; analyst assertion')
    parser.add_argument('--evidence',type=Path,action='append',help='Existing repository-relative engineering record; may repeat')
    parser.add_argument('--association-basis',help='Why the selected activity belongs to the milestone; reviewed locally')
    args=parser.parse_args(argv)
    if args.telemetry_only and (not args.telemetry or args.session or args.execution_only or args.mode=='modeling'):
        parser.error('Telemetry-only requires explicit captures and no session/execution/modeling selection')
    if args.telemetry and len(args.telemetry)>20:
        parser.error('Select at most 20 native captures')
    if not 1<=args.recent<=20 or not 1<=args.last_runs<=500 or (args.execution_only and args.agent_only):
        parser.error('Select 1..20 sessions, 1..500 runs, and compatible source modes')
    since=timestamp(args.since);until=timestamp(args.until)
    if (args.since and since is None) or (args.until and until is None) or (since is not None and until is not None and since>until):
        parser.error('Time bounds require ordered timezone-aware ISO timestamps')
    investigation={'mode':args.mode,'question':args.question}
    if args.mode=='modeling':
        if not all((args.session, args.since, args.until, args.milestone, args.outcome, args.evidence, args.association_basis)):
            parser.error('Modeling mode requires explicit sessions, since/until, milestone, outcome, evidence and association-basis')
        if len(args.evidence)>20:
            parser.error('Select at most 20 evidence references')
        evidence=[]
        for path in args.evidence:
            target=(args.repo/path).resolve()
            if path.is_absolute() or not target.is_relative_to(args.repo.resolve()) or not target.is_file() or target.stat().st_size>16*1024*1024:
                parser.error('Evidence must be an existing repository-relative file of at most 16 MiB')
            evidence.append({'path':str(target.relative_to(args.repo.resolve())), 'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
        investigation.update(milestone=args.milestone,outcome=args.outcome,evidence=evidence,
                             association_basis=args.association_basis,since=since,until=until)
    elif any((args.milestone,args.outcome,args.evidence,args.association_basis)):
        parser.error('Milestone fields require modeling mode')
    paths=[] if args.execution_only or args.telemetry_only else (args.session or discover(args.repo,args.codex_home/'sessions' if args.codex_home else session_root(),args.recent))
    if len(paths)>20:
        parser.error('Explicit session bound is 20')
    paths=list(dict.fromkeys(p.resolve() for p in paths))
    sessions=[parse(p) for p in paths]
    # Bounds select whole sessions (not partial counters). Explicit sessions stay explicit.
    if not args.session:
        sessions=[s for s in sessions if (since is None or (s.end is not None and s.end>=since)) and (until is None or (s.start is not None and s.start<=until))]
    root=Path(os.environ.get('ENGINEERING_DATA',args.repo/'.execution'))
    all_records=list(iter_records(root)) if not args.agent_only and not args.telemetry_only else []
    all_records.sort(key=lambda r:r.get('start_unix_ns',0),reverse=True)
    if sessions:
        windows=[(s.start,s.end) for s in sessions if s.start is not None and s.end is not None]
    else:
        windows=[]
    selected=[]
    for r in all_records:
        a,b=interval(r)
        if a is None or (since is not None and b<since) or (until is not None and a>until):
            continue
        if windows and not any(a<=end and b>=start for start,end in windows):
            continue
        selected.append(r)
        if len(selected)>=args.last_runs:
            break
    spans=[]; seen_spans=set()
    for resource,span in iter_spans(root,trace_ids={r['trace_id'] for r in selected if isinstance(r.get('trace_id'),str)}):
        identity=(span.get('traceId'),span.get('spanId'))
        if all(isinstance(part,str) for part in identity) and identity not in seen_spans:
            spans.append((resource,span));seen_spans.add(identity)
    captures=args.telemetry or (sorted((p for p in (root/'workflow-analysis').glob('otel-*') if p.is_dir()),key=lambda p:p.stat().st_mtime,reverse=True)[:20] if sessions else [])
    captures=[p for p in captures if p.is_dir()]
    native=native_capture(captures,sessions,explicit_scope=args.telemetry_only) if captures else None
    summary=analyze(sessions,selected,spans,native=native)
    if args.telemetry and not captures:
        summary['quality']['no_readable_native_captures']=1
    summary['investigation']=investigation
    if since is not None or until is not None:
        summary['quality']['sessions_extend_time_bounds']=sum((since is not None and s.start is not None and s.start<since) or
            (until is not None and s.end is not None and s.end>until) for s in sessions)
    if not sessions:
        summary['quality']['no_selected_sessions']=1
    elif not any(s.start is not None for s in sessions):
        summary['quality']['no_readable_session_times']=1
    if not selected:
        summary['quality']['no_selected_executions']=1
    summary['quality']['unreadable_execution_records']=max(0,len(list((root/'runs').glob('*.json')))-len(all_records)) if not args.agent_only else 0
    directory=local_directory(root,args.repo)
    report=save_local(directory,summary,sessions,spans,args.timeline,native=native)
    print(json.dumps({'local_report':str(report),'summary':summary},indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
