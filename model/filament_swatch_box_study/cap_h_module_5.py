"""H: G-sized module with a wider drop-in key, no protruding arm. Millimetres."""
import cap_g_module_5 as g
from cap_g_module_5 import *

KEY_WAIST_HALF_X = 4.0
KEY_HEAD_HALF_X = 8.0
KEY_EMBED = 3.2
NAIL_RADIUS = 1.5
NAIL_X = KEY_WAIST_HALF_X+1.0
NAIL_BOTTOM_Z = KEY_FLOOR_Z-.4
ENTRY_EDGE_ROUND = .35
KEY_PRINT_ANCHOR = (210,135,0)


def key_outline():
    seam=MODULE_GAP/2
    head=seam+KEY_EMBED
    return (cq.Workplane('XY').polyline([
        (-KEY_WAIST_HALF_X,-seam),(-KEY_HEAD_HALF_X,-head),
        (KEY_HEAD_HALF_X,-head),(KEY_WAIST_HALF_X,-seam),
        (KEY_WAIST_HALF_X,seam),(KEY_HEAD_HALF_X,head),
        (-KEY_HEAD_HALF_X,head),(-KEY_WAIST_HALF_X,seam)]).close())


def socket(end=1):
    cy=end*MODULE_PITCH/2
    pocket=(key_outline().offset2D(KEY_FIT_GAP)
            .extrude(SEAM_Z-KEY_FLOOR_Z+.3).translate((0,cy,KEY_FLOOR_Z)))
    # A straight-sided notch above the foot admits the wider key and lets it
    # leave sideways after clearing the foot, without lifting above the wall.
    reach=MODULE_GAP/2+KEY_EMBED+KEY_FIT_GAP
    entry=block(-KEY_HEAD_HALF_X-KEY_FIT_GAP,KEY_HEAD_HALF_X+KEY_FIT_GAP,
                cy-reach,cy+reach,SEAM_Z,TOP_Z+.3)
    pocket=pocket.union(entry)
    for side in (-1,1):
        recess=(cq.Workplane('XY').center(side*NAIL_X,cy).circle(NAIL_RADIUS)
                .extrude(SEAM_Z-NAIL_BOTTOM_Z+.3).translate((0,0,NAIL_BOTTOM_Z)))
        pocket=pocket.union(recess)
    return pocket


def base(count=COUNT,include_detents=True):
    part=(g.base(count,include_detents,include_sockets=False)
          .cut(socket(1)).cut(socket(-1)))
    # The new tall-wall mouth corners are hand-accessible when the hood is off.
    mouth=part.edges('|Z').filter(lambda e:
        abs(abs(e.Center().x)-(KEY_HEAD_HALF_X+KEY_FIT_GAP))<1e-5
        and abs(abs(e.Center().y)-BODY_DEPTH/2)<1e-5)
    if len(mouth.vals())!=4:
        raise ValueError('Expected four new tall-wall mouth edges for rounding')
    return mouth.fillet(ENTRY_EDGE_ROUND)


def connector():
    return (key_outline().extrude(KEY_TOP_Z-KEY_FLOOR_Z)
            .translate((0,0,KEY_FLOOR_Z)).faces('>Z or <Z').edges().chamfer(.15))


def key_print():
    return connector().translate((0,0,-KEY_FLOOR_Z))


def end_fixture(end=1):
    lo,hi=(FOOT_DEPTH/2-FIXTURE_DEPTH,FOOT_DEPTH/2+.1) if end>0 else (-FOOT_DEPTH/2-.1,-FOOT_DEPTH/2+FIXTURE_DEPTH)
    return (base().intersect(block(-FOOT_X/2-.1,FOOT_X/2+.1,lo,hi,0,SEAM_Z))
            .translate((0,-end*FOOT_DEPTH/2,0)))


def print_layout():
    return compound(base().translate(PRINT_ANCHOR),
        hood_print(cap()).translate((PRINT_ANCHOR[0]+HOOD_SHIFT,PRINT_ANCHOR[1],0)),
        key_print().translate(KEY_PRINT_ANCHOR))


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
