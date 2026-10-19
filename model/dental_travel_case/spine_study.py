"""C8 actual-CAD use-path and clear-interior comparison, no force calibration."""
import json
from pathlib import Path
import math
from clamshell_study import hashes
import spine_design as d
import internal_hinge_design as old

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'notes/spine'
INPUTS=('spine_design.py','spine_study.py','internal_hinge_design.py','clamshell_design.py','m1_design.py','../sunglasses_case/e_closure.py')


def inspect():
    cases={}
    for size_name,size in (('mini',d.MINI),('full',d.FULL)):
        # Continuous rear plane replaces isolated shelves. The extra .8mm wall
        # is declared explicitly; the clear-space witness does not hide it.
        gauge=d.base.prism(size.width-4,size.depth-4.8,4,4,size.length-8).translate((0,-.4,0))
        body_contents=d.base.prism(size.width-4,size.depth-4.8,4,4,size.seam-4.8).translate((0,-.4,0))
        for kind in ('tpu_spine','edge_pin'):
            p=d.build(kind,size=size);rows=[]
            for n in ('body','lid','keeper'):
                assert p[n].val().isValid() and len(p[n].solids().vals())==1,(size_name,kind,n)
            intrusion=sum(p[n].intersect(gauge).val().Volume() for n in ('body','lid'))
            for angle in (0,1,2,5,10,20,45,70,90,120,150,180):
                cap=d.moving(p,p['structural_lid'],angle)
                hit=sum(cap.intersect(m).val().Volume() for m in (p['body'],p['keeper']))
                released=d.moving(p,p['loop'].translate((0,-3.5,0)),angle)
                release_hit=sum(released.intersect(m).val().Volume() for m in (p['body'],p['keeper']))
                contents_hit=cap.intersect(body_contents).val().Volume()
                spines=[]
                if kind=='tpu_spine':
                    for c in p['centers']:
                        s=d.strap(size,c,angle)
                        spines.append(dict(connected_solids=len(s.solids().vals()),
                            shell_intersection_mm3=sum(s.intersect(m).val().Volume() for m in (p['body'],cap)),
                            contents_intersection_mm3=s.intersect(gauge).val().Volume()))
                rows.append(dict(angle_deg=angle,shell_intersection_mm3=hit,release_intersection_mm3=release_hit,
                    lower_cavity_intersection_mm3=contents_hit,spines=spines))
            cases[size_name+'_'+kind]=dict(closed_cavity_intrusion_mm3=intrusion,poses=rows)
            assert intrusion<1e-5,(size_name,kind,'cavity obstruction',intrusion)
            assert all(r['shell_intersection_mm3']<1e-5 and r['release_intersection_mm3']<1e-5
                and r['lower_cavity_intersection_mm3']<1e-5 for r in rows),(size_name,kind,'motion')
            assert all(s['shell_intersection_mm3']<1e-5 and s['contents_intersection_mm3']<1e-5
                and s['connected_solids']==1 for r in rows for s in r['spines'])
            print(size_name,kind,cases[size_name+'_'+kind],flush=True)
        baseline=old.build('internal_screw',size=old.Size(size.width,size.depth))
        # Both faces of the old open shelf lie within the closed storage region.
        hit=baseline['lid'].intersect(gauge).val().Volume()+baseline['body'].intersect(gauge).val().Volume()
        cases[size_name+'_C7']=dict(closed_cavity_intrusion_mm3=hit,operating_limit_deg=100)
    record=dict(scope='Feasible prescribed folding geometry; constant neutral arclength, not TPU equilibrium, force, fatigue or payload qualification',
        source_sha256=hashes(INPUTS),cases=cases,spine=dict(neutral_length_mm=16,thickness_mm=.8,
            flat_open_radius_mm=16/math.pi,illustrative_outer_fibre_strain=.8*math.pi/32,
            rear_wall_extra_mm=.8,flat_open_back_gap_mm=32/math.pi-.8))
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'motion.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':inspect()
