"""Flush movable conical head, solid thread and retained successful interfaces."""
import hashlib,json
from pathlib import Path
import cadquery as cq
import m1_design as base
from rotary_conical_design import (printed_axle,screw_print_pose,HEAD_RADIUS,
    RADIAL_SEAM,HEAD_DEPTH,SOCKET_AF,SOCKET_DEPTH,FACE_EXTENSION,SOCKET_ROOF)
from rotary_printed_fastener_design import printed_axle as old_axle,ROOT_RADIUS,TIP
from rotary_refinement_design import build,rotor_pose
from rotary_case_design import CURRENT,case
from rotary_refinement_checks import clear,material

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_conical_design.py','rotary_conical_checks.py','rotary_printed_fastener_design.py',
        'rotary_refinement_design.py','rotary_case_design.py','rotary_r1_design.py','m1_design.py')


def main():
    identity={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}
    screw=printed_axle();old=old_axle();p=case();d=CURRENT;checks=[]
    # The drive roof ends in the shoulder; no hole reaches the thread.
    core=cq.Workplane('XY',origin=(0,0,4.2)).circle(ROOT_RADIUS-.02).extrude(TIP-4.2-.01)
    core_result=material(screw,core,'Complete solid thread core beyond tapered blind-drive roof')
    thread_window=base.box(0,0,(4.2+TIP)/2,10,10,TIP-4.2)
    delta=screw.intersect(thread_window).cut(old).val().Volume()+old.intersect(thread_window).cut(screw).val().Volume()
    assert delta<1e-5,('Successful thread changed',delta)
    baseline=build('wheel',dimensions=CURRENT,fastener='printed-coarse')
    unchanged=[]
    for name in ('body','cap','pivot_nut','detent_pin','stop_pin'):
        a,b=p[name],baseline[name]
        v=a.cut(b).val().Volume()+b.cut(a).val().Volume()
        assert v<1e-5,(name,v)
        unchanged.append(dict(part=name,symmetric_difference_mm3=v))
    # Only the central recess is changed; spring and nose retain exact material.
    hub=(cq.Workplane('XZ',origin=(0,-d.wheel_front-1,d.pivot)).circle(6.7).extrude(-12))
    for name in ('rotor','rotor_rigid'):
        a,b=p[name].cut(hub),baseline[name].cut(hub)
        v=a.cut(b).val().Volume()+b.cut(a).val().Volume()
        assert v<1e-5,(name,v)
    for a in range(0,91,10):
        checks.append(clear(rotor_pose(p,a),p['pivot_axle'],'Conical head clears rotating wheel at shoulder seated'))
    # Cone is an outboard travel stop, not a clamp at the shoulder-seated pose.
    for direction,target in ((-.3,'pivot_axle'),(.4,'body')):
        v=p['rotor'].translate((0,direction,0)).intersect(p[target]).val().Volume()
        assert v>.01,(direction,target,v)
        checks.append(dict(intent='Wheel remains axially captured',shift_y_mm=direction,target=target,blocked_mm3=v))
    # Nominal gap, flush ring and driver floor are measured material questions.
    face=(cq.Workplane('XZ',origin=(0,-d.wheel_front+.01,d.pivot))
          .circle(5.8).circle(2.).extrude(.005))
    flush=material(p['pivot_axle'],face,'Head annulus reaches wheel front plane within .01mm')
    # Check radial clearance in the actual assembled section, at three depths.
    gaps=[]
    for depth in (.2,1.,1.8):
        radius=HEAD_RADIUS-depth
        gap_witness=(cq.Workplane('XZ',origin=(0,-d.wheel_front+depth,d.pivot))
             .circle(radius+RADIAL_SEAM-.01).circle(radius+.01).extrude(.005))
        checks.append(clear(gap_witness,p['rotor'],'Conical running seam clear of wheel'))
        checks.append(clear(gap_witness,p['pivot_axle'],'Conical running seam clear of screw'))
        gaps.append(dict(depth_mm=depth,radial_gap_mm=RADIAL_SEAM))
    assert {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}==identity
    out=dict(source_sha256=identity,solid_core=core_result,thread_difference_mm3=delta,
         unchanged_interfaces=unchanged,checks=checks,flush_face=flush,cone_gap=gaps,
         slope_radius_per_height=1.,socket_across_flats_mm=SOCKET_AF,socket_depth_mm=SOCKET_DEPTH,socket_roof_height_mm=SOCKET_ROOF,
         limits='Rigid CAD only; printed driver strength, cone finish, free rotation and thread fit after head revision remain untested')
    path=ROOT/'notes/rotary_case/conical_cad.json';path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(solid_core=core_result,thread_delta=delta,checks=len(checks),flush=flush)))


if __name__=='__main__':main()
