"""Recheck guide-first rocking after moving guide walls toward the perimeter."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import math
import m1_design as m1
import m5_design as design
from overlap_exploration import onset
from overlap_diagonal import first_contact,pose
from retention_geometry import planar_faces

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m5'


def run():
    cases={}
    choices=[('nominal',design.D),('short_guide_control',replace(design.D,lap=30.)),
        ('rejected_loose_corners',replace(design.D,matched_corner_bearing=False,lap_clearance=.2,axial_play=.35))]+[
        (f'fit_{c}_{a}',replace(design.D,lap_clearance=c,axial_play=a))
        for c in (.1,.15,.2) for a in (.35,.4,.45)]
    for name,d in choices:
        parts=design.build(d)
        cap=parts['cap'].val()
        hooks={s:m1.at_end(design.hook(d),s).val() for s in (-1,1)}
        paths={}
        for axis in ('y','x'):
            guide=onset(parts['fixed'].val(),cap,d,axis=axis,transverse=d.lap_clearance)
            catches={str(s):onset(h,cap,d,axis=axis,transverse=d.lap_clearance) for s,h in hooks.items()}
            event=min(c['angle_deg'] for c in catches.values() if c['angle_deg'] is not None)
            paths[axis]=dict(guide=guide,catches=catches,guide_before_catch=guide['angle_deg']<event)
            if axis=='y':
                theta=math.radians(guide['angle_deg'])
                far=d.beam_outer+d.hook_projection-.25
                demand=(far+d.width/2-d.lap_clearance)*math.tan(theta)+(d.catch_height-d.axial_play)/math.cos(theta)-d.catch_height
                paths[axis]['far_land_axial_demand_mm']=demand
        if name in ('nominal','fit_0.2_0.35','rejected_loose_corners'):
            guide=first_contact(parts['fixed'].val(),cap,d)
            catch=first_contact(hooks[-1].fuse(hooks[1]),cap,d)
            face=pose(planar_faces(cap,d.hook_bottom-d.axial_play,1)[0],d,guide)
            center,normal=face.Center(),face.normalAt()
            demands=[]
            for x in (-1,1):
                for y in (-1,1):
                    xx=x*(d.beam_outer+d.hook_projection-.25)
                    yy=y*d.hook_width/2
                    demands.append(center.z-(normal.x*(xx-center.x)+normal.y*(yy-center.y))/normal.z-d.hook_bottom)
            paths['diagonal']=dict(guide_angle_deg=guide,catch_angle_deg=catch,
                                  maximum_land_axial_demand_mm=max(demands))
        cases[name]=paths
        print(name,[(a,p['guide_before_catch']) for a,p in paths.items() if a!='diagonal'],flush=True)
    result=dict(scope=__doc__+' Finite prescribed poses, no force or shell deformation prediction.',
        source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in
            ('m1_design.py','m2b_design.py','m3_design.py','m4_design.py','m5_design.py',
             'overlap_exploration.py','overlap_diagonal.py','m5_contacts.py')},cases=cases)
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'contact.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':run()
