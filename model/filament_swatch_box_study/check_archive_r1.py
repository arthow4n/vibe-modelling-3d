"""R1 intent checks: real cards, desk containment, EXACT G and two key ends.

Rigid geometry only. No friction, print fit, comfort, carrying or impact rating.
"""
import hashlib
import json
import math
from pathlib import Path
import cadquery as cq
import archive_r1_base_15 as a
import cap_j4_base_5 as j4
import cap_i_grip_keys as keys
import swatch_reference as ref
from check_corner_seat import card_envelope

directory = Path(__file__).parent
base = a.base().val()
rigid = a.base(include_detents=False).val()
old = j4.base().val()
hood = a.g.cap().val()
assert base.isValid() and len(base.Solids())==1, 'Disconnected archive support'
assert rigid.isValid()

# Preserve the actual J4 closure/grip geometry, not just nominal parameters.
grip_mask = a.grips.changed_region().val()
closure_regions = []
for y in a.g.detent_centres(a.g.COUNT):
    mask = a.g.block(a.g.OUTER_WIDTH/2-a.g.STEM_THICKNESS,
        a.g.OUTER_WIDTH/2+1.5,y-a.g.STEM_WIDTH/2,y+a.g.STEM_WIDTH/2,
        a.g.ROOT_Z+.01,a.g.TIP_TOP_Z+.1).val()
    closure_regions.extend([mask,mask.mirror('YZ')])
for mask in [grip_mask,*closure_regions]:
    x,y = base.intersect(mask),old.intersect(mask)
    assert x.cut(y).Volume()<1e-6 and y.cut(x).Volume()<1e-6, \
        'Accepted hood leaf or recessed grip changed'
port_records = []
for end in (-1,1):
    lo,hi = sorted((end*18.75,end*(a.g.FOOT_DEPTH/2+.1)))
    region = a.g.block(-9,9,lo,hi,keys.h.KEY_FLOOR_Z-.1,a.g.SEAM_Z).val()
    x,y = base.intersect(region),old.intersect(region)
    assert x.cut(y).Volume()<1e-6 and y.cut(x).Volume()<1e-6, 'Lower key capture/stop changed'
    port_records.append(dict(end=end,J4_lower_capture_exactly_preserved=True))

# Archive joins J4 in both orientations, with the same existing key and G hood.
key = keys.seated_key(3).val()
space = keys.seated_key(3,projection=keys.h.KEY_FIT_GAP).val()
core = (keys.key_outline().offset2D(keys.CORE_GROWTH).extrude(keys.KEY_HEIGHT)
    .translate((0,0,keys.h.KEY_FLOOR_Z))).val()
for archive_end in (-1,1):
    centres = keys.module_centres()
    components = [base if archive_end==1 else old,old if archive_end==1 else base]
    joined = cq.Compound.makeCompound([p.translate((0,y,0)) for p,y in zip(components,centres)])
    assert core.intersect(joined).Volume()<1e-6, 'Key core requires force against a rigid stop'
    for lift in (0,.2,1,2,4,8,20,48):
        assert space.translate((0,0,lift)).intersect(joined).Volume()<1e-6, 'Taller archive wall roofs over key entry'
    for xs in (-1,1):
        for ys in (-1,1):
            lo,hi = sorted((xs*3,xs*9))
            yl,yh = sorted((ys*.15,ys*4))
            patch = a.g.block(lo,hi,yl,yh,keys.h.KEY_FLOOR_Z,keys.h.KEY_TOP_Z+.1).val()
            assert key.intersect(joined).intersect(patch).Volume()>1e-5, 'Missing key flank capture at one end'
    for y in centres:
        cover = hood.translate((0,y,0))
        assert key.intersect(cover).Volume()<1e-6
        assert key.translate((0,0,.4)).intersect(cover).Volume()>1e-6, 'Closed G no longer covers key escape'

# Actual source swatches all seat on the same floor, free of rigid obstructions.
one = ref.card(-a.STACK_DEPTH/2).val()
cards = [one.translate((0,n*ref.THICKNESS,0)) for n in range(a.COUNT)]
floor_contacts = []
floor = a.g.block(-a.POCKET_WIDTH/2,a.POCKET_WIDTH/2,
    -a.POCKET_DEPTH/2,a.POCKET_DEPTH/2,0,a.FLOOR).val()
for card in cards:
    assert card.intersect(base).Volume()<1e-6, 'Source card cannot seat upright'
    assert card.distance(floor)<1e-7, 'Card floats above its supporting floor'
    overlap = card.translate((0,0,-.02)).intersect(floor).Volume()
    assert overlap>1e-4, 'No actual bottom material on the flat floor'
    floor_contacts.append(overlap/.02)
stack = cq.Compound.makeCompound(cards)

# Entire conservative stack enters from eight horizontal directions, then descends.
envelope = card_envelope(ref.HEIGHT,a.STACK_DEPTH,4).translate((0,a.STACK_DEPTH/2,0)).val()
entry_samples = 0
for sx,sy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
    for step in range(9):
        f = step/8
        pose = envelope.translate((sx*(1-f),sy*(1-f),a.TOP_Z-a.FUNNEL_HEIGHT*f+.01))
        assert pose.intersect(base).Volume()<1e-6, 'Flared entry cannot correct placement'
        entry_samples += 1
