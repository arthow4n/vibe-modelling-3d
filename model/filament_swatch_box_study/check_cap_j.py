"""Specific centered-panel, rigid-card path and unchanged mating-interface checks.

Relaxed panel/card overlap is intentional; reduced pad space is not a solved
deformed spring. Beam forces/strains are conditional short-term screens only.
"""
import hashlib
import json
import math
from pathlib import Path
import cap_j_base_5 as j
import cap_i_grip_keys as i
from check_corner_seat import card_envelope,seated_height
from physical_analysis.screening import rectangular_cantilever,elastic_friction_grip

d=Path(__file__).parent
base=j.base().val()
rigid=j.base(include_panels=False,include_detents=False).val()
old=j.h.base().val()
assert base.isValid() and len(base.Solids())==1,'Card panels must remain attached to the printed base'
changed_x_min=min(j.PANEL_CENTRE_X-j.PANEL_WIDTH/2-j.RELIEF_SIDE_GAP,
                  j.seats.FRONT_PAD_X-j.seats.FRONT_LEAF_WIDTH/2-j.seats.RELIEF_SIDE_GAP)
changed_x_max=max(j.PANEL_CENTRE_X+j.PANEL_WIDTH/2+j.RELIEF_SIDE_GAP,
                  j.seats.FRONT_PAD_X+j.seats.FRONT_LEAF_WIDTH/2+j.seats.RELIEF_SIDE_GAP)
change=j.g.block(changed_x_min-.01,changed_x_max+.01,-j.g.BODY_DEPTH/2,j.g.BODY_DEPTH/2,
    j.slots.FLOOR-j.ROOT_OVERLAP-.01,j.g.TOP_Z+.2).val()
old_mates=old.cut(change);new_mates=base.cut(change)
assert old_mates.cut(new_mates).Volume()<1e-6 and new_mates.cut(old_mates).Volume()<1e-6,\
    'Foot, hood contacts, connector sockets or exterior outside card panels changed'
panel=j.card_panel(0).val()
assert panel.cut(panel.mirror('YZ')).Volume()<1e-6,'Card panel is not centered/symmetric across card width'
free_y=panel.BoundingBox().ymax  # Targeted measurement: actual rounded gripping surface.
old_free_y=j.seats.front_leaf(0).val().BoundingBox().ymin
cases=[]
for index in range(j.COUNT):
    y=j.slots.slot_y(index,j.COUNT)
    p=j.card_panel(y).val()
    for width,thickness,chamfer in ((49.6,1.8,3.8),(49.6,2.2,4.2),
                                  (50,2,4),(50.4,1.8,3.8),(50.4,2.2,4.2)):
        z=seated_height(width,chamfer)
        card=card_envelope(width,thickness,chamfer).translate((0,y+j.slots.SLOT_WIDTH/2,z)).val()
        assert card.intersect(rigid).Volume()<1e-6,'Fixed front datum/root obstructs the seated card'
        assert max(card.distance(j.seats.corner_seat(y,s).val()) for s in (-1,1))<1e-6,\
            'Card no longer reaches both rigid corner seats'
        assert p.intersect(card).Volume()>1e-5,'No seated spring/card contact'
        actual_overlap=thickness-j.slots.SLOT_WIDTH/2+free_y
        assert elastic_friction_grip(interference_mm=actual_overlap)['preload_present']
        for side in (-1,1):
            assert card.translate((side*.1,0,0)).intersect(rigid).Volume()>1e-5,\
                'Corner seating no longer takes up lateral play'
        cases.append(dict(slot=index,width_mm=width,thickness_mm=thickness,
            corner_chamfer_mm=chamfer,actual_rounded_normal_overlap_mm=actual_overlap))
# Same four-direction funnel task, with hand correction to the opposite datum.
for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
    for step in range(11):
        f=step/10
        ax,ay,yaw=sy*2*(1-f),sx*2*(1-f),sx*(1-f)
        drop=25.2*abs(math.sin(math.radians(ay)))+1.1*abs(
            math.sin(math.radians(ax))*math.cos(math.radians(ay)))
        card=(card_envelope(50.4,2.2,4).translate((0,1.1,0))
              .rotate((0,0,0),(1,0,0),ax).rotate((0,0,0),(0,1,0),ay)
              .rotate((0,0,0),(0,0,1),yaw)
              .translate((sx*1.5*(1-f),sy*(1-f)+.3*f,
                          j.g.TOP_Z-.2-3.8*f+drop))).val()
        assert card.intersect(rigid).Volume()<1e-6,'Centered-panel root obstructs the corrected funnel path'
