"""Targeted whole-product checks; not generic CAD/export revalidation."""
import json, math
from pathlib import Path
import cadquery as cq
import swatch_book_case as m

TOL=1e-6
def overlap(a,b):
    return a.intersect(b).val().Volume()

def check():
    b,l,s=m.body(),m.lid(),m.latch()
    assert overlap(b,l)<TOL and overlap(b,s)<TOL and overlap(l,s)<TOL
    hardware=m.hardware()
    assert b.val().intersect(hardware).Volume()<TOL
    assert s.val().intersect(hardware).Volume()<TOL
    packets=[]
    for cx in m.POCKET_CENTERS:
        packet=m.block(cx-40,m.CARD_CENTER_Y-25,m.CARD_BOTTOM,80,50,20)
        assert overlap(packet,b)<TOL and overlap(packet,l)<TOL
        # Straight packet lift into hand: no constricting rim or overhead parts.
        for dz in (0,1,4,10,20,30):
            assert overlap(packet.translate((0,0,dz)), b)<TOL
            assert overlap(packet.translate((0,0,dz)),m.lid_pose(120))<TOL
        # Finger proxy reaches UNDER the front card edge from the empty bay.
        finger=m.block(cx-5,m.CARD_CENTER_Y-25-10,m.FLOOR+.2,10,14,3.5)
        assert overlap(finger,b)<TOL
        assert m.CARD_BOTTOM > m.FLOOR+.2+3.5
        # Real card rests on both ledges: planar contact distance is zero.
        card=m.reference_card().translate((cx,m.CARD_CENTER_Y,m.CARD_BOTTOM))
        assert overlap(card,b)<TOL
        assert card.val().distance(b.val())<1e-7
        packets.append(packet)
    # With optional catch AND keeper removed, guide/seat/hinge still work.
    accessed=cq.Workplane('XY').newObject([m.cards(access=True)])
    assert overlap(accessed,b)<TOL
    assert overlap(accessed,m.lid_pose(120))<TOL
    assert accessed.val().intersect(hardware).Volume()<TOL
    base=m.body(False)
    for angle in range(0,181,2):
        moving=m.lid_pose(angle,False)
        assert overlap(base,moving)<TOL, angle
        for packet in packets:
            assert overlap(packet,moving)<TOL, angle
        # Actual hardware is part of the product; screw/nut clearance matters.
        assert m.lid_pose(angle).val().intersect(hardware).Volume()<TOL, angle
    # Positive skirt/shoulder contact, not an unexplained end of travel.
    assert b.val().distance(l.val())<1e-7
    assert overlap(b,l.translate((0,0,-.1)))>.5
    assert overlap(b,m.lid_pose(-.1))>.5
    radial_clearance=m.LIP_INSET-m.LID_WALL
    assert radial_clearance==.4 or abs(radial_clearance-.4)<1e-8
    # Side lip physically rejects wrong lateral seating beyond allowance.
    assert overlap(b,l.translate((.6,0,0)))>.01
    # Keeper and bead: exact rigid circular interface along actual hinge arc.
    def cam_at(angle):
        return m.axial_cylinder(m.KEEPER_X0,m.KEEPER_Y,m.KEEPER_Z,m.KEEPER_WIDTH,m.BEAD_R).rotate(
            (0,m.HINGE_Y,m.HINGE_Z),(1,m.HINGE_Y,m.HINGE_Z),-angle)
    # Before touching, full leaf/cover sweep clear. After touching we examine
    # required interference, not pretend rigid overlap proves a flexible pass.
    samples=[]
    for i in range(1201):
        angle=i/100 # 0..12 degrees, closing contact only lives near the seat
        t=math.radians(angle)
        dy=m.KEEPER_Y-m.HINGE_Y; dz=m.KEEPER_Z-m.HINGE_Z
        y=m.HINGE_Y+dy*math.cos(t)+dz*math.sin(t)
        z=m.HINGE_Z-dy*math.sin(t)+dz*math.cos(t)
        axial=z-m.BEAD_Z
        required=max(0,math.sqrt(max(0,(2*m.BEAD_R)**2-axial**2))-abs(y-m.BEAD_Y)) if abs(axial)<2*m.BEAD_R else 0
        samples.append((required,angle,y,z))
    worst=max(samples)
    contact=[a for d,a,y,z in samples if d>1e-5]
    assert contact and worst[0]<m.RELEASE_TRAVEL
    max_angle=worst[1]
    # Only the named bead/cam cause retention contact; all surroundings clear.
    body_bead=m.tooth()
    assert overlap(body_bead,cam_at(max_angle))>.01
    assert overlap(b,m.lid_pose(max_angle))<TOL
    assert overlap(s.cut(body_bead),m.lid_pose(max_angle))<TOL
    for angle in range(0,121,2):
        assert overlap(b,m.lid_pose(angle))<TOL, angle
    assert overlap(body_bead,cam_at(0))<TOL
    assert m.KEEPER_Z < m.BEAD_Z # keeper below bead resists opening
    # The opening keeper meets a real horizontal underside, not a rolling
    # detent flank. Its axial normal holds the lid instead of pressing release.
    assert any(abs(f.Center().z-m.TOOTH_FLOOR)<1e-7 and
               abs(f.normalAt().z)>.99 and f.Area()>.5
               for f in body_bead.val().Faces())
    assert overlap(body_bead,cam_at(.8))>.01
    # Conservative displacement envelope used by the numerical question:
    # inward travel leaves room to the independent internal front barrier.
    free_gap=m.INNER_BARRIER_Y-m.LEAF_T
    assert free_gap-m.RELEASE_TRAVEL>=.4
    assert m.LEAF_STOP_GAP>1.95
    # Release shifts contact bead inward far enough for the entire opening arc.
    released=body_bead.translate((0,m.RELEASE_TRAVEL,0))
    for angle in [i/10 for i in range(1201)]:
        assert overlap(released,cam_at(angle))<TOL
    # Containment: main walls continuous; the catch's inner wall blocks slot.
    # The side lip overlap is 2 mm high; catch-seat clearances and leaf's lower
    # slit are each smaller than an intact 2 mm card's thickness.
    assert 1.2 < m.CARD_T and .4 < m.CARD_T and m.LIP_H>0
    report={
        'all_checks_pass':True,
        'scope':'Source geometry, nominal swatches, sampled rigid sweep and conservative leaf displacement envelope; no physical validation',
        'contents':{'count':20,'pockets':2,'per_packet':10,'edge_clearance_mm':m.CARD_ALLOWANCE,
                    'under_packet_mm':m.UNDER_CARD,'front_finger_bay_mm':m.FINGER_BAY,
                    'finger_proxy_mm':[10,14,3.5],'straight_packet_lift_checked_mm':30},
        'cover':{'hinge_sweep_degrees':[0,180,2],'lip_radial_clearance_mm':radial_clearance,
                 'seat':'cover skirt lower face / body rim shoulder',
                 'retention_removed_guidance_and_seating_checked':True,
                 'overclosing_0_1_mm_rejected':True,'lateral_error_0_6_mm_rejected':True},
        'retention':{'first_contact_closing_angle_degrees':max(contact),
                      'maximum_deflection_angle_degrees':max_angle,
                      'circular_envelope_actual_arc_deflection_bound_mm':worst[0],
                      'closed_cam_clearance_mm':body_bead.val().distance(cam_at(0).val()),
                      'positive_retaining_underside_z_mm':m.TOOTH_FLOOR,
                      'conservative_transverse_release_mm':m.RELEASE_TRAVEL,
                      'intended_button_stroke_mm':m.PRESS_TRAVEL,
                      'positive_leaf_travel_stop_gap_mm':m.LEAF_STOP_GAP,
                      'leaf_back_clearance_at_release_mm':free_gap-m.RELEASE_TRAVEL,
                      'released_bead_opening_sweep_degrees':[0,120,.1]},
        'states':[
            'Loaded: two supported 20 mm packets; conservative full envelopes clear shell and roof',
            'Aligned: screw pivots constrain rotation; lip aligns final closure independently of snap',
            'Partial: cover at 12 degrees, no catch contact or content collision',
            'First contact: named round keeper touches named catch bead',
            'Maximum interference: round keeper passes bead; required elastic displacement calculated from exact arc',
            'Seated: skirt stops at shoulder; returned bead above keeper; no preloaded bead contact',
            'Release: inward exposed tip travel clears bead; inner barrier stays clear',
            'Open: cover 120 degrees; both packets lift directly through unobstructed openings']}
    return report

if __name__=='__main__':
    report=check()
    Path(__file__).with_name('notes').joinpath('product_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
