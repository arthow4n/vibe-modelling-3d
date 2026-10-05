"""Read-only Codex rollout adapter. Never retain conversation/argument/output text.

Event is harness-neutral; only the adapter knows rollout payload types. Private
IDs are used for deduplication/relationships in memory, never as event labels.
"""
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re

TOKENS = ('input_tokens', 'output_tokens', 'cached_input_tokens', 'reasoning_output_tokens')
MAX_LINE = 16 * 1024 * 1024
MAX_EVENTS = 100_000
NATIVE_SOURCE_QUALIFIED_VERSIONS = frozenset({'0.160.0', '0.160.1'})
NATIVE_COMPATIBLE_FAMILIES = frozenset(
    tuple(map(int, version.split('.')[:2])) for version in NATIVE_SOURCE_QUALIFIED_VERSIONS)


def native_version_compatibility(version):
    """Allow structurally checked patches, retaining their qualification scope.

    A patch update must still pass every native boundary/usage check. Different
    major/minor producers need qualification rather than guessed timing semantics.
    """
    if not isinstance(version,str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)',version):
        return None
    if version in NATIVE_SOURCE_QUALIFIED_VERSIONS:
        return 'source_checked'
    if tuple(map(int,version.split('.')[:2])) in NATIVE_COMPATIBLE_FAMILIES:
        return 'compatible_patch_structure'
    return None


def timestamp(value):
    try:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.timestamp() if dt.tzinfo else None
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            return float(value) if math.isfinite(value) else None
    except (ValueError, OverflowError):
        pass
    return None


def records(path, issues):
    """Bound individual lines; stream records from a fixed file-size snapshot."""
    try:
        with path.open('rb') as stream:
            remaining = path.stat().st_size
            while remaining > 0:
                line = stream.readline(min(MAX_LINE + 1, remaining))
                if not line:
                    break
                remaining -= len(line)
                if len(line) > MAX_LINE:
                    issues['oversized_lines'] += 1
                    while not line.endswith(b'\n') and remaining > 0:
                        line = stream.readline(min(MAX_LINE + 1, remaining))
                        remaining -= len(line)
                    continue
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError()
                    yield record
                except (ValueError, UnicodeDecodeError):
                    issues['malformed_lines'] += 1
    except OSError:
        issues['inaccessible_records'] += 1


def session_root():
    return Path(os.environ.get('CODEX_HOME', Path.home()/'.codex'))/'sessions'


def metadata(path):
    issues = Counter()
    for i, record in enumerate(records(path, issues)):
        if record.get('type') == 'session_meta':
            payload = record.get('payload')
            return payload if isinstance(payload, dict) else {}
        if i >= 8:
            break
    return {}


def belongs(meta, repo):
    cwd = meta.get('cwd')
    try:
        return isinstance(cwd, str) and Path(cwd).is_absolute() and Path(cwd).resolve().is_relative_to(repo.resolve())
    except OSError:
        return False


def discover(repo, root=None, recent=3):
    """Inspect headers only for unrelated sessions; never read their conversations."""
    found = []
    for path in (root or session_root()).rglob('*.jsonl'):
        meta = metadata(path)
        if belongs(meta, repo):
            found.append((timestamp(meta.get('timestamp')) or 0, path))
    return [p for _, p in sorted(found, reverse=True)[:recent]]


def category(name):
    # Fixed labels, never arbitrary server/tool/model strings from private data.
    name = str(name or '').split('.')[-1]
    return {'exec': 'orchestration', 'exec_command': 'shell', 'shell_command': 'shell',
            'write_stdin': 'poll', 'wait': 'wait', 'sleep': 'wait', 'apply_patch': 'edit',
            'view_image': 'image', 'spawn_agent': 'subagent', 'send_message': 'subagent',
            'wait_agent': 'subagent', 'web__run': 'web', 'run': 'other'}.get(name, 'other')


def command_category(command):
    # Only classify; do not retain commands or their digests.
    if isinstance(command, list):
        command = ' '.join(part for part in command if isinstance(part, str))
    if not isinstance(command, str):
        return 'shell'
    if re.search(r'\bevaluate_model\.py\b', command):
        return 'cad'
    if re.search(r'\bexecute\.py\b', command):
        return 'script'
    if re.search(r'\b(?:orca|OrcaSlicer)\b', command):
        return 'slicing'
    return 'shell'


