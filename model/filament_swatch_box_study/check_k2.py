"""K2 real-face engagement, failed-reference regression and upright support."""
import json
from pathlib import Path
import cadquery as cq
import cap_k2_base_5 as v
import swatch_reference as ref
from revision_checks import check_base,sources

k=v.k
j=k.j
back=-j.slots.SLOT_WIDTH/2
card=ref.card(back).val()
record=check_base(v,label='K2',datum_side=-1,panel=v.panel().val(),previous=k.rough_base().val())
centre=ref.point(ref.DOME_SOURCE,back)
assert centre[0]==-16 and centre[2]==j.slots.FLOOR+14
# Independent source landmarks through the actual rigid transform.
source=cq.Vertex.makeVertex(*ref.DOME_SOURCE)
placed=ref.upright(cq.Workplane('XY').newObject([source]),back).val().Center()
assert (placed-cq.Vector(*centre)).Length<1e-8
axes=[cq.Vector(*ref.point(p,0))-cq.Vector(*ref.point((0,0,0),0))
      for p in ((1,0,0),(0,1,0),(0,0,1))]
assert axes[0].cross(axes[1]).dot(axes[2])>0,'Source pose reflects the real item'
follower=v.panel().val()
seated=follower.translate((0,k.SEATED_TRAVEL_Y,0))
assert seated.intersect(card).Volume()<1e-7 and seated.distance(card)<1e-6,\
    'Correctly rotated REAL card does not settle to follower contact'
assert follower.cut(v.crown().val()).intersect(card).Volume()<1e-7,\
    'Stem/backing touches the card outside intended shoulders'
assert seated.intersect(card.translate((0,0,1))).Volume()>1e-6,\
    'Actual dome does not require more follower motion on withdrawal'
# Old K must FAIL the real source card contact in its claimed seated pose.
legacy=k.card_panel().val().translate((0,k.SEATED_TRAVEL_Y,0))
legacy_wrong_contact=legacy.intersect(card).Volume()
assert legacy_wrong_contact>1e-4,'Regression does not distinguish old reflected reference'
# Turning the real card around moves its bowl to the other side AND faces it away.
cy=back+ref.THICKNESS/2
wrong=card.rotate((0,cy,0),(0,cy,1),180)
wrong_face_contact=seated.intersect(wrong).Volume()
assert wrong_face_contact>1e-4,'Wrong-face insertion looks falsely seated'
record['dome']=dict(source_centre=list(ref.DOME_SOURCE),holder_centre=list(centre),
    real_rotation_determinant=1,correct_face_seated_contact=True,
    old_K_wrong_seated_overlap_mm3=legacy_wrong_contact,
    turned_card_wrong_seated_overlap_mm3=wrong_face_contact,
    seated_spring_travel_y_mm=k.SEATED_TRAVEL_Y,card_lift_requires_extra_motion=True)
record['sources_sha256']=sources(('cap_k2_base_5.py','dome_latch_study.py','swatch_reference.py',
    'upright_datums.py','revision_checks.py','check_k2.py','../filament_archive_swatch/filament_archive_swatch.scad'))
(Path(__file__).parent/'notes/k2_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,variant='K2',dome=record['dome'],contact_z_mm=record['contact_z_mm'])))