hood=j.g.cap().val()
cards=j.g.compound(*[card_envelope(50.4,2.2,4).translate(
    (0,j.slots.slot_y(n,j.COUNT)+j.slots.SLOT_WIDTH/2,seated_height(50.4,4)))
    for n in range(j.COUNT)])
assert hood.distance(rigid)<1e-6,'G hood no longer seats to J rim'
for lift in (0,.2,1,4,12,16,40,84):
    cover=hood.translate((0,0,lift))
    assert cover.intersect(rigid).Volume()<1e-6,'G hood hits J rigid body'
    assert cover.intersect(cards).Volume()<1e-6,'G hood hits front-datum-seated card envelopes'
    for n in range(j.COUNT):
        assert cover.intersect(j.card_panel(j.slots.slot_y(n,j.COUNT)).val()).Volume()<1e-6,\
            'Taller card panel hits hood'
# I key and H ports are unchanged; equivalent interface check above covers their
# transfer. Verify the seated key against actual J geometry and existing hood.
joined=j.g.compound(*[rigid.translate((0,y,0)) for y in i.module_centres()])
space=i.seated_key(3,projection=i.h.KEY_FIT_GAP).val()
for lift in (0,.2,1,2,4,8,16,22):
    assert space.translate((0,0,lift)).intersect(joined).Volume()<1e-6,'Accepted key required-space path blocked'
screens=[]
for E in (1000,1200,2000):
    for thickness in (1.8,2.0,2.2):
        answer=j.grip_screen(thickness,E)
        assert answer['small_deflection_applicable'] and answer['root_strain']<.015
        assert answer['tip_displacement_mm']<j.RELIEF_BACK_Y-j.ROOT_Y-j.PANEL_THICKNESS
        screens.append(dict(effective_modulus_MPa=E,card_thickness_mm=thickness,beam=answer))
old_beam=rectangular_cantilever(length_mm=j.seats.PAD_HEIGHT,
    width_mm=j.seats.FRONT_LEAF_WIDTH,thickness_mm=j.seats.FRONT_LEAF_THICKNESS,
    youngs_modulus_MPa=1200,tip_displacement_mm=.6-old_free_y)
new_beam=rectangular_cantilever(length_mm=j.CONTACT_HEIGHT-j.ROOT_BLEND,
    width_mm=j.PANEL_WIDTH,thickness_mm=j.PANEL_THICKNESS,
    youngs_modulus_MPa=1200,tip_displacement_mm=.6+free_y)
assert new_beam['force_N']>old_beam['force_N'] and new_beam['root_strain']<old_beam['root_strain'],\
    'Proposed width/length tradeoff does not improve the idealized force/strain screen'
record=dict(panel=dict(centre_x_mm=j.PANEL_CENTRE_X,width_mm=j.PANEL_WIDTH,
    contact_width_mm=j.CONTACT_WIDTH,thickness_mm=j.PANEL_THICKNESS,
    contact_height_mm=j.CONTACT_HEIGHT,root_blend_mm=j.ROOT_BLEND,
    actual_free_contact_y_mm=free_y,mirror_symmetric=True,plain_back_contact=True),
    seating_cases=cases,guidance=dict(samples=88,rigid_path_clear=True,springs_omitted=True),
    unchanged_interfaces=dict(foot_hood_socket_exterior_difference_outside_panels_mm3=0,
        G_hood_seats=True,G_hood_card_path_clear=True,I_key_required_space_path_clear=True),
    nominal_comparison=dict(old=old_beam,new=new_beam,
        conditional_force_ratio=new_beam['force_N']/old_beam['force_N'],
        conditional_strain_ratio=new_beam['root_strain']/old_beam['root_strain']),
    beam_screens=screens,
    assumptions='Uncalibrated effective homogeneous isotropic PETG E=1000–2000 MPa, '
        'provisional short-term strain screen 1.5%. Uniform full-width beam loading; '
        'local pad/plate bending, root concentrations, layer bonding and actual fill not qualified. '
        'Actual card thickness/material/settings unknown. No creep or lifetime rating.',
    inputs_sha256={p:hashlib.sha256((d/p).read_bytes()).hexdigest() for p in
        ('cap_j_base_5.py','check_cap_j.py','cap_h_module_5.py','cap_g_module_5.py',
         'cap_i_grip_keys.py','card_base_corner_seat_5.py','card_base_test.py')})
(d/'notes/cap_j_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,seating_cases=len(cases),centered=True,
    nominal_conditional_force_ratio=record['nominal_comparison']['conditional_force_ratio'],
    nominal_conditional_strain_ratio=record['nominal_comparison']['conditional_strain_ratio'])))
