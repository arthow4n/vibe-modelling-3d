"""Validate deliberately authored reviews, then create them without overwrite.

No transcript sanitizer or automatic publication. A human/agent must review the
text and its factual support first. Scanning is a secondary, imperfect safeguard.
"""
import argparse
from datetime import datetime
from pathlib import Path
import re
import sys
import uuid

SECTIONS = ('Scope','Measurements','Findings','Implications','Changes or recommendations','Verification and limitations')
PATTERNS = (
    r'/(?:home|Users|root)/', r'[A-Z]:\\Users\\', r'\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b',
    r'\b(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{8,}',
    r'\b(?:password|api[_-]?key|access[_-]?token|secret)\s*[:=]\s*\S+',
    r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
    r'\b(?:rollout-|session_id|response_id|thread_id|call_id|start_unix_ns|traceEvents|response_item|event_msg|token_usage_record)\b',
    r'\b[0-9a-f]{32}\b', r'Traceback \(most recent call last\)',
    r'"(?:arguments|payload|prompt|aggregated_output|base_instructions)"\s*:',
    r'https?://(?:localhost|127\.0\.0\.1|10\.|192\.168\.|[^/\s]+\.internal)',
)


def validate(text):
    errors=[]
    if len(text.encode())>32*1024:
        errors.append('Review exceeds 32 KiB')
    for section in SECTIONS:
        if not re.search(r'^'+re.escape(section)+r':\s*\S',text,re.M):
            errors.append('Missing section: '+section)
    for i,pattern in enumerate(PATTERNS):
        if re.search(pattern,text,re.I):
            errors.append(f'Potential sensitive content (rule {i+1}); inspect locally')
    return errors


def create_review(directory,subject,text,now=None):
    errors=validate(text)
    if errors:
        raise ValueError('; '.join(errors))
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',subject) or len(subject)>64:
        raise ValueError('Subject requires lowercase words separated by hyphens (<=64 characters)')
    directory.mkdir(parents=True,exist_ok=True)
    stem=(now or datetime.now().astimezone()).strftime('%Y-%m-%d-%H%M%S')+'-'+subject
    for attempt in range(10):
        path=directory/(stem+('' if attempt==0 else '-'+uuid.uuid4().hex[:6])+'.md')
        try:
            with path.open('x') as output:
                output.write(text)
            return path
        except FileExistsError:
            continue
    raise FileExistsError('Unable to reserve review filename')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draft',type=Path)
    parser.add_argument('--publish-reviewed',metavar='SUBJECT',help='Copy a deliberately reviewed draft to performance/reviews; never commit/push')
    args=parser.parse_args(argv)
    text=args.draft.read_text()
    errors=validate(text)
    if errors:
        print('\n'.join(errors));return 1
    if args.publish_reviewed:
        print(create_review(Path(__file__).resolve().parent/'reviews',args.publish_reviewed,text))
    else:
        print('Structure and recognizable-sensitive-content checks passed; factual/privacy review still required.')
    return 0


if __name__=='__main__':
    sys.exit(main())
