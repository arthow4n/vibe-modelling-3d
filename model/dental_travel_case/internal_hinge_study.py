"""Actual CAD motion controls for the recessed C7 hinge exploration."""
import json
from pathlib import Path
import hashlib
import internal_hinge_design as d

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/internal_hinge'


def inspect():
    records={}
    for size_name,size in (('mini',d.MINI),('full',d.FULL)):
        for kind in d.KINDS:
            p=d.build(kind,size=size)
            moving=p['structural_lid']
            sweep=[]
            for angle in (0,1,2,5,10,20,45,70,90,100,110,120,150,180):
                posed=d.rotate(p,moving,angle)
                hit=sum(mate.intersect(posed).val().Volume() for mate in (p['body'],p['keeper']))
                sweep.append(dict(angle_deg=angle,intersection_mm3=hit))
            operation=[]
            if kind in ('internal_screw','internal_cone'):
                for angle in (0,1,2,5,10,20,45,70,90,100):
                    released=d.rotate(p,p['loop'].translate((0,-3.5,0)),angle)
                    hit=sum(mate.intersect(released).val().Volume() for mate in (p['body'],p['keeper']))
                    assert hit<1e-5,(kind,'loop release',angle,hit)
                    if angle>=20:
                        recovered=d.rotate(p,p['loop'],angle)
                        assert sum(mate.intersect(recovered).val().Volume() for mate in (p['body'],p['keeper']))<1e-5
                    operation.append(dict(angle_deg=angle,released_loop_intersection_mm3=hit))
                assert all(r['intersection_mm3']<1e-5 for r in sweep if r['angle_deg']<=100)
                assert p['keeper'].intersect(p['loop'].translate((0,0,.4))).val().Volume()>.01
            insertion=[]
            if kind=='internal_screw' and size_name=='mini':
                import cadquery as cq
                for c in p['centers']:
                    direction=1 if c<0 else -1  # insert from each outer end
                    for travel in (0,3,6,9,12):
                        start=c-direction*15.5+direction*travel
                        shaft=cq.Workplane('YZ',origin=(start,size.axis_y,size.seam)).circle(1.5).extrude(direction*12)
                        head=cq.Workplane('YZ',origin=(start-direction*3,size.axis_y,size.seam)).circle(3.).extrude(direction*3)
                        envelope=shaft.union(head)
                        hit=sum(m.intersect(envelope).val().Volume() for m in (p['body'],p['lid']))
                        assert hit<1e-5,('hardware insertion',c,travel,hit)
                        insertion.append(dict(center_x_mm=c,travel_mm=travel,intersection_mm3=hit))
            records[size_name+'_'+kind]=dict(
                connected_solids={n:len(p[n].solids().vals()) for n in ('body','lid')},
                valid=all(p[n].val().isValid() for n in ('body','lid')),
                sweep=sweep,released_loop_sweep=operation,screw_insertion=insertion)
            if kind in ('internal_screw','internal_cone'):
                gap=p['body'].val().distance(d.rotate(p,p['lid'],90).val())
                assert gap>.29,(size_name,kind,'print gap',gap)
                records[size_name+'_'+kind]['open90_minimum_surface_gap_mm']=gap
            print(size_name,kind,records[size_name+'_'+kind],flush=True)
    inputs=('internal_hinge_design.py','internal_hinge_study.py','clamshell_design.py','m1_design.py','../sunglasses_case/e_closure.py')
    record=dict(scope='Rigid CAD operation only; unprinted, no force or durability rating',
        source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in inputs},cases=records)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'motion.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':inspect()
