"""Verify uniform normal sections and existing fixture assembly, not printed strength."""
from pathlib import Path
import hashlib,json
from math import sin,cos,radians
import cadquery as cq
import uniform_l20_design as d
from checks import no_overlap,contained

ROOT=Path(__file__).resolve().parent
INPUTS=('l20_standard.py','uniform_l20_design.py','uniform_l20_checks.py','uniform_l20.py',
        'thin_gap_design.py','t_skin_design.py','design.py')


def main():
    p=d.cup();pad=d.pad_print();installed=p.translate((0,0,d.fixture.FLOOR));closed=d.pad_closed()
    for lift in (0,8,20,36):
        no_overlap(installed.translate((0,0,lift)),d.fixture.body())
        no_overlap(closed.translate((0,0,lift)),d.fixture.body())
        no_overlap(closed.translate((0,0,lift)),installed)
    no_overlap(installed,d.fixture.lid_closed());no_overlap(closed,d.fixture.lid_closed())
    seat_gap=closed.val().distance(installed.val())
    lid_gap=closed.val().distance(d.fixture.lid_closed().val())
    assert seat_gap<1e-6 and lid_gap<1e-6,(seat_gap,lid_gap)
    stop=closed.translate((0,0,-.1)).intersect(installed).val().Volume()
    assert stop>.01,stop
    no_overlap(d.block(d.CLEAR,d.CLEAR,30.,z=d.TOTAL),p)
    x=(d.centres(d.SIZE,end_margin=d.LAND)[1]+d.centres(d.SIZE,end_margin=d.LAND)[2])/2
    probes=[]
    def probe(part,point,expected,label):
        actual=part.val().isInside(cq.Vector(*point),1e-6)
        assert actual==expected,(label,point,actual)
        probes.append(dict(label=label,point_mm=point,material=actual))
    for label,part in (('cup floor',p),('lid pad',pad)):
        for z,material in ((.2,True),(.6,True),(1.,False),(1.4,True),(1.8,True)):
            probe(part,(x,x,z),material,label)
        post=d.centres(d.PAD_SIZE if label=='lid pad' else d.SIZE,end_margin=d.LAND)[1]
        probe(part,(post,post,1.),True,label+' post')
    for angle in (0,90,180,270):
        for inset,material in ((.2,True),(.6,True),(1.,False),(1.4,True),(1.8,True)):
            point=cq.Vector(-17+inset,x,15.)
            # Rotate the physical witness to all four walls.
            a=radians(angle);point=(point.x*cos(a)-point.y*sin(a),point.x*sin(a)+point.y*cos(a),15.)
            probe(p,point,material,'upright wall')
    from thin_gap_design import cup as old_cup
    old=old_cup('L20')
    assert not old.val().isInside(cq.Vector(1.1,1.1,.6),1e-6)
    assert p.val().isInside(cq.Vector(1.1,1.1,.6),1e-6)
    out=dict(source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS},
        profile_mm=[d.SKIN,d.CORE,d.SKIN],total_mm=d.TOTAL,
        probes=probes,pad_seat_gap_mm=seat_gap,pad_lid_gap_mm=lid_gap,pad_seat_downward_obstruction_mm3=stop,old_floor_negative_control='Old floor is air at z0.6; new floor contains backing material',
        fixture='Original body/lid, no pad preload; same 30x30x30 clear chamber',
        limits='Rigid geometry only; printed damping, bridging, fit and durability unqualified')
    directory=ROOT/'notes/uniform_l20';directory.mkdir(exist_ok=True)
    (directory/'cad.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':
    main()
