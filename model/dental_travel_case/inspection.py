"""Open assembled inspection pose; not a print placement."""
from pathlib import Path
import runpy
D=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/dental_travel_case/inspection.py')).resolve().parent
ns=runpy.run_path(str(D/'dental_travel_case.py'))
result=ns['opened']