def run_references(value, depth=0):
    """Extract IDs only from JSON objects in known tool-result envelopes."""
    if depth > 4:
        return set()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return set()
    if not isinstance(value, dict):
        return set()
    refs = set()
    identifier = value.get('run_id')
    if isinstance(identifier, str) and re.fullmatch(r'[0-9a-f]{32}', identifier):
        refs.add(identifier)
    for field in ('output', 'result', 'data'):
        if field in value:
            refs.update(run_references(value[field], depth+1))
    return refs


def counters(value):
    return {k: value[k] for k in TOKENS if isinstance(value, dict)
            and isinstance(value.get(k), int) and not isinstance(value[k], bool) and value[k] >= 0}


def nonnegative(value):
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0 else None


def model_name(value):
    # Configuration is allowlisted; arbitrary provider strings can contain private data.
    return value if isinstance(value, str) and re.fullmatch(r'(?:gpt-\d+(?:\.\d+)?o?(?:-(?:sol|astra|luna|mini|nano|codex|pro|turbo|max))*|o\d+(?:-mini)?)', value) else 'unknown'


def effort_name(value):
    return value if isinstance(value, str) and value in ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra') else 'unknown'


def request_metrics(duration_s, first_token_delay_s, usage):
    """Arithmetic for qualified response observations, never turn/session totals.

    The rollout adapter currently supplies neither request timing input. Keep
    this calculation separate so unsupported fields cannot accidentally enable it.
    output_tokens already includes reasoning_output_tokens as a subset; never
    add that subset again. The full request duration includes reasoning time and
    waiting; these rates are not visible-text speed.
    """
    duration = nonnegative(duration_s); delay = nonnegative(first_token_delay_s)
    output = counters(usage).get('output_tokens')
    end_to_end = output / duration if output is not None and duration is not None and duration > 0 else None
    generation = output / (duration-delay) if output is not None and duration is not None and delay is not None and duration > delay else None
    return {'duration_s': duration, 'first_token_delay_s': delay,
            'output_tokens_per_s': end_to_end, 'approx_generation_tokens_per_s': generation}


def outcome(value, exit_code=None):
    if exit_code is not None:
        return 'success' if exit_code == 0 else 'failed'
    return ({'completed': 'completed', 'failed': 'failed', 'interrupted': 'interrupted',
             'in_progress': 'incomplete'}.get(value, 'unknown') if isinstance(value,str) else 'unknown')


@dataclass
class Event:
    kind: str
    start: float | None
    end: float | None
    category: str
    outcome: str = 'unknown'
    # Local only: exact IDs observed in structured run_id output fields.
    run_refs: list[str] = field(default_factory=list)
    duration_s: float | None = None
    native_first_token_delay_s: float | None = None
    model: str = 'unknown'
    effort: str = 'unknown'
    turn_key: str | None = field(default=None, repr=False)


@dataclass
class Response:
    # Only a completed usage observation; not an invented request interval.
    recorded_at: float | None
    tokens: dict
    turn_model: str = 'unknown'
    turn_effort: str = 'unknown'
    configuration_scope: str = 'unavailable'
    turn_key: str | None = field(default=None, repr=False)
    usage_key: tuple | None = field(default=None, repr=False)


@dataclass
class Session:
    events: list[Event] = field(default_factory=list)
    tokens: dict = field(default_factory=dict)
    quality: Counter = field(default_factory=Counter)
    start: float | None = None
    end: float | None = None
    usage_method: str = 'unavailable'
    version: str = 'unknown'
    models: set = field(default_factory=set)
    modes: set = field(default_factory=set)
    subagent: bool = False
    response_keys: set = field(default_factory=set, repr=False)
    turn_keys: set = field(default_factory=set, repr=False)
    source_ids: set = field(default_factory=set, repr=False)
    responses: list[Response] = field(default_factory=list)
    configurations: list[dict] = field(default_factory=list)
    turn_order: list[str] = field(default_factory=list, repr=False)

    def normalized(self):
        indices = {key: i for i, key in enumerate(self.turn_order, 1)}
        def local_labels(item):
            value = asdict(item)
            key = value.pop('turn_key', None)
            value.pop('usage_key', None)
            value['turn_index'] = indices.get(key)
            return value
        return dict(events=[local_labels(e) for e in self.events], tokens=self.tokens,
                    quality=dict(self.quality), start=self.start, end=self.end,
                    usage_method=self.usage_method, version=self.version,
                    models=sorted(self.models), modes=sorted(self.modes), subagent=self.subagent,
                    responses=[local_labels(r) for r in self.responses], configurations=self.configurations)


