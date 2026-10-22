"""Replacement compatibility, solid core and mating thread engagement evidence."""
from pathlib import Path
import hashlib,json
import cadquery as cq
from rotary_printed_fastener_design import printed_axle,printed_nut,PITCH,ROOT_RADIUS
from rotary_refinement_design import build,D,SAMPLE,printed_axle as legacy_axle
from rotary_refinement_checks import check_size,clear,material

ROOT=Path(__file__).resolve().parent


def main():
    inputs=('rotary_printed_fastener_design.py','rotary_printed_fasteners.py',
            'rotary_printed_fastener_checks.py','rotary_refinement_design.py',
            'rotary_refinement_checks.py','rotary_r1_design.py','m1_design.py')
    hashes=lambda:{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in inputs}
    identity=hashes();screw=printed_axle();nut=printed_nut()
    # This explicitly tests the suspected empty screw, not just solid validity.
    core=cq.Workplane('XY').circle(ROOT_RADIUS-.02).extrude(10.59)
    filled=material(screw,core,'Uninterrupted solid axial core from head through thread tip')
    middle=cq.Workplane('XY',origin=(0,0,5.)).circle(1.5).extrude(4.)
    legacy_missing=middle.cut(legacy_axle()).val().Volume()
    assert legacy_missing>28.,'Negative control must detect the known hollow old thread'
    export_cores=[]
    # Concrete reported failure: inspect actual delivered STEP material at the
    # failed thread centre, rather than repeating a general STEP reimport audit.
    for name,expected_empty in (('rotary_refinement_axle.step',True),
                                ('rotary_printed_fasteners.step',False)):
        part=cq.importers.importStep(str(ROOT/name))
        missing=middle.cut(part).val().Volume()
        assert missing>28. if expected_empty else missing<1e-5,(name,missing)
        export_cores.append(dict(file=name,missing_core_mm3=missing,
                                 expected_empty=expected_empty))
    for name,part in (('screw',screw),('nut',nut)):
        assert len(part.val().Solids())==1,name
    mating=[]
    for angle in range(0,1081,45):
        retreat=angle/360*PITCH
        posed=screw.rotate((0,0,0),(0,0,1),-angle).translate((0,0,-retreat))
        mating.append(clear(posed,nut,f'Matching helical removal / insertion path at {angle} degrees'))
    # A threaded interface must resist straight withdrawal, not only fit loosely.
    pull=[]
    for dz in (-.6,-1.2):
        v=screw.translate((0,0,dz)).intersect(nut).val().Volume()
        assert v>.05,('No thread engagement',dz,v)
        pull.append(dict(axial_withdrawal_mm=-dz,blocked_mm3=v))
    full=check_size(D,contents=True,fastener='printed-coarse')
    sample=check_size(SAMPLE,contents=False,fastener='printed-coarse')
    # The existing body, cap and wheel can be retained; changing only the pair
    # must not silently widen a bore, move a shoulder or change the spring.
    old=build('wheel',dimensions=SAMPLE,fastener='legacy-m6')
    new=build('wheel',dimensions=SAMPLE,fastener='printed-coarse')
    unchanged=[]
    for name in ('body','cap','rotor'):
        delta=old[name].cut(new[name]).val().Volume()+new[name].cut(old[name]).val().Volume()
        assert delta<1e-5,(name,delta)
        unchanged.append(dict(part=name,symmetric_difference_mm3=delta))
    # Nut slides into the unchanged top-loading slot with the cap removed.
    nut_drop=[]
    for lift in (0,1,3,6,10,16,25):
        nut_drop.append(clear(new['pivot_nut'].translate((0,0,lift)),new['body'],
                              'Printed nut top-loading assembly path'))
    assert hashes()==identity
    out=dict(source_sha256=identity,solid_core=filled,
             legacy_negative_control_missing_mm3=legacy_missing,
             exported_thread_cores=export_cores,helical_path=mating,
             straight_pull_obstruction=pull,unchanged_sample_parts=unchanged,
             nut_insertion=nut_drop,full=full,sample=sample,
             limits='Rigid CAD and nominal fit only; actual fit, force, strength and shake retention unmeasured')
    path=ROOT/'notes/printed_fasteners/cad.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(solid_core=filled,unchanged=unchanged,pull=pull,
                         helical_poses=len(mating),report=str(path))))


if __name__=='__main__':main()
