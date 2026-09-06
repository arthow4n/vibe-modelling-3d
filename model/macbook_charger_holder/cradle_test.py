"""Optional fit coupon, same rails and print orientation as the full holder.

Run from the repository root, or evaluate this entry point through the MCP.
Only validates connector fit, not whole-band grip or cable winding.
"""
from pathlib import Path
import runpy
directory = Path(__file__).resolve().parent if '__file__' in globals() else Path('/home/hevar/git/vibe-modelling-3d/model/macbook_charger_holder')
ns = runpy.run_path(str(directory/'macbook_charger_holder.py'))
result = ns['result'].intersect(ns['box'](-1,25,-9,0,0,30))
assert result.val().isValid() and len(result.solids().vals()) == 1