def parse(path):
    session = Session()
    pending = {}; seen_calls = set(); seen_items = set(); seen_responses = {}
    response_sums = Counter(); fields_seen = Counter(); final_thread = {}
    cumulative = {}; cumulative_sums = Counter(); cumulative_fields = Counter()
    turns = {}; completed_turns = set()
    contexts = {}; response_turns = []; turn_events = []; compaction_responses = set()
    response_owners = {}; ambiguous_response_keys = set()
    previous_t = None
    metadata_count = 0
    ordered_turns = set()
    for record in records(path, session.quality):
        if max(len(session.events), len(seen_responses), len(session.configurations), len(turns)) >= MAX_EVENTS:
            session.quality['event_limit_reached'] += 1
            break
        typ = record.get('type'); p = record.get('payload', {})
        if not isinstance(p, dict):
            session.quality['malformed_payloads'] += 1
            continue
        t = timestamp(record.get('timestamp'))
        if t is None:
            session.quality['missing_timestamps'] += 1
        else:
            if previous_t is not None and t < previous_t:
                session.quality['out_of_order_timestamps'] += 1
            previous_t = t
            session.start = min(session.start, t) if session.start is not None else t
            session.end = max(session.end, t) if session.end is not None else t
        sub = p.get('type')
        turn_key = p.get('turn_id')
        if (typ == 'turn_context' or (typ == 'event_msg' and sub == 'task_started')) and isinstance(turn_key, str) and turn_key not in ordered_turns:
            ordered_turns.add(turn_key)
            session.turn_order.append(turn_key)
        if typ == 'session_meta':
            if isinstance(p.get('id'), str):
                session.source_ids.add(p['id'])
            metadata_count += 1
            if metadata_count > 1:
                session.quality['repeated_session_metadata_inherited_history_possible'] += 1
            v = str(p.get('cli_version', ''))
            session.version = v if re.fullmatch(r'\d+\.\d+\.\d+', v) else 'unknown'
            session.subagent = isinstance(p.get('source'), dict) and 'subagent' in p['source']
            if p.get('forked_from_id'):
                session.quality['forked_session_inherited_usage_possible'] += 1
        elif typ == 'turn_context':
            model = model_name(p.get('model')); effort = effort_name(p.get('effort'))
            if model != 'unknown':
                session.models.add(model)
            config = (model, effort)
            session.configurations.append({'recorded_at': t, 'model': model, 'effort': effort, 'scope': 'initial_turn_snapshot'})
            turn_id = p.get('turn_id')
            if isinstance(turn_id, str):
                contexts.setdefault(turn_id, set()).add(config)
            mode = p.get('collaboration_mode', {})
            if isinstance(mode, dict) and mode.get('mode') in ('default', 'plan'):
                session.modes.add(mode['mode'])
        elif typ == 'token_usage_record':
            key = (p.get('thread_id'), p.get('response_id'))
            if not all(isinstance(part,str) and part for part in key):
                session.quality['unkeyed_response_usage'] += 1
                continue
            usage = counters(p.get('usage'))
            if usage.get('cached_input_tokens', 0) > usage.get('input_tokens', math.inf) or usage.get('reasoning_output_tokens', 0) > usage.get('output_tokens', math.inf):
                session.quality['invalid_token_subsets'] += 1
            if not key[0] or not key[1] or not usage:
                session.quality['unkeyed_response_usage'] += 1
                continue
            if key in seen_responses:
                session.quality['duplicate_response_usage'] += 1
                if seen_responses[key] != usage:
                    session.quality['conflicting_response_usage'] += 1
                if response_owners[key] != p.get('turn_id'):
                    session.quality['conflicting_response_turn'] += 1
                    ambiguous_response_keys.add(key)
                continue
            seen_responses[key] = usage
            response_owners[key] = p.get('turn_id')
            session.responses.append(Response(t, usage, turn_key=turn_key if isinstance(turn_key, str) else None, usage_key=key))
            response_turns.append((key, p.get('turn_id')))
            response_sums.update(usage); fields_seen.update(usage.keys())
            final_thread[key[0]] = counters(p.get('thread_token_usage'))
        elif typ == 'compacted':
            session.quality['compactions'] += 1
            identifier = p.get('compaction_response_id')
            if isinstance(identifier, str):
                compaction_responses.add(identifier)
        elif typ == 'inter_agent_communication_metadata':
            session.quality['subagent_activity'] += 1
        elif typ == 'response_item' and sub in ('function_call', 'custom_tool_call'):
            call = p.get('call_id')
            if isinstance(call,str) and call in seen_calls:
                session.quality['duplicate_calls'] += 1
                continue
            if not isinstance(call, str):
                session.quality['missing_call_ids'] += 1
                continue
            seen_calls.add(call)
            pending[call] = Event('tool', t, None, category(p.get('name')))
        elif typ == 'response_item' and sub in ('function_call_output', 'custom_tool_call_output'):
            call=p.get('call_id')
            event = pending.pop(call, None) if isinstance(call,str) else None
            if event:
                event.end = t
                # A return is not proof of success. Never retain arbitrary output.
                out = p.get('output')
                if isinstance(out, str):
                    event.run_refs = sorted(run_references(out))[:20]
                event.outcome = 'returned'
                session.events.append(event)
            else:
                session.quality['orphan_outputs'] += 1
        elif typ == 'event_msg':
            if sub in ('error', 'stream_error'):
                # A stream error is a surfaced reconnect notice in this version,
                # not a complete retry history or measured backoff interval.
                session.quality['observed_'+sub+'_events'] += 1
            elif sub == 'thread_settings_applied':
                settings = p.get('thread_settings')
                if isinstance(settings, dict):
                    config = (model_name(settings.get('model')), effort_name(settings.get('reasoning_effort')))
                    session.configurations.append({'recorded_at': t, 'model': config[0], 'effort': config[1], 'scope': 'thread_settings'})
                    for key in turns:
                        contexts.setdefault(key, set()).add(config)
            elif sub == 'token_count':
                info = p.get('info') or {}
                if not isinstance(info, dict):
                    session.quality['malformed_usage'] += 1
                    continue
                usage = counters(info.get('total_token_usage'))
                if usage and usage == cumulative:
                    session.quality['duplicate_cumulative_snapshots'] += 1
                if any(k in cumulative and value<cumulative[k] for k,value in usage.items()):
                    session.quality['counter_resets'] += 1
                for k, value in usage.items():
                    old = cumulative.get(k)
                    if old is None:
                        # First cumulative value is a baseline, not observed new work.
                        session.quality['cumulative_baseline_fields_excluded'] += 1
                    elif value < old:
                        session.quality['reset_baseline_fields_excluded'] += 1
                        # Reset origin is unknown: exclude the new baseline.
                    else:
                        cumulative_sums[k] += value - old
                        cumulative_fields[k] += 1
                    cumulative[k] = value
            elif sub == 'task_started':
                key = p.get('turn_id')
                if not isinstance(key,str):
                    session.quality['missing_turn_ids'] += 1
                    continue
                if key in turns:
                    session.quality['repeated_turn_start'] += 1
                else:
                    turns[key] = timestamp(p.get('started_at')) or t
            elif sub in ('task_complete', 'turn_aborted'):
                key = p.get('turn_id')
                if not isinstance(key,str):
                    session.quality['missing_turn_ids'] += 1
                    continue
                if key in completed_turns:
                    session.quality['duplicate_turn_end'] += 1
                    continue
                completed_turns.add(key)
                start = timestamp(p.get('started_at')) or turns.pop(key, None)
                turns.pop(key, None)
                end = timestamp(p.get('completed_at')) or t
                event = Event('turn', start, end, 'turn',
                              'interrupted' if sub == 'turn_aborted' else 'failed' if p.get('error') is not None else 'completed', turn_key=key)
                duration = nonnegative(p.get('duration_ms'))
                delay = nonnegative(p.get('time_to_first_token_ms'))
                for name, value in (('duration_ms', duration), ('time_to_first_token_ms', delay)):
                    if p.get(name) is not None and value is None:
                        session.quality['invalid_native_timing_fields'] += 1
                event.duration_s = duration/1000 if duration is not None else None
                event.native_first_token_delay_s = delay/1000 if delay is not None else None
                if event.duration_s is not None and start is not None and end is not None and abs(event.duration_s-(end-start))>2:
                    session.quality['native_wall_turn_duration_disagreement'] += 1
                if event.duration_s is not None and event.native_first_token_delay_s is not None and event.native_first_token_delay_s > event.duration_s:
                    session.quality['invalid_native_first_token_delay'] += 1
                    event.native_first_token_delay_s = None
                session.events.append(event); turn_events.append((key, event))
            elif sub == 'item_completed':
                item = p.get('item', {})
                if not isinstance(item, dict):
                    continue
                key = (p.get('thread_id'), item.get('id'))
                if not all(part is None or isinstance(part,str) for part in key):
                    session.quality['malformed_item_ids'] += 1
                    continue
                if key[1] and key in seen_items:
                    session.quality['duplicate_items'] += 1
                    continue
                seen_items.add(key)
                kinds = {'CommandExecution': 'shell', 'FileChange': 'edit', 'McpToolCall': 'mcp',
                         'ImageView': 'image', 'CollabAgentToolCall': 'subagent',
                         'SubAgentActivity': 'subagent_activity', 'ContextCompaction': 'compaction',
                         'Reasoning': 'reasoning_item', 'AgentMessage': 'message_item'}
                cat = kinds.get(item.get('type')) if isinstance(item.get('type'),str) else None
                if cat:
                    start = timestamp(p.get('started_at_ms')); end = timestamp(p.get('completed_at_ms'))
                    start = start/1000 if start is not None else None
                    end = end/1000 if end is not None else None
                    if cat == 'shell':
                        cat = command_category(item.get('command'))
                    session.events.append(Event('item', start, end, cat,
                                                outcome(item.get('status'), item.get('exit_code'))))
        elif typ not in ('response_item', 'world_state'):
            session.quality['unknown_record_types'] += 1
    session.events.extend(pending.values())
    session.quality['incomplete_tools'] += len(pending)
    for key, start in turns.items():
        session.events.append(Event('turn', start, None, 'turn', 'incomplete', turn_key=key))
    session.quality['incomplete_turns'] += len(turns)
    session.turn_keys = completed_turns | set(turns)
    # Never correlate by a preceding tool return or token-record timestamp.
    # TurnContext is an initial configuration snapshot, not backend identity.
    for response, (key, turn_id) in zip(session.responses, response_turns):
        if key in ambiguous_response_keys:
            response.turn_key = None
        configs = contexts.get(turn_id, set()) if isinstance(turn_id, str) else set()
        if len(configs) == 1 and key[1] not in compaction_responses and key not in ambiguous_response_keys:
            response.turn_model, response.turn_effort = next(iter(configs))
            response.configuration_scope = 'initial_turn_snapshot'
        else:
            session.quality['ambiguous_or_missing_response_configuration'] += 1
    for key, event in turn_events:
        configs = contexts.get(key, set())
        if len(configs) == 1:
            event.model, event.effort = next(iter(configs))
        elif len(configs) > 1:
            session.quality['ambiguous_turn_configuration'] += 1
    for e in session.events:
        if e.start is not None and e.end is not None and e.end < e.start:
            session.quality['negative_intervals'] += 1
            e.end = None
    if seen_responses:
        session.response_keys = set(seen_responses)
        session.usage_method = 'unique response usage; thread totals cross-check'
        session.tokens = {k: response_sums[k] if fields_seen[k] == len(seen_responses) else None for k in TOKENS}
        session.quality['responses'] = len(seen_responses)
        for thread, total in final_thread.items():
            if not total:
                session.quality['missing_thread_usage_crosscheck'] += 1
            sums = Counter()
            for (tid, _), usage in seen_responses.items():
                if tid == thread:
                    sums.update(usage)
            if any(total[k] != sums[k] for k in total):
                session.quality['response_thread_total_mismatch'] += 1
        if session.quality['response_thread_total_mismatch']:
            session.usage_method += ' (incomplete/inherited scope)'
        elif session.quality['missing_thread_usage_crosscheck']:
            session.usage_method += ' (cross-check unavailable)'
    else:
        session.usage_method = ('cumulative differences; first/reset baselines excluded (incomplete)'
                                if cumulative else 'unavailable')
        session.tokens = {k: cumulative_sums[k] if cumulative_fields[k] else None for k in TOKENS}
    return session


