"""Local F path checks: thin shell, hidden pocket skin and unchanged E leaves."""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from cap_f_flat_5 import *
from cap_e_thin_5 import OUTER_WIDTH,STEM_THICKNESS

gcode=Path(sys.argv[1])
paths=list(orca_linear_paths(gcode))
sections=[]
def sample(feature,x,z,span):
    sections.append(dict(feature=feature,x_mm=x,z_mm=z,
        **section_coverage(paths,x_mm=x,z_mm=z,span_mm=span)))

for z in (10,14):
    for y in detent_centres():
        for side in (-1,1):
            for offset in (.2,.6,1.0):
                sample('E_base_leaf',PRINT_ANCHOR[0]+side*(OUTER_WIDTH/2-STEM_THICKNESS+offset),
                       z,(PRINT_ANCHOR[1]+y-STEM_WIDTH/2+.3,
                          PRINT_ANCHOR[1]+y+STEM_WIDTH/2-.3))
hx=PRINT_ANCHOR[0]+hood_shift()
hy=PRINT_ANCHOR[1]
for z in (35,45):
    for side in (-1,1):
        for offset in (.2,.6):
            sample('thin_sidewall',hx+side*(UPPER_INNER_X/2+offset),ROOF_TOP-z,(hy-12,hy+12))
for z in (.2,.4,.6,.8):
    sample('thin_roof',hx,z,(hy-12,hy+12))
for y in detent_centres():
    for side in (-1,1):
        for offset in (.15,.5,.8):
            sample('blind_pocket_skin',hx+side*(CAP_INNER_X/2+GROOVE_DEPTH+offset),
                   ROOF_TOP-19.8,(hy-y-STEM_WIDTH/2+.4,hy-y+STEM_WIDTH/2-.4))
assert all(s['uncovered_width_mm']<.05 for s in sections),sections
d=Path(__file__).resolve().parents[1]
record=dict(placement='Preserve source paired placement',sections=sections,
    result='48 sampled leaf, thin-wall/roof and blind-pocket sections filled within 0.05 mm',
    limits='Requested stroke width coverage; no optical, material, adhesion or physical holding qualification.',
    identities={name:hashlib.sha256((d/name).read_bytes()).hexdigest()
                for name in ('cap_f_flat_5.py','cap_e_thin_5.py','cap_f_flat_5.stl')},
    gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest())
d.joinpath('notes/cap_f_paths.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(result=record['result'],sections=len(sections),
                     maximum_uncovered_mm=max(s['uncovered_width_mm'] for s in sections))))
