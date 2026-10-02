"""F affected checks; E base-leaf mechanics are unchanged, not newly calibrated."""
import hashlib
import json
from pathlib import Path
from cap_f_flat_5 import *

records=[]
for count in (5,20):
    lower=base(count,include_detents=False).val()
    hood=cap(count).val()
    cards=compound(*[cq.Workplane('XY').box(50.4,2.2,80.2,centered=(True,True,False))
                    .translate((0,slot_y(i,count)-.3,MAX_SEAT_HEIGHT))
                    for i in range(count)])
    assert hood.distance(lower)<1e-6,'Rim does not seat on E foot'
    for lift in (0,.2,1,4,12,16,40,84):
        pose=hood.translate((0,0,lift))
        assert pose.intersect(lower).Volume()<1e-6,'Hood obstructs E base'
        assert pose.intersect(cards).Volume()<1e-6,'Hood obstructs card envelope'
    for y in detent_centres(count):
        for side in (-1,1):
            p=pad(y,side).val()
            assert p.intersect(hood).Volume()>1e-6,'Missing closed preload contact'
            assert p.intersect(hood.translate((0,0,1))).Volume()>1e-6,'No relaxed retention obstruction'
            for lift in (0,1,4,12,16):
                for play in (-FIT_GAP,FIT_GAP):
                    moved=p.translate((-side*(MAX_CREST_TRAVEL-MATING_HALF_WIDTH_ERROR),0,0))
                    assert moved.intersect(hood.translate((play,0,lift))).Volume()<1e-6,\
                        'Pad escape space lost'
            skin=mirrored(block(CAP_INNER_X/2+GROOVE_DEPTH+.01,BAND_X/2-.01,
                                y-.5,y+.5,19.5,19.9),side).val()
            assert abs(skin.Volume()-skin.intersect(hood).Volume())<1e-6,'Pocket skin lost'
    records.append(dict(count=count,rim_seated=True,rigid_withdrawal_clear=True,
                        pad_contact_and_escape_space=True,pocket_skin_mm=BAND_WALL-GROOVE_DEPTH))
d=Path(__file__).parent
record=dict(configurations=records,base_identity=hashlib.sha256((d/'cap_e_thin_5.py').read_bytes()).hexdigest(),
            unchanged_base_screen='cap_e_checks.json; unchanged leaves, material assumptions and relief',
            limits='Rigid pad translation is not an elastic release solution. Physical hood '
                   'smoothness, shell compliance and closure forces remain unknown.')
d.joinpath('notes/cap_f_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
