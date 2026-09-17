"""Reference smoke slice each exterior coupon; run from repository root."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
repo = root.parents[1]
configs = json.loads((root / 'notes/variants.json').read_text())

def run(config):
    name = config['name']
    folder = root / 'test_pieces' / name
    command = [
        sys.executable,
        str(repo / '.codex/skills/prusa-slicer-printability/scripts/review_print.py'),
        '--model', str(folder / f'{name}_coupon.stl'),
        '--profile', str(root / 'notes/review.ini'),
        '--out', str(folder / 'slice_review'),
        '--bed', '250', '250', '250',
        '--expect-no-supports',
    ]
    job = subprocess.run(command, capture_output=True, text=True)
    print(name, job.returncode, job.stdout.strip(), job.stderr.strip(), flush=True)
    if job.returncode:
        raise RuntimeError(name)

with ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(run, configs))
