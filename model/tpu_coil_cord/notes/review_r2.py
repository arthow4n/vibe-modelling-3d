"""Targeted R2 clearance/section screen and actual TPU toolpath review.

Run from root: ./execute.py model/tpu_coil_cord/notes/review_r2.py ORCA_RUN_DIR
"""
import ast
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OBJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(OBJECT))
import coil_r2_horizontal as m
from gcode_paths import extrusions as paths


def section_screen():
    # Read literal R1 dimensions without rebuilding the unchanged printed control.
    values={}
    for node in ast.parse((OBJECT/'tpu_coil_cord.py').read_text()).body:
        if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant):
            for name in node.targets:
                if isinstance(name,ast.Name):values[name.id]=node.value.value
    w,h,f=(values[k]/2 for k in ('RADIAL_WIDTH','AXIAL_HEIGHT','FLAT_WIDTH'))
    polygon=[(-f,-h),(f,-h),(w,0),(f,h),(-f,h),(-w,0)]
    area=polar=0.
    for (x,y),(u,v) in zip(polygon,polygon[1:]+polygon[:1]):
        cross=x*v-u*y
        area+=cross/2
        polar+=cross*(x*x+x*u+u*u+y*y+y*v+v*v)/12
    radius=m.CORD_DIAMETER/2
    return dict(scope='Ideal straight, untrimmed sections under homogeneous isotropic elasticity; not full-coil force or recovery.',
                r1_hex_area_mm2=area,r1_hex_polar_moment_mm4=polar,
                r2_circle_area_mm2=math.pi*radius**2,r2_circle_torsion_constant_mm4=math.pi*radius**4/2,
                area_ratio=math.pi*radius**2/area,
                circle_J_to_hex_polar_upper_bound_ratio=(math.pi*radius**4/2)/polar,
                note='Hexagonal Saint-Venant torsion constant is no greater than its polar area moment. Foot flattening, bending, thick curved-rod effects, eye/tab restraint and TPU hysteresis are excluded; no spring-force multiplier is established.')


shape=m.build_sample().val()
solids=shape.Solids()
def material(point):return any(s.isInside(cq.Vector(*point),1e-6) for s in solids)
spine=m.coil_spine(m.loop_wire())
witnesses=[]
for turn in (1,2):
    for fraction in (.05,.15,.25,.35,.45,.55,.65,.75,.85,.95):
        point=spine.positionAt((turn+fraction)/m.TURNS)
        gap=point+cq.Vector(m.PITCH/2,0,0)
        witness=dict(turn=turn,fraction=fraction,material=material(point.toTuple()),
                     gap_clear=not material(gap.toTuple()),
                     gap_near_sides_clear=all(not material((gap+cq.Vector(dx,0,0)).toTuple()) for dx in (-.2,.2)))
        witnesses.append(witness)
assert all(w['material'] and w['gap_clear'] and w['gap_near_sides_clear'] for w in witnesses)
# These native crops isolate matching local tube regions across an actual gap.
# The faces facing the gap are retained, rather than accepting a nominal pitch.
gaps=[]
for fraction in (.10,.32,.58):
    point=spine.positionAt((1+fraction)/m.TURNS)
    regions=[]
    for dx in (0,m.PITCH):
        box=(cq.Workplane('XY').box(m.PITCH,1.5,1.5)
             .translate((point.x+dx,point.y,point.z)).val())
        crop=shape.intersect(box)
        if crop.isNull() or not crop.Solids():raise ValueError('Missing local material crop')
        regions.append(crop)
    distance=regions[0].distance(regions[1])
    gaps.append(dict(fraction=fraction,gap_mm=distance,minimum_trial_gap_mm=.6))
assert all(g['gap_mm']>=g['minimum_trial_gap_mm'] for g in gaps)
for x in (-m.END_FRAME_OFFSET,m.AXIAL_RISE+m.END_FRAME_OFFSET):
    assert not material((x,0,m.BASE_CENTER_Z+m.SIDE_HEIGHT))
    assert material((x,0,m.BASE_CENTER_Z))

run=Path(sys.argv[1])
files=dict(primary=run/'plate_1.gcode',probe=run/'support_probe/plate_1.gcode')
segments={name:list(paths(file)) for name,file in files.items()}
roles={name:sorted({s['role'] for s in ss}) for name,ss in segments.items()}
support=[s for s in segments['probe'] if s['role'] in ('Support','Support interface')]
bridges=[s for s in segments['primary'] if s['role']=='Bridge']
fig,axes=plt.subplots(1,3,figsize=(15,4.5),layout='constrained')
for s in segments['primary']:
    if abs(s['z']-.2)<1e-5:axes[0].plot(s['x'],s['y'],color='#286a9e',lw=.6)
for s in support:axes[1].plot(s['x'],[s['z'],s['z']],color='#b35c2a',lw=.65)
bridge_z=min(s['z'] for s in bridges) if bridges else 14.0
for s in segments['primary']:
    if abs(s['z']-(bridge_z-.2))<1e-5:
        axes[2].plot(s['x'],s['y'],color='#b9c1c7',lw=2)
for s in segments['primary']:
    if abs(s['z']-bridge_z)<1e-5:
        axes[2].plot(s['x'],s['y'],color='#bf6329' if s['role']=='Bridge' else '#286a9e',lw=.8)
if not support:axes[1].text(.5,.5,'No support extrusion',ha='center',transform=axes[1].transAxes)
for ax,title in zip(axes,('Primary: bed layer Z0.2','Auto-probe support: X vs Z',f'Roof closure Z{bridge_z:g}: bridge orange, prior gray')):
    ax.set(title=title,xlabel='Bed X (mm)',ylabel='Z (mm)' if ax==axes[1] else 'Bed Y (mm)')
    if ax!=axes[1]:ax.set_aspect('equal')
fig.savefig(OBJECT/'notes/r2_actual_paths.png',dpi=150)
plt.close(fig)
report=dict(scope='Targeted actual CAD clearance and selected-profile path evidence; physical release, surface finish and recoil remain unmeasured.',
            section_screen=section_screen(),witnesses=witnesses,local_native_gaps=gaps,
            extrusion_roles=roles,gcode_sha256={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in files.items()},
            support=dict(segment_count=len(support),layers_mm=sorted({round(s['z'],3) for s in support}),
                         x_range_mm=[min(min(s['x']) for s in support),max(max(s['x']) for s in support)] if support else None,
                         y_range_mm=[min(min(s['y']) for s in support),max(max(s['y']) for s in support)] if support else None),
            primary_bridges=dict(segment_count=len(bridges),layers_mm=sorted({round(s['z'],3) for s in bridges}),
                                 longest_deposition_segment_mm=max((math.dist((s['x'][0],s['y'][0]),(s['x'][1],s['y'][1])) for s in bridges),default=None),
                                 note='Segment length includes anchored deposition; not an unsupported-span measurement.'))
(OBJECT/'notes/r2_targeted_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
