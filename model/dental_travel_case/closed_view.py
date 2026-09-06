"""Closed inspection pose, camera-oriented only. Not for printing."""
from pathlib import Path
import runpy
D=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/dental_travel_case/closed_view.py')).resolve().parent
ns=runpy.run_path(str(D/'dental_travel_case.py'))
result=ns['closed'].rotate((0,0,0),(1,0,0),-90)
