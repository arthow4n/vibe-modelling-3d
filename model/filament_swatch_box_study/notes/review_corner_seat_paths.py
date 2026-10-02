"""Targeted thicker front-stem coverage in the centered reference slice.

This checks the solid-stem idealization, not bed fit or ordinary wall paths.
"""
import hashlib
import json
import sys
from pathlib import Path
from physical_analysis.manufacturing import orca_linear_paths, section_coverage

gcode=Path(sys.argv[1])
paths=list(orca_linear_paths(gcode))
# Unchanged symmetric footprint is centered at (135,135) by Orca's arrangement.
reviews=[]
for z in (8.0,11.0):
    for x in (-5,7,19):
        review=section_coverage(paths,x_mm=x+135,z_mm=z,span_mm=(136.4,137.6))
        reviews.append(dict(x_mm=x+135,z_mm=z,**review))
assert all(r['uncovered_width_mm']<.05 for r in reviews), reviews
obj=Path(__file__).resolve().parents[1]
record=dict(scope='Six uniform front-stem sections; no layer bonding/material calibration',
    sections=reviews,result='All selected 1.2 mm stem sections filled within 0.05 mm',
    gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
    stl_sha256=hashlib.sha256((obj/'card_base_corner_seat_5.stl').read_bytes()).hexdigest())
(obj/'notes/corner_seat_paths.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
