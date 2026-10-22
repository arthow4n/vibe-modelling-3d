"""Changed coupon: open end frames, unchanged local mechanism, shorter guide."""
from pathlib import Path
import hashlib,json
import cadquery as cq
import m1_design as base
from rotary_quick_design import build,QUICK
from rotary_refinement_design import build as build_case,SAMPLE,rotor_pose
from rotary_refinement_checks import clear,material

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_quick_design.py','rotary_quick_test.py','rotary_quick_assembled.py',
        'rotary_quick_checks.py','rotary_refinement_design.py',
        'rotary_printed_fastener_design.py','rotary_refinement_checks.py',
        'rotary_r1_design.py','m1_design.py')


def main():
    hashes=lambda:{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}
    identity=hashes();p=build();d=QUICK
    old=build_case('wheel',dimensions=SAMPLE,fastener='printed-coarse')
    rows=[];unchanged=[]
    for name in ('body','cap','rotor'):
        assert len(p[name].val().Solids())==1,('Opening disconnected part',name)
    # Exact local changes only: shorter shells and cut end panels. The original
    # wheel and threaded pair carry their existing source-associated evidence.
    for name,zone in (('body',base.box(0,0,22.25,100,100,39.5)),
                      ('cap',base.box(0,0,33.5,100,100,13.))):
        a=old[name].intersect(zone);b=p[name].intersect(zone)
        delta=a.cut(b).val().Volume()+b.cut(a).val().Volume()
        assert delta<1e-5,(name,delta)
        unchanged.append(dict(part=name,intent='Retained local walls, guide and mechanism',difference_mm3=delta))
    for name in ('rotor','pivot_axle','pivot_nut'):
        delta=old[name].cut(p[name]).val().Volume()+p[name].cut(old[name]).val().Volume()
        assert delta<1e-5,(name,delta)
        unchanged.append(dict(part=name,intent='Identical complete component',difference_mm3=delta))
    rows.append(clear(p['body'],p['cap'],'Seated shells have no interference'))
    assert p['body'].val().distance(p['cap'].val())<1e-6
    assert p['body'].intersect(p['cap'].translate((0,0,-.1))).val().Volume()>.1
    # Large real openings with a continuous frame; not just thinner end panels.
    for name,z in (('body',-1.),('cap',d.length-3.)):
        opening=base.prism(48.,28.,2.,z,4.)
        rows.append(clear(p[name],opening,'Through end opening permits finger purchase'))
    skins=material(p['body'],base.box(0,-23.1,d.seam+d.lap/2,12,2,d.lap),
                   'Full 2mm front guide wall retained at the shorter sleeve')
    gaps=[]
    for x,y in ((35.6,0),(-35.6,0),(0,24.1),(0,-24.1)):
        point=cq.Vertex.makeVertex(x,y,32.)
        assert point.distance(p['body'].val())<1e-6
        gap=point.distance(p['cap'].val());assert abs(gap-.3)<1e-6
        gaps.append(dict(sleeve_point_mm=[x,y,32.],cap_gap_mm=gap))
    captures=[]
    for x,y in ((0,0),(.3,0),(-.3,0),(0,.3),(0,-.3),(.2,.2),(-.2,-.2)):
        cap=p['cap'].translate((x,y,0))
        rows.append(clear(p['body'],cap,'Short-guide seated play'))
        for axial in (-.3,0,.2):
            v=cap.translate((0,0,1.5)).intersect(p['rotor'].translate((0,axial,0))).val().Volume()
            assert v>.01,(x,y,axial,v)
            captures.append(dict(cap_shift_mm=[x,y],wheel_axial_shift_mm=axial,blocked_mm3=v))
    for lift in (0,.5,1.5,5,15,18,30,50):
        cap=p['cap'].translate((0,0,lift))
        rows.append(clear(p['body'],cap,'Open-end cap straight withdrawal'))
        rows.append(clear(rotor_pose(p,90),cap,'Unlocked wheel permits cap removal'))
    for angle in (0,5,10,15,45,90):
        rotor=rotor_pose(p,angle)
        rows.append(clear(rotor,p['cap'],'Turn still clears shortened cap'))
        rows.append(clear(rotor,p['body_core'],'Only existing detent pin contacts leaf'))
    for angle in (5,10,15):
        assert p['cap'].translate((0,0,1.5)).intersect(rotor_pose(p,angle)).val().Volume()>.01
    assert hashes()==identity
    out=dict(source_sha256=identity,closed_height_mm=d.length,body_height_mm=d.seam+d.lap,
        cap_height_mm=d.length-d.rim,sleeve_height_mm=d.lap,engaged_guide_mm=d.lap-d.reveal,
        reveal_mm=d.reveal,end_opening_mm=[50,30],hole_edge_chamfer_mm=.4,
        unchanged=unchanged,guide_gap_witnesses=gaps,guide_skin=skins,
        checks=rows,capture_witnesses=captures,
        limits='Shorter guide and open end frames change stiffness and tilt restraint. No full-case peel, shaking, force or printed-fit qualification. Chamber-overheat cause is a user hypothesis, not isolated evidence.')
    path=ROOT/'notes/quick_rotary/cad.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(heights=[d.length,d.seam+d.lap,d.length-d.rim],gaps=gaps,
                          unchanged=unchanged,report=str(path))))


if __name__=='__main__':main()
