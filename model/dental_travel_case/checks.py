"""Design-intent checks; sampled CAD evidence, never printed-fit qualification."""
import math
from parameters import *
from reference_items import reference_items
from mechanisms import front_latch
from components import clip, socket

OVERLAP_LIMIT = 0.001  # mm3: numerical intersection allowance, not user tolerance


def construction_check(case):
    for name in ('body', 'lid'):
        assert case[name].val().isValid(), name
        assert len(case[name].solids().vals()) == 1, name + ' must be connected'
    assert clip().val().isValid() and len(clip().solids().vals()) == 1
    # Planned print envelope from construction, not repeated mesh/bounds audits.
    assert OW + 6 <= 270, 'Shell length plus 3 mm brim exceeds printer'
    assert 2*OD + 2*(HY-OD/2) + 6 + 6 <= 270
    assert min(SEAM-HINGE_RADIUS*2**0.5-abs(HY-(OD/2-1)),
               SEAM-15) > FLOOR, 'Mechanism root would start below supported wall'


def brush_check(case):
    items = {name: item for name,item in reference_items().items() if name != "paste"}
    for name, item in items.items():
        for shell in ('body', 'lid'):
            assert item.intersect(case[shell]).val().Volume() < OVERLAP_LIMIT, (name, shell)
    for c in case['installed_clips']:
        assert items['handle'].intersect(c).val().Volume() < OVERLAP_LIMIT, 'Handle bore interferes'
    # Button location is tentative: keep entire 105..125 mm band from butt clear.
    for x in CLIP_POSITIONS:
        distance = BRUSH_LENGTH/2-x
        assert distance+CLIP_WIDTH/2 < 105 or distance-CLIP_WIDTH/2 > 125
    assert BRUSH_LENGTH-HANDLE_LENGTH == 90
    assert CLIP_Z+CRADLE_LIFT+HANDLE_DIAMETER/2 < IH, 'Brush hits closed roof'



def paste_check(case):
    paste = reference_items()['paste']
    assert PASTE_LENGTH >= 160 and PASTE_WIDTH >= 55 and PASTE_THICKNESS >= 40
    assert paste.intersect(case['body']).val().Volume() < OVERLAP_LIMIT
    for angle in range(0,181,10):
        lid = case['lid'].rotate((0,HY,SEAM),(1,HY,SEAM),-angle)
        assert paste.intersect(lid).val().Volume() < OVERLAP_LIMIT, ('Tube/lid', angle)


def contents_check(case):
    brush_check(case)
    paste_check(case)

def shells_check(case):
    assert case['body'].intersect(case['lid']).val().Volume() < OVERLAP_LIMIT
    items = reference_items()
    for angle in range(0, 181, 10):
        moving = case['lid'].rotate((0, HY, SEAM), (1, HY, SEAM), -angle)
        assert case['body'].intersect(moving).val().Volume() < OVERLAP_LIMIT, ('Shell path', angle)
        for name, item in items.items():
            assert moving.intersect(item).val().Volume() < OVERLAP_LIMIT, ('Loaded path', angle, name)
        for c in case['installed_clips']:
            assert moving.intersect(c).val().Volume() < OVERLAP_LIMIT, ('Clip/lid path', angle)
    # Ten-degree sampling cannot resolve near-closed detent engagement.
    # latch_check separately tests its obstruction and released lift path.


def clips_check(case):
    assert len(case['installed_clips']) == 2, 'Both brush clips are required'
    assert CLIP_THROAT < HANDLE_DIAMETER, 'No geometric throat capture'
    assert CLIP_RADIUS*2 > HANDLE_DIAMETER, 'Bore would force continuous squeeze'
    for c in case['installed_clips']:
        seated = case['body'].intersect(c).val().Volume()
        assert 0 < seated < 2, ('Expected small friction-rib preload only', seated)
        assert case['body'].intersect(c.translate((1,0,0))).val().Volume() > seated, 'Missing socket back stop'
        assert case['body'].intersect(c.translate((0,0,1))).val().Volume() > seated, 'Missing vertical dovetail capture'
    # Ribs project beyond the nominal channel by 0.15 mm at their apex.
    assert GRIP_BUMP > SOCKET_CLEARANCE, 'Friction cartridge has no designed preload'


def compliance_check():
    # Provisional straight-beam analogy for the curved free arc: a cheap screen,
    # not a force/material calibration or curved-beam stress solution.
    length = CLIP_RADIUS*(math.acos(CLIP_THROAT/(2*CLIP_RADIUS))+math.pi/4)
    displacement = (HANDLE_DIAMETER-CLIP_THROAT)/2
    strain = 3*CLIP_WALL*displacement/(2*length**2)
    assert strain < 0.01, 'Exceeds agent-selected 1% provisional strain screen'


def latch_check(case):
    from samples import hinge_test
    hinge_test()  # exact production hinge: 15 degree sweep and +/-1 mm axial obstruction
    latch = front_latch().rotate((0,HY,SEAM),(1,HY,SEAM),180)
    assert latch.intersect(case['body']).val().Volume() < OVERLAP_LIMIT
    assert latch.translate((0,0,1)).intersect(case['body']).val().Volume() > OVERLAP_LIMIT, 'No latch obstruction to initial lift'
    released = latch.translate((0,-3,0))
    for dz in (0,1,2,3,4,6):
        assert released.translate((0,0,dz)).intersect(case['body']).val().Volume() < OVERLAP_LIMIT, ('Latch release',dz)
