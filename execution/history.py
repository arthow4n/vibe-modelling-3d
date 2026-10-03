"""Analyze retained execution summaries or export overlapping OTLP spans to Perfetto."""
import argparse
import json
from pathlib import Path
from .telemetry import data_root


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--last', type=int, default=20)
    p.add_argument('--perfetto', type=Path)
    p.add_argument('--run')
    args = p.parse_args(argv)
    if args.perfetto:
        events=[]
        for path in (data_root()/'traces').glob(f'{args.run or "*"}*.otlp.jsonl'):
            for line in path.read_text().splitlines():
                for resource in json.loads(line).get('resourceSpans', []):
                    attributes = {a['key']: a['value'] for a in resource['resource'].get('attributes', [])}
                    pid = attributes.get('process.pid', {}).get('intValue', 0)
                    for scope in resource.get('scopeSpans', []):
                        for s in scope.get('spans', []):
                            events.append(dict(name=s['name'],cat='engineering',ph='X',pid=pid,tid=s.get('parentSpanId','root'),
                                ts=int(s['startTimeUnixNano'])/1000,
                                dur=(int(s['endTimeUnixNano'])-int(s['startTimeUnixNano']))/1000,
                                args=dict(trace_id=s['traceId'],span_id=s['spanId'])))
        args.perfetto.write_text(json.dumps({'traceEvents':events}))
        return 0
    files=sorted((data_root()/'runs').glob('*.json'),key=lambda p:p.stat().st_mtime,reverse=True)[:args.last]
    print(json.dumps([json.loads(p.read_text()) for p in files],indent=2))
    return 0
if __name__ == '__main__': raise SystemExit(main())
