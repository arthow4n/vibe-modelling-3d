"""Analyze retained execution summaries or export overlapping OTLP spans to Perfetto."""
import argparse
import json
import statistics
from pathlib import Path
from .telemetry import data_root


def iter_records(root=None):
    """Read retained summaries without changing them; malformed files are skipped.

    Consumers needing completeness counts should compare yielded files with the
    directory inventory. Records retain unrestricted local source identities.
    """
    for path in sorted(((root or data_root())/'runs').glob('*.json')):
        try:
            record = json.loads(path.read_text())
            if isinstance(record, dict):
                yield record
        except (OSError, ValueError):
            continue


def iter_spans(root=None, trace_ids=None):
    """Stream the existing OTLP format, optionally selecting exact trace IDs."""
    for path in sorted(((root or data_root())/'traces').glob('*.otlp.jsonl')):
        try:
            with path.open() as stream:
                for line in stream:
                    try:
                        for resource in json.loads(line).get('resourceSpans', []):
                            for scope in resource.get('scopeSpans', []):
                                for span in scope.get('spans', []):
                                    if trace_ids is None or span.get('traceId') in trace_ids:
                                        yield resource.get('resource', {}), span
                    except (ValueError, TypeError, AttributeError):
                        continue
        except OSError:
            continue


def perfetto_event(resource, span):
    """Convert one existing engineering span; callers may redact names/IDs."""
    attrs = {a['key']: a['value'] for a in resource.get('attributes', [])}
    attributes = {a['key']: a['value'] for a in span.get('attributes', [])}
    return dict(name=span['name'], cat='engineering', ph='X',
                pid=attrs.get('process.pid', {}).get('intValue', 0),
                tid=attributes.get('thread.id', {}).get('intValue', 0),
                ts=int(span['startTimeUnixNano'])/1000,
                dur=(int(span['endTimeUnixNano'])-int(span['startTimeUnixNano']))/1000,
                args=dict(trace_id=span['traceId'], span_id=span['spanId'],
                          parent_span_id=span.get('parentSpanId')))


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--last', type=int, default=20)
    p.add_argument('--perfetto', type=Path)
    p.add_argument('--run')
    p.add_argument('--incomplete',action='store_true')
    p.add_argument('--stats',action='store_true',help='Compare grouped historical latency without rerunning work')
    p.add_argument('--compare',nargs=2,metavar=('RUN_A','RUN_B'))
    args = p.parse_args(argv)
    if args.incomplete:
        files=list((data_root()/'jobs').glob('*.json'))
        from .lifecycle import process_identity
        records=[]
        for path in files:
            d=json.loads(path.read_text())
            if d['status'] not in ('queued','running','interrupted','failed','timeout'):continue
            if d['status'] in ('queued','running'):
                try:alive=process_identity(d['owner_pid'])==d.get('owner_identity')
                except (ProcessLookupError,OSError):alive=False
                if not alive:d['observed_status']='owner_lost'
            records.append(d)
        print(json.dumps(records,indent=2))
        return 0
    if args.compare:
        records=[json.loads((data_root()/'runs'/f'{id}.json').read_text()) for id in args.compare]
        keys=('source_sha256','repository_python_sha256','lock_sha256','arguments_sha256','strategy')
        a,b=records
        print(json.dumps(dict(runs=args.compare,matching_inputs=all(a.get(k)==b.get(k) for k in keys),
            changed_fields=[k for k in keys if a.get(k)!=b.get(k)],
            elapsed_seconds=[r.get('elapsed_seconds') for r in records],statuses=[r.get('status') for r in records]),indent=2))
        return 0
    if args.perfetto:
        events=[]
        selected_trace=None
        if args.run:
            summary=data_root()/'runs'/f'{args.run}.json'
            if summary.exists():selected_trace=json.loads(summary.read_text()).get('trace_id')
        selected = {selected_trace} if selected_trace else (set() if args.run else None)
        events = [perfetto_event(resource, s) for resource, s in iter_spans(trace_ids=selected)]
        args.perfetto.write_text(json.dumps({'traceEvents':events}))
        return 0
    files=sorted((data_root()/'runs').glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:args.last]
    records=[json.loads(p.read_text()) for p in files]
    if args.stats:
        groups={}
        for r in records:
            key=(r.get('operation'),r.get('strategy'),r.get('source_sha256'),r.get('repository_python_sha256'))
            groups.setdefault(key,[]).append(r)
        records=[dict(operation=k[0],strategy=k[1],source_sha256=k[2],repository_python_sha256=k[3],runs=len(rows),
            statuses={s:sum(r.get('status')==s for r in rows) for s in {r.get('status') for r in rows}},
            median_seconds=statistics.median(times) if (times:=[r['elapsed_seconds'] for r in rows if 'elapsed_seconds' in r]) else None)
            for k,rows in groups.items()]
    print(json.dumps(records,indent=2))
    return 0
if __name__ == '__main__': raise SystemExit(main())
