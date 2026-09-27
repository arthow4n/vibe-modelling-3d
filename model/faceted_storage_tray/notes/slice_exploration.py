"""Reference smoke slice each final alternative; run from the repository root."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess
import sys
root = Path(__file__).resolve().parent.parent
repo = root.parents[1]
configs = json.loads((root/'notes/variants.json').read_text())
def run(config):
    name = config['name']
    folder = root/'variants'/name
    command = [sys.executable,str(repo/'.codex/skills/orca-slicer-printability/scripts/review_print.py'),
               '--model',str(folder/(name+'.stl'))]
    job = subprocess.run(command,capture_output=True,text=True)
    print(name,job.returncode,job.stdout.strip(),job.stderr.strip(),flush=True)
    if job.returncode:
        raise RuntimeError(name)
with ThreadPoolExecutor(max_workers=2) as pool:
    list(pool.map(run,configs))
