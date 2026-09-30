"""Card access, covered enclosure, interface integration and useful load screens."""
import json
import hashlib
from pathlib import Path
from components import *
from physical_analysis.screening import rectangular_cantilever

def overlap(a,b):
    return a.intersect(b).val().Volume()

def verify():
    b,l=body(),lid()
    assert overlap(b,l)<1e-7,'closed assembly collision'
    trial=block(-(CARD_X+1)/2,-COUNT*(CARD_T+.1)/2,FLOOR,CARD_X+1,COUNT*(CARD_T+.1),CARD_Y+1)
    poses=[]
    for dx in (-2,0,2):
        for dy in (-4,0,4):
            t=trial.translate((dx,dy,0))
            assert overlap(t,b)<1e-7,(dx,dy,'body')
            assert overlap(t,l)<1e-7,(dx,dy,'lid')
            poses.append([dx,dy])
    # First/last cards can lean outward to expose a selected card, with the
    # cap removed. Sample rotation about the long bottom edge, not all cards
    # forced to rotate together. Intermediate cards can translate into the gap.
    fan=[]
    for i,sign in ((0,1),(COUNT-1,-1)):
        y=-COUNT*CARD_T/2+i*CARD_T
        if sign<0: y+=CARD_T  # outer bottom edge, so the card lifts off the floor
        for angle in (0,4,8,12):
            c=card(i).rotate((-CARD_X/2,y,FLOOR),(CARD_X/2,y,FLOOR),sign*angle)
            v=overlap(c,b);assert v<1e-7,(i,angle,v)
            fan.append(dict(card_index=i,angle_deg=sign*angle,body_overlap_mm3=v))
    # Top grip envelope on either long card edge. It lies entirely above the
    # body, allowing fingertips to approach a card's 20.4 mm exposed portion.
    grips=[]
    for sign in (-1,1):
        finger=cq.Workplane('XY').center(0,sign*24).ellipse(9,6).extrude(12).translate((0,0,RIM_Z+1))
        v=overlap(finger,b);assert v<1e-7,v
        grips.append(dict(side=sign,ellipse_mm=[18,12],body_overlap_mm3=v))
    missing=[]
    # Straight thickness strips omit rounded transitions. A complete rounded
    # 1 mm boundary below separately checks those corners for a through path.
    targets=[block(-INNER_X/2+3,INNER_Y/2,FLOOR,INNER_X-6,closure.SNAP_LINER,RIM_Z-FLOOR),
        block(-INNER_X/2+3,BACK_Y,FLOOR,INNER_X-6,WALL,RIM_Z-FLOOR)]
    for x in (-INNER_X/2-WALL,INNER_X/2):
        targets.append(block(x,-INNER_Y/2+3,FLOOR,WALL,INNER_Y-6,RIM_Z-FLOOR))
    for target in targets:
        v=target.cut(b).val().Volume();assert v<1e-7,v;missing.append(v)
    boundary=rounded(INNER_X+2,INNER_Y+2,RIM_Z-FLOOR,FLOOR,r=2,cy=0).cut(
        rounded(INNER_X,INNER_Y,RIM_Z-FLOOR+.2,FLOOR-.1,r=1,cy=0))
    v=boundary.cut(b).val().Volume();assert v<1e-7,v;missing.append(v)
    upper=[]
    for y in (SEAL_CENTER_Y+SEAL_Y/2+FIT,SEAL_CENTER_Y-SEAL_Y/2-FIT-WALL):
        upper.append(block(-INNER_X/2+1,y,SHIELD_BOTTOM,INNER_X-2,WALL,ROOF_Z-SHIELD_BOTTOM))
    for x in (-SEAL_X/2-FIT-WALL,SEAL_X/2+FIT):
        upper.append(block(x,-INNER_Y/2+1,SHIELD_BOTTOM,WALL,INNER_Y-2,ROOF_Z-SHIELD_BOTTOM))
    for t in upper:
        v=t.cut(l).val().Volume();assert v<1e-7,v;missing.append(v)
    cover=block(-INNER_X/2,-INNER_Y/2,ROOF_Z+.5,INNER_X,INNER_Y,.2)
    assert cover.cut(l).val().Volume()<1e-7
    floor=block(-INNER_X/2+1,-INNER_Y/2+1,.3,INNER_X-2,INNER_Y-2,FLOOR-.6)
    assert floor.cut(b).val().Volume()<1e-7
    arm=snap_arm();rigid=b.cut(arm)
    travel=[]
    for lift in (0,.25,.5,1,2,3,4,6,8,10,12,26,36):
        v=overlap(rigid,l.translate((0,0,lift)));assert v<1e-7,(lift,v)
        # The card stack must remain clear throughout, not only when closed.
        v2=overlap(trial,l.translate((0,0,lift)));assert v2<1e-7,(lift,v2)
        travel.append(lift)
    for dy in (-FIT,0,FIT):
        locked=overlap(arm,l.translate((0,dy,1)));assert locked>1e-3,locked
        for lift in (0,.5,1,2,4,8,12):
            v=overlap(arm.translate((0,-1.4,0)),l.translate((0,dy,lift)))
            assert v<1e-7,(dy,lift,v)
    # One front catch raises a different whole-cap question: can the rear
    # simply peel away while the front remains at the shoulder? Sample that
    # rigid path, including its nominal 0.7 mm vertical retaining play.
    rocking=[]
    for dz in (0,.7):
        path=[]
        for angle in (0,2,4,6,8,12):
            c=l.translate((0,0,dz)).rotate((-OUT_X/2,HEAD_Y,HEAD_Z-.6+dz),
                (OUT_X/2,HEAD_Y,HEAD_Z-.6+dz),-angle)
            path.append(dict(angle_deg=angle,body_intersection_mm3=overlap(rigid,c)))
        assert next(row['angle_deg'] for row in path if row['body_intersection_mm3']>1e-3)==6
        rocking.append(dict(front_lift_mm=dz,poses=path))
    free=arm.intersect(block(-20,0,ROOT_Z+.7,40,60,ARM_L+5))
    clearance=[]
    for inward in (0,.4,.8,1.4,2.2):
        for dx,dz in ((0,0),(.2,.9),(-.2,.9),(.2,-.3),(-.2,-.3)):
            f=free.translate((dx,-inward,dz))
            assert overlap(f,rigid)<1e-7,(inward,dx,dz,'body')
            assert overlap(f,l)<1e-7,(inward,dx,dz,'cap')
        clearance.append(inward)
    # Compare the actual contacting cap band in the old local coordinates.
    # Upper shield/roof differ, so whole-fixture/global-shell equivalence is
    # explicitly not claimed. Compare only surfaces crossed by the head/pad.
    window=block(-12,closure.INNER_Y/2+WALL+.2,closure.HEAD_Z-7,24,15,closure.RIM_Z-.01-(closure.HEAD_Z-7))
    actual=l.translate((0,-SHIFT_Y,-SHIFT_Z)).intersect(window)
    previous=closure.lid().intersect(window)
    mismatch=actual.cut(previous).val().Volume()+previous.cut(actual).val().Volume()
    assert mismatch<1e-6,mismatch
    beam=rectangular_cantilever(length_mm=ARM_L,width_mm=ARM_W,thickness_mm=ARM_T,
        youngs_modulus_MPa=1200,tip_displacement_mm=closure.OVERLAP)
    load=.25*9.81*2
    strain=(load/(ARM_W*ARM_T)+load*2.5*(ARM_T/2)/(ARM_W*ARM_T**3/12))/1200
    sources=[Path(__file__).parent/'components.py',_closure_path(),SWATCH_SOURCE]
    root=Path(__file__).resolve().parents[2]
    return dict(capacity=dict(count=COUNT,cavity_mm=[INNER_X,INNER_Y],nominal_card_mm=[CARD_X,CARD_T,CARD_Y],
        variation_stack_mm=[CARD_X+1,COUNT*(CARD_T+.1),CARD_Y+1],variation_poses_mm=poses,
        nominal_exposed_card_height_mm=FLOOR+CARD_Y-RIM_Z,minimum_variation_roof_gap_mm=ROOF_Z-(FLOOR+CARD_Y+1)),
        access=dict(fan_poses=fan,finger_grips=grips,limits='Rigid card and assumed fingertips; no skin, comfort or printed friction.'),
        enclosure=dict(missing_target_wall_mm3=missing,shield_overlap_mm=4,shield_fit_gap_mm=FIT),
        rigid_cap_lift_samples_mm=travel,local_cap_band_difference_mm3=mismatch,
        rear_peel_screen=dict(pivot_yz_mm=[HEAD_Y,HEAD_Z-.6],paths=rocking,
            limits='This sampled rigid path is blocked by 6 degrees; not all possible paths, wall compliance or a physical retention rating.'),
        free_tab_inward_envelope_samples_mm=clearance,beam_screen=beam,
        retention_screen=dict(assumed_payload_kg=.25,assumed_acceleration_g=2,force_on_single_snap_N=load,
            assumed_eccentricity_mm=2.5,ideal_root_strain=strain,limits='Ideal axial/eccentric section; no shell, notch, contact bearing or printed bonding rating.'),
        source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        numerical_evidence='Lift-box interface evidence applies only to identical local contact geometry and clamped-root assumption. Its contact-quality failure remains unresolved; not a new qualified force prediction.')

def _closure_path():
    return Path(closure.__file__)

if __name__=='__main__':
    answer=verify();print(json.dumps(answer,indent=2))
