"""Affected full-case relationships; physical feel and impact remain unmeasured."""
import hashlib
import json
from pathlib import Path
from rotary_case_design import CURRENT,case
from rotary_refinement_checks import check_size,clear
from rotary_refinement_design import rotor_pose,seating_stops

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_case_design.py','rotary_case_checks.py','rotary_refinement_design.py',
        'rotary_refinement_checks.py','rotary_printed_fastener_design.py',
        'rotary_r1_design.py','m1_design.py','rotary_conical_design.py')


def hashes():
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}


def main():
    identity=hashes()
    r=check_size(CURRENT,contents=True,fastener='printed-cone')
    p=case();seats=[]
    for stop in seating_stops(CURRENT):
        stop=stop.mirror('XZ')
        assert stop.val().distance(p['cap'].val())<1e-6
        v=stop.intersect(p['cap'].translate((0,0,-.1))).val().Volume()
        assert v>.01
        seats.append(dict(overclose_mm=.1,obstruction_mm3=v))
    # At seated guide extremes and both wheel axial limits the enlarged cap
    # ledge must permit the entire sampled turn, not just LOCK and OPEN.
    turn_play=[]
    g=CURRENT.guide_clearance
    for dx,dy in ((g,0),(-g,0),(0,g),(0,-g)):
        for axial in (-.3,.2):
            for angle in range(0,91,10):
                turn_play.append(clear(rotor_pose(p,angle).translate((0,axial,0)),
                    p['cap'].translate((dx,dy,0)),
                    f'Wide keeper clears turn {angle}; guide {dx,dy}; axle {axial}'))
    r['corner_seats']=seats;r['turn_with_play']=turn_play
    r['guide_clearance_per_side_mm']=g
    r['keeper_span_mm']=CURRENT.keeper_span
    r['keeper_radial_gap_mm']=CURRENT.nose_inner-CURRENT.keeper_radius
    assert hashes()==identity
    out=ROOT/'notes/rotary_case/cad.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(dict(source_sha256=identity,full=r),indent=2)+'\n')
    print(json.dumps(dict(checks=len(r['checks']),turn_play=len(turn_play),seats=seats)))


if __name__=='__main__':main()