for z in (a.STRAIGHT_TOP,30,20,10,a.FLOOR):
    assert envelope.translate((0,0,z)).intersect(base).Volume()<1e-6, 'Straight descent obstructed'
# Individual extraction from the middle and both ends, with neighbours in place.
for n in (0,7,14):
    for lift in (0,.5,4,15,45,82):
        lifted = cards[n].translate((0,0,lift))
        assert lifted.intersect(base).Volume()<1e-6, 'Individual card extraction blocked'
        for neighbour in (n-1,n+1):
            if 0<=neighbour<a.COUNT:
                assert lifted.intersect(cards[neighbour]).Volume()<1e-6

# Free lean reaches real retaining walls before the centroid crosses the pocket.
# Exclude the floor from witnesses; floor penetration is not wall containment.
walls = base.intersect(a.g.block(-40,40,-30,30,a.FLOOR+.5,a.TOP_Z+1).val())
tilt_records = []
single_card = ref.card(-ref.THICKNESS/2).val()
def leaned(y,axis,angle):
    c = single_card.translate((0,y,0))
    pivot = (0,y,a.FLOOR)
    end = (1,y,a.FLOOR) if axis=='X' else (0,y+1,a.FLOOR)
    floor_lift = (ref.THICKNESS/2 if axis=='X' else ref.HEIGHT/2)*abs(math.sin(math.radians(angle)))
    return c.rotate(pivot,end,angle).translate((0,0,floor_lift))

for y in (-a.POCKET_DEPTH/2+ref.THICKNESS/2,0,a.POCKET_DEPTH/2-ref.THICKNESS/2):
    for axis in ('X','Y'):
        for sign in (-1,1):
            low,high = 0.,45.
            assert leaned(y,axis,sign*high).intersect(walls).Volume()>1e-5
            for _ in range(9):
                mid = (low+high)/2
                if leaned(y,axis,sign*mid).intersect(walls).Volume()>1e-5:
                    high = mid
                else:
                    low = mid
            witness = leaned(y,axis,sign*high)
            com = witness.Center()
            assert abs(com.x)<a.POCKET_WIDTH/2 and abs(com.y)<a.POCKET_DEPTH/2, \
                'Card centroid crosses the pocket before its retaining contact'
            tilt_records.append(dict(y_mm=y,axis=axis,direction=sign,
                first_contact_bracket_deg=[low,high],centroid_xy_mm=[com.x,com.y]))

# A one-degree full-stack lean cannot bypass the straight guides.
for axis in ('X','Y'):
    for angle in (-1,1):
        pivot = (0,0,a.FLOOR)
        end = (1,0,a.FLOOR) if axis=='X' else (0,1,a.FLOOR)
        lift = (a.STACK_DEPTH/2 if axis=='X' else ref.HEIGHT/2)*abs(math.sin(math.radians(angle)))
        tilted = stack.rotate(pivot,end,angle).translate((0,0,lift))
        assert tilted.intersect(walls).Volume()>1e-5, 'Fully seated stack lacks upright guidance'

# Exact hood rigid clearance during lifting; intentional catches are excluded.
for lift in (0,.2,2,10,25,50,84):
    cover = hood.translate((0,0,lift))
    assert cover.intersect(rigid).Volume()<1e-6, 'Existing G hood clashes with archive structure'
    assert cover.intersect(stack).Volume()<1e-6, 'Existing G roof cannot cover the full stack'
assert hood.distance(rigid)<1e-7, 'G rim no longer lands on the base'

record = dict(ok=True,nominal_capacity=a.COUNT,pocket_mm=[a.POCKET_WIDTH,a.POCKET_DEPTH],
    total_seated_allowance_mm=[a.WIDTH_ALLOWANCE,a.STACK_ALLOWANCE],
    guide_height_mm=a.STRAIGHT_TOP-a.FLOOR,wall_height_mm=a.WALL_HEIGHT,
    floor_contacts_proxy_area_mm2=floor_contacts,entry_direction_samples=entry_samples,
    entry_offset_mm=1.,individual_extraction=True,desk_lean_witnesses=tilt_records,
    full_stack_one_degree_lean_blocked=True,exact_G_rigid_seats_lifts_and_covers=True,
    hood_leaf_and_grip_geometry_preserved=True,ports=port_records,
    I3_complete_join_both_orientations=True,closed_G_covers_key_escape=True,
    source_sha256={name:hashlib.sha256((directory/name).read_bytes()).hexdigest()
        for name in ('archive_r1_base_15.py','check_archive_r1.py','swatch_reference.py',
                     'cap_i_grip_keys.py','cap_j4_base_5.py','cap_g_module_5.py',
                     'cap_h_module_5.py','cap_e_thin_5.py','recessed_grips.py')},
    limits='Nominal 2 mm rigid cards. Engraving omitted. Sampled hand-guided entry and vertical extraction; '
           'lean witnesses are quasistatic geometric contact, not a dynamic escape proof. '
           'Actual friction, support response, comfort, printed fit and durability untested. '
           'Key preload is inherited geometry, not a new force qualification.')
(directory/'notes/archive_r1_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
