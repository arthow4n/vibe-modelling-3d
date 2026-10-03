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

    def normalized(self):
        return dict(events=[asdict(e) for e in self.events], tokens=self.tokens,
                    quality=dict(self.quality), start=self.start, end=self.end,
                    usage_method=self.usage_method, version=self.version,
                    models=sorted(self.models), modes=sorted(self.modes), subagent=self.subagent)


def parse(path):
    session = Session()
    pending = {}; seen_calls = set(); seen_items = set(); seen_responses = {}
    response_sums = Counter(); fields_seen = Counter(); final_thread = {}
    cumulative = {}; cumulative_sums = Counter(); cumulative_fields = Counter()
    turns = {}; completed_turns = set()
    for record in records(path, session.quality):
        if len(session.events) >= MAX_EVENTS or len(seen_responses) >= MAX_EVENTS:
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
            session.start = min(session.start, t) if session.start is not None else t
            session.end = max(session.end, t) if session.end is not None else t
        sub = p.get('type')
        if typ == 'session_meta':
            v = str(p.get('cli_version', ''))
            session.version = v if re.fullmatch(r'\d+\.\d+\.\d+', v) else 'unknown'
            session.subagent = isinstance(p.get('source'), dict) and 'subagent' in p['source']
            if p.get('forked_from_id'):
                session.quality['forked_session_inherited_usage_possible'] += 1
        elif typ == 'turn_context':
            model = p.get('model', '')
            if isinstance(model, str) and re.fullmatch(r'(?:gpt-\d+(?:\.\d+)?o?(?:-(?:sol|astra|luna|mini|nano|codex|pro|turbo|max))*|o\d+(?:-mini)?)', model):
                session.models.add(model)
            mode = p.get('collaboration_mode', {})
            if isinstance(mode, dict) and mode.get('mode') in ('default', 'plan'):
                session.modes.add(mode['mode'])
        elif typ == 'token_usage_record':
            key = (p.get('thread_id'), p.get('response_id'))
            if not all(isinstance(part,str) and part for part in key):
                session.quality['unkeyed_response_usage'] += 1
                continue
            usage = counters(p.get('usage'))
            if not key[0] or not key[1] or not usage:
                session.quality['unkeyed_response_usage'] += 1
                continue
            if key in seen_responses:
                session.quality['duplicate_response_usage'] += 1
                if seen_responses[key] != usage:
                    session.quality['conflicting_response_usage'] += 1
                continue
            seen_responses[key] = usage
            response_sums.update(usage); fields_seen.update(usage.keys())
            final_thread[key[0]] = counters(p.get('thread_token_usage'))
        elif typ == 'compacted':
            session.quality['compactions'] += 1
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
            if sub == 'token_count':
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
                session.events.append(Event('turn', start, end, 'turn',
                                            'interrupted' if sub == 'turn_aborted' else 'completed'))
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
    for start in turns.values():
        session.events.append(Event('turn', start, None, 'turn', 'incomplete'))
    session.quality['incomplete_turns'] += len(turns)
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
