"""C: sweep with contents, bearing clearance and conditional axial capture."""
import json
from pathlib import Path
from cap_c_hinged_5 import *

checks=[]
for count in (5,20):
    fixed=frame(count).val(); lid=cap(count).val()
    pin=axle(count).val(); keeper=key(count).val()
    cards=compound(*[cq.Workplane('XY').box(50.4,2.2,80.2,centered=(True,True,False))
                    .translate((0,slot_y(i,count)-.3,MAX_SEAT_HEIGHT))
                    for i in range(count)])
    angles=[0,.5,1,2,5,10,20,35,50,70,90,110,135,160,180]
    for angle in angles:
        pose=opened(lid,count,angle)
        overlap=pose.intersect(fixed).Volume()
        assert overlap<1e-6,f'Count {count}: frame blocks lid at {angle}: {overlap}'
        overlap=pose.intersect(cards).Volume()
        assert overlap<1e-6,f'Count {count}: lid hits contents at {angle}: {overlap}'
        assert pose.intersect(pin).Volume()<1e-6,f'Pin blocks rotating lid at {angle}'
    assert pin.intersect(fixed).Volume()<1e-6,'Axle does not fit frame'
    assert keeper.intersect(pin).Volume()<1e-6,'Key does not fit cross slot'
    assert keeper.intersect(fixed).Volume()<1e-6,'Key obstructed by frame'
    assert pin.translate((.7,0,0)).intersect(fixed).Volume()>1e-6,'Head does not stop axle'
    assert compound(pin,keeper).translate((-3,0,0)).intersect(fixed).Volume()>1e-6,\
        'Inserted key does not stop axle withdrawal'
    assert opened(lid,count,181).intersect(fixed).Volume()>1e-6,'No open stop beyond 180 degrees'
    # Stability sensitivity, not slicer-derived weight. CAD volumes supply
    # shape centroids; the fixed/lid effective-density ratio is explicitly varied.
    open_lid=opened(lid,count,180)
    rear=end_y(count)+REAR_FOOT_REACH
    stability=[]
    for ratio in (.5,1):
        v_fixed=fixed.Volume()*ratio;v_lid=lid.Volume()
        cy=(v_fixed*fixed.Center().y+v_lid*open_lid.Center().y)/(v_fixed+v_lid)
        assert cy<rear-5,'Open empty box has inadequate screened rear margin'
        stability.append(dict(fixed_to_lid_effective_density_ratio=ratio,
                              open_empty_COM_Y_mm=cy,rear_support_Y_mm=rear,
                              rear_margin_mm=rear-cy))
    checks.append(dict(count=count,angles_degrees=angles,bearing_normal_gap_mm=BEARING_GAP,
        hinge_above_conservative_card_top_mm=HINGE_Z-(MAX_SEAT_HEIGHT+80.2),
        stability_sensitivity=stability,
        scope='Rigid sampled sweep and centred axle fit. No continuous motion proof, '
              'key friction, hinge strength or physical validation. Stability uses assumed '
              'effective-density ratios, excluding touch forces; actual masses remain unknown.'))
Path(__file__).parent.joinpath('notes/cap_c_checks.json').write_text(
    json.dumps(dict(checks=checks),indent=2)+'\n')
print(json.dumps(checks))
