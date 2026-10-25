"""Targeted gap witnesses and actual layer views for the first coil experiment.

Run from repository root with ./execute.py SCRIPT RETAINED_ORCA_DIRECTORY.
"""
import json
import math
from pathlib import Path
import re
import sys

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OBJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OBJECT))
import tpu_coil_cord as model

shape = model.result.val()
solids = shape.Solids()
def material(point):
    return any(s.isInside(cq.Vector(*point), 1e-6) for s in solids)

# Positive material controls prevent an empty or misplaced coil passing the void test.
witnesses = []
for turn in (1, 2, 3):
    for degrees in (30, 90, 150, 210, 270, 330):
        theta = math.radians(degrees)
        x, y = model.MEAN_RADIUS*math.cos(theta), model.MEAN_RADIUS*math.sin(theta)
        center = model.AXIAL_HEIGHT/2 + (turn+degrees/360)*model.PITCH
        occupied = material((x,y,center))
        clear = not material((x,y,center+model.PITCH/2))
        witnesses.append(dict(turn=turn, degrees=degrees, material=occupied, gap_clear=clear))
assert all(w['material'] and w['gap_clear'] for w in witnesses)
assert not material((0,0,model.AXIAL_HEIGHT/2))
assert not material((0,0,model.AXIAL_HEIGHT/2+model.RISE))

# The retained Orca file uses absolute XYZ and relative E. Reject another dialect.
gcode = Path(sys.argv[1])/'plate_1.gcode'
source = gcode.read_text()
assert 'M83' in source
source = source[source.index(';LAYER_CHANGE'): ]
commands = [line.split(';')[0].strip().split() for line in source.splitlines()]
assert not any(c and c[0] in ('G91', 'M82') for c in commands)
number = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
position = dict(X=0.,Y=0.,Z=0.)
roles = {}
layers = {0.2:[], 5.4:[], 22.0:[]}
role = ''
for line in source.splitlines():
    if line.startswith(';TYPE:'): role=line[6:].strip()
    code=line.split(';')[0].strip()
    if not code or code.split()[0] not in ('G0','G1'): continue
    values={a:float(v) for a,v in re.findall(r'([XYZE])('+number+r')',code)}
    before=position.copy()
    position.update({a:v for a,v in values.items() if a in position})
    if values.get('E',0)<=0 or not any(a in values for a in ('X','Y')): continue
    roles[role]=roles.get(role,0)+1
    for z,segments in layers.items():
        if abs(position['Z']-z)<1e-5:
            segments.append(([before['X'],position['X']],[before['Y'],position['Y']],role))
assert all(layers.values())
fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for ax,(z,segments) in zip(axes,layers.items()):
    for x,y,role in segments:
        ax.plot(x,y,color='#b65c23' if role=='Bridge' else '#266ba4',lw=.7)
    ax.set(title=f'Actual TPU extrusion: Z {z:g} mm',xlabel='Bed X (mm)',ylabel='Bed Y (mm)',aspect='equal')
fig.savefig(OBJECT/'notes/actual_layers.png',dpi=150)
plt.close(fig)
report=dict(scope='Sampled CAD material/void witnesses and selected extrusion layers; not physical gap or strength qualification.',
            witnesses=witnesses, extrusion_roles=roles, selected_layers_mm=list(layers))
(OBJECT/'notes/targeted_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
