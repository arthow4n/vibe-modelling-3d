#!/usr/bin/env python3
"""Run ordinary Python files through the shared engineering environment."""
from execution.bootstrap import ensure
if __name__=='__main__':ensure()
import argparse
import json
import math
import sys
from execution.client import script


def positive(value):
    number=float(value)
    if not math.isfinite(number) or number<=0:raise argparse.ArgumentTypeError('Expected a finite positive value')
    return number


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cwd')
    p.add_argument('--restart',help='Explicitly restart a retained run with the same script/arguments; never automatic')
    p.add_argument('--strategy',choices=['isolated','preinitialized'],default='isolated')
    p.add_argument('--preload',choices=['scientific','cad'],default='scientific')
    p.add_argument('--timeout',type=positive)
    p.add_argument('--threads',default='50%',help='Integer or percent of shared CPU capacity; default 50%')
    p.add_argument('--memory-mb',type=int,default=2048)
    p.add_argument('--profile',choices=['cpu','allocations'])
    p.add_argument('--isolated',action='store_true',help='Bypass coordinator using the same traced lifecycle')
    p.add_argument('script')
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    args=p.parse_args(argv)
    from execution.resources import cores,cpu_capacity
    try:args.threads=cores(args.threads,cpu_capacity())
    except ValueError as exc:p.error(str(exc))
    if args.memory_mb<1:p.error('Memory budget must be positive')
    try:
        if args.restart:
            from execution.journal import check_restart
            check_restart(args.restart,args.script,args.arguments)
        answer=script(args.script,args.arguments,cwd=args.cwd,strategy=args.strategy,preload=args.preload,
            timeout=args.timeout,threads=args.threads,memory_mb=args.memory_mb,profile=args.profile,coordinator=not args.isolated)
        if answer.get('error'):print(answer['error'],file=sys.stderr)
        return answer['exit_code'] if answer['exit_code']>=0 else 128-answer['exit_code']
    except KeyboardInterrupt:return 130
    except Exception as exc:print(f'Execution failed: {exc}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
