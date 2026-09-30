"""Capacity, enclosure, handling and rigid interfaces; no generic CAD audits."""
import json
from components import *
from physical_analysis.screening import rectangular_cantilever,circular_cam_detent

def verify():
    b,l=body(),lid()
    trial=block(-CARD_X/2-.5,-CARD_Y/2-.5,STACK_Z,CARD_X+1,CARD_Y+1,COUNT*(CARD_T+.1))
    assert b.intersect(trial).val().Volume()<1e-7
    assert l.intersect(trial).val().Volume()<1e-7
    positions=[]
    for dx in (-1,0,1):
        for dy in (-2,0,2):
            shifted=trial.translate((dx,dy,0))
            assert b.intersect(shifted).val().Volume()<1e-7,(dx,dy,'body')
            assert l.intersect(shifted).val().Volume()<1e-7,(dx,dy,'cap')
            positions.append([dx,dy])
    assert b.intersect(l).val().Volume()<1e-7
    locked=snap_arm().intersect(l.translate((0,0,1))).val().Volume()
    assert locked>1e-3,locked
    worst_locked=snap_arm().intersect(l.translate((0,FIT,1))).val().Volume()
    assert worst_locked>1e-3,worst_locked
    released=[]
    for lift in (0,.25,.5,.75,1,2,3,4,6,8,10,12):
        v=snap_arm().translate((0,-1.4,0)).intersect(l.translate((0,0,lift))).val().Volume()
        assert v<1e-7,(lift,v)
        released.append(lift)
    # Both extrema of allowed side play still clear the released head. This
    # checks nominal geometric play, not unmeasured print dimensional error.
    for dy in (-FIT,FIT):
        for lift in (0,.5,1,2,4,8,12):
            v=snap_arm().translate((0,-1.4,0)).intersect(l.translate((0,dy,lift))).val().Volume()
            assert v<1e-7,(dy,lift,v)
    # Continuous cavity boundary, including behind the snap slots. Target
    # strips omit the 1 mm rounded inner corners, not the exterior recesses.
    walls=[]
    for sign in (-1,1):
        y=INNER_Y/2 if sign>0 else -INNER_Y/2-SNAP_LINER
        x=INNER_X/2 if sign>0 else -INNER_X/2-WALL
        targets=[block(-INNER_X/2+1,y,FLOOR,INNER_X-2,SNAP_LINER,CAVITY_H),
                 block(x,-INNER_Y/2+1,FLOOR,WALL,INNER_Y-2,CAVITY_H)]
        for target in targets:
            missing=target.cut(b).val().Volume();assert missing<1e-7,missing
            walls.append(missing)
    cover=block(-INNER_X/2,-INNER_Y/2,RIM_Z+.5,INNER_X,INNER_Y,.2)
    missing=cover.cut(l).val().Volume();assert missing<1e-7,missing
    base=block(-CARD_X/2,-CARD_Y/2,.3,CARD_X,CARD_Y,FLOOR-.6)
    assert base.cut(b).val().Volume()<1e-7
    # Exclude only actual snap arms, not guides/rim/locating lip.
    rigid=b.cut(snap_arm()).cut(snap_arm().mirror('XZ'))
    travel=[]
    for lift in (0,.25,.5,1,2,3,4,6,8,10,12):
        v=rigid.intersect(l.translate((0,0,lift))).val().Volume()
        assert v<1e-7,(lift,v)
        travel.append(dict(lift_mm=lift,unintended_intersection_mm3=v))
    # Whole free tab/head envelope, with explicit allowance for other axes.
    free=snap_arm().intersect(block(-20,0,ROOT_Z+.7,40,50,ARM_L+5))
    relief=[]
    for inward in (0,.4,.8,1.4,RELIEF_TRAVEL):
        for dx,dz in ((0,0),(.2,.9),(-.2,.9),(.2,-.3),(-.2,-.3)):
            v=free.translate((dx,-inward,dz)).intersect(rigid).val().Volume()
            assert v<1e-7,(inward,dx,dz,v)
            gap=free.translate((dx,-inward,dz)).val().distance(rigid.val())
            assert gap>.05,(inward,dx,dz,gap)
        relief.append(inward)
    # Assumed fingertip ellipse (12 mm along X, 18 mm along Y) approaches
    # vertically in either internal end well; overlap with card edge is intended.
    access=[]
    for sign in (-1,1):
        finger=cq.Workplane('XY').center(sign*(CARD_X/2+3.5),0).ellipse(6,9).extrude(RIM_Z+5).translate((0,0,FLOOR+.2))
        v=finger.intersect(b).val().Volume();assert v<1e-7,v
        access.append(dict(side=sign,ellipse_mm=[12,18],vertical_sweep_z_mm=[FLOOR+.2,FLOOR+.2+RIM_Z+5],body_intersection_mm3=v))
    beam=rectangular_cantilever(length_mm=ARM_L,width_mm=ARM_W,thickness_mm=ARM_T,
        youngs_modulus_MPa=1200,tip_displacement_mm=OVERLAP)
    cam=circular_cam_detent(stiffness_N_mm=beam['stiffness_N_mm'],radius_sum_mm=2*CAM_R,
        transverse_spacing_mm=LID_CAM_Y-HEAD_Y)
    # Contents weight is a separate, cheap question from snap passage. A
    # deliberately assumed 250 g payload at 2 g shares between two catches.
    # This ideal axial-plus-eccentric beam screen is not a retention rating.
    load=.25*9.81*2/2
    eccentricity=2.5
    area=ARM_W*ARM_T;inertia=ARM_W*ARM_T**3/12
    retention_strain=(load/area+load*eccentricity*(ARM_T/2)/inertia)/1200
    return dict(capacity=dict(count=COUNT,source=str(SWATCH_SOURCE.relative_to(SWATCH_SOURCE.parents[2])),
        nominal_stack_mm=[CARD_X,CARD_Y,COUNT*CARD_T],allowance_trial_mm=[CARD_X+1,CARD_Y+1,COUNT*(CARD_T+.1)],
        cavity_mm=[INNER_X,INNER_Y,CAVITY_H],platform_mm=PLATFORM,nominal_top_gap_mm=6.4,
        allowance_stack_displaced_positions_mm=positions),
        enclosure=dict(missing_wall_mm3=walls,missing_cover_mm3=missing,inner_lip_overlap_mm=4,lip_radial_gap_mm=FIT,
            minimum_liner_mm=SNAP_LINER),
        rigid_lid_lift=travel,locked_intersection_at_1mm_lift_mm3=locked,
        locked_at_outward_guide_play_mm3=worst_locked,
        shoulder_overlap_mm=2*(CAM_R**2-.6**2)**.5-(LID_CAM_Y-HEAD_Y),
        minimum_overlap_with_guide_play_mm=2*(CAM_R**2-.6**2)**.5-(LID_CAM_Y-HEAD_Y)-FIT,
        released_rigid_tab_lift_samples_mm=released,release_tab_translation_mm=1.4,
        full_free_tab_relief_mm=relief,extra_axial_envelope_mm=.2,extra_vertical_envelope_mm=[-.3,.9],
        end_finger_access=access,beam_screen=beam,rounded_contact_order_screen=cam,
        retention_weight_screen=dict(assumed_payload_kg=.25,assumed_acceleration_g=2,
            force_per_snap_N=load,assumed_eccentricity_mm=eccentricity,ideal_root_strain=retention_strain,
            limits='Equal load sharing and ideal axial/eccentric beam section; no shell compliance, notch, '
                   'bonding, contact-bearing strength or accidental pulling/dropping rating.'),
        limits='Sampled rigid poses; assumed finger envelope is not comfort; envelope is conservative rigid translation, not a saved elastic mesh; circle formula omits head torsion and ramp additions; enclosure has unsealed seams.')

if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
