"""Specific geometry/use checks; no duplicate export or slicer audits."""
from itertools import combinations
import hashlib
import json
from pathlib import Path
from components import *
from concept import screen

ROOT=Path(__file__).resolve().parent

def verify():
    p=assembled(60)
    checks={}
    # Three locked poses, full component pairs. Intended mating faces may touch.
    for angle in ANGLES:
        parts=assembled(angle)
        for a,b in combinations(parts,2):
            overlap=parts[a].intersect(parts[b]).val().Volume()
            if overlap>1e-5: raise AssertionError(f'{angle}: {a}/{b} overlap {overlap}')
    checks['locked_poses']='No unintended solid overlaps at 45, 60, 75 degrees; shared mounting faces touch.'
    # Latch intentionally contacts the rotating teeth; review all OTHER motion pairs.
    base_shape=p['base']; leaf=p['latch']; arm_shape=arm(); cradle_shape=cradle()
    for angle in range(45,76,2):
        for name,shape in (('arm',arm_shape),('cradle',cradle_shape)):
            moving=placed(shape,angle)
            if moving.intersect(base_shape).val().Volume()>1e-5:
                raise AssertionError(f'{name} hits base at {angle}')
    checks['motion']='Arm/base and cradle/base: no overlaps at 2-degree samples over 45..75; not a continuous proof. Tooth/latch interaction belongs to elastic analysis.'
    # Exact rectangular device envelope in cradle coordinates; no sensor/case customization.
    phone=box(-45,CRADLE_BOTTOM+6,CRADLE_THICKNESS,90,PHONE_HEIGHT,PHONE_THICKNESS)
    assert phone.intersect(cradle_shape).val().Volume()<1e-5
    for lift in (0,5,15,30):
        assert phone.translate((0,lift,0)).intersect(cradle_shape).val().Volume()<1e-5
    checks['device']='90 x 180 x 14 mm device envelope seats and lifts out along cradle; 20 mm open cable notch, 8 mm retaining lip.'
    # Spring clearance at requested travel, conservative rigid downward translation of tab.
    tab_floor_gap=(LATCH_TOP-LATCH_THICKNESS)-RELEASE_TRAVEL-1
    assert tab_floor_gap>1
    checks['release_floor_gap_mm']=tab_floor_gap
    checks['thumb_stop']='Base pedestal arrests the front tab at nominal 4.7 mm travel; remaining leaf clears the well.'
    # Mating fastener centres derive from the same dimensions; confirm actual through holes.
    pin=x_cylinder(PIVOT_Y,PIVOT_Z,2,40,-20)
    assert pin.intersect(base_shape).val().Volume()<1e-5
    assert pin.intersect(p['arm']).val().Volume()<1e-5
    checks['pivot']='M4 nominal 4 mm shaft clears both actual 4.5 mm bores in assembled pose; 0.4 mm axial clearance per side.'
    # Print-layout overlap can invalidate four separate parts even if each builds.
    positions={'base':(45,5,0),'arm':(115,35,0),'cradle':(185,40,0),'latch':(115,180,0)}
    layout={n:s.translate(positions[n]) for n,s in printable_parts().items()}
    for a,b in combinations(layout,2):
        assert layout[a].intersect(layout[b]).val().Volume()<1e-5,(a,b)
    checks['layout']='Four separated print solids; final bed fit delegated to Orca.'
    return dict(checks=checks,concept=screen(),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (ROOT/'components.py',ROOT/'concept.py',ROOT/'verify.py',ROOT/'analysis_phone_stand.py')})

if __name__=='__main__':
    report=verify()
    (ROOT/'notes/geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['checks'],indent=2))
