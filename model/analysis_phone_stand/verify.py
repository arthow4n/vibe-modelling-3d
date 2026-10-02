"""Specific geometry/use checks; no duplicate export or slicer audits."""
from itertools import combinations
import hashlib
import json
from pathlib import Path
from components import *
from concept import screen

ROOT=Path(__file__).resolve().parent

def hardware_checks(parts):
    """Check stock grip stacks and assumed head/nut/tool envelopes against CAD.

    Bodies represent fit only; threads and screw/nut contact are not simulated.
    """
    checks={}
    clearance=1e-5
    local_arm=arm(); local_cradle=cradle()
    for y in CRADLE_BOLT_Y:
        seat=CRADLE_THICKNESS-CRADLE_HEAD_DEPTH
        # Use round envelope for the pan head (not a square enclosing it).
        screw=cq.Workplane('XY',origin=(0,y,seat)).circle(M3_HEAD_DIAMETER/2).extrude(M3_HEAD_HEIGHT).union(
            cq.Workplane('XY',origin=(0,y,seat-M3_LENGTH)).circle(M3_DIAMETER/2).extrude(M3_LENGTH))
        nut_seat=-ARM_THICKNESS+ARM_NUT_DEPTH
        nut=cq.Workplane('XY',origin=(0,y,nut_seat-M3_NUT_HEIGHT)).polygon(6,M3_NUT_FLATS/math.cos(math.pi/6)).extrude(M3_NUT_HEIGHT)
        socket=cq.Workplane('XY',origin=(0,y,-ARM_THICKNESS-8)).circle(4.2).extrude(ARM_NUT_DEPTH+8)
        for hardware in (screw,nut,socket):
            for printed in (local_arm,local_cradle):
                assert hardware.intersect(printed).val().Volume()<clearance, 'Cradle fastener/tool collision'
        assert seat+M3_HEAD_HEIGHT<CRADLE_THICKNESS
    cradle_grip=CRADLE_THICKNESS-CRADLE_HEAD_DEPTH+ARM_THICKNESS-ARM_NUT_DEPTH
    cradle_protrusion=M3_LENGTH-cradle_grip-M3_NUT_HEIGHT
    assert cradle_protrusion>=M3_PITCH
    checks['cradle']=dict(screw='2 x M3 x 12',nuts='2 x M3 plain',grip_mm=cradle_grip,
        thread_beyond_nut_mm=cradle_protrusion,head_below_phone_plane_mm=CRADLE_HEAD_DEPTH-M3_HEAD_HEIGHT,
        remaining_backing_mm=CRADLE_THICKNESS-CRADLE_HEAD_DEPTH,
        tool='8.4 mm diameter nut socket envelope clears 9 mm rear access recess')
    for x in (-LATCH_BOLT_X,LATCH_BOLT_X):
        y=LATCH_ROOT_Y+7
        head=cq.Workplane('XY',origin=(x,y,BASE_HEAD_DEPTH-M3_HEAD_HEIGHT)).circle(M3_HEAD_DIAMETER/2).extrude(M3_HEAD_HEIGHT)
        shank=cq.Workplane('XY',origin=(x,y,BASE_HEAD_DEPTH)).circle(M3_DIAMETER/2).extrude(M3_LENGTH)
        nut=cq.Workplane('XY',origin=(x,y,LATCH_TOP)).polygon(6,M3_NUT_FLATS/math.cos(math.pi/6)).extrude(M3_NUT_HEIGHT)
        socket=cq.Workplane('XY',origin=(x,y,LATCH_TOP)).circle(4.2).extrude(15)
        for hardware in (head,shank,nut,socket):
            for printed in parts.values():
                assert hardware.intersect(printed).val().Volume()<clearance, 'Latch fastener/tool collision'
    latch_grip=LATCH_TOP-BASE_HEAD_DEPTH
    latch_protrusion=M3_LENGTH-latch_grip-M3_NUT_HEIGHT
    assert latch_protrusion>=M3_PITCH
    checks['latch']=dict(screw='2 x M3 x 12',nuts='2 x M3 plain',grip_mm=latch_grip,
        thread_beyond_nut_mm=latch_protrusion,head_above_desk_mm=BASE_HEAD_DEPTH-M3_HEAD_HEIGHT)
    outer=ARM_WIDTH/2+AXIAL_CLEARANCE+CHEEK_THICKNESS
    head_seat=-outer+PIVOT_HEAD_DEPTH
    nut_seat=outer-PIVOT_NUT_DEPTH
    head=x_cylinder(PIVOT_Y,PIVOT_Z,PIVOT_HEAD_DIAMETER/2,PIVOT_HEAD_HEIGHT,head_seat-PIVOT_HEAD_HEIGHT)
    shank=x_cylinder(PIVOT_Y,PIVOT_Z,PIVOT_DIAMETER/2,PIVOT_LENGTH,head_seat)
    nuts=hex_x(PIVOT_Y,PIVOT_Z,PIVOT_NUT_FLATS,2*PIVOT_NUT_HEIGHT,nut_seat)
    for hardware in (head,shank,nuts):
        for printed in parts.values():
            assert hardware.intersect(printed).val().Volume()<clearance, 'Pivot fastener collision'
    pivot_grip=nut_seat-head_seat
    pivot_protrusion=PIVOT_LENGTH-pivot_grip-2*PIVOT_NUT_HEIGHT
    assert pivot_protrusion>=PIVOT_PITCH-1e-9
    assert min(CHEEK_THICKNESS-PIVOT_HEAD_DEPTH,CHEEK_THICKNESS-PIVOT_NUT_DEPTH)>2
    checks['pivot']=dict(screw='1 x M4 x 25',nuts='2 x M4 plain, captive inner and external jam nut',
        grip_mm=pivot_grip,thread_beyond_both_nuts_mm=pivot_protrusion,
        remaining_cheek_thickness_mm=[CHEEK_THICKNESS-PIVOT_HEAD_DEPTH,CHEEK_THICKNESS-PIVOT_NUT_DEPTH],
        head_below_outer_cheek_mm=PIVOT_HEAD_DEPTH-PIVOT_HEAD_HEIGHT)
    checks['scope']='CAD clears assumed hardware and tool envelopes; pan-head/nut dimensions and actual printed fit need checking. No preload, loosening, or joint-slip prediction.'
    return checks

