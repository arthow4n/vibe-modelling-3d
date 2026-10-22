"""Rough-study decisions: external cam clearance, capture and usable passage.

No strength, detent, force, far-edge peel or full packing qualification.
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
import m1_design as base
from assembly_geometry import PairRequirement,check_pair
from rotary_refinement_design import build,rotor_pose,configuration

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_refinement_design.py','rotary_refinement_checks.py',
        'rotary_r1_design.py','m1_design.py','rotary_refinement_wheel.py',
        'rotary_refinement_paddle.py','rotary_refinement_print_study.py','rotary_refinement_open.py')


def hashes():return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}


def clear(a,b,intent):
    r=check_pair(a,b,PairRequirement(intent,max_overlap_mm3=1e-5));r.require_passed()
    return r.to_dict()


def main():
    identity=hashes();p=build('wheel');d=p['dimensions'];rows=[]
    for name in ('body','cap','rotor'):assert len(p[name].val().Solids())==1,name
    rows.append(clear(p['body'],p['cap'],'Seated shells remain distinct'))
    assert p['body'].val().distance(p['cap'].val())<1e-6
    assert p['body'].intersect(p['cap'].translate((0,0,-.1))).val().Volume()>.1
    for name in ('pivot_screw','pivot_nut','pivot_jam','keeper_screw','keeper_nut'):
        for target in ('body','cap','rotor'):
            rows.append(clear(p[name],p[target],'Nominal metal hardware fits its printed surroundings'))
    for angle in range(0,91,5):
        rotor=rotor_pose(p,angle)
        for target in ('body','cap','keeper_screw','keeper_nut'):
            rows.append(clear(rotor,p[target],f'Quarter turn {angle} deg versus {target}'))
    witnesses=[]
    for x,y in ((0,0),(.3,0),(-.3,0),(0,.3),(0,-.3),(.2,.2),(-.2,-.2)):
        cap=p['cap'].translate((x,y,0));pin=p['keeper_screw'].translate((x,y,0))
        rows.append(clear(p['body'],cap,'Guide-play pose including the opened sleeve track'))
        v=pin.translate((0,0,1.5)).intersect(p['rotor']).val().Volume()
        assert v>.01,('Missing head capture',x,y,v)
        witnesses.append(dict(shift_mm=[x,y],lift_mm=1.5,blocked_mm3=v))
    for lift in (0,.5,1.5,5,15,30,45,95):
        cap=p['cap'].translate((0,0,lift))
        rows.append(clear(p['body'],cap,'Unlocked cap clears body'))
        rows.append(clear(rotor_pose(p,90),cap,'Unlocked cap clears wheel'))
        for name in ('keeper_screw','keeper_nut'):
            part=p[name].translate((0,0,lift))
            rows.append(clear(p['body'],part,'Cap keeper hardware clears open-ended guide track'))
            rows.append(clear(rotor_pose(p,90),part,'Parked nose permits keeper withdrawal'))
    # A full-size tube passes the body with an explicitly shifted loading axis;
    # the cap keeper stays with the removed cap. Contents not loaded together.
    tube=base.box(0,1.7,82,55,40,160)
    for shift in (0,30,90,160,204):
        moved=tube.translate((0,0,shift))
        for name in ('body','pivot_screw','pivot_nut','pivot_jam'):
            rows.append(clear(moved,p[name],'55x40 tube straight loading passage at Y+1.7'))
    brush=cq.Workplane('XY',origin=(0,0,2)).circle(15).extrude(255)
    for name in ('body','cap','keeper_screw','keeper_nut','pivot_screw','pivot_nut','pivot_jam'):
        rows.append(clear(brush,p[name],'Individual 30mm brush envelope, not combined packing'))
    limits=[]
    for angle in (-15.,105.):
        v=p['body'].intersect(rotor_pose(p,angle)).val().Volume()
        assert v>.01,('Missing wheel travel stop',angle,v)
        limits.append(dict(angle_deg=angle,blocked_mm3=v))
    assert hashes()==identity
    out=dict(scope='Rough R1 external screw-head keeper feasibility; no adopted case or physical qualification',
             source_sha256=identity,checks=rows,locked_witnesses=witnesses,travel_stops=limits,
             nominal_keeper_head_diameter_mm=5.5,nominal_keeper_head_height_mm=2.,
             nominal_nose_clearance_mm=.8,guide_track_width_mm=10.4,
             tube_loading_offset_y_mm=1.7,unknowns=['actual screw heads','printed fit','position detent',
             'strength','far-edge peel','combined packing','handling','PLA/PETG behavior'])
    path=ROOT/'notes/rotary_refinement/cad.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='checks'}))


if __name__=='__main__':main()
