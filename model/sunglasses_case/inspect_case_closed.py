"""Evaluate the current case closed; never replace the print-ready exports."""
from pathlib import Path
import runpy
ROOT=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/inspect_case_closed.py')).resolve().parent
model=runpy.run_path(str(ROOT/'sunglasses_case.py'),init_globals={'LAYOUT':'closed','EXPORT':False})
result=model['result']
