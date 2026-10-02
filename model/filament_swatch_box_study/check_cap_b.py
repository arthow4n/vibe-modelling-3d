"""B running fit, front stop, enclosure clearance and sampled drawer travel."""
import json
from pathlib import Path
import cadquery as cq
from cap_common import *
from cap_b_drawer_5 import drawer,housing,front_structure

checks=[]
for count in (5,20):
    fixed=housing(count).val();moving=drawer(count).val()
    front=front_structure(count).val()
    assert moving.intersect(fixed).Volume()<1e-6,'Closed drawer obstruction'
    assert front.distance(fixed)<1e-6,'Front panel has no seating stop'
    cards=[cq.Workplane('XY').box(50.4,2.2,80.2,centered=(True,True,False))
           .translate((0,slot_y(i,count)-.3,MAX_SEAT_HEIGHT)).val() for i in range(count)]
    assert all(front.intersect(c).Volume()<1e-6 for c in cards),'Door lip touches card'
    pulls=[0,.2,4,12,30,outer_depth(count)/2,outer_depth(count)+8]
    for pull in pulls:
        pose=moving.translate((0,-pull,0))
        assert pose.intersect(fixed).Volume()<1e-6,f'Drawer blocked at {pull}'
        assert all(fixed.intersect(c.translate((0,-pull,0))).Volume()<1e-6 for c in cards)
    checks.append(dict(count=count,pulls_mm=pulls,side_running_gap_mm=FIT_GAP,
        front_lip_depth_mm=3,scope='Rigid horizontal withdrawal; tray floor supported until removal. '
            'No friction, tilt, retention or comfortable grip qualification.'))
out=Path(__file__).parent/'notes/cap_b_checks.json'
out.write_text(json.dumps(dict(checks=checks),indent=2)+'\n')
print(json.dumps(checks))
