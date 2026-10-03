"""K concept screen and actual mixed K/J mates; no print or solver validation."""
import hashlib
import json
import math
from pathlib import Path
import dome_latch_study as k
import cap_j_base_5 as j
import cap_i_grip_keys as i
from check_corner_seat import card_envelope

d=Path(__file__).parent
full=k.rough_base().val()
rigid=k.rough_base(include_panels=False,include_detents=False).val()
previous=j.base().val()
assert full.isValid() and len(full.Solids())==1,'Dome crowns must attach to the base'
changed=j.g.block(-j.PANEL_WIDTH/2-j.RELIEF_SIDE_GAP-.01,
    j.PANEL_WIDTH/2+j.RELIEF_SIDE_GAP+.01,-j.g.BODY_DEPTH/2,j.g.BODY_DEPTH/2,
    j.slots.FLOOR-j.ROOT_OVERLAP-.01,
    max(j.g.TOP_Z,j.slots.FLOOR+k.PANEL_HEIGHT,k.DOME_Z+k.SHOULDER_OUTER_RADIUS)+.2).val()
a,b=full.cut(changed),previous.cut(changed)
assert a.cut(b).Volume()<1e-6 and b.cut(a).Volume()<1e-6,\
    'The dome study changed external mates outside the card-panel regions'
panel=k.card_panel().val();crown=k.shoulder_crown().val();card=k.dome_card().val()
assert len(panel.Solids())==1
assert crown.BoundingBox().xmax<j.PANEL_WIDTH/2+j.RELIEF_SIDE_GAP,\
    'Rounded noses extend outside the actual spring relief'
assert panel.intersect(card).Volume()>1e-5,'No designed seated preload'
assert panel.cut(crown).intersect(card).Volume()<1e-7,'Stem/carrier touches an unintended card feature'
seated=panel.translate((0,k.SEATED_TRAVEL_Y,0))
assert seated.intersect(card).Volume()<1e-7 and seated.distance(card)<1e-6,\
    'Proposed relaxed dome engagement does not settle to actual contact'
assert seated.intersect(card.translate((0,0,1))).Volume()>1e-6,\
    'Upward card removal does not require additional follower motion'
# Screen fit-space for the largest flat-face passage. Whole-panel translations
# stand in for required upper space only, not a solved bending shape.
screens=[]
for thickness in (1.8,2.0,2.2):
    screen=k.travel_screen(thickness)
    assert screen['seated_travel_y_mm']>0,'Thin card consumes the low seated preload'
    assert screen['pass_flat_face_travel_y_mm']<screen['available_rear_space_mm']
    assert screen['passage_beam']['root_strain']<.015
    screens.append(dict(card_thickness_mm=thickness,screen=screen))
max_travel=max(r['screen']['pass_flat_face_travel_y_mm'] for r in screens)
for index in range(j.COUNT):
    y=j.slots.slot_y(index,j.COUNT)
    c=k.dome_card(y).val()
    assert rigid.intersect(c).Volume()<1e-6,'Nominal card blocked by rigid guides'
    upper=k.card_panel(y).val().intersect(j.g.block(-22,22,y-2,y+5,
        j.slots.FLOOR+j.ROOT_BLEND+.1,23).val())
    assert upper.translate((0,max_travel,0)).intersect(rigid).Volume()<1e-6,\
        'Required passage space hits the rear wall or another slot'

# Reuse J's rigid four-direction guided funnel poses, reflected to K's datum.
# Spring contact is deliberately excluded; these establish guide/root access,
# not free-fall insertion or actual actuation force.
for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
    for step in range(11):
        f=step/10
        ax,ay,yaw=sy*2*(1-f),sx*2*(1-f),sx*(1-f)
        drop=25.2*abs(math.sin(math.radians(ay)))+1.1*abs(
            math.sin(math.radians(ax))*math.cos(math.radians(ay)))
        c=(card_envelope(50.4,2.2,4).translate((0,1.1,0))
           .rotate((0,0,0),(1,0,0),ax).rotate((0,0,0),(0,1,0),ay)
           .rotate((0,0,0),(0,0,1),yaw)
           .translate((sx*1.5*(1-f),sy*(1-f)+.3*f,
                       j.g.TOP_Z-.2-3.8*f+drop)).mirror('XZ')).val()
        assert c.intersect(rigid).Volume()<1e-6,'K root obstructs the corrected funnel path'

