"""Retain compact existing-run evidence; never launch or change an analysis."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
from .results import AnalysisResult
from .backends.structural import evidence_files


def retain_run(run, destination):
    """Archive a completed or failed CalculiX run to a new object-owned directory.

    Keep history/provenance unchanged and record only available replay artifacts.
    Large raw fields are excluded. Their omission does not remove them from run.
    No geometry, meshing, solver or result-extraction work is repeated.
    """
    run, destination = Path(run), Path(destination)
    result = AnalysisResult(**json.loads((run/'result.json').read_text()))
    if result.provenance.get('backend', 'CalculiX') != 'CalculiX':
        raise ValueError('Evidence retention currently supports CalculiX runs only')
    files, replay = evidence_files(run)
    destination.mkdir(parents=True, exist_ok=False)
    try:
        artifacts = {}
        for role, entries in files.items():
            multiple = isinstance(entries, list)
            saved = []
            for name, compress in entries if multiple else [entries]:
                source = run/name
                if not source.is_file():
                    continue
                target_name = name + ('.gz' if compress else '')
                target = destination/target_name
                if compress:
                    with source.open('rb') as src, target.open('wb') as dst:
                        with gzip.GzipFile(filename='', fileobj=dst, mode='wb', mtime=0) as zipped:
                            shutil.copyfileobj(src, zipped)
                else:
                    shutil.copyfile(source, target)
                saved.append(target_name)
            if saved:
                artifacts[role] = saved if multiple else saved[0]
        artifacts['raw_fields_retained'] = False
        if 'input' in artifacts:
            artifacts['reproduce'] = replay
        result.artifacts = artifacts
        result.write(destination/'result.json')
    except Exception:
        shutil.rmtree(destination)
        raise
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(retain_run(args.run, args.destination))


if __name__ == '__main__':
    main()
