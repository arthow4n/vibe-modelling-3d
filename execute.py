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
    p.add_argument('--strategy',choices=['isolated','preinitialized'],default='isolated')
    p.add_argument('--preload',choices=['scientific','cad'],default='scientific')
    p.add_argument('--timeout',type=positive)
    p.add_argument('--threads',type=int,default=1)
    p.add_argument('--memory-mb',type=int,default=2048)
    p.add_argument('--profile',choices=['cpu','allocations'])
    p.add_argument('--isolated',action='store_true',help='Bypass coordinator using the same traced lifecycle')
    p.add_argument('script')
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    args=p.parse_args(argv)
    if args.threads<1 or args.memory_mb<1:p.error('Thread and memory budgets must be positive')
    try:
        answer=script(args.script,args.arguments,cwd=args.cwd,strategy=args.strategy,preload=args.preload,
            timeout=args.timeout,threads=args.threads,memory_mb=args.memory_mb,profile=args.profile,coordinator=not args.isolated)
        if answer.get('error'):print(answer['error'],file=sys.stderr)
        return answer['exit_code'] if answer['exit_code']>=0 else 128-answer['exit_code']
    except KeyboardInterrupt:return 130
    except Exception as exc:print(f'Execution failed: {exc}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
