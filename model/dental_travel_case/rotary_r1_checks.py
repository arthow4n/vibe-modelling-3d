"""Actual R1a coupon: clear rotation, nose capture, opening and seating.

The intentionally shallow indexing bump is excluded only from the rigid turn
screen. This does not predict finger effort, jam-nut adjustment or printed wear.
"""
from pathlib import Path
import hashlib
import json
from assembly_geometry import Configuration, PairRequirement, check_pair
from rotary_r1_design import build, configuration, tab_pose, hardware
import m1_design as base

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_r1_design.py','rotary_r1_checks.py','rotary_r1_draw.py',
        'rotary_r1_test.py','rotary_r1_test_assembled.py','rotary_r1_test_open.py','m1_design.py')


def hashes():return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}


def clear(a,b,intent):
    r=check_pair(a,b,PairRequirement(intent,max_overlap_mm3=1e-5))
    r.require_passed()
    return r.to_dict()


def main():
    identity=hashes();p=build();d=p['dimensions']
    # Specific connectivity risks: the keeper crown and the tab's inward nose.
    for name in ('body','cap','tab'):assert len(p[name].val().Solids())==1,name
    states={}
    for state in ('print','locked','unlocked','open'):
        c=Configuration.explicit(configuration(p,state),name=state,
                                 kind='print' if state=='print' else 'operating')
        rows=[]
        for a,b in (('body','cap'),('body','tab'),('cap','tab')):
            r=c.check(a,b,PairRequirement('Distinct R1a components',max_overlap_mm3=1e-5));r.require_passed();rows.append(r.to_dict())
        states[state]=rows
    assert p['body'].val().distance(p['cap'].val())<1e-6
    seat=p['body'].intersect(p['cap'].translate((0,0,-.1))).val().Volume()
    assert seat>.1,'Corner pads must independently stop overclosing'
    turns=[]
    for angle in range(0,91,5):
        tab=tab_pose(p,angle)
        clear(p['cap'],tab,'The tab must sweep past the keeper, not force it aside')
        clear(p['body_core'],tab,'Angular stops permit the intended quarter-turn')
        turns.append(dict(angle_deg=angle,indexing_interference_mm3=p['body'].intersect(tab).val().Volume()))
    assert turns[0]['indexing_interference_mm3']<1e-5
    assert turns[-1]['indexing_interference_mm3']<1e-5
    assert max(r['indexing_interference_mm3'] for r in turns)>.0001
    captures=[]
    guide_poses=((0,0),(.3,0),(-.3,0),(0,.3),(0,-.3),(.2,.2),(-.2,.2),(.2,-.2),(-.2,-.2))
    for sx,sy in guide_poses:
        clear(p['body'],p['cap'].translate((sx,sy,0)),'Seated guide play with independent corner seats')
        for dy in (-.3,0.,.2):
            v=p['cap'].translate((sx,sy,1.4)).intersect(p['tab'].translate((0,dy,0))).val().Volume()
            assert v>.1,('Missing locked capture',sx,sy,dy,v)
            captures.append(dict(cap_shift_mm=[sx,sy],tab_axial_shift_mm=dy,lift_mm=1.4,obstruction_mm3=v))
    flat=p['tab'].cut(p['nose'])
    clear(p['cap'].translate((0,0,1.4)),flat,'Removing the inward nose must remove axial capture')
    release=[]
    for lift in (0.,.5,1.4,4.,12.,27.,31.,36.):
        cap=p['cap'].translate((0,0,lift))
        clear(p['body'],cap,'Unlocked cap clears the guide and seating pads')
        clear(tab_pose(p,90),cap,'Parked tab permits cap withdrawal')
        release.append(lift)
    limits=[]
    for angle in (-10.,100.):
        v=p['body_core'].intersect(tab_pose(p,angle)).val().Volume()
        assert v>.01,('Missing angular stop',angle,v)
        limits.append(dict(angle_deg=angle,obstruction_mm3=v))
    for name,part in hardware(p).items():
        for target in ('body','cap','tab'):
            clear(part,p[target],'Nominal hardware envelope clears printed components')
    # A concrete access concern: small opposing pliers jaws must reach the
    # first nut through the open ring, rather than needing a custom tool.
    tool_access=[]
    for sign in (-1,1):
        jaw=base.box(sign*3.5,-11.8,d.pivot_z,1.4,25.,3.)
        tool_access.append(clear(p['body'],jaw,'Space for a narrow jam-nut holding jaw'))
    assert hashes()==identity
    result=dict(source_sha256=identity,configurations=states,seat_obstruction_mm3=seat,
                turn=turns,locked_capture=captures,unlocked_lifts_mm=release,
                angular_limits=limits,flat_tab_negative_control='no capture',
                tool_jaw_clearance=tool_access,
                scope='R1a nominal rigid geometry plus sampled guide/axial play; indexing interference is not force. Bolt/nut shapes omit threads. Printed fit, radial axle wobble, opposite-edge peel and durability remain unqualified.')
    path=ROOT/'notes/rotary_r1/cad.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
