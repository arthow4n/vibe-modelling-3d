"""H proof checks: compact enclosure and actual open-top key insertion/capture.

Collision witnesses establish constrained rigid motions, not force or strength.
"""
import hashlib
import json
from pathlib import Path
from cap_h_module_5 import *

lower=base(include_detents=False).val()
hood=cap().val()
cards=compound(*[cq.Workplane('XY').box(50.4,2.2,80.2,centered=(True,True,False))
                .translate((0,slot_y(i,COUNT)-.3,MAX_SEAT_HEIGHT)) for i in range(COUNT)])
assert hood.distance(lower)<1e-6,'Compact hood rim does not seat'
lifts=(0,.2,1,4,12,16,40,84)
for lift in lifts:
    pose=hood.translate((0,0,lift))
    assert pose.intersect(lower).Volume()<1e-6,'Compact cap hits rigid base'
    assert pose.intersect(cards).Volume()<1e-6,'Compact cap hits card envelope'
for y in detent_centres(COUNT):
    for side in (-1,1):
        p=pad(y,side).val()
        assert p.intersect(hood).Volume()>1e-6,'Closed preload contact missing'
        assert p.intersect(hood.translate((0,0,1))).Volume()>1e-6,'No relaxed withdrawal hold'
        for lift in (0,1,4,12,16):
            moved=p.translate((-side*(MAX_CREST_TRAVEL-MATING_HALF_WIDTH_ERROR),0,0))
            for play in (-FIT_GAP,FIT_GAP):
                assert moved.intersect(hood.translate((play,0,lift))).Volume()<1e-6,'Pad escape space lost'
        assert leaf(y,side).val().translate((-side*MAX_CREST_TRAVEL,0,0)).intersect(cards).Volume()<1e-6

# Test the actual end geometry under the key, not a separate idealized socket.
ends=[]
for y,end in zip(module_centres(2),(1,-1)):
    lo,hi=(FOOT_DEPTH/2-FIXTURE_DEPTH,FOOT_DEPTH/2+.1) if end>0 else (-FOOT_DEPTH/2-.1,-FOOT_DEPTH/2+FIXTURE_DEPTH)
    crop=lower.intersect(block(-FOOT_X/2-.1,FOOT_X/2+.1,lo,hi,0,SEAM_Z).val())
    ends.append(crop.translate((0,y,0)))
joint=compound(*ends)
full_joint=compound(*[lower.translate((0,y,0)) for y in module_centres(2)])
key=connector().val()
stroke=(0,.5,1,2,3,4,8,16,22)
for z in stroke:
    assert key.translate((0,0,z)).intersect(full_joint).Volume()<1e-6,f'Key drop-in blocked at {z}'
assert key.translate((0,0,-.3)).intersect(joint).Volume()>1e-6,'Pocket floor stop missing'
for dx,dy in ((.8,0),(-.8,0),(0,.8),(0,-.8)):
    assert key.translate((dx,dy,0)).intersect(joint).Volume()>1e-6,'Planar capture missing'
for end,y in zip(ends,module_centres(2)):
    outward=-.8 if y<0 else .8
    assert end.translate((0,outward,0)).intersect(key).Volume()>1e-6,'Key does not resist spreading'
    assert end.rotate((0,y,0),(0,y,1),2).intersect(key).Volume()>1e-6,'No yaw constraint'
for y in module_centres(2):
    seated=hood.translate((0,y,0))
    assert seated.intersect(key).Volume()<1e-6,'Key obstructs hood seat'
    assert seated.intersect(key.translate((0,0,.4))).Volume()>1e-6,'Hood does not cover key escape'
# Coupon uses the actual end floor; no independent idealized female fixture.
for end in (1,-1):
    floor=block(-1,1,end*(FOOT_DEPTH/2-1)-.1,end*(FOOT_DEPTH/2-1)+.1,
                .8,KEY_FLOOR_Z-.01).val()
    assert abs(floor.Volume()-floor.intersect(lower).Volume())<1e-6,'Pocket floor missing'

# Occasional separation without pulling the key by a handle: the raised floor
# carries it upward while the other base stays on the desk, with hoods off.
fixed=lower.translate((0,module_centres(2)[1],0))
for z in stroke:
    moving=lower.translate((0,module_centres(2)[0],z))
    assert moving.intersect(fixed).Volume()<1e-6,'Raised base hits stationary base'
    assert key.translate((0,0,z)).intersect(fixed).Volume()<1e-6,'Carried key cannot leave other pocket'
assert KEY_FLOOR_Z+4>SEAM_Z,'Four mm lift does not clear the other pocket'
for dy in (0,-.5,-1,-3,-8):
    assert key.translate((0,dy,4)).intersect(fixed).Volume()<1e-6,'Key cannot leave tall wall notch'
    assert lower.translate((0,module_centres(2)[0]+dy,4)).intersect(fixed).Volume()<1e-6,'Raised base cannot move away'
# A nominal thin nail tip can enter the little recess from above and slide under
# the edge. This access envelope is not a finger-comfort or nail-strength claim.
for side in (-1,1):
    tip=block(3.9,4.7,.3,.5,KEY_FLOOR_Z-.3,KEY_FLOOR_Z-.05).val()
    if side<0: tip=tip.mirror('YZ')
    assert tip.intersect(joint).Volume()<1e-6,'Nail-tip underside access blocked'
    for z in (0,.5,1,2,4):
        entrance=block(5.7,6.0,.3,.5,KEY_FLOOR_Z-.3+z,KEY_FLOOR_Z-.05+z).val()
        if side<0: entrance=entrance.mirror('YZ')
        assert entrance.intersect(full_joint).Volume()<1e-6,'Nail recess entry blocked'
        assert entrance.intersect(key).Volume()<1e-6,'Nail recess blocked by key'

d=Path(__file__).parent
record=dict(compact_module=dict(count=5,body_depth_mm=BODY_DEPTH,foot_depth_mm=FOOT_DEPTH,
                mouth_end_margin_mm=BODY_DEPTH/2-(slot_y(4,COUNT)+2.8),
                cap_seated=True,card_path_clear=True,pad_escape_space=True),
            connector=dict(no_external_handle=True,head_width_mm=2*KEY_HEAD_HALF_X,
                nail_access_envelope_clear=True,relative_base_lift_clear=True,
                vertical_insertion_samples_mm=stroke,nominal_fit_clear=True,
                pocket_floor_stop=True,planar_spread_yaw_obstruction=True,
                hood_covers_vertical_escape=True,embed_mm=KEY_EMBED,
                tall_wall_entry_notch=True,entry_notch_plan_clearance_mm=KEY_FIT_GAP,
                key_to_hood_gap_mm=SEAM_Z-KEY_TOP_Z,
                scope='Full base vertical entry, actual cropped foot contacts and rigid collision witnesses; no load capacity'),
            packing=dict(four_modules_length_mm=4*FOOT_DEPTH+3*MODULE_GAP,
                         former_four_F_modules_mm=4*48.8+3*MODULE_GAP),
            limits='Open hoods allow vertical key removal; no calibrated force, printed fit, group carrying, creep or fatigue qualification. '
                   'Unchanged leaf dimensions inherit E provisional beam assumptions only.',
            source_sha256=hashlib.sha256((d/'cap_h_module_5.py').read_bytes()).hexdigest())
d.joinpath('notes/cap_h_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
