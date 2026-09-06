"""Open case with nominal item envelopes. Inspection only, not for printing."""
from pathlib import Path
import runpy
D=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/dental_travel_case/fit_preview.py')).resolve().parent
ns=runpy.run_path(str(D/'dental_travel_case.py'))
from components import compound
from reference_items import reference_items
result=compound(ns['opened'],*reference_items().values())
