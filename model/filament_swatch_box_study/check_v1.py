"""V1 single-wall product geometry and existing base/key relationships."""
import json
from pathlib import Path
import cap_v1_vase_hood_5 as v
import cap_j2_base_5 as j2
import cap_k2_base_5 as k2
import cap_i_grip_keys as keys
import cap_e_thin_5 as catch
import swatch_reference as ref
from revision_checks import sources
from physical_analysis.screening import rectangular_cantilever

g=v.g
shell=v.nominal_shell().val()
assert shell.isValid() and len(shell.Solids())==1,'Single nominal shell must be connected'
rigids=[m.base(include_panels=False,include_detents=False).val() for m in (j2,k2)]
full=j2.base().val()
panel=k2.panel().val()
cards=[]
for mode in ('J2','K2'):
    back=j2.j.slots.SLOT_WIDTH/2-2.2 if mode=='J2' else -j2.j.slots.SLOT_WIDTH/2
    card=ref.card(back,2.2).val()
    cards.extend(card.translate((0,j2.j.slots.slot_y(n,j2.j.COUNT),0)) for n in range(j2.j.COUNT))
for rigid in rigids:
    assert shell.intersect(rigid).Volume()<1e-6,'Waist/rim hits rigid body or original leaf stems'
    assert shell.distance(rigid)<1e-6,'Vase rim does not touch the accepted base rim'
bottom=min(shell.Faces(),key=lambda face:face.Center().z)
rim_support=[]
for rigid in rigids:
    seat_faces=[f for f in rigid.Faces() if f.geomType()=='PLANE'
                and abs(f.Center().z-g.SEAM_Z)<1e-6 and f.normalAt().z>.9]
    area=sum(bottom.intersect(face).Area() for face in seat_faces)
    ratio=area/bottom.Area()
    assert ratio>.4,('Thin rim lacks a substantial landing on the actual rounded base',ratio)
    rim_support.append(dict(contact_area_mm2=area,rim_area_mm2=bottom.Area(),supported_fraction=ratio))
for lift in (0,.2,.5,.8,1.2,2,3,8,16,84):
    cover=shell.translate((0,0,lift))
    for rigid in rigids:
        assert cover.intersect(rigid).Volume()<1e-6,'Base blocks hood passage'
    for c in cards:
        assert cover.intersect(c).Volume()<1e-6,'Hood touches actual card'
    assert cover.intersect(panel).Volume()<1e-6,'Waist hits K2 panel'
retention=[]
for lift in (0,.3,.6,.9,1.2,2,3):
    volume=shell.translate((0,0,lift)).intersect(full).Volume()
    retention.append(dict(hood_lift_mm=lift,relaxed_leaf_interference_mm3=volume))
assert retention[0]['relaxed_leaf_interference_mm3']>1e-5,'No seated contact/preload'
assert max(p['relaxed_leaf_interference_mm3'] for p in retention)>retention[0]['relaxed_leaf_interference_mm3'],\
    'Opening does not require additional deformation'
assert retention[-1]['relaxed_leaf_interference_mm3']<1e-7,'Catch never releases'
peak=catch.TIP_X-(g.OUTSIDE_X/2-v.NECK_DEPTH-v.LINE_WIDTH)
beam=rectangular_cantilever(length_mm=catch.FLEX_LENGTH,width_mm=g.STEM_WIDTH,
    thickness_mm=g.STEM_THICKNESS,youngs_modulus_MPa=1200,tip_displacement_mm=peak)
assert peak>0 and peak<g.BACK_RELIEF and beam['root_strain']<.015
for side in (-1,1):
    for y in g.detent_centres(g.COUNT):
        assert shell.intersect(g.pad(y,side).val()).Volume()>1e-5,'A closure contact is missing'
        assert shell.intersect(g.leaf(y,side).val().translate((-side*(peak+.02),0,0))).Volume()<1e-7,\
            'Nominal passage space does not clear the catch'
for mode in ('J2','K2'):
    back=j2.j.slots.SLOT_WIDTH/2-2.2 if mode=='J2' else -j2.j.slots.SLOT_WIDTH/2
    c=ref.card(back,2.2).val()
    assert c.intersect(shell).Volume()<1e-7
key=keys.seated_key(3).val()
for cy in keys.module_centres():
    cover=shell.translate((0,cy,0))
    assert cover.intersect(key).Volume()<1e-7,'Thin hood touches seated I key'
    assert cover.intersect(key.translate((0,0,.4))).Volume()>1e-5,'Thin hood fails key escape coverage'
record=dict(scope='Nominal .42 mm shell CAD; actual Orca wall placement checked separately. No force/optical/creep validation.',
    overall_outer_dimensions_match_G=True,rim_seats_on_existing_base=True,rim_support=rim_support,
    profile=dict(line_width_mm=v.LINE_WIDTH,roof_mm=v.ROOF,neck_depth_per_X_side_mm=v.NECK_DEPTH,
                 neck_centre_z_mm=v.NECK_Z,neck_half_span_mm=v.NECK_HALF_SPAN,
                 outside_corner_radius_mm=v.OUTSIDE_RADIUS,rim_inset_mm=v.RIM_INSET,rim_taper_height_mm=v.RIM_HEIGHT),
    retention=retention,peak_leaf_translation_screen_mm=peak,conditional_leaf_beam=beam,
    captures_all_four_existing_contacts=True,cards_panels_and_rigid_body_clear=True,I_key_covered=True,
    sources_sha256=sources(('cap_v1_vase_hood_5.py','check_v1.py','cap_j2_base_5.py','cap_k2_base_5.py','swatch_reference.py')))
(Path(__file__).parent/'notes/v1_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,retention=retention,peak_leaf_translation_screen_mm=peak)))
