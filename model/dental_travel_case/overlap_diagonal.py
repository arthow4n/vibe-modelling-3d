"""Challenge guide-first contact with combined corner rocking and full side play."""
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import cadquery as cq

import m1_design as m1
import m4_design as m4
from retention_geometry import planar_faces
from retention_proxy import from_dimensions,receiver_stiffness,first_capture_loss,rod

ROOT=Path(__file__).resolve().parent


def pose(shape,d,angle):
    pivot=(-d.width/2,-d.depth/2,d.seam)
    return shape.rotate(pivot,(pivot[0]+1,pivot[1]-1,pivot[2]),angle).translate(
        (d.lap_clearance/math.sqrt(2),d.lap_clearance/math.sqrt(2),0))


def first_contact(shape,cap,d):
    def volume(angle):return shape.intersect(pose(cap,d,angle)).Volume()
    assert volume(0)<1e-5
    lo,hi=0.,3.
    assert volume(hi)>1e-5
    while hi-lo>.0005:
        middle=(lo+hi)/2
        if volume(middle)>1e-5:hi=middle
        else:lo=middle
    return lo


def run():
    results={}
    for name,d in (('nominal',m4.D),('larger_gap_smaller_axial_play',replace(m4.D,lap_clearance=.20,axial_play=.35))):
        parts=m4.build(d)
        cap=parts['cap'].val()
        guide=first_contact(parts['fixed'].val(),cap,d)
        hooks=m1.at_end(m4.hook(d),-1).val().fuse(m1.at_end(m4.hook(d),1).val())
        catch=first_contact(hooks,cap,d)
        face=planar_faces(cap,d.hook_bottom-d.axial_play,1)[0]
        transformed=pose(face,d,guide)
        point=transformed.Center()
        normal=transformed.normalAt()
        corners=[]
        for x in (-1,1):
            for y in (-1,1):
                xx=x*(d.beam_outer+d.hook_projection-.25)
                yy=y*d.hook_width/2
                z=point.z-(normal.x*(xx-point.x)+normal.y*(yy-point.y))/normal.z
                corners.append(z-d.hook_bottom)
        minimum_proxy_rise=[]
        leaf=from_dimensions(d,1200)
        for offset in (-.75,0,.75):
            varied=replace(leaf,eccentricity=leaf.eccentricity+offset)
            force=first_capture_loss(varied,engagement=d.hook_projection-.25-d.lap_clearance,
                fit_loss=.5,receiver_k=receiver_stiffness(d,1200,end_fixity=1),follower=True)
            minimum_proxy_rise.append(rod(varied,force,follower=True)['tooth_axial_motion_mm'])
        results[name]=dict(guide_angle_deg=guide,catch_angle_deg=catch,
            maximum_corner_axial_demand_mm=max(corners),minimum_proxy_axial_rise_mm=min(minimum_proxy_rise),
            scope='Actual diagonal path with side shift of magnitude equal to clearance; not unrestricted search or force equilibrium.')
        print(name,results[name],flush=True)
    output=dict(cases=results,source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
        ('m1_design.py','m2b_design.py','m3_design.py','m4_design.py','overlap_diagonal.py','retention_proxy.py')})
    (ROOT/'notes/overlap_exploration/diagonal_witness.json').write_text(json.dumps(output,indent=2)+'\n')


if __name__=='__main__':run()
