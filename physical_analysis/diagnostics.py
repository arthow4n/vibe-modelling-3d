"""Read saved contact evidence without rebuilding or rerunning an analysis."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from .backends.structural import runtime_environment


def contact_frames(directory, fractions=None, *, rigid_parts=()):
    """Locate face-to-face contact at existing saved fractions.

    Optionally compare deformed slave-face samples with saved CAD for explicitly
    named rigid parts. Their recorded nodal motion must be a uniform translation.
    Omit fractions to inspect the saved frame with greatest reported penetration.
    Numerical gaps and sampled CAD distances are distinct evidence; neither
    replaces the original quality screen. Raw native fields must still exist.
    Explicit accepted fractions may use frozen run metadata before a final
    result exists; this never infers completion or writes a result file.
    Native imports and solver-specific field handling stay in an isolated worker.
    """
    request = dict(directory=str(Path(directory).resolve()),
                   fractions=None if fractions is None else list(fractions), rigid_parts=list(rigid_parts))
    code = ('import json,sys; '
            'from physical_analysis.backends.contact_diagnostics import contact_frames; '
            'print(json.dumps(contact_frames(**json.load(sys.stdin)),allow_nan=False))')
    run = subprocess.run([sys.executable, '-c', code], input=json.dumps(request),
                         env=runtime_environment(), capture_output=True, text=True)
    if run.returncode:
        raise ValueError('Contact diagnostics failed: '+run.stderr.strip())
    return json.loads(run.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--fractions', nargs='+', type=float)
    parser.add_argument('--rigid-parts', nargs='*', default=[])
    args = parser.parse_args()
    answer = contact_frames(args.run, args.fractions, rigid_parts=args.rigid_parts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(answer, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(output=str(args.output), frames=len(answer['frames']),
                          input_sha256=answer['input_sha256'])))


if __name__ == '__main__':
    main()
