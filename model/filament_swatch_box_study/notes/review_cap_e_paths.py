"""E local path evidence for base leaves and the optically important thin shell.

Not a new bed/mesh checker; sampled requested-width coverage is not material data.
"""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from cap_e_thin_5 import *

gcode=Path(sys.argv[1])
paths=list(orca_linear_paths(gcode))
sections=[]
def sample(feature,x,z,span):
    review=section_coverage(paths,x_mm=x,z_mm=z,span_mm=span)
    sections.append(dict(feature=feature,x_mm=x,z_mm=z,**review))

for z in (10,14):
    for y in detent_centres():
        py=PRINT_ANCHOR[1]+y
        for side in (-1,1):
            for offset in (.2,.6,1.0):
                sample('base_leaf',PRINT_ANCHOR[0]+side*(OUTER_WIDTH/2-STEM_THICKNESS+offset),
                       z,(py-STEM_WIDTH/2+.3,py+STEM_WIDTH/2-.3))
hood_x=PRINT_ANCHOR[0]+hood_shift()
hood_y=PRINT_ANCHOR[1]
for assembly_z in (35,45):
    for side in (-1,1):
        for offset in (.2,.6):
            sample('thin_sidewall',hood_x+side*(CAP_INNER_X/2+offset),
                   ROOF_TOP-assembly_z,(hood_y-12,hood_y+12))
for z in (.2,.4,.6,.8):
    sample('thin_roof',hood_x,z,(hood_y-12,hood_y+12))
assert all(s['uncovered_width_mm']<.05 for s in sections),sections
directory=Path(__file__).resolve().parents[1]
record=dict(placement='Preserve source placement at PRINT_ANCHOR',sections=sections,
    result='Sampled base leaves, 0.8 mm sidewalls and four roof layers filled within 0.05 mm',
    limits='Sampled coverage uses requested stroke widths, not measured polymer. '
           'No modulus, layer bonding, optical clarity or whole-feature strength calibration.',
    gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
    source_sha256=hashlib.sha256((directory/'cap_e_thin_5.py').read_bytes()).hexdigest(),
    stl_sha256=hashlib.sha256((directory/'cap_e_thin_5.stl').read_bytes()).hexdigest())
directory.joinpath('notes/cap_e_paths.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(result=record['result'],sections=len(sections),
    maximum_uncovered_mm=max(s['uncovered_width_mm'] for s in sections))))
