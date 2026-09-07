"""Folded main mechanism; pack the removable spreader alongside it."""
import sys, importlib
from pathlib import Path
HERE=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/inspect_folded.py')).resolve().parent
sys.path.insert(0,str(HERE))
import glove_drying_insert as m
importlib.reload(m)
result=m.compound(m.assembled(0,False))
