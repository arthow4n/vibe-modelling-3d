import sys, importlib
from pathlib import Path
sys.path.insert(0,str(Path(globals().get("__file__","/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/inspect.py")).resolve().parent))
import glove_drying_insert as m
importlib.reload(m)
result=m.compound(m.assembled())
