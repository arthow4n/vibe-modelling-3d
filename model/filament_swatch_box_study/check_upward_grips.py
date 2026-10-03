"""J3/K3: real upward bearing surfaces, closed-hood finger access and mates.

Unchanged card geometry is proved outside the bounded lower side region;
earlier J2/K2 checks remain narrower evidence, not printed validation.
"""
import json
from pathlib import Path
import cadquery as cq
import cap_j3_base_5 as j3
import cap_k3_base_5 as k3
import cap_i_grip_keys as keys
import cap_v1_vase_hood_5 as vase
import upward_grips as grips
from revision_checks import sources

g=grips.g
mask=grips.changed_region().val()
hoods={'G':g.cap().val(),'V1 nominal shell':vase.nominal_shell().val()}
fingers={side:grips.finger(side).val() for side in (-1,1)}
results=[]
for label,module in (('J3',j3),('K3',k3)):
    old=module.previous.base().val()
    new=grips.revise(cq.Workplane('XY').newObject([old])).val()
    assert new.isValid() and len(new.Solids())==1,'Base and ledges must be one valid connected solid'
    a,b=new.cut(mask),old.cut(mask)
    assert a.cut(b).Volume()<1e-6 and b.cut(a).Volume()<1e-6,\
        'Card springs/supports, closure roots, rim seating or key geometry changed'
    assert old.cut(new).Volume()<1e-6,'Revision removed existing load-bearing material'
    for name,hood in hoods.items():
        assert hood.intersect(mask.intersect(new)).Volume()<1e-7,'Grip blocks closed hood'
        for lift in (0,.2,1,3,16,84):
            assert hood.translate((0,0,lift)).intersect(mask.intersect(new)).Volume()<1e-7,\
                'New lower geometry blocks hood lifting'
    top_faces=[face for face in new.Faces() if face.geomType()=='PLANE'
               and abs(face.Center().z-grips.HEIGHT)<1e-6 and face.normalAt().z>.99]
    contacts=[]
    for side in (-1,1):
        faces=[f for f in top_faces if side*f.Center().x>g.FOOT_X/2]
        area=sum(f.Area() for f in faces)
        assert area>100,'Upward ledge lacks broad exposed bearing area'
        x0,x1=sorted((side*(grips.CONTACT_X-.5),side*(grips.CONTACT_X+1)))
        patch=g.block(x0,x1,-9.5,9.5,grips.HEIGHT-.05,grips.HEIGHT).val()
        assert new.intersect(patch).Volume()>1.4,'Intended contact footprint is not supported'
        fingertip=fingers[side]
        assert fingertip.isValid() and len(fingertip.Solids())==1,'Finger envelope is invalid'
        assert fingertip.intersect(new).Volume()<1e-7,'Resting finger envelope hits base'
        assert fingertip.translate((0,0,-.05)).intersect(new).Volume()>1e-5,\
            'Downward finger motion does not contact the ledge'
        for lift in (0,1,4,8):
            p=fingertip.translate((0,0,lift))
            assert p.intersect(new).Volume()<1e-7,'Vertical finger approach hits base'
            for hood in hoods.values():
                assert p.intersect(hood).Volume()<1e-7,'Closed hood blocks finger access'
        contacts.append(dict(side=side,upward_planar_area_mm2=area,
                             contact_normal=[0,0,1],finger_force_on_base=[0,0,-1]))
    neighbour_y=g.FOOT_DEPTH
    neighbour=new.translate((0,neighbour_y,0))
    assert new.intersect(neighbour).Volume()<1e-7,'Joined ledges collide'
    for finger in fingers.values():
        assert finger.intersect(neighbour).Volume()<1e-7,'Joined neighbour blocks grip'
        for hood in hoods.values():
            assert finger.intersect(hood.translate((0,neighbour_y,0))).Volume()<1e-7
    added=new.cut(old)
    joined_added=g.compound(*[cq.Workplane('XY').newObject([added]).translate((0,y,0))
                             for y in keys.module_centres()])
    key=keys.seated_key(3).val()
    for lift in (0,.2,1,2,4,8,16,22):
        assert key.translate((0,0,lift)).intersect(joined_added).Volume()<1e-7,\
            'New material blocks I key entry/release'
    results.append(dict(variant=label,connected_valid_base=True,
        preserved_geometry_outside_lower_grip_region=True,contacts=contacts,
        finger_envelope_access_G_and_V1=True,joined_access_clear=True,I_key_clear=True,
        scope='Unchanged card/closure mates proved in CAD; assumed fingertip access and downward contact, not printed comfort/force.'))

record=dict(variants=results,grip=dict(extension_per_X_side_mm=grips.EXTENSION,
    length_Y_mm=grips.LENGTH_Y,height_mm=grips.HEIGHT,unchanged_module_pitch=True),
    assumed_distal_finger=dict(width_mm=2*grips.FINGER_HALF_Y,thickness_mm=2*grips.FINGER_HALF_Z,
                              front_extent_from_contact_mm=grips.FINGER_NOSE,contact_x_mm=grips.CONTACT_X,
                              representation='Rounded bounding block; not an anatomical hand or comfort simulation'),
    load_path='Upward planar contact gives downward base reaction; the ledges have bed-backed bottoms for desk opening. Off-desk strength/effort and human comfort need the print trial; no calibrated load rating.',
    sources_sha256=sources(('cap_j3_base_5.py','cap_k3_base_5.py','upward_grips.py','check_upward_grips.py',
        'cap_j2_base_5.py','cap_k2_base_5.py','cap_v1_vase_hood_5.py')))
(Path(__file__).parent/'notes/upward_grip_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,variants=results)))
