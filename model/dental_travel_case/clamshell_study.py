"""Actual-CAD architectural comparison and short-loop operation screens."""
import json
from pathlib import Path
import hashlib
import clamshell_design as design
from clamshell_design import base, D

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/clamshell'
INPUTS=('clamshell_design.py','clamshell_study.py','m1_design.py','../sunglasses_case/e_closure.py')


def hashes(names):return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}


def inspect():
    rows={}
    for kind in design.KINDS:
        p=design.build(kind)
        for name in ('body','lid','keeper'):
            assert p[name].val().isValid() and len(p[name].solids().vals())==1,(kind,name)
        body,lid,keeper=p['body'],p['lid'],p['keeper']
        closed=body.intersect(lid).val().Volume()
        assert closed<1e-4,(kind,'closed',closed)
        # Original rounded interior, not invented simultaneous packing proxies.
        gauge=base.prism(260,70.2,4,4,43.2)
        cavity_hit=sum(p[n].intersect(gauge).val().Volume() for n in ('body','lid','keeper'))
        assert cavity_hit<1e-4,(kind,'storage intrusion',cavity_hit)
        assert keeper.intersect(lid).val().Volume()<1e-4
        lift=keeper.intersect(p['loop'].translate((0,0,.4))).val().Volume()
        assert lift>.01,(kind,'no flat capture')
        released=p['loop'].translate((0,-3.5,0))
        for z in (0,.4,2,5,9):
            assert body.union(keeper).intersect(released.translate((0,0,z))).val().Volume()<1e-4
        sweep=[]
        if kind!='lift_off':
            # Shell and rotating ear sweep excludes loop against unreleased
            # keeper; the loop is held outward until it has passed the tooth.
            moving=lid.cut(p['loop']).union(p['shell_lid'])
            for angle in (0,1,2,5,10,20,45,70,90,120,150,180):
                posed=moving.rotate((0,p['axis_y'],D.seam),(1,p['axis_y'],D.seam),-angle)
                hit=body.intersect(posed).val().Volume()
                assert hit<1e-4,(kind,'sweep',angle,hit)
                loop=released.rotate((0,p['axis_y'],D.seam),(1,p['axis_y'],D.seam),-angle)
                assert body.union(keeper).intersect(loop).val().Volume()<1e-4,(kind,'released loop',angle)
                if angle>=10:
                    recovered=p['loop'].rotate((0,p['axis_y'],D.seam),(1,p['axis_y'],D.seam),-angle)
                    assert body.union(keeper).intersect(recovered).val().Volume()<1e-4,(kind,'loop return',angle)
                sweep.append(dict(angle_deg=angle,shell_intersection_mm3=hit))
        else:
            moving=lid.cut(p['loop']).union(p['shell_lid'])
            rear_lift=moving.rotate((0,-D.depth/2,D.seam),(1,-D.depth/2,D.seam),2)
            assert body.intersect(rear_lift).val().Volume()<1e-4,'Negative rear-capture control changed'
        rail_faces=[f for f in p['loop'].val().Faces() if abs(f.Center().z-(D.seam-5.8-design.SEATED_GAP))<1e-6 and f.normalAt().z>.99]
        keeper_faces=[f for f in keeper.val().Faces() if abs(f.Center().z-(D.seam-5.8))<1e-6 and f.normalAt().z<-.99]
        assert rail_faces and keeper_faces
        overlap=sum(a.translate((0,0,design.SEATED_GAP)).intersect(b).Area() for a in rail_faces for b in keeper_faces)
        assert overlap>10
        rows[kind]=dict(rear_projection_mm=(2*p['hinge_radius']+.3 if kind!='lift_off' else 4.3),
            nominal_barrel_diameter_mm=(2*p['hinge_radius'] if kind!='lift_off' else None),
            shell_sweep=sweep,closed_intersection_mm3=closed,storage_intrusion_mm3=cavity_hit,
            loop_retaining_intersection_at_point4mm_lift_mm3=lift,
            retaining_faces=dict(loop_normal=[0,0,1],keeper_normal=[0,0,-1],axial_gap_mm=design.SEATED_GAP,
                projected_contact_area_mm2=overlap,radial_release_travel_mm=3.2),
            status=('CAD motion candidate, new hinge and flexure physically unknown' if kind!='lift_off'
                    else 'Rejected: drop-in locators do not positively capture rear lift; extraction mechanism unresolved'))
    # Beam estimates compare operation only, never cap holding force. Roots are
    # ideally fixed; full wall/rail coupling and printed material remain unknown.
    beam={}
    for name,length,t in (('accepted_e',27.5,2.8),('short',20.,1.8)):
        delta=3.2;width=3.;inertia=width*t**3/12
        clear=length-3
        beam[name]=dict(root_to_upper_rail_mm=length,clear_span_to_lower_rail_mm=clear,leaf_thickness_mm=t,release_travel_mm=delta,
            two_leaf_force_E900_to1800_N=[2*3*e*inertia*delta/length**3 for e in (900,1800)],
            estimated_root_surface_strain=1.5*t*delta/length**2,
            effective_length_sensitivity_force_N=[2*3*900*inertia*delta/length**3,2*3*1800*inertia*delta/clear**3],
            effective_length_sensitivity_strain=[1.5*t*delta/length**2,1.5*t*delta/clear**2],
            scope='Ideal straight end-loaded beam; root-to-upper-rail nominal span, lower-rail span sensitivity. No acceptance limit or pull-off prediction')
    # Rail + gripping top exactly retain E contact shape at the inner edge;
    # outer thickness differs. The separate keeper/receiver are unchanged.
    record=dict(scope='C6 computational prototype: dimensional/CAD operation, not force, fatigue, quietness or full-product physical acceptance',
        source_sha256=hashes(INPUTS),interior_straight_extents_mm=[260,70.2,47.2],shell_exterior_mm=[264,74.2,51.2],
        hypotheses=rows,loop_actuation_screen=beam)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'cad.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record),flush=True)


if __name__=='__main__':inspect()
