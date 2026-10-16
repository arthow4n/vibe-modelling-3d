"""Inspection-only feasibility study; does not revise the printable liner.

Left: existing solid corner; right: curved air core with radial supports.
Run through execute.py for geometric witness results, evaluate_model.py for views.
No exports or slicing are performed by this module.
"""
from functools import cache
from math import asin, cos, sin, radians, degrees
import json
import cadquery as cq
import design as d


def corner_locations():
    length,width,_,radius = d.dimensions()
    return tuple((sx,sy,sx*(length/2-radius),sy*(width/2-radius))
                 for sx in (-1,1) for sy in (-1,1))


def quarter_slots():
    _,_,height,radius = d.dimensions()
    inner = radius-d.BACKING-d.CORE
    outer = radius-d.BACKING
    # At the inner core radius, two adjacent half-ribs retain 0.9 mm minimum
    # chord width. Three sectors keep corner spacing below the 4.4 mm S16 pitch.
    half_rib_angle = degrees(asin(d.WEB/(2*inner)))
    ring = (cq.Workplane('XY').circle(outer).circle(inner)
            .extrude(height-d.THICKNESS-d.SKIN).translate((0,0,d.THICKNESS)))
    slots=[]
    for low in (0,30,60):
        lo,hi = radians(low+half_rib_angle),radians(low+30-half_rib_angle)
        reach = 2*radius
        wedge = (cq.Workplane('XY').polyline([(0,0),
                 (reach*cos(lo),reach*sin(lo)),(reach*cos(hi),reach*sin(hi))])
                 .close().extrude(height))
        slots.append(ring.intersect(wedge).val())
    return cq.Workplane(obj=cq.Compound.makeCompound(slots))


@cache
def candidate():
    slots = quarter_slots()
    cuts=[]
    for sx,sy,x,y in corner_locations():
        local=slots
        if sx<0: local=local.mirror('YZ')
        if sy<0: local=local.mirror('XZ')
        cuts.append(local.translate((x,y,0)).val())
    return d.cup().cut(cq.Compound.makeCompound(cuts)).clean()


def probe(x,y,z,radius=.1):
    return cq.Workplane('XY').sphere(radius).translate((x,y,z))


def check_corners():
    old,new = d.cup(),candidate()
    _,_,height,radius = d.dimensions()
    assert new.val().isValid() and len(new.solids().vals())==1, 'Candidate must stay connected and valid'
    air_checks=skin_checks=0
    for sx,sy,cx,cy in corner_locations():
        for angle in (15,45,75):
            co,si=cos(radians(angle)),sin(radians(angle))
            for z in (2.,15.,height-.6):
                core_radius=radius-d.BACKING-d.CORE/2
                air=probe(cx+sx*core_radius*co,cy+sy*core_radius*si,z)
                assert air.cut(old).val().Volume()<1e-6, 'Baseline corner unexpectedly hollow'
                assert air.intersect(new).val().Volume()<1e-6, 'Proposed corner air gap blocked'
                air_checks+=1
                for skin_radius in (radius-d.BACKING/2,radius-d.THICKNESS+d.SKIN/2):
                    skin=probe(cx+sx*skin_radius*co,cy+sy*skin_radius*si,z)
                    assert skin.cut(new).val().Volume()<1e-6, 'Corner skin lost'
                    skin_checks+=1
    return dict(scope='CAD corner coverage only; no stiffness, acoustic or print qualification',
                baseline='solid corner at all sampled air-core locations',
                candidate='0.8 mm curved core between 0.4 mm skins, with radial ribs',
                corner_pockets=12,air_samples=air_checks,skin_samples=skin_checks,
                rib_min_chord_mm=d.WEB,corner_sector_pitch_deg=30,
                core_radial_gap_mm=d.CORE,production_files_changed=False)


def section_comparison():
    length,width,_,radius=d.dimensions()
    cx,cy=length/2-radius,width/2-radius
    mask=d.block(14,14,.2,cx+.5,cy+.5,15.)
    original=d.cup().intersect(mask).translate((-cx,-cy,-15))
    proposed=candidate().intersect(mask).translate((-cx+20,-cy,-15))
    return cq.Assembly(name='corner_feasibility').add(original,name='existing_left').add(proposed,name='proposed_right')


if __name__=='__main__':
    print(json.dumps(check_corners(),indent=2))
else:
    result=section_comparison()
