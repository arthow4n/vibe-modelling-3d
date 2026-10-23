"""Selected-gap material witnesses and actual fixture/pad seating paths."""
from pathlib import Path
import json,hashlib
from math import sin,cos,radians
import cadquery as cq
import gap_comparison_design as d
from checks import no_overlap
ROOT=Path(__file__).resolve().parent
INPUTS=('gap_comparison_design.py','gap_comparison_checks.py','gap_G08.py','gap_G16.py',
        'l20_standard.py','design.py','t_skin_design.py')


def check(name):
    v=d.variant_named(name);cup=d.cup(name);pad=d.pad_print(name)
    installed=cup.translate((0,0,d.fixture.FLOOR));closed=d.pad_closed(name)
    for lift in (0,8,20,36):
        no_overlap(installed.translate((0,0,lift)),d.fixture.body())
        no_overlap(closed.translate((0,0,lift)),d.fixture.body())
        no_overlap(closed.translate((0,0,lift)),installed)
    no_overlap(installed,d.fixture.lid_closed());no_overlap(closed,d.fixture.lid_closed())
    seat=closed.val().distance(installed.val());lid=closed.val().distance(d.fixture.lid_closed().val())
    assert seat<1e-6 and lid<1e-6,(name,seat,lid)
    obstruction=closed.translate((0,0,-.1)).intersect(installed).val().Volume();assert obstruction>.01
    no_overlap(d.block(v.clear,v.clear,v.clear,z=v.total),cup)
    probes=[]
    def probe(part,point,expected,label):
        actual=part.val().isInside(cq.Vector(*point),1e-6);assert actual==expected,(name,label,point,actual)
        probes.append(dict(label=label,point_mm=point,material=actual))
    section=((.2,True),(.6,True),(d.SKIN+v.gap/2,False),
             (d.SKIN+v.gap+.2,True),(v.total-.2,True))
    for label,part in (('floor',cup),('pad',pad)):
        for z,material in section:probe(part,(1.1,1.1,z),material,label)
        for z in (d.SKIN+.1,d.SKIN+v.gap-.1):
            probe(part,(-6.6,-6.6,z),True,label+' post')
        no_overlap(d.label(name,d.PAD_SIZE if label=='pad' else d.SIZE),part)
    height=(d.wall_rows(name)[2]+d.wall_rows(name)[3])/2
    for angle in (0,90,180,270):
        a=radians(angle)
        for inset,material in section:
            x,y=-17+inset,-4.4
            probe(cup,(x*cos(a)-y*sin(a),x*sin(a)+y*cos(a),height),material,'wall')
    out=dict(source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS},
        variant=name,skin_mm=d.SKIN,gap_mm=v.gap,total_mm=v.total,clear_cube_mm=v.clear,
        probes=probes,pad_seat_gap_mm=seat,pad_lid_gap_mm=lid,pad_stop_obstruction_mm3=obstruction,
        limits='Rigid section/fit only; cavity size changes with gap. No measured damping, stiffness, sag or durability.')
    directory=ROOT/'notes/gap_comparison'/name;directory.mkdir(parents=True,exist_ok=True)
    (directory/'cad.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(variant=name,gap_mm=v.gap,clear_cube_mm=v.clear,probes=len(probes))))


if __name__=='__main__':
    for name in ('G08','G16'):check(name)
