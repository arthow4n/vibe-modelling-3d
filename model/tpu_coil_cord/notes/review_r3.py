"""R3 native material/gap witnesses and actual horizontal TPU path review.

Run through ./execute.py from the repository root, supplying the retained Orca
run directory from r3_cad_slice_review.json.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OBJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(OBJECT))
import coil_r3_round as m
from gcode_paths import extrusions

shape=m.build_sample().val()
solids=shape.Solids()
def occupied(point):return any(s.isInside(cq.Vector(*point),1e-6) for s in solids)
def center(turn,angle):
    theta=math.radians(angle)
    return (m.AXIAL_HEIGHT/2+(turn+angle/360)*m.PITCH,
            m.MEAN_RADIUS*math.sin(theta),m.OUTER_RADIUS-m.MEAN_RADIUS*math.cos(theta))
witnesses=[]
for turn in (2,10,17):
    for angle in (0,45,90,135,180,225,270,315):
        point=center(turn,angle)
        gap=(point[0]+m.PITCH/2,point[1],point[2])
        witnesses.append(dict(turn=turn,degrees=angle,material=occupied(point),
            gap_clear=all(not occupied((gap[0]+dx,gap[1],gap[2])) for dx in (-.025,0,.025))))
assert all(w['material'] and w['gap_clear'] for w in witnesses)
anchors=[center(t,0) for t in (0,10,m.TURNS)]
assert any(all(s.isInside(cq.Vector(*p),1e-6) for p in anchors) for s in solids)
for x in (m.AXIAL_HEIGHT/2,m.AXIAL_HEIGHT/2+m.RISE):
    assert not occupied((x,0,m.OUTER_RADIUS))

gaps=[]
for angle in (90,180):
    point=center(10,angle)
    crops=[]
    for dx in (0,m.PITCH):
        box=(cq.Workplane('XY').box(m.PITCH,.8,.8)
             .translate((point[0]+dx,point[1],point[2])).val())
        crop=shape.intersect(box)
        if not crop.Faces():raise ValueError('Missing local material witness')
        crops.append(crop)
    gap=crops[0].distance(crops[1])
    gaps.append(dict(degrees=angle,shortest_gap_mm=gap,geometric_minimum_mm=.10))
assert all(g['shortest_gap_mm']>=g['geometric_minimum_mm'] for g in gaps)

run=Path(sys.argv[1])
files=dict(primary=run/'plate_1.gcode',probe=run/'support_probe/plate_1.gcode')
paths={name:list(extrusions(file)) for name,file in files.items()}
assert any(abs(s['z']-.2)<1e-5 for s in paths['primary'])
support=[s for s in paths['probe'] if s['role'] in ('Support','Support interface')]
bridges=[s for s in paths['primary'] if s['role']=='Bridge']
roof_z=min((s['z'] for s in bridges if s['z']>m.OUTER_RADIUS),default=12.0)
fig,axes=plt.subplots(1,3,figsize=(15,4.8),layout='constrained')
for s in paths['primary']:
    if abs(s['z']-.2)<1e-5:axes[0].plot(s['x'],s['y'],color='#286a9e',lw=.6)
    if abs(s['z']-(roof_z-.2))<1e-5:axes[2].plot(s['x'],s['y'],color='#b9c1c7',lw=1.8)
for s in support:axes[1].plot(s['x'],[s['z'],s['z']],color='#b35c2a',lw=.55)
for s in paths['primary']:
    if abs(s['z']-roof_z)<1e-5:axes[2].plot(s['x'],s['y'],color='#bf6329' if s['role']=='Bridge' else '#286a9e',lw=.7)
for ax,title in zip(axes,('Primary bed layer Z0.2','Auto-probe supports: X vs Z',f'Roof Z{roof_z:g}: bridge orange, prior gray')):
    ax.set(title=title,xlabel='Bed X (mm)',ylabel='Z (mm)' if ax==axes[1] else 'Bed Y (mm)')
    if ax!=axes[1]:ax.set_aspect('equal')
fig.savefig(OBJECT/'notes/r3_actual_paths.png',dpi=150)
plt.close(fig)
answer=dict(scope='Local native geometry and selected-profile path review; not printed release, roof quality or recoil qualification.',
    witnesses=witnesses,native_local_gaps=gaps,connected_terminal_and_middle_material=True,terminal_bores_open=True,
    input_gcode_sha256={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()},
    primary_roles=sorted({s['role'] for s in paths['primary']}),
    support=dict(roles=sorted({s['role'] for s in support}),layers_mm=sorted({round(s['z'],3) for s in support})),
    primary_bridges=dict(layers_mm=sorted({round(s['z'],3) for s in bridges}),
        longest_deposition_segment_mm=max((math.dist((s['x'][0],s['y'][0]),(s['x'][1],s['y'][1])) for s in bridges),default=None),
        note='Deposition length includes anchors, not an unsupported-span measurement.'),
    selected_roof_layer_mm=roof_z)
(OBJECT/'notes/r3_targeted_checks.json').write_text(json.dumps(answer,indent=2)+'\n')
print(json.dumps(answer))
