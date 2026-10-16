"""Inspection of retained solid-corner baseline versus current revised liner.

Left: existing solid corner; right: curved air core with radial supports.
Run through execute.py for geometric witness results, evaluate_model.py for views.
No exports or slicing are performed by this module.
"""
from math import cos, sin, radians
import json
import cadquery as cq
import design as d


def probe(x,y,z,radius=.1):
    return cq.Workplane('XY').sphere(radius).translate((x,y,z))


def check_corners():
    old,new = d.solid_corner_cup(),d.cup()
    _,_,height,radius = d.dimensions()
    assert new.val().isValid() and len(new.solids().vals())==1, 'Candidate must stay connected and valid'
    air_checks=skin_checks=0
    for sx,sy,cx,cy in d.corner_locations():
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
                core_radial_gap_mm=d.CORE,production_builder="design.cup")


def section_comparison():
    length,width,_,radius=d.dimensions()
    cx,cy=length/2-radius,width/2-radius
    mask=d.block(14,14,.2,cx+.5,cy+.5,15.)
    original=d.solid_corner_cup().intersect(mask).translate((-cx,-cy,-15))
    proposed=d.cup().intersect(mask).translate((-cx+20,-cy,-15))
    return cq.Assembly(name='corner_feasibility').add(original,name='existing_left').add(proposed,name='proposed_right')


if __name__=='__main__':
    print(json.dumps(check_corners(),indent=2))
else:
    result=section_comparison()