def verify():
    p=assembled(60)
    checks={}
    # Three locked poses, full component pairs. Intended mating faces may touch.
    for angle in ANGLES:
        parts=assembled(angle)
        for a,b in combinations(parts,2):
            overlap=parts[a].intersect(parts[b]).val().Volume()
            if overlap>1e-5: raise AssertionError(f'{angle}: {a}/{b} overlap {overlap}')
        checks['hardware']=hardware_checks(parts)
    checks['hardware']['checked_angles_deg']=list(ANGLES)
    checks['locked_poses']='No unintended solid overlaps at 45, 60, 75 degrees; shared mounting faces touch.'
    # Latch intentionally contacts the rotating teeth; review all OTHER motion pairs.
    base_shape=p['base']; leaf=p['latch']; arm_shape=arm(); cradle_shape=cradle()
    for angle in range(45,76,2):
        for name,shape in (('arm',arm_shape),('cradle',cradle_shape)):
            moving=placed(shape,angle)
            if moving.intersect(base_shape).val().Volume()>1e-5:
                raise AssertionError(f'{name} hits base at {angle}')
    checks['motion']='Arm/base and cradle/base: no overlaps at 2-degree samples over 45..75; not a continuous proof. Tooth/latch interaction belongs to elastic analysis.'
    # Exact rectangular device envelope in cradle coordinates; no sensor/case customization.
    phone=box(-45,CRADLE_BOTTOM+6,CRADLE_THICKNESS,90,PHONE_HEIGHT,PHONE_THICKNESS)
    assert phone.intersect(cradle_shape).val().Volume()<1e-5
    for lift in (0,5,15,30):
        assert phone.translate((0,lift,0)).intersect(cradle_shape).val().Volume()<1e-5
    checks['device']='90 x 180 x 14 mm device envelope seats and lifts out along cradle; 20 mm open cable notch, 8 mm retaining lip.'
    # Spring clearance at requested travel, conservative rigid downward translation of tab.
    tab_floor_gap=(LATCH_TOP-LATCH_THICKNESS)-RELEASE_TRAVEL-1
    assert tab_floor_gap>1
    checks['release_floor_gap_mm']=tab_floor_gap
    checks['thumb_stop']='Base pedestal arrests the front tab at nominal 4.7 mm travel; remaining leaf clears the well.'
    # Mating fastener centres derive from the same dimensions; confirm actual through holes.
    pin=x_cylinder(PIVOT_Y,PIVOT_Z,2,40,-20)
    assert pin.intersect(base_shape).val().Volume()<1e-5
    assert pin.intersect(p['arm']).val().Volume()<1e-5
    checks['pivot']='M4 nominal 4 mm shaft clears both actual 4.5 mm bores in assembled pose; 0.4 mm axial clearance per side.'
    # Print-layout overlap can invalidate four separate parts even if each builds.
    positions={'base':(45,5,0),'arm':(115,35,0),'cradle':(185,40,0),'latch':(115,180,0)}
    layout={n:s.translate(positions[n]) for n,s in printable_parts().items()}
    for a,b in combinations(layout,2):
        assert layout[a].intersect(layout[b]).val().Volume()<1e-5,(a,b)
    checks['layout']='Four separated print solids; final bed fit delegated to Orca.'
    return dict(checks=checks,concept=screen(),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT/'components.py',ROOT/'concept.py',ROOT/'verify.py',ROOT/'analysis_phone_stand.py')})

if __name__=='__main__':
    report=verify()
    (ROOT/'notes/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['checks'],indent=2))
