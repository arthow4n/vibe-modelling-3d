"""J4/K4 targeted grip checks: no flaps, upward floor, closed-G access.

Local grip changes must preserve card/support/catch/key geometry. Contact nose
is an explicit access assumption; CAD checks cannot qualify actual hand comfort.
"""
import json
from pathlib import Path
import cap_j4_base_5 as j4
import cap_k4_base_5 as k4
import recessed_grips as grips
from revision_checks import sources

g=grips.g
mask=grips.changed_region().val()
foot=g.rounded_block(g.FOOT_X,g.FOOT_DEPTH,g.SEAM_Z,0,g.FOOT_RADIUS).val()
hood=g.cap().val()
rim_region=g.block(-g.FOOT_X/2-.1,g.FOOT_X/2+.1,
                   -g.FOOT_DEPTH/2-.1,g.FOOT_DEPTH/2+.1,0,g.SEAM_Z+.01).val()
results=[]
for label,module in (('J4',j4),('K4',k4)):
    old=module.previous.base().val()
    new=grips.revise(g.cq.Workplane('XY').newObject([old])).val()
    assert new.isValid() and len(new.Solids())==1,'Pocket floors must remain connected to the base'
    a,b=new.cut(mask),old.cut(mask)
    assert a.cut(b).Volume()<1e-6 and b.cut(a).Volume()<1e-6,\
        'Card supports, spring/dome follower, closure roots or key sockets changed'
    assert new.cut(old).cut(foot).Volume()<1e-6,'Added material projects beyond the original foot'
    for lift in (0,.2,1,3,16,84):
        assert hood.translate((0,0,lift)).intersect(new.intersect(mask)).Volume()<1e-7,\
            'New lower geometry obstructs G hood lifting'
    old_bearing=hood.translate((0,0,-.05)).intersect(old.intersect(rim_region)).Volume()
    new_bearing=hood.translate((0,0,-.05)).intersect(new.intersect(rim_region)).Volume()
    assert old_bearing>0 and new_bearing>0,'Closed hood lacks a supported rim'
    for side in (-1,1):
        for end in (-1,1):
            x0,x1=sorted((side*30.8,side*31.3))
            y0,y1=sorted((end*12.5,end*13.5))
            support=g.block(x0,x1,y0,y1,g.SEAM_Z-.05,g.SEAM_Z).val()
            assert new.intersect(support).Volume()>.02, 'Missing unchanged rim bearing outside the grip'
            assert hood.translate((0,0,-.05)).intersect(support).Volume()>1e-5,\
                'Rim does not land on the claimed bearing'
    contacts=[]
    for side in (-1,1):
        faces=[f for f in new.Faces() if f.geomType()=='PLANE'
            and abs(f.Center().z-grips.FLOOR_Z)<1e-6 and f.normalAt().z>.99
            and side*f.Center().x>grips.INNER_X]
        area=sum(f.Area() for f in faces)
        assert area>10,'Pocket does not expose an upward floor'
        x0,x1=sorted((side*grips.NOSE_X,side*(g.FOOT_X/2-grips.CONTACT_EDGE_ROUND)))
        # Inside the preserved bottom chamfer, the loaded floor has direct bed support.
        support_x=min(g.FOOT_X/2-grips.CONTACT_EDGE_ROUND,
                      g.FOOT_X/2-g.FOOT_BOTTOM_CHAMFER)
        sx0,sx1=sorted((side*grips.NOSE_X,side*support_x))
        floor=g.block(sx0,sx1,-grips.NOSE_WIDTH/2,grips.NOSE_WIDTH/2,0,grips.FLOOR_Z).val()
        assert floor.cut(new).Volume()<1e-7,'Contact floor is not solid down to the bed'
        nose=grips.finger(side).val()
        assert nose.isValid() and len(nose.Solids())==1,'Invalid contact reference'
        assert nose.intersect(new).Volume()<1e-7,'Resting contact reference intersects the base'
        assert grips.finger(side,press=.05).val().intersect(new).Volume()>1e-5,\
            'Downward hand motion misses the upward floor'
        for withdrawal in (0,.25,.5,1,2,4,8):
            p=grips.finger(side,withdrawal=withdrawal).val()
            assert p.intersect(new).Volume()<1e-7,'Side entry hits base'
            assert p.intersect(hood).Volume()<1e-7,'Closed hood blocks the assumed distal-pad edge'
            assert p.intersect(new.translate((0,g.FOOT_DEPTH,0))).Volume()<1e-7
            assert p.intersect(hood.translate((0,g.FOOT_DEPTH,0))).Volume()<1e-7
        contacts.append(dict(side=side,upward_planar_area_mm2=area,
            contact_normal=[0,0,1],finger_force_on_base=[0,0,-1],solid_floor_mm=grips.FLOOR_Z))
    results.append(dict(variant=label,valid_connected_base=True,
        card_support_closure_and_key_geometry_preserved=True,no_outward_additions=True,
        contacts=contacts,closed_G_side_entry_clear=True,joined_neighbour_clear=True,
        G_rim_bearing_proxy_retained_fraction=new_bearing/old_bearing,
        bearing_scope='Rigid .05 mm downward overlap proxy, not pressure or strength; four actual seating patches checked outside the grip.'))

record=dict(variants=results,grip=dict(length_Y_mm=grips.LENGTH_Y,
    recess_depth_X_mm=g.FOOT_X/2-grips.INNER_X,nominal_floor_mm=grips.FLOOR_Z,
    gap_below_closed_hood_mm=g.SEAM_Z-grips.FLOOR_Z,
    exposed_edge_radius_mm=grips.CONTACT_EDGE_ROUND,unchanged_width_mm=g.FOOT_X,
    unchanged_module_pitch=True),
    assumed_contact=dict(nose_width_mm=grips.NOSE_WIDTH,nose_thickness_mm=grips.NOSE_THICKNESS,
        body_thickness_mm=8,method='Thin distal-pad/nail-edge envelope with thicker body outside hood; sampled horizontal side entry. Not an anatomical hand or comfort/force simulation.'),
    load_path='Upward floor reaction lets the hand press the base down as the hood is lifted. Inner contact patch is solid to the bed; the exposed outer edge retains the existing bottom chamfer. No grip-force or strength rating. Actual small-recess reach and skin/nail comfort require printing.',
    sources_sha256=sources(('cap_j4_base_5.py','cap_k4_base_5.py','recessed_grips.py',
        'check_recessed_grips.py','upward_grips.py','cap_j2_base_5.py','cap_k2_base_5.py')))
(Path(__file__).parent/'notes/recessed_grip_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,variants=results)))
