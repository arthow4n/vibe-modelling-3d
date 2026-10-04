"""Attribute reviewed whole turns to repository objects; local evidence only.

A manifest is an analyst's task association, never an automatic path-frequency
classifier. Reuses qualified usage and native request adapters without estimates.
"""
import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from performance.sessions import TOKENS, parse, native_capture, metadata, belongs
from performance.workflow import local_directory, model_latency, measurement, union


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def token_totals(responses):
    return {k: sum(r.tokens[k] for r in responses) if responses and all(k in r.tokens for r in responses) else None for k in TOKENS}


def select_turns(session, indices):
    """Select explicit turn ownership, never usage timestamps or prorated totals."""
    if indices == 'all':
        return session, set(session.turn_order)
    if not isinstance(indices, list) or not indices or any(type(i) is not int or not 1 <= i <= len(session.turn_order) for i in indices) or len(set(indices)) != len(indices):
        raise ValueError('Select distinct existing 1-based turn indices or all')
    keys = {session.turn_order[i-1] for i in indices}
    responses = [r for r in session.responses if r.turn_key in keys]
    selected = replace(session, responses=responses, tokens=token_totals(responses),
                       response_keys={r.usage_key for r in responses},
                       events=[e for e in session.events if e.kind == 'turn' and e.turn_key in keys],
                       turn_keys=keys, usage_method='selected unique response usage' if session.responses else 'unavailable: partial legacy session')
    return selected, keys


