"""Analyze retained execution summaries or export overlapping OTLP spans to Perfetto."""
import argparse
import json
import statistics
from pathlib import Path
from .telemetry import data_root


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
        for path in (data_root()/'traces').glob('*.otlp.jsonl'):
            if args.run and not selected_trace and not path.name.startswith(args.run):continue
            for line in path.read_text().splitlines():
                if selected_trace and selected_trace not in line:continue
                for resource in json.loads(line).get('resourceSpans', []):
                    attributes = {a['key']: a['value'] for a in resource['resource'].get('attributes', [])}
                    pid = attributes.get('process.pid', {}).get('intValue', 0)
                    for scope in resource.get('scopeSpans', []):
                        for s in scope.get('spans', []):
                            if selected_trace and s['traceId']!=selected_trace:continue
                            attributes={a['key']:a['value'] for a in s.get('attributes',[])}
                            events.append(dict(name=s['name'],cat='engineering',ph='X',pid=pid,tid=attributes.get('thread.id',{}).get('intValue',0),
                                ts=int(s['startTimeUnixNano'])/1000,
                                dur=(int(s['endTimeUnixNano'])-int(s['startTimeUnixNano']))/1000,
                                args=dict(trace_id=s['traceId'],span_id=s['spanId'],parent_span_id=s.get('parentSpanId'))))
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
