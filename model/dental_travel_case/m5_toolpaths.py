"""Review primary bridges and support locations in retained M5 diagnostic runs."""
from pathlib import Path
import sys
from m3_joint_toolpaths import inspect

if __name__=='__main__':
    if len(sys.argv)!=3 or sys.argv[1] not in ('case','joint'):
        raise SystemExit('Usage: m5_toolpaths.py {case|joint} RETAINED_DIRECTORY')
    inspect(Path(sys.argv[2]),output=Path(__file__).resolve().parent/'notes/m5'/f'{sys.argv[1]}_toolpaths.svg')
