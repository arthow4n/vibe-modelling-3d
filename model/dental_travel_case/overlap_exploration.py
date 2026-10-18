"""Actual-CAD rocking/contact exploration; preserve poses for visual judgment.

No force solver. Peeling rotates the cap about the outer near-side seam line,
with no imposed spring deformation. Guide-only limits deliberately omit hooks;
actual catch pickup is measured separately, so blocked ghost poses cannot be
presented as free motion of the closed assembly.
"""
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
import m1_design as m1
import m3_design as m3
import m4_design as m4
from retention_proxy import from_dimensions, receiver_stiffness, first_capture_loss, rod

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/overlap_exploration'
EPS=1e-5
RESOLUTION_DEG=.0005


def peel(shape,d,angle,*,axis='y',transverse=0.):
    if axis=='x':
        pivot=(0,-d.depth/2,d.seam)
        return shape.rotate(pivot,(1,pivot[1],pivot[2]),angle).translate((0,transverse,0))
    if axis!='y':raise ValueError(axis)
    pivot=(-d.width/2,0,d.seam)
    return shape.rotate(pivot,(pivot[0],1,pivot[2]),-angle).translate((transverse,0,0))


def onset(first,cap,d,*,axis='y',transverse=0.):
    def common(angle):return first.intersect(peel(cap,d,angle,axis=axis,transverse=transverse))
    assert common(0).Volume()<EPS,'Nominal assembly has interference'
    lo,hi=0.,6.
    if common(hi).Volume()<=EPS:
        return dict(angle_deg=None,reason='No contact by 6 degrees')
    while hi-lo>RESOLUTION_DEG:
        mid=(lo+hi)/2
        if common(mid).Volume()>EPS:hi=mid
        else:lo=mid
    intersection=common(hi)
    bounds=intersection.BoundingBox()
    return dict(angle_deg=lo,bracket_deg=[lo,hi],
        contact_center_mm=list(intersection.Center().toTuple()),
        contact_extent_mm=[bounds.xmin,bounds.xmax,bounds.ymin,bounds.ymax,bounds.zmin,bounds.zmax])


def point_after_peel(point,d,angle):
    theta=math.radians(angle)
    x,y,z=point
    r=x+d.width/2
    s=z-d.seam
    return (-d.width/2+r*math.cos(theta)-s*math.sin(theta),y,
            d.seam+r*math.sin(theta)+s*math.cos(theta))


def explore():
    OUT.mkdir(exist_ok=True,parents=True)
    records={}
    choices=[('M1',m1,m1.D,False),('M3',m3,m3.D,False)]+[
        ('M3_overlap_'+str(length),m3,replace(m3.D,lap=float(length)),False)
        for length in (12,24,36,48,54,60,66,72,78)]+[
        ('M3_overlap_'+str(length)+'_floating',m3,replace(m3.D,lap=float(length)),True)
        for length in (12,30,36,48,60,66,72,78)]+[
        ('M4_centered',m4,m4.D,False),('M4',m4,m4.D,True),
        ('M4_rejected_centered_only',m4,replace(m4.D,lap=72.,lap_clearance=.2,axial_play=.3),True)]+[
        ('M4_fit_'+str(c)+'_'+str(a),m4,replace(m4.D,lap_clearance=c,axial_play=a),True)
        for c in (.10,.15,.20) for a in (.35,.40,.45)]
    for name,module,d,floating in choices:
        shift=d.lap_clearance if floating else 0.
        parts=module.build(d)
        cap,fixed=parts['cap'].val(),parts['fixed'].val()
        guide=onset(fixed,cap,d,transverse=shift)
        catches={str(sign):onset(m1.at_end(module.hook(d),sign).val(),cap,d,transverse=shift)
                 for sign in (-1,1)}
        first=min(x['angle_deg'] for x in catches.values() if x['angle_deg'] is not None)
        angle=guide['angle_deg']
        # Actual far outer edge of the nominal 1.5mm flat land, receiver side.
        far_x=d.beam_outer+d.hook_projection-.25
        receiver=(far_x,0,d.hook_bottom-d.axial_play)
        moved=point_after_peel(receiver,d,angle)
        # Height of the tilted receiver plane at the FIXED tooth edge, allowing
        # cap translation; following one cap material point would bias the gap.
        theta=math.radians(angle)
        receiver_height=d.seam+(far_x+d.width/2-shift)*math.tan(theta)+(d.catch_height-d.axial_play)/math.cos(theta)
        required=receiver_height-d.hook_bottom
        engagement=d.hook_projection-.25-d.lap_clearance
        leaf=from_dimensions(d,1200)
        loss=first_capture_loss(leaf,engagement=engagement,fit_loss=.5,
            receiver_k=receiver_stiffness(d,1200,end_fixity=1),follower=True)
        proxy=rod(leaf,loss,follower=True)
        # Contact lever arm includes first/outer edge uncertainty; no fitted values.
        controls=[]
        for offset in (-.75,0,.75):
            altered=replace(leaf,eccentricity=leaf.eccentricity+offset)
            P=first_capture_loss(altered,engagement=engagement,fit_loss=.5,
                receiver_k=receiver_stiffness(d,1200,end_fixity=1),follower=True)
            response=rod(altered,P,follower=True)
            controls.append(dict(lever_offset_mm=offset,first_capture_loss_per_catch_N=P,
                tooth_centroid_axial_rise_mm=response['tooth_axial_motion_mm']))
        top=(0,0,d.length)
        top_pose=point_after_peel(top,d,angle)
        top_pose=(top_pose[0]+shift,top_pose[1],top_pose[2])
        record=dict(transverse_shift_mm=shift,dimensions=dict(lap_mm=d.lap,width_mm=d.width,axial_play_mm=d.axial_play,
            guide_clearance_per_side_mm=d.lap_clearance,cap_length_mm=d.length-d.seam),
            guide_only_onset=guide,catch_onsets=catches,first_catch_contact_deg=first,
            top_center_motion_mm=[top_pose[i]-top[i] for i in range(3)],
            far_receiver_rise_at_guide_onset_mm=receiver_height-receiver[2],
            demanded_far_land_axial_motion_mm=required,
            proxy_center_axial_motion_at_adverse_capture_loss_mm=proxy['tooth_axial_motion_mm'],
            proxy_contact_edge_controls=controls,
            hook_intersection_at_guide_only_pose_mm3={str(sign):m1.at_end(module.hook(d),sign).val().intersect(peel(cap,d,angle,transverse=shift)).Volume() for sign in (-1,1)},
            decision_scope='Comparison of one declared peel path and local proxy; not complete contact equilibrium or measured holding force.')
        if name=='M4':
            record['depth_rocking']=dict(guide=onset(fixed,cap,d,axis='x',transverse=shift),
                catches={str(sign):onset(m1.at_end(module.hook(d),sign).val(),cap,d,axis='x',transverse=shift) for sign in (-1,1)})
        records[name]=record
        print(name,'catch',round(first,4),'guide',round(angle,4),
              'far axial demand',round(required,4),'proxy rise at loss',round(proxy['tooth_axial_motion_mm'],4),flush=True)
    answer=dict(scope=__doc__,boolean_volume_epsilon_mm3=EPS,angle_resolution_deg=RESOLUTION_DEG,
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
            ('m1_design.py','m2b_design.py','m3_design.py','m4_design.py','retention_proxy.py','overlap_exploration.py')},
        cases=records)
    (OUT/'contact_sequence.json').write_text(json.dumps(answer,indent=2)+'\n')


if __name__=='__main__':explore()
