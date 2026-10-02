"""A cap seats on its four pads, clears cards and lifts past them.

This is rigid fit/motion evidence, not a measured friction fit or carrying latch.
"""
import json
from pathlib import Path
import cadquery as cq
from cap_common import *
from cap_a_lift_off_5 import cap

checks=[]
for count in (5,20):
    base=rounded_base(count).val()
    hood=cap(count).val()
    assert base.intersect(hood).Volume()<1e-6, 'Cap penetrates base'
    assert base.distance(hood)<1e-6, 'Cap has no independent seat stop'
    if count==5:
        from card_base_petg_5 import build_base as previous_base
        legacy=previous_base().val()
        assert legacy.intersect(hood).Volume()<1e-6, 'Cap does not fit earlier footprint'
        assert legacy.distance(hood)<1e-6, 'Previous base does not reach stop pads'
    for card in contents(count):
        assert hood.intersect(card).Volume()<1e-6, 'Cap or stop touches card'
    # Conservative max-height unchamfered card envelopes.
    cards=[cq.Workplane('XY').box(50.4,2.2,80.2,centered=(True,True,False))
           .translate((0,slot_y(i,count)-.3,MAX_SEAT_HEIGHT)).val() for i in range(count)]
    assert all(hood.intersect(card).Volume()<1e-6 for card in cards)
    for lift in (0,.2,1,4,12,30,60,76):
        moving=hood.translate((0,0,lift))
        assert moving.intersect(base).Volume()<1e-6
        assert all(moving.intersect(card).Volume()<1e-6 for card in cards)
    checks.append(dict(count=count,pad_seat=True,roof_headroom_mm=HEADROOM,
        lifts_mm=[0,.2,1,4,12,30,60,76],scope='Nominal vertical lift; no tilt, friction or retention qualification'))
path=Path(__file__).parent/'notes/cap_a_checks.json'
path.write_text(json.dumps(dict(checks=checks,retention='Unlatched desk cover; no lifting-by-cap qualification'),indent=2)+'\n')
print(json.dumps(checks))
