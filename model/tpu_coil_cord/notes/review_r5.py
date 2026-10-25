"""R5 faceted-profile, contact, spacing and actual bridge-path checks.

Run from repository root with ./execute.py SCRIPT RETAINED_ORCA_RUN_DIRECTORY.
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
from matplotlib.collections import LineCollection

OBJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(OBJECT))
import coil_r5_octagonal as m
from gcode_paths import extrusions

shape=m.build_sample().val()
solids=shape.Solids()
def occupied(point,tolerance=1e-6):return any(s.isInside(cq.Vector(*point),tolerance) for s in solids)
path=m.winding_path()
checks=[]
for turn in (1,2,3):
    for fraction in (.05,.15,.25,.35,.45,.55,.65,.75):
        p=path.positionAt((turn+fraction)/m.TURNS)
        g=p+cq.Vector(m.PITCH/2,0,0)
        checks.append(dict(turn=turn,fraction=fraction,material=occupied(p.toTuple()),
            gap_clear=all(not occupied((g+cq.Vector(dx,0,0)).toTuple()) for dx in (-.3,0,.3))))
assert all(c['material'] and c['gap_clear'] for c in checks)
anchors=[(m.AXIAL_WIDTH/2+t*m.PITCH,0,m.AXIS_HEIGHT-m.MEAN_APOTHEM) for t in (0,2,m.TURNS)]
assert any(all(s.isInside(cq.Vector(*p),1e-6) for p in anchors) for s in solids)
for x in (m.AXIAL_WIDTH/2,m.AXIAL_WIDTH/2+m.RISE):
    assert not occupied((x,0,m.AXIS_HEIGHT))

# Verify flat inner AND outer walls in every octagonal direction on actual CAD.
facets=[]
faces=shape.Faces()
for i in range(8):
    angle=i*math.pi/4
    ny,nz=math.sin(angle),math.cos(angle)
    found={name:False for name in ('inner','outer')}
    for face in faces:
        normal,p=face.normalAt(),face.Center()
        if abs(normal.x)>1e-5 or abs(abs(normal.y*ny+normal.z*nz)-1)>1e-5:continue
        offset=p.y*ny+(p.z-m.AXIS_HEIGHT)*nz
        for name,distance in [('inner',m.MEAN_APOTHEM-m.RADIAL_WIDTH/2),('outer',m.OUTSIDE_ACROSS_FLATS/2)]:
            if abs(offset-distance)<1e-5:found[name]=True
    facets.append(dict(degrees=i*45,**found))
assert all(f['inner'] and f['outer'] for f in facets)

bed=[f for f in faces if abs(f.Center().z)<1e-5 and abs(f.normalAt().z)>.999999]
contact=[]
for turn in (1,2,3,4):
    x=m.AXIAL_WIDTH/2+turn*m.PITCH
    area=sum(f.Area() for f in bed if abs(f.Center().x-x)<m.PITCH/2)
    contact.append(dict(turn=turn,contact_area_mm2=area,geometric_minimum_mm2=5.0))
assert all(c['contact_area_mm2']>=c['geometric_minimum_mm2'] for c in contact)

p=path.positionAt(2.25/m.TURNS)
crops=[]
for dx in (0,m.PITCH):
    box=cq.Workplane('XY').box(m.PITCH,.5,.5).translate((p.x+dx,p.y,p.z)).val()
    part=shape.intersect(box)
    if not part.Faces():raise ValueError('Missing adjacent-turn crop')
    crops.append(part)
gap=crops[0].distance(crops[1])
assert gap>=1.0

run=Path(sys.argv[1])
files=dict(primary=run/'plate_1.gcode',probe=run/'support_probe/plate_1.gcode')
paths={name:list(extrusions(file)) for name,file in files.items()}
bridges=[s for s in paths['primary'] if s['role']=='Bridge']
support=[s for s in paths['probe'] if s['role'] in ('Support','Support interface')]
assert any(abs(s['z']-.2)<1e-5 for s in paths['primary'])
# Known centered placement; source dimensions define the translation, not a mesh audit.
shift_x=135-m.OVERALL_LENGTH/2
bridge_outside=[]
for s in bridges:
    point=((sum(s['x'])/2)-shift_x,(sum(s['y'])/2)-135,s['z']-.1)
    if not occupied(point,tolerance=.005):bridge_outside.append(dict(point=point,path=s))
# 0.005 mm covers absolute STL deflection and G-code rounding, not gap allowance.
assert not bridge_outside,bridge_outside[:5]

roof=min((s['z'] for s in bridges if s['z']>m.AXIS_HEIGHT),default=11.0)
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
def draw(ax,selected,color,*,xz=False,width=.6):
    lines=[[(s['x'][0],s['z'] if xz else s['y'][0]),(s['x'][1],s['z'] if xz else s['y'][1])] for s in selected]
    if lines:ax.add_collection(LineCollection(lines,colors=color,linewidths=width));ax.autoscale_view()
draw(axes[0,0],[s for s in paths['primary'] if abs(s['z']-.2)<1e-5],'#286a9e')
draw(axes[0,1],[s for s in paths['primary'] if abs(s['z']-7.0)<1e-5],'#286a9e')
draw(axes[1,0],support,'#b35c2a',xz=True)
draw(axes[1,1],[s for s in paths['primary'] if abs(s['z']-(roof-.2))<1e-5],'#b9c1c7',width=1.8)
draw(axes[1,1],[s for s in paths['primary'] if abs(s['z']-roof)<1e-5 and s['role']!='Bridge'],'#286a9e')
draw(axes[1,1],[s for s in bridges if abs(s['z']-roof)<1e-5],'#b35c2a',width=.8)
for ax,title in zip(axes.flat,('R5 bed layer Z0.2','R5 side-wall layer Z7.0','R5 auto-probe supports: X vs Z',f'R5 roof Z{roof:g}: bridge orange, prior gray')):
    ax.set(title=title,xlabel='Bed X (mm)',ylabel='Z (mm)' if ax==axes[1,0] else 'Bed Y (mm)')
    if ax!=axes[1,0]:ax.set_aspect('equal')
fig.savefig(OBJECT/'notes/r5_actual_paths.png',dpi=150)
plt.close(fig)
answer=dict(scope='Local CAD and selected-profile reference paths; not physical separation, bridge quality, adhesion or recoil qualification.',
    material_gap_witnesses=checks,faceted_inner_and_outer_walls=facets,bed_contact_samples=contact,
    total_planar_bed_contact_mm2=sum(f.Area() for f in bed),native_local_gap_mm=gap,geometric_gap_minimum_mm=1.0,
    terminal_bores_open=True,connected_terminal_and_middle_material=True,
    gcode_sha256={name:hashlib.sha256(file.read_bytes()).hexdigest() for name,file in files.items()},
    support=dict(roles=sorted({s['role'] for s in support}),layers_mm=sorted({s['z'] for s in support})),
    primary_bridge_layers_mm=sorted({s['z'] for s in bridges}),
    bridge_midpoint_material_check=dict(midpoints_checked=len(bridges),outside=bridge_outside,tolerance_mm=.005,
        note='Only bridge-role deposition midpoints at representative layer mid-height; not a full bead-width or all-path gap audit.'),
    selected_roof_layer_mm=roof)
(OBJECT/'notes/r5_targeted_checks.json').write_text(json.dumps(answer,indent=2)+'\n')
print(json.dumps(answer))
