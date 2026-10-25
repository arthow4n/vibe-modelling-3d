"""R4 contact, clearance and actual path evidence; run with ./execute.py RUN_DIR."""
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
import coil_r4_four_flats as m
from gcode_paths import extrusions

shape=m.build_sample().val()
solids=shape.Solids()
def occupied(point):return any(s.isInside(cq.Vector(*point),1e-6) for s in solids)
def center(turn,angle):
    theta=math.radians(angle)
    return (m.AXIAL_HEIGHT/2+(turn+angle/360)*m.PITCH,
            m.MEAN_RADIUS*math.sin(theta),m.ACROSS_FLATS/2-m.MEAN_RADIUS*math.cos(theta))
witnesses=[]
for turn in (2,9,16):
    for angle in (0,45,90,135,180,225,270,315):
        point=center(turn,angle)
        gap=(point[0]+m.PITCH/2,point[1],point[2])
        witnesses.append(dict(turn=turn,degrees=angle,material=occupied(point),
            gap_clear=all(not occupied((gap[0]+dx,gap[1],gap[2])) for dx in (-.1,0,.1))))
assert all(w['material'] and w['gap_clear'] for w in witnesses)
assert any(all(s.isInside(cq.Vector(*center(t,0)),1e-6) for t in (0,9,m.TURNS)) for s in solids)
for x in (m.AXIAL_HEIGHT/2,m.AXIAL_HEIGHT/2+m.RISE):
    assert not occupied((x,0,m.ACROSS_FLATS/2))

# Actual planar bed faces, rather than a bound or first-layer path proxy.
contacts=[]
flat_faces={name:[] for name in ('bottom','top','left','right')}
for face in shape.Faces():
    if face.geomType()!='PLANE':continue
    normal,point=face.normalAt(),face.Center()
    if abs(normal.z)>.999999:
        if abs(point.z)<1e-5:flat_faces['bottom'].append(face)
        if abs(point.z-m.ACROSS_FLATS)<1e-5:flat_faces['top'].append(face)
    if abs(normal.y)>.999999:
        if abs(point.y+m.ACROSS_FLATS/2)<1e-5:flat_faces['left'].append(face)
        if abs(point.y-m.ACROSS_FLATS/2)<1e-5:flat_faces['right'].append(face)
assert all(flat_faces.values())
for turn in (3,9,15):
    x=m.AXIAL_HEIGHT/2+turn*m.PITCH
    area=sum(f.Area() for f in flat_faces['bottom'] if abs(f.Center().x-x)<m.PITCH/2)
    contacts.append(dict(turn=turn,planar_contact_area_mm2=area,geometric_trial_minimum_mm2=5.0))
assert all(c['planar_contact_area_mm2']>=c['geometric_trial_minimum_mm2'] for c in contacts)

point=center(9,90)
crops=[]
for dx in (0,m.PITCH):
    box=(cq.Workplane('XY').box(m.PITCH,.8,.8)
         .translate((point[0]+dx,point[1],point[2])).val())
    crop=shape.intersect(box)
    if not crop.Faces():raise ValueError('Missing local material witness')
    crops.append(crop)
gap=crops[0].distance(crops[1])
assert gap>=.30

run=Path(sys.argv[1])
files=dict(primary=run/'plate_1.gcode',probe=run/'support_probe/plate_1.gcode')
paths={n:list(extrusions(p)) for n,p in files.items()}
r3=json.loads((OBJECT/'notes/r3_cad_slice_review.json').read_text())
old_gcode=Path(r3['slice']['kept_run_directory'])/'plate_1.gcode'
old_paths=list(extrusions(old_gcode))
support=[s for s in paths['probe'] if s['role'] in ('Support','Support interface')]
bridges=[s for s in paths['primary'] if s['role']=='Bridge']
roof_z=min((s['z'] for s in bridges if s['z']>m.ACROSS_FLATS/2),default=12.0)
assert any(abs(s['z']-.2)<1e-5 for s in paths['primary'])
fig,axes=plt.subplots(2,2,figsize=(13,6),layout='constrained')

def draw(ax,segments,color,*,xz=False,width=.6):
    lines=[[(s['x'][0],s['z'] if xz else s['y'][0]),(s['x'][1],s['z'] if xz else s['y'][1])] for s in segments]
    if lines:ax.add_collection(LineCollection(lines,colors=color,linewidths=width));ax.autoscale_view()

draw(axes[0,0],[s for s in old_paths if abs(s['z']-.2)<1e-5],'#286a9e')
draw(axes[0,1],[s for s in paths['primary'] if abs(s['z']-.2)<1e-5],'#286a9e')
draw(axes[1,0],support,'#b35c2a',xz=True,width=.5)
draw(axes[1,1],[s for s in paths['primary'] if abs(s['z']-(roof_z-.2))<1e-5],'#b9c1c7',width=1.8)
draw(axes[1,1],[s for s in paths['primary'] if abs(s['z']-roof_z)<1e-5 and s['role']!='Bridge'],'#286a9e')
draw(axes[1,1],[s for s in bridges if abs(s['z']-roof_z)<1e-5],'#b35c2a',width=.8)
for ax,title in zip(axes.flat,('R3 reference bed layer Z0.2','R4 reference bed layer Z0.2','R4 auto-probe supports: X vs Z',f'R4 roof Z{roof_z:g}: bridge orange, prior gray')):
    ax.set(title=title,xlabel='Bed X (mm)',ylabel='Z (mm)' if ax==axes[1,0] else 'Bed Y (mm)')
    if ax!=axes[1,0]:ax.set_aspect('equal')
fig.savefig(OBJECT/'notes/r4_actual_paths.png',dpi=150)
plt.close(fig)
answer=dict(scope='Native geometric contact/clearance and Orca reference paths; not Cura qualification or adhesion calibration.',
    witnesses=witnesses,flat_faces_present={name:bool(fs) for name,fs in flat_faces.items()},
    contact_samples=contacts,total_native_planar_bed_contact_mm2=sum(f.Area() for f in flat_faces['bottom']),
    native_local_gap_mm=gap,geometric_gap_minimum_mm=.30,terminal_bores_open=True,connected_terminal_and_middle_material=True,
    profile_symmetry='Intersection of a centered circle with an equal-sided centered square: two perpendicular mirror axes, diagonal mirror axes, and 90-degree rotations of the nominal outer profile. Not a mirror symmetry claim for the chiral helix.',
    input_gcode_sha256={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()},
    r3_reference_gcode_sha256=hashlib.sha256(old_gcode.read_bytes()).hexdigest(),
    support=dict(roles=sorted({s['role'] for s in support}),layers_mm=sorted({round(s['z'],3) for s in support})),
    primary_bridge_layers_mm=sorted({round(s['z'],3) for s in bridges}),selected_roof_layer_mm=roof_z)
(OBJECT/'notes/r4_targeted_checks.json').write_text(json.dumps(answer,indent=2)+'\n')
print(json.dumps(answer))
