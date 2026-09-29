"""Targeted capacity, guide path and snap engagement checks; no export audit."""
import json
from components import *
from physical_analysis.screening import rectangular_cantilever, circular_cam_detent
from physical_analysis import PETG_SCREEN

def run():
    b,l=body(),lid()
    stack=block(-CARD_X/2,-CARD_Y/2,FLOOR, CARD_X,CARD_Y,COUNT*CARD_T)
    assert b.intersect(stack).val().Volume()<1e-6, 'Stack envelope hits storage walls'
    assert LID_Z-(FLOOR+COUNT*CARD_T)>=STACK_ALLOWANCE
    # Snap contacts deliberately excluded: they are the separate elastic problem.
    rigid_lid=l.cut(snap_arm())
    # The cam head projects inward beyond the straight beam. Screen its full
    # numerical deflection envelope against the real lid relief, including .3 mm
    # margin and ±.15 mm axial tip drift. This does not model the beam deformation.
    head=cq.Workplane('XY').center(ARM_TIP_X,ARM_Y).circle(CAM_R).extrude(LID_T)
    for dx in (-.15,0,.15):
        for dy in (0,-RELIEF_INWARD_SCREEN/2,-RELIEF_INWARD_SCREEN):
            assert rigid_lid.intersect(head.translate((dx,dy,0))).val().Volume()<1e-6, 'Cam head hits lid relief'
    assert b.intersect(rigid_lid.translate((0,0,LID_Z+1))).val().Volume()>.1, 'Guides do not retain lid vertically'
    # At cam crossing the negative-side guide permits .4 mm nominal sideways
    # play. The catch must still obstruct the head at that extreme, rather than
    # allowing rigid bypass. Local FEA assumes centered guides, so its force is
    # conditional on registration; the strain screen covers the larger bend.
    assert b.intersect(rigid_lid.translate((-4,-.4,LID_Z))).val().Volume()<1e-5
    assert b.intersect(rigid_lid.translate((-4,-.45,LID_Z))).val().Volume()>.1
    assert b.intersect(l.translate((-4,-.4,LID_Z))).val().Volume()>.1, 'Snap can bypass within guide play'
    assert b.intersect(rigid_lid.translate((.5,0,LID_Z))).val().Volume()>.1, 'Back stop missing'
    hits=[]
    for shift in range(-92,1,2):
        volume=b.intersect(rigid_lid.translate((shift,0,LID_Z))).val().Volume()
        if volume>1e-5: hits.append((shift,volume))
    seated=b.intersect(l.translate((0,0,LID_Z))).val().Volume()
    crossing=b.intersect(l.translate((-4,0,LID_Z))).val().Volume()
    assert not hits, hits
    assert seated<1e-5, seated
    assert crossing>.1, 'No snap engagement'
    beam=rectangular_cantilever(length_mm=ARM_ROOT_X-ARM_TIP_X,width_mm=LID_T,
        thickness_mm=ARM_T,youngs_modulus_MPa=PETG_SCREEN.youngs_modulus_MPa,
        tip_displacement_mm=CAM_OVERLAP)
    cam=circular_cam_detent(stiffness_N_mm=beam['stiffness_N_mm'],radius_sum_mm=2*CAM_R,
        transverse_spacing_mm=BASE_CAM_Y-ARM_Y)
    loose_cam=circular_cam_detent(stiffness_N_mm=beam['stiffness_N_mm'],radius_sum_mm=2*CAM_R,
        transverse_spacing_mm=BASE_CAM_Y-ARM_Y+.4)
    return dict(stack_count=COUNT,card_envelope_mm=[CARD_X,CARD_Y,CARD_T],
        cavity_mm=[INNER_X,INNER_Y,CAVITY_H],stack_top_clearance_mm=LID_Z-FLOOR-COUNT*CARD_T,
        rigid_slide_samples=47,rigid_slide_range_mm=[-92,0],step_mm=2,
        rigid_collision_volume_max_mm3=max([v for _,v in hits],default=0),
        seated_intersection_mm3=seated,undeformed_snap_crossing_intersection_mm3=crossing,
        nominal_snap_deflection_mm=CAM_OVERLAP,
        cam_head_relief_checked_mm=dict(inward=RELIEF_INWARD_SCREEN,axial_drift=.15),
        vertical_guide_retention_at_1mm=True,closed_stop_at_half_mm=True,
        inward_guide_play_mm=.4,rigid_snap_bypass_at_guide_limit=False,
        beam_screen=beam,rounded_cam_screen=cam,guide_limit_cam_screen=loose_cam)


if __name__=='__main__': print(json.dumps(run(),indent=2))
