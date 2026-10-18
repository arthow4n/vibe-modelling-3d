"""Review the current full or sample bridges/supports using the existing reader."""
from pathlib import Path
import sys
from m3_joint_toolpaths import inspect

ROOT=Path(__file__).resolve().parent

if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1] not in ('case','joint'):
        raise SystemExit('Usage: m4_toolpaths.py {case|joint} RETAINED_SLICE_DIRECTORY')
    inspect(Path(sys.argv[2]),output=ROOT/'notes/m4'/(sys.argv[1]+'_toolpaths.svg'))