centres=i.module_centres()
mixed=(rigid.translate((0,centres[0],0)),previous.translate((0,centres[1],0)))
assert mixed[0].intersect(mixed[1]).Volume()<1e-7 and mixed[0].distance(mixed[1])<1e-7
joint=j.g.compound(*mixed)
space=i.seated_key(3,projection=i.h.KEY_FIT_GAP).val()
for lift in (0,.2,1,2,4,8,16,22):
    assert space.translate((0,0,lift)).intersect(joint).Volume()<1e-6,'Shared key entry space blocked'
key=i.seated_key(3).val()
for side in (-1,1):
    for end in (-1,1):
        xl,xh=sorted((side*3,side*9));yl,yh=sorted((end*.15,end*4))
        quadrant=j.g.block(xl,xh,yl,yh,i.h.KEY_FLOOR_Z,i.h.KEY_TOP_Z+.1).val()
        assert key.intersect(joint).intersect(quadrant).Volume()>1e-5,\
            'Mixed pairing loses an accepted key preload pad'
hood=j.g.cap().val()
for base,y in ((rigid,centres[0]),(previous,centres[1])):
    assert hood.distance(base)<1e-6,'G hood does not reach the base rim'
    cover=hood.translate((0,y,0))
    assert key.intersect(cover).Volume()<1e-7
    assert key.translate((0,0,.4)).intersect(cover).Volume()>1e-7
for lift in (0,1,16,84):
    assert hood.translate((0,0,lift)).intersect(rigid).Volume()<1e-6
    for n in range(j.COUNT):
        y=j.slots.slot_y(n,j.COUNT)
        assert hood.translate((0,0,lift)).intersect(k.card_panel(y).val()).Volume()<1e-6
        assert hood.translate((0,0,lift)).intersect(k.dome_card(y).val()).Volume()<1e-6

remaining=lambda radius:k.DOME_SOURCE_HEIGHT-math.sqrt(k.SPHERE_RADIUS**2-radius**2)
nominal=k.travel_screen()
j_comparison=json.loads((d/'notes/cap_j_checks.json').read_text())['nominal_comparison']['new']
record=dict(scope='K printable-base CAD checks and mixed K/J shared mates. Not a full contact path, '
    'deformation solution, release-force rating or creep prediction.',
    dome=dict(source_shape='Concave sphere subtraction',radius_mm=k.SPHERE_RADIUS,
        centre_x_mm=k.DOME_X,centre_height_from_floor_mm=k.DOME_SOURCE_X,
        source_remaining_at_centre_mm=remaining(0),
        source_material_at_nominal_contact_mm=remaining(k.NOSE_CONTACT_RADIUS),
        nominal_contact_radius_mm=k.NOSE_CONTACT_RADIUS,nose_radius_mm=k.NOSE_RADIUS,
        actual_nose_centres_mm=k.nose_centres(),
        center_contact_avoided=True,carrier_contact_avoided=True),
    guidance=dict(rigid_funnel_samples=88,reflected_J_paths_clear=True,springs_excluded=True),
    screens=screens,mixed_K_J=dict(same_footprint=True,unchanged_outer_mates=True,
        bases_butt_without_overlap=True,I_key_3_entry_and_four_pads=True,
        G_hood_seats_and_covers_key_escape=True),
    comparison_to_J=dict(nominal_seated_strain_ratio=nominal['seated_beam']['root_strain']/j_comparison['root_strain'],
        nominal_passage_strain_ratio=nominal['passage_beam']['root_strain']/j_comparison['root_strain']),
    assumptions='Effective isotropic E=1200 MPa, provisional short-term strain screen 1.5%. '
        'Uniform full-width beam idealization; off-centre plate/torsion and local nose strain need '
        'the separate nonlinear screen, which is also conditional. '
        'Material/fill/layer bonding not calibrated. Thickness interval is a screening envelope, not measured print error. '
        'Seated normal force, grip/release and long-term strain relaxation require physical evidence.',
    remaining_questions=['Actual printed dome profile and card thickness','Actual plate response beyond the conditional normal-load fixture',
        'Coupled entry/release with friction and real card features','Dwell and recovery'],
    sources_sha256={p:hashlib.sha256((d/p).read_bytes()).hexdigest() for p in
        ('cap_k_base_5.py','dome_latch_study.py','check_dome_study.py','cap_j_base_5.py','cap_i_grip_keys.py',
         '../filament_archive_swatch/filament_archive_swatch.scad')})
(d/'notes/dome_study_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,mixed_K_J=record['mixed_K_J'],comparison_to_J=record['comparison_to_J'])))
