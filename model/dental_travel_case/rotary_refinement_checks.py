"""Stock-only packaging: complete storage skin, shoulder axle, indexed release.

Rigid motion excludes only the identified curved spring against its detent pin.
Geometric spring travel is not measured torque or a bag-shake qualification.
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
import m1_design as base
from assembly_geometry import PairRequirement,check_pair
from rotary_refinement_design import build,rotor_pose,D,SAMPLE
from rotary_r1_design import yz_prism

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_refinement_design.py','rotary_refinement_checks.py','rotary_refinement_axle.py','rotary_index_test.py',
    'rotary_r1_design.py','m1_design.py','rotary_refinement_wheel.py',
    'rotary_refinement_paddle.py','rotary_refinement_print_study.py','rotary_refinement_open.py')


def hashes():return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}


def clear(a,b,intent):
    r=check_pair(a,b,PairRequirement(intent,max_overlap_mm3=1e-5));r.require_passed()
    return r.to_dict()


def material(part,witness,intent):
    missing=witness.cut(part).val().Volume()
    assert missing<1e-5,(intent,missing)
    return dict(intent=intent,missing_mm3=missing)


def check_size(dimensions,*,contents,fastener):
    p=build('wheel',dimensions=dimensions,fastener=fastener);d=p['dimensions'];rows=[]
    for name in ('body','cap','rotor','pivot_axle'):assert len(p[name].val().Solids())==1,name
    rows.append(clear(p['body'],p['cap'],'Seated shells remain distinct'))
    assert p['body'].val().distance(p['cap'].val())<1e-6
    assert p['body'].intersect(p['cap'].translate((0,0,-.1))).val().Volume()>.1
    for name in ('pivot_axle','pivot_nut'):
        for target in ('body','cap','rotor','body_void','cap_void'):
            rows.append(clear(p[name],p[target],f'{name} clears {target}; no hardware in storage void'))
    skins=[material(p['body'],base.box(0,-23.1,d.seam+d.lap/2,12,2,d.lap),
                    'Complete 2mm front sleeve wall; old hardware track removed')]
    # Protect the unchanged storage surface beside the blind nut pocket.
    low=d.pivot-6.
    body_skin=yz_prism([(24.4,low),(25.6,low),(25.6,d.seam-6),
        (23.3,d.seam),(22.1,d.seam),(24.4,d.seam-6)],-6,12).mirror('XZ')
    skins.append(material(p['body'],body_skin,'At least 1.2mm uninterrupted storage-facing skin below seam'))
    cap_skin=base.box(0,-25.1,(d.rim+d.pivot+23.5)/2,18,1.4,d.pivot+23.5-d.rim)
    skins.append(material(p['cap'],cap_skin,'Original continuous cap inner wall remains intact'))
    # Head below the wheel face; only a smooth printed head is visible.
    beyond=base.box(0,-d.wheel_front-10,d.pivot,30,20,30)
    rows.append(clear(p['pivot_axle'],beyond,'Printed head is recessed below wheel face'))
    # Body/rotor seat carries the tightened shoulder, not the moving wheel.
    assert p['pivot_axle'].val().distance(p['body'].val())<1e-6
    assert p['pivot_axle'].intersect(p['body']).val().Volume()<1e-5
    turns=[]
    for angle in range(0,91,5):
        rotor=rotor_pose(p,angle)
        rows.append(clear(rotor,p['cap'],'Exterior nose clears cap/keeper during turning'))
        rows.append(clear(rotor,p['body_core'],'Only the declared detent pin can contact the spring'))
        rows.append(clear(rotor_pose(p,angle,rigid=True),p['body'],'Detent contact confined to spring region'))
        v=rotor.intersect(p['detent_pin']).val().Volume()
        turns.append(dict(angle_deg=angle,spring_pin_rigid_overlap_mm3=v))
    assert turns[0]['spring_pin_rigid_overlap_mm3']<1e-5
    assert turns[-1]['spring_pin_rigid_overlap_mm3']<1e-5
    assert max(r['spring_pin_rigid_overlap_mm3'] for r in turns if 0<r['angle_deg']<=15)>.01
    # The detent barrier starts while the cap is still captured.
    barrier=[]
    for angle in (5,10,15):
        v=p['cap'].translate((0,0,1.5)).intersect(rotor_pose(p,angle)).val().Volume()
        assert v>.01,('Detent must act before release',angle,v)
        barrier.append(dict(angle_deg=angle,lift_mm=1.5,blocked_mm3=v))
    play_barrier=[]
    # The 8.4mm wheel bore around an 8mm journal permits 0.2mm radial play.
    # It must not let the wheel move away from the pin and bypass indexing.
    for sx,sz in ((.2,0),(-.2,0),(0,.2),(0,-.2),(.14,.14),(-.14,-.14)):
        for angle in (10,15):
            v=rotor_pose(p,angle).translate((sx,0,sz)).intersect(p['detent_pin']).val().Volume()
            assert v>1e-5,('Radial play bypasses detent',sx,sz,angle,v)
            play_barrier.append(dict(wheel_shift_xz_mm=[sx,sz],angle_deg=angle,blocked_mm3=v))
    witnesses=[]
    for x,y in ((0,0),(.3,0),(-.3,0),(0,.3),(0,-.3),(.2,.2),(-.2,-.2)):
        rows.append(clear(p['body'],p['cap'].translate((x,y,0)),'Seated guide play'))
        for axial in (-.3,0,.2):
            v=p['cap'].translate((x,y,1.5)).intersect(p['rotor'].translate((0,axial,0))).val().Volume()
            assert v>.01,('Missing capture with guide/axle play',x,y,axial,v)
            witnesses.append(dict(shift_mm=[x,y],axle_shift_mm=axial,lift_mm=1.5,blocked_mm3=v))
    for lift in (0,.5,1.5,5,15,30,45,95):
        cap=p['cap'].translate((0,0,lift))
        rows.append(clear(p['body'],cap,'Unlocked cap clears body'))
        rows.append(clear(rotor_pose(p,90),cap,'Parked nose permits withdrawal'))
    if contents:
        tube=base.box(0,0,82,55,40,160)
        for shift in (0,30,90,160,204):
            for name in ('body','pivot_axle','pivot_nut'):
                rows.append(clear(tube.translate((0,0,shift)),p[name],'Centred 55x40 tube passage; no shifted loading axis'))
        brush=cq.Workplane('XY',origin=(0,0,2)).circle(15).extrude(255)
        for name in ('body','cap','pivot_axle','pivot_nut'):
            rows.append(clear(brush,p[name],'Individual 30mm brush envelope'))
    for angle in (-15.,105.):
        assert p['body'].intersect(rotor_pose(p,angle)).val().Volume()>.01
    # Socket envelope with an explicit known-size limit, not a hand model.
    socket=(cq.Workplane('XZ',origin=(0,-d.wheel_front-20,d.pivot)).circle(6.4)
            .polygon(6,8.3/(3**.5/2)).extrude(-(20+d.wheel_front-d.axle_under-.1)))
    for name in ('body','cap','rotor','pivot_axle'):
        rows.append(clear(socket,p[name],'8mm socket, <=12.8mm outside diameter, reaches external hex'))
    out=dict(scope='Indexed rotary geometry; no physical thread/detent/strength qualification',
        checks=rows,protected_skins=skins,turn=turns,
        detent_before_release=barrier,detent_with_radial_play=play_barrier,locked_witnesses=witnesses,
        hardware=fastener,
        nominal_detent_radial_travel_mm=d.detent_radial_travel,
        pivot_head_recess_mm=d.wheel_front-d.axle_front,
        maximum_control_projection_mm=d.wheel_front-d.depth/2,
        guide_track_width_mm=0.,tube_loading_offset_y_mm=0.,
        unknowns=['Printed thread fit','detent force/return/wear','keeper strength',
                  'far-edge peel','bag shake','combined packing','actual socket outside diameter'])
    return out


def main():
    identity=hashes()
    full=check_size(D,contents=True,fastener='legacy-m6')
    sample=check_size(SAMPLE,contents=False,fastener='legacy-m6')
    assert hashes()==identity
    out=dict(source_sha256=identity,full=full,sample=sample)
    path=ROOT/'notes/rotary_refinement/cad.json';path.write_text(json.dumps(out,indent=2)+'\n')
    for name,result in (('full',full),('sample',sample)):
        print(json.dumps(dict(size=name,skins=result['protected_skins'],turn=result['turn'],
            barrier=result['detent_before_release'],head_recess=result['pivot_head_recess_mm'],
            control_projection=result['maximum_control_projection_mm'])))


if __name__=='__main__':main()
