"""Consequential solid-stem screen for D's explicit preserved print placement.

Checks selected uniform sections only; solid paths do not calibrate PETG or layers.
"""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from cap_d_snap_5 import *

gcode=Path(sys.argv[1])
paths=list(orca_linear_paths(gcode))
cap_x=PRINT_ANCHOR[0]+OUTER_WIDTH/2+OUTSIDE_X/2+10
sections=[]
for assembly_z in (22,25):
    print_z=ROOF_TOP-assembly_z
    for y in detent_centres(COUNT):
        py=PRINT_ANCHOR[1]-y
        for side in (-1,1):
            for inside_offset in (.2,.6,1.0):
                px=cap_x+side*(CAP_INNER_X/2+inside_offset)
                review=section_coverage(paths,x_mm=px,z_mm=print_z,
                    span_mm=(py-STEM_WIDTH/2+.3,py+STEM_WIDTH/2-.3))
                sections.append(dict(x_mm=px,y_center_mm=py,z_mm=print_z,**review))
assert all(s['uncovered_width_mm']<.05 for s in sections), sections
directory=Path(__file__).resolve().parents[1]
record=dict(placement='Preserve source geometry at PRINT_ANCHOR; no GUI rearrangement qualified',
    scope='24 sections of four 1.2 mm stems in uniform span; width endpoints trimmed by 0.3 mm',
    sections=sections,result='Selected stem sections filled within 0.05 mm',
    limits='Coverage uses requested stroke widths, not deposited polymer. '
           'No modulus, layer bonding, root strength, contact or friction calibration.',
    gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
    source_sha256=hashlib.sha256((directory/'cap_d_snap_5.py').read_bytes()).hexdigest(),
    stl_sha256=hashlib.sha256((directory/'cap_d_snap_5.stl').read_bytes()).hexdigest())
directory.joinpath('notes/cap_d_paths.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(result=record['result'],sections=len(sections),
    maximum_uncovered_mm=max(s['uncovered_width_mm'] for s in sections))))
