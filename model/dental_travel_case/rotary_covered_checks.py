"""Keyed co-rotation, matching grip profile and complete covered-case operation."""
import hashlib,json
from pathlib import Path
import cadquery as cq
import m1_design as base
from rotary_covered_design import (covered_case,face_pose,printed_axle,EXTENSION,
    KEY_ENGAGEMENT,grip_outline,SKIRT_OFFSET,SKIRT_CLEARANCE,FACE_THICKNESS)
from rotary_case_design import case as exposed_case
from rotary_refinement_design import rotor_pose,wheel_plate
from rotary_refinement_checks import check_parts,clear,material
from rotary_printed_fastener_design import printed_axle as old_axle,ROOT_RADIUS,TIP

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_covered_design.py','rotary_covered_checks.py','rotary_refinement_design.py',
 'rotary_refinement_checks.py','rotary_conical_design.py','rotary_case_design.py',
 'rotary_printed_fastener_design.py','rotary_r1_design.py','m1_design.py')


def hashes():
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}


def main():
    identity=hashes();p=covered_case();d=p['dimensions'];rows=[]
    full=check_parts(p,contents=True)
    for name in ('facecap','rotor','pivot_axle'):
        assert p[name].val().isValid(),name
        assert len(p[name].val().Solids())==1,name
    rows.append(clear(p['facecap'],p['rotor'],'Keys clear pockets; hub spacer seats without interference'))
    assert p['facecap'].val().distance(p['rotor'].val())<1e-6
    assert p['facecap'].translate((0,.05,0)).intersect(p['rotor']).val().Volume()>.01
    baseline=exposed_case();preserved=[]
    for name in ('body','cap','pivot_nut'):
        a,b=p[name],baseline[name]
        v=a.cut(b).val().Volume()+b.cut(a).val().Volume();assert v<1e-5,(name,v)
        preserved.append(dict(part=name,symmetric_difference_mm3=v))
    # The cup follows a parallel offset of the same scallops, rather than
    # changing to a circular puck. Compare the delivered face's outer contour.
    local=(p['facecap'].mirror('XZ').translate((0,-p['control_front'],-d.pivot))
           .rotate((0,0,0),(1,0,0),-90))
    slab=local.intersect(base.box(0,0,.6,50,50,.04))
    wire=slab.faces('>Z').val().outerWire().translate((0,0,-.62))
    amid=cq.Workplane('XY').add(wire).toPending().extrude(.04)
    bmid=grip_outline(d,offset=SKIRT_OFFSET).extrude(.04)
    outline_delta=amid.cut(bmid).val().Volume()+bmid.cut(amid).val().Volume()
    assert outline_delta<1e-5,outline_delta
    # A continuous wall covers the whole wheel edge, including the face gap.
    # Explicit outward spring-envelope translations are clearance screens,
    # not predictions of a deflected spring shape or its required force.
    spring=p['rotor'].cut(p['rotor_rigid'])
    spring_screens=[]
    from math import sin,cos,radians
    for angle in range(0,360,30):
        shift=(.35*cos(radians(angle)),0,.35*sin(radians(angle)))
        spring_screens.append(clear(p['facecap'],spring.translate(shift),
                                    'Cover clears 0.35mm translated spring envelope'))
    for height in (FACE_THICKNESS+.2,3.,p['control_front']-d.wheel_back-.3):
        band=(grip_outline(d,offset=SKIRT_OFFSET-.25).extrude(.04)
              .cut(grip_outline(d,offset=SKIRT_CLEARANCE+.25).extrude(.04))
              .translate((0,0,height)))
        material(local,band,'Continuous wraparound wall behind hidden face gap')
    # Only the hub changes. The flexible track and the locking nose stay exact.
    hub=cq.Workplane('XZ',origin=(0,-45,d.pivot)).circle(8.9).extrude(-20)
    for name in ('rotor','rotor_rigid'):
        a,b=p[name].cut(hub),baseline[name].cut(hub)
        v=a.cut(b).val().Volume()+b.cut(a).val().Volume();assert v<1e-5,(name,v)
    turns=[]
    for angle in range(0,91,5):
        cover=face_pose(p,angle);wheel=rotor_pose(p,angle)
        for name in ('body','cap','pivot_axle','pivot_nut'):
            rows.append(clear(cover,p[name],'Moving facecap clears '+name))
        rows.append(clear(cover,wheel,'Keys remain registered through common rotation'))
        turns.append(angle)
    for lift in (0,1.5,5,30,95):
        rows.append(clear(face_pose(p,90),p['cap'].translate((0,0,lift)),
                          'Covered control permits unlocked cap withdrawal'))
    # Assembly insertion is from the front, not through the spring/pins.
    for distance in (0,.2,.5,1.,1.6,3.,6.):
        rows.append(clear(p['facecap'].translate((0,-distance,0)),p['rotor'],
                          'Facecap keys enter pockets along the axle'))
    # Relative turn MUST hit the keys in both directions, even with all the
    # conservative 0.7mm relative axial separation still below disengagement.
    # The screw and body obstruct the independent extremes before that sum.
    assert p['facecap'].translate((0,-.3,0)).intersect(p['pivot_axle']).val().Volume()>.01
    assert p['rotor'].translate((0,.4,0)).intersect(p['body']).val().Volume()>.01
    coupling=[]
    for separation in (0.,.3,.5,.7):
        for dx,dz in ((0,0),(.1,0),(-.1,0),(0,.1),(0,-.1)):
            for angle in (-2.,2.):
                cover=face_pose(p,angle).translate((dx,-separation,dz))
                v=cover.intersect(p['rotor']).val().Volume()
                assert v>1e-5,('Lost positive key drive',separation,dx,dz,angle,v)
                coupling.append(dict(axial_separation_mm=separation,shift_xz_mm=[dx,dz],
                                     relative_angle_deg=angle,obstruction_mm3=v))
    negative=[]
    for angle in (-2.,2.):
        bare=p['facecap_without_keys'].rotate((0,0,d.pivot),(0,1,d.pivot),angle)
        negative.append(clear(bare,p['rotor'],'Removing drive keys removes the relative-turn stop'))
    screw=printed_axle();old=old_axle()
    core=cq.Workplane('XY',origin=(0,0,4.2)).circle(ROOT_RADIUS-.02).extrude(TIP-4.2-.01)
    filled=material(screw,core,'Solid full thread core below blind socket roof')
    window=base.box(0,0,(4.2+TIP)/2,10,10,TIP-4.2)
    delta=screw.intersect(window).cut(old).val().Volume()+old.intersect(window).cut(screw).val().Volume()
    assert delta<1e-5,delta
    assert hashes()==identity
    out=dict(source_sha256=identity,full=full,checks=rows,turn_angles=turns,
      positive_key_witnesses=coupling,key_removed_controls=negative,outline_difference_mm3=outline_delta,
      unchanged_parts=preserved,solid_thread_core=filled,thread_difference_mm3=delta,
      extra_projection_mm=p['control_front']-d.wheel_front,axle_face_extension_mm=EXTENSION,
      nominal_key_engagement_mm=KEY_ENGAGEMENT,
      wraparound=dict(radial_clearance_mm=SKIRT_CLEARANCE,outer_offset_mm=SKIRT_OFFSET,
          axial_overlap_mm=d.wheel_front-d.wheel_back,spring_envelope_checks=spring_screens),
      limits='Rigid clearance and positive engagement, not measured backlash, printed torque capacity, force, comfort or durability')
    target=ROOT/'notes/covered_rotary/cad.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(full_checks=len(full['checks']),cover_checks=len(rows),
          coupling_poses=len(coupling),outline_difference_mm3=outline_delta,solid_core=filled)))


if __name__=='__main__':main()
