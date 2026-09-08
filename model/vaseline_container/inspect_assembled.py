"""Closed inspection pose only; use vaseline_container.py for printing."""
from pathlib import Path
import runpy
import cadquery as cq
D = Path('/home/hevar/git/vibe-modelling-3d/model/vaseline_container')
m = runpy.run_path(str(D/'vaseline_container.py'))
result = cq.Compound.makeCompound([m['base'].val(),m['lid'].val()])