def native_capture(paths, sessions=(), explicit_scope=False):
    """Read only allowlisted local captures; join spans structurally, never by time.

    Qualified producer family: stream_request is the client.stream entry; the receiving
    child of a completed handle_responses ends when completion reaches the core.
    This includes client preparation/transport/scheduling, not just backend work.
    Native log TTFT starts later and must not be subtracted from this interval.
    """
    from performance.telemetry import pseudonym
    issues = Counter(); spans = {}; conflicts = set(); allowed = set(); logs = []
    total_records = 0
    for path in paths:
        if total_records >= MAX_EVENTS:
            issues['native_record_limit'] += 1; break
        try:
            meta = json.loads((path/'capture.json').read_text())
            if meta.get('schema') != 1 or meta.get('source') != 'codex-native-otel':
                raise ValueError()
            key = bytes.fromhex(meta['key'])
            if len(key) != 32 or (path/'records.jsonl').stat().st_size > 16*1024*1024:
                raise ValueError()
            allowed.update(pseudonym(ident, key, 'session') for s in sessions for ident in s.source_ids)
            if meta.get('active'):
                issues['capture_snapshot'] += 1
            issues['capture_limit_reached'] += meta.get('counts', {}).get('limit_reached', 0)
            issues['capture_rejected_batches'] += meta.get('counts', {}).get('rejected_batches', 0)
        except (OSError, ValueError, KeyError, TypeError):
            issues['unreadable_or_unsupported_capture'] += 1
            continue
        for n, row in enumerate(records(path/'records.jsonl', issues)):
            if total_records >= MAX_EVENTS:
                issues['native_record_limit'] += 1; break
            total_records += 1
            if row.get('type') == 'span':
                ident = (row.get('trace_key'), row.get('span_key'))
                if not all(isinstance(v, str) and re.fullmatch(r'[0-9a-f]{32}', v) for v in ident):
                    issues['unkeyed_native_span'] += 1; continue
                if ident in spans:
                    issues['duplicate_native_spans'] += 1
                    if spans[ident] != row:
                        conflicts.add(ident); issues['conflicting_native_spans'] += 1
                else:
                    spans[ident] = row
            elif row.get('type') == 'log':
                logs.append(row)
    for ident in conflicts:
        spans.pop(ident, None)
    children = {}
    for ident, row in spans.items():
        children.setdefault((ident[0], row.get('parent_key')), []).append(row)
    def session_keys(row):
        result = set(); seen = set()
        for _ in range(64):
            if not row: break
            ident = (row.get('trace_key'), row.get('span_key'))
            if ident in seen:
                issues['native_ancestor_cycle'] += 1; break
            seen.add(ident)
            result.update(r['session_key'] for r in [row]+row.get('events', []) if r.get('session_key'))
            row = spans.get((ident[0], row.get('parent_key')))
        return result
    def eligible(row):
        keys = session_keys(row) if row.get('type') == 'span' else {row.get('session_key')}
        return explicit_scope if not sessions else len(keys) == 1 and bool(keys & allowed)
    requests = []
    for root in spans.values():
        if root.get('name') != 'try_run_sampling_request' or not eligible(root): continue
        versions = {r['version'] for r in [root]+root.get('events', []) if r.get('version')}
        version = next(iter(versions)) if len(versions) == 1 else 'unknown'
        version_support = native_version_compatibility(version)
        direct = children.get((root['trace_key'], root['span_key']), [])
        starts = [r for r in direct if r.get('name') == 'stream_request']
        streams = [r for r in direct if r.get('name') == 'receiving_stream']
        completions = [r for stream in streams for r in children.get((stream['trace_key'], stream['span_key']), [])
                       if r.get('name') == 'handle_responses' and any(k in r for k in
                           ('gen_ai.usage.input_tokens','gen_ai.usage.output_tokens','codex.usage.reasoning_output_tokens'))]
        req = {'label': f'native-request-{len(requests)+1}', 'start': None, 'end': None,
               'duration_s': None, 'output_tokens_per_s': None, 'tokens': {},
               'first_observable_delta_delay_s': None,
               'model': model_name(root.get('model')), 'effort': 'unknown', 'version': version,
               'version_qualification': version_support or 'unsupported',
               'outcome': 'failed' if root.get('error_status') else 'incomplete_or_unassociated',
               'association': 'selected_session_key' if sessions else 'explicit_capture_scope'}
        # Installed exports omit the non-completion handle_responses event kind.
        # Do not identify text/reasoning deltas from generic receiving spans.
        if version_support is None:
            issues['unsupported_native_version'] += 1
        elif len(starts) != 1 or len(streams) != 1 or len(completions) != 1:
            issues['missing_or_ambiguous_native_boundaries'] += 1
        else:
            complete = completions[0]
            receiving = [r for r in children.get((complete['trace_key'], complete['span_key']), []) if r.get('name') == 'receiving']
            a = nonnegative(starts[0].get('start'))
            b = nonnegative(receiving[0].get('end')) if len(receiving) == 1 else None
            root_start = nonnegative(root.get('start')); root_end = nonnegative(root.get('end'))
            if a is None or b is None or b < a or root_start is None or root_end is None or not (root_start <= a <= b <= root_end):
                issues['invalid_or_missing_native_timestamps'] += 1
            else:
                req.update(start=a, end=b, duration_s=b-a, outcome='completed')
                req['effort'] = effort_name(complete.get('codex.request.reasoning_effort'))
                for source, target in [('gen_ai.usage.input_tokens', 'input_tokens'),
                                       ('gen_ai.usage.cache_read.input_tokens', 'cached_input_tokens'),
                                       ('gen_ai.usage.output_tokens', 'output_tokens'),
                                       ('codex.usage.reasoning_output_tokens', 'reasoning_output_tokens')]:
                    value = nonnegative(complete.get(source))
                    if value is not None and value.is_integer(): req['tokens'][target] = int(value)
                req['output_tokens_per_s'] = request_metrics(b-a, None, req['tokens'])['output_tokens_per_s']
                if version_support == 'compatible_patch_structure':
                    issues['patch_compatible_native_requests'] += 1
                if b == a: issues['zero_native_duration'] += 1
        requests.append(req)
    native_delays = []; completion_logs = 0; seen_logs = set(); attempts = []; errors = 0
    for row in logs:
        if not eligible(row): continue
        # Identical retransmitted log observations are counted once. Equal usage
        # without timestamp identity remains separate and cannot join to requests.
        identity = json.dumps(row, sort_keys=True)
        if identity in seen_logs and row.get('at') is not None:
            issues['duplicate_native_logs'] += 1; continue
        seen_logs.add(identity)
        errors += bool(row.get('has_error') or row.get('success') is False)
        if row.get('event_name') in ('codex.api_request', 'codex.websocket_request'):
            attempts.append({'duration_s': (v/1000 if (v := nonnegative(row.get('duration_ms'))) is not None else None),
                             'attempt': nonnegative(row.get('attempt')), 'failed': bool(row.get('has_error') or row.get('success') is False)})
        if row.get('event_name') == 'codex.sse_event' and row.get('event_kind') == 'response.completed' and 'output_token_count' in row:
            completion_logs += 1
            support = native_version_compatibility(row.get('version'))
            if support is not None and (delay := nonnegative(row.get('ttft_ms'))) is not None:
                native_delays.append(delay/1000)
                if support == 'compatible_patch_structure':
                    issues['patch_compatible_native_first_item_logs'] += 1
    return {'requests': requests, 'quality': dict(issues), 'native_stream_first_item_delays': native_delays,
            'native_completion_logs': completion_logs, 'transport_attempts': attempts, 'error_notices': errors,
            'scope': 'selected sessions by structured session key' if sessions else 'explicitly selected capture; not a modeling-task association'}