def attribute(manifest, repo=ROOT, captures=()):
    entries = manifest.get('entries')
    if manifest.get('schema') != 1 or not isinstance(entries, list) or not 1 <= len(entries) <= 100:
        raise ValueError('Manifest requires schema 1 and 1..100 reviewed entries')
    sources = {}; fingerprints = {}; rows = []; allocated = set(); usage_owners = set(); turn_owners = {}; native_by_source = {}
    for entry in entries:
        object_path = Path('model')/entry['object']
        target = (repo/object_path).resolve()
        if not target.is_relative_to((repo/'model').resolve()) or not target.is_dir() or len(object_path.parts) != 2:
            raise ValueError('Object must name an existing model directory')
        if entry.get('scope') not in ('direct', 'mixed', 'follow_up', 'integration'):
            raise ValueError('Scope must be direct, mixed, follow_up or integration')
        if not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ('milestone', 'outcome')):
            raise ValueError('Each entry needs an established milestone and outcome')
        evidence = []
        for ref in entry.get('evidence', []):
            path = Path(ref); actual = (repo/path).resolve()
            if path.is_absolute() or not actual.is_relative_to(repo.resolve()) or not actual.is_file():
                raise ValueError('Evidence must be an existing repository-relative file')
            evidence.append({'path': str(path), 'sha256': digest(actual)})
        if not evidence:
            raise ValueError('At least one engineering evidence reference is required')
        selections = entry.get('selections', [])
        if not selections or len(selections) > 100:
            raise ValueError('Each entry needs 1..100 selections')
        chosen = []; links = []; requests = []; selected_windows = []; source_quality = Counter()
        for selection in selections:
            if not isinstance(selection.get('basis'), str) or not selection['basis'].strip():
                raise ValueError('Each selection needs a reviewed association basis')
            path = Path(selection['session']).resolve()
            if path not in sources:
                if len(sources) >= 100 or not belongs(metadata(path), repo):
                    raise ValueError('Select at most 100 repository-associated sessions')
                fingerprints[path] = digest(path)
                session = parse(path)
                if session.subagent or session.quality['forked_session_inherited_usage_possible']:
                    raise ValueError('Related forks/subagents require separate ownership review; excluded here')
                sources[path] = session
                selected_captures = [Path(p) for p in manifest.get('telemetry', {}).get(str(path), captures)]
                if len(selected_captures) > 20:
                    raise ValueError('Select at most 20 native bundles per source')
                native_by_source[path] = native_capture(selected_captures, [session]) if selected_captures else {'requests': [], 'quality': {}}
                native_by_source[path]['selected_capture_count'] = len(selected_captures)
            if selection.get('source_sha256_at_selection', fingerprints[path]) != fingerprints[path]:
                raise ValueError('Source differs from reviewed selection fingerprint; review turn ownership again')
            session = sources[path]
            subset, keys = select_turns(session, selection['turns'])
            # Whole-session scopes also reserve responses whose turn is unavailable.
            reservations = {(path, k) for k in keys} | ({(path, '__whole_session__')} if selection['turns'] == 'all' else set())
            if reservations & allocated or (path, '__whole_session__') in allocated:
                raise ValueError('A source turn cannot be charged to multiple entries')
            if selection['turns'] == 'all' and any(p == path for p, _ in allocated):
                raise ValueError('Whole-session selection overlaps previously allocated turns')
            if subset.response_keys & usage_owners:
                raise ValueError('Shared response histories: exclude inherited/duplicate selections')
            if any(key in turn_owners and turn_owners[key] != path for key in keys):
                raise ValueError('Shared turn histories: exclude inherited/duplicate selections')
            turn_owners.update({key:path for key in keys})
            allocated.update(reservations); usage_owners.update(subset.response_keys)
            chosen.append(subset); source_quality.update(session.quality)
            windows = [(e.start, e.end) for e in subset.events if e.kind == 'turn' and e.start is not None and e.end is not None]
            selected_windows.extend(windows)
            native = native_by_source[path]
            measured = []
            for request in native['requests']:
                if request['start'] is None or request['end'] is None:
                    continue
                owners = [e for e in session.events if e.kind == 'turn' and e.start is not None and e.end is not None
                          and e.start <= request['start'] and request['end'] <= e.end]
                if len(owners) == 1 and (selection['turns'] == 'all' or owners[0].turn_key in keys):
                    measured.append(request)
            requests.extend(measured)
            links.append({'source': list(sources).index(path)+1, 'turns': selection['turns'], 'basis': selection['basis'],
                          'usage_method': subset.usage_method, 'native_association': 'structured session key and unique full turn containment; reviewed task association',
                          'source_native_candidates': len(native['requests']), 'selected_native_requests': len(measured),
                          'source_native_capture_count': native['selected_capture_count'],
                          'source_native_quality': native['quality']})
        latency = model_latency(chosen)
        totals = {k: sum(s.tokens[k] for s in chosen) if all(s.tokens.get(k) is not None for s in chosen) else None for k in TOKENS}
        uncached = totals['input_tokens']-totals['cached_input_tokens'] if totals['input_tokens'] is not None and totals['cached_input_tokens'] is not None and totals['input_tokens'] >= totals['cached_input_tokens'] else None
        legacy = any('cumulative' in s.usage_method or 'legacy' in s.usage_method for s in chosen)
        coverage = latency['token_measurements'] if not legacy else {
            k:dict(value=value, quality='derived incomplete' if value is not None else 'unavailable', eligible=None, measured=None,
                   scope='includes legacy cumulative differences; response coverage unavailable')
            for k,value in dict(totals, uncached_input_tokens=uncached).items()}
        rows.append(dict(object=entry['object'], scope=entry['scope'], milestone=entry['milestone'], outcome=entry['outcome'],
                         evidence=evidence, selections=links, tokens=totals, uncached_input_tokens=uncached,
                         response_count=latency['response_count'] if not legacy and any(s.responses for s in chosen) else None, token_coverage=coverage,
                         configurations=latency['configured_turn_groups'], versions=sorted({s.version for s in chosen}),
                         selected_turn_count=sum(len(s.events) if s.usage_method.startswith('selected') else sum(e.kind == 'turn' for e in s.events) for s in chosen),
                         measured_turn_union_s=union(selected_windows),
                         native=dict(request_count=len(requests), operation_union_s=union([(r['start'], r['end']) for r in requests]) if requests else None,
                                     duration=measurement([r['duration_s'] for r in requests], len(requests), 'derived'),
                                     throughput=measurement([r['output_tokens_per_s'] for r in requests], len(requests), 'derived', 'tokens/s'),
                                     tokens={k:sum(r['tokens'][k] for r in requests) if requests and all(k in r['tokens'] for r in requests) else None for k in TOKENS},
                                     configurations=sorted({(r['model'], r['effort']) for r in requests})),
                         source_quality=dict(source_quality)))
    inventory = []
    for path, session in sources.items():
        if digest(path) != fingerprints[path]:
            raise ValueError('Source changed during analysis; retry a stable snapshot')
        source_index = list(sources).index(path)+1
        assigned = {k for p, k in allocated if p == path}
        unassigned = [] if '__whole_session__' in assigned else [r for r in session.responses if r.turn_key not in assigned]
        inventory.append(dict(source=source_index, path=str(path), sha256=fingerprints[path], start=session.start, end=session.end,
                              turn_count=len(session.turn_order), responses=len(session.responses),
                              unassigned_response_count=len(unassigned), unassigned_tokens=token_totals(unassigned), quality=dict(session.quality)))
    return dict(schema=1, entries=rows, sources=inventory,
                analyzer_sha256={f: digest(ROOT/'performance'/f) for f in ('attribution.py', 'sessions.py', 'workflow.py', 'telemetry.py')},
                limitations=['Reviewed task association; not exhaustive lifetime cost or billing.',
                             'Input includes carried conversation/context; cached input is an input subset and reasoning an output subset.',
                             'Mixed/shared work is separate and never proportionally allocated.',
                             'Native timing describes captured client request operations, not backend inference or visible-text speed.',
                             'Native completion usage is separate from rollout accounting; rates use each request own output and duration.',
                             'Turn time includes tools/waiting; missing capture or boundary is unavailable, never zero.'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, help='Reviewed local manifest; contains private source locations')
    parser.add_argument('--repo', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.manifest.stat().st_size > 1024*1024:
        parser.error('Manifest exceeds 1 MiB')
    directory = local_directory(Path(os.environ.get('ENGINEERING_DATA', args.repo/'.execution')), args.repo)
    captures = sorted((p for p in directory.glob('otel-*') if p.is_dir()), key=lambda p:p.stat().st_mtime, reverse=True)[:20]
    try:
        result = attribute(json.loads(args.manifest.read_text()), args.repo, captures)
    except (ValueError, KeyError, TypeError) as error:
        parser.error(str(error))
    encoded = json.dumps(result, sort_keys=True, indent=2)
    if len(encoded.encode()) > 16*1024*1024:
        parser.error('Attribution output exceeds 16 MiB')
    target = directory/f'attribution-{hashlib.sha256(encoded.encode()).hexdigest()[:16]}.json'
    if not target.exists():
        with target.open('x') as stream:
            stream.write(encoded)
        target.chmod(0o600)
    reports = [p for p in directory.glob('attribution-*.json') if re.fullmatch(r'attribution-[0-9a-f]{16}\.json', p.name)]
    for old in sorted(reports, key=lambda p:p.stat().st_mtime, reverse=True)[20:]:
        old.unlink()
    print(json.dumps({'local_report':str(target), 'entries':len(result['entries']), 'sources':len(result['sources'])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
