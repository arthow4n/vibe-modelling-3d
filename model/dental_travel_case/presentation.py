"""Open inspection pose rotated for the renderer's Y-up camera. Not for printing."""
from pathlib import Path
import runpy
D=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/dental_travel_case/presentation.py')).resolve().parent
ns=runpy.run_path(str(D/'dental_travel_case.py'))
result=ns['opened'].rotate((0,0,0),(1,0,0),-55)
