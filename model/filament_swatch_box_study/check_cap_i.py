"""I retention screen and real-H contact/entry checks; no printed force claim."""
import hashlib
import json
from pathlib import Path
import cap_i_grip_keys as i
from physical_analysis.screening import elastic_friction_grip, rectangular_cantilever

h=i.h
directory=Path(__file__).parent
lower=h.base(include_detents=False).val()
bases=[lower.translate((0,y,0)) for y in i.module_centres()]
assert bases[0].intersect(bases[1]).Volume()<1e-7,'Butted H bases overlap'
assert bases[0].distance(bases[1])<1e-7,'The intended fully seated bases do not touch'
full=h.compound(*bases)
hood=h.cap().val()
no_grip=elastic_friction_grip(interference_mm=-h.KEY_FIT_GAP,contact_count=4)
assert no_grip['retention_screen_passes'] is False, 'Unpreloaded H must fail retention'
records=[]
for number,projection in enumerate(i.PROJECTIONS,1):
    key=i.seated_key(number).val()
    assert key.isValid()
    assert len(key.Solids())==1,'A grip key must print as one piece with attached arms'
    normal_overlap=i.seated_interference(projection)
    grip=elastic_friction_grip(interference_mm=normal_overlap,contact_count=4)
    assert grip['preload_present'] and grip['retention_screen_passes'] is None
    assert normal_overlap<i.RELIEF_WIDTH,'Required flexure consumes the whole relief'
    contacts=[]
    for xs in (-1,1):
        for ys in (-1,1):
            lo,hi=sorted((xs*3,xs*9))
            ylo,yhi=sorted((ys*.15,ys*4))
            quadrant=h.block(lo,hi,ylo,yhi,h.KEY_FLOOR_Z,h.KEY_TOP_Z+.1).val()
            overlap=key.intersect(full).intersect(quadrant).Volume()
            assert overlap>1e-5,'A specified grip pad does not meet its actual H pocket'
            # Each flank's outward reaction on its base points towards the seam.
            assert -ys*i.NORMAL[1]*ys>0,'Pad would push the blocks apart'
            contacts.append(dict(side=(xs,ys),relaxed_overlap_mm3=overlap))
    # Bottom 0.1 mm and whole solid core enter without forced contact.
    nose=key.intersect(h.block(-9,9,-4,4,h.KEY_FLOOR_Z,h.KEY_FLOOR_Z+.1).val())
    assert nose.intersect(full).Volume()<1e-7,'Lead-in already collides at first contact'
    core=(i.key_outline().offset2D(i.CORE_GROWTH).extrude(i.KEY_HEIGHT)
          .translate((0,0,h.KEY_FLOOR_Z))).val()
    assert core.intersect(full).Volume()<1e-7,'Solid core consumes the intended normal clearance'
    # Reduced pad envelope represents the required seated space, not a solved
    # deformed flexure. Actual force/deformation must be screened separately.
    space=i.seated_key(number,projection=h.KEY_FIT_GAP).val()
    for lift in (0,.2,1,2,4,8,16,22):
        assert space.translate((0,0,lift)).intersect(full).Volume()<1e-7,'Required seated/entry envelope blocked'
    upper=full.intersect(h.block(-10,10,-5,5,h.SEAM_Z+.01,h.TOP_Z+.1).val())
    for lift in (0,.2,1,2,4,8,16,22):
        assert key.translate((0,0,lift)).intersect(upper).Volume()<1e-7,'Relaxed key hits the full-height H mouth'
    for y in i.module_centres():
        cover=hood.translate((0,y,0))
        assert key.intersect(cover).Volume()<1e-7,'Replacement key blocks hood seating'
        assert key.translate((0,0,.4)).intersect(cover).Volume()>1e-7,'Closed hood no longer covers upward key escape'
    for dy in (0,-.5,-1,-3,-8):
        assert key.translate((0,dy,4)).intersect(bases[1]).Volume()<1e-7,'Key cannot withdraw after a relative-base lift'
        assert bases[0].translate((0,dy,4)).intersect(bases[1]).Volume()<1e-7,'Butted bases cannot separate after lifting'
    beam=rectangular_cantilever(length_mm=i.PAD_STATION,width_mm=i.KEY_HEIGHT,
        thickness_mm=i.ARM_THICKNESS,youngs_modulus_MPa=1200,tip_displacement_mm=normal_overlap)
    # These short arms do not meet the shared slender-beam applicability test.
    # Keep the rejected idealization visible instead of claiming its force.
    assert not beam['small_deflection_applicable']
    records.append(dict(number=number,pad_projection_mm=projection,
        seated_seam_gap_mm=i.KEY_SEAM_GAP,
        nominal_normal_interference_mm=normal_overlap,grip_screen=grip,contacts=contacts,
        single_connected_key=True,lead_in_clear=True,solid_core_clear=True,
        full_mouth_clear=True,hood_seating_clear=True,required_space_envelope_clear=True,
        closed_hood_covers_escape=True,lift_and_withdraw_clear=True,
        beam_idealization=beam,beam_force_not_qualified=True))
sources=['cap_i_grip_keys.py','check_cap_i.py','cap_h_module_5.py','cap_g_module_5.py','cap_e_thin_5.py']
record=dict(original_H=no_grip,variants=records,
    bases_butt_without_overlap=True,
    inputs_sha256={name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in sources},
    scope='Real H CAD contact and required-space screens. Relaxed overlap is intentional. '
          'Space envelope is not a nonlinear contact solution. Actual fit/holding/creep unprinted.')
(directory/'notes/cap_i_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,original_H_rejected=True,variants=[
    dict(number=r['number'],normal_interference_mm=r['nominal_normal_interference_mm'],
         four_contacts=len(r['contacts'])) for r in records])))
