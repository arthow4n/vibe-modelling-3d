"""G: compact five-card module plus one drop-in alignment key, millimetres.

Desk-supported row proof, not a joined-group carrying design. Previous versions
remain intact. Print base floor down, hood roof down, key flat.
"""
from cap_e_thin_5 import (cq,rounded_base,rounded_block,compound,contents,slot_y,
    OUTER_WIDTH,TOP_Z,ROOF_TOP,ROOF_UNDERSIDE,ROOF_RADIUS,WALL,BAND_WALL,
    BAND_TOP,BAND_TRANSITION,SEAM_Z,CAP_INNER_X,CAP_INNER_RADIUS,MAX_SEAT_HEIGHT,
    FIT_GAP,MOUTH_HEIGHT,MOUTH_EXPANSION,STEM_WIDTH,STEM_THICKNESS,
    ROOT_Z,TIP_TOP_Z,BACK_RELIEF,SIDE_RELIEF,ROOT_BLEND,FOOT_X,FOOT_RADIUS,
    FOOT_TOP_ROUND,FOOT_BOTTOM_CHAMFER,GROOVE_DEPTH,MAX_CREST_TRAVEL,
    MATING_HALF_WIDTH_ERROR,block,mirrored,leaf,pad,groove,hood_print,
    outer_depth,detent_centres)

COUNT = 5
END_TRIM = 2.0
BODY_DEPTH = outer_depth(COUNT)-2*END_TRIM
INNER_DEPTH = BODY_DEPTH+2*FIT_GAP
OUTSIDE_X = CAP_INNER_X+2*BAND_WALL
OUTSIDE_DEPTH = INNER_DEPTH+2*BAND_WALL
OUTSIDE_RADIUS = CAP_INNER_RADIUS+BAND_WALL
UPPER_INNER_X = OUTSIDE_X-2*WALL
UPPER_INNER_DEPTH = OUTSIDE_DEPTH-2*WALL
FOOT_DEPTH = OUTSIDE_DEPTH+.4
MODULE_GAP = .3
MODULE_PITCH = FOOT_DEPTH+MODULE_GAP
KEY_FLOOR_Z = 1.5
KEY_TOP_Z = SEAM_Z-.1
KEY_FIT_GAP = .2
KEY_EMBED = 1.8  # Leaves 0.4 mm to the tall body end for vertical key entry.
KEY_WAIST_HALF_X = 3.0
KEY_HEAD_HALF_X = 5.0
KEY_ARM_HALF_Y = 1.0
KEY_END_X = FOOT_X/2
GRIP_LENGTH = 4.0
GRIP_DEPTH = 8.6
PRINT_ANCHOR = (80,135,0)
HOOD_SHIFT = FOOT_X/2+OUTSIDE_X/2+10
KEY_PRINT_ANCHOR = (220,135,0)
FIXTURE_DEPTH = 8.0


def require_five(count):
    if count!=COUNT:
        raise ValueError('G is the five-card proof; no ten-card module is included')


def key_outline():
    """One planar bow-tie head with a side-access pull arm."""
    seam=MODULE_GAP/2
    head=seam+KEY_EMBED
    points=[(-KEY_WAIST_HALF_X,-seam),(-KEY_HEAD_HALF_X,-head),
            (KEY_HEAD_HALF_X,-head),(KEY_WAIST_HALF_X,-seam),
            (KEY_WAIST_HALF_X,seam),(KEY_HEAD_HALF_X,head),
            (-KEY_HEAD_HALF_X,head),(-KEY_WAIST_HALF_X,seam)]
    return cq.Workplane('XY').polyline(points).close()


def socket(end=1):
    """Open-top pocket; translating the same key outline sets both end mates."""
    cy=end*MODULE_PITCH/2
    pocket=(key_outline().offset2D(KEY_FIT_GAP)
            .extrude(SEAM_Z-KEY_FLOOR_Z+.3).translate((0,cy,KEY_FLOOR_Z)))
    arm=block(0,KEY_END_X+GRIP_LENGTH+1,
              cy-KEY_ARM_HALF_Y-KEY_FIT_GAP,cy+KEY_ARM_HALF_Y+KEY_FIT_GAP,
              KEY_FLOOR_Z,SEAM_Z+.3)
    return pocket.union(arm)


def base(count=COUNT,include_detents=True,include_sockets=True):
    require_five(count)
    envelope=(rounded_block(OUTER_WIDTH,BODY_DEPTH,TOP_Z,0,5.0)
              .faces('>Z').edges().fillet(1.0))
    body=rounded_base(count).intersect(envelope)
    foot=(rounded_block(FOOT_X,FOOT_DEPTH,SEAM_Z,0,FOOT_RADIUS)
          .faces('<Z').edges().chamfer(FOOT_BOTTOM_CHAMFER)
          .faces('>Z').edges().fillet(FOOT_TOP_ROUND))
    grip=(cq.Workplane('XZ',origin=(0,9,0))
          .polyline([(FOOT_X/2-2,-.1),(FOOT_X/2-2,1),
                     (FOOT_X/2+.5,3.5),(FOOT_X/2+2,3.5),(FOOT_X/2+2,-.1)])
          .close().extrude(18).edges('|Y').fillet(.35))
    foot=foot.cut(grip).cut(grip.mirror('YZ'))
    foot=foot.cut(rounded_block(OUTER_WIDTH-.4,BODY_DEPTH-.4,SEAM_Z+.2,-.1,4.8))
    body=body.union(foot)
    face=OUTER_WIDTH/2
    for y in detent_centres(COUNT):
        outer=block(face-STEM_THICKNESS,face+1.5,y-STEM_WIDTH/2-SIDE_RELIEF,
                    y+STEM_WIDTH/2+SIDE_RELIEF,ROOT_Z,TIP_TOP_Z+.5)
        rear=block(face-STEM_THICKNESS-BACK_RELIEF,face-STEM_THICKNESS,
                   y-STEM_WIDTH/2,y+STEM_WIDTH/2,ROOT_Z,TIP_TOP_Z+.5)
        rear=rear.edges('|Y and <Z').fillet(ROOT_BLEND)
        for side in (-1,1):
            body=body.cut(mirrored(outer,side)).cut(mirrored(rear,side))
            for edge in (-1,1):
                lo,hi=sorted((y+edge*STEM_WIDTH/2,
                              y+edge*(STEM_WIDTH/2+SIDE_RELIEF)))
                body=body.cut(mirrored(block(face-STEM_THICKNESS-BACK_RELIEF,
                    face+1.5,lo,hi,ROOT_Z,TIP_TOP_Z+.5),side))
            body=body.union(leaf(y,side,include_detents))
    if include_sockets:
        body=body.cut(socket(1)).cut(socket(-1))
    return body


def cap(count=COUNT,include_pockets=True):
    require_five(count)
    outer=(rounded_block(OUTSIDE_X,OUTSIDE_DEPTH,ROOF_TOP-SEAM_Z,SEAM_Z,OUTSIDE_RADIUS)
           .faces('>Z').edges().fillet(ROOF_RADIUS)
           .faces('<Z').edges().fillet(.2))
    lower=rounded_block(CAP_INNER_X,INNER_DEPTH,BAND_TOP-SEAM_Z+.1,
                        SEAM_Z-.1,CAP_INNER_RADIUS)
    start=BAND_TOP-BAND_TRANSITION
    upper=(rounded_block(UPPER_INNER_X,UPPER_INNER_DEPTH,ROOF_UNDERSIDE-start,
                         start,OUTSIDE_RADIUS-WALL)
           .faces('>Z').edges().fillet(ROOF_RADIUS-WALL)
           .faces('<Z').edges().chamfer(BAND_TRANSITION))
    body=outer.cut(lower.union(upper))
    mouth=(rounded_block(CAP_INNER_X+2*MOUTH_EXPANSION,
                         INNER_DEPTH+2*MOUTH_EXPANSION,MOUTH_HEIGHT+.1,SEAM_Z-.1,
                         CAP_INNER_RADIUS+MOUTH_EXPANSION)
           .faces('>Z').edges().chamfer(MOUTH_EXPANSION))
    body=body.cut(mouth)
    if include_pockets:
        for y in detent_centres(COUNT):
            for side in (-1,1):
                body=body.cut(groove(y,side))
    return body


def connector():
    """Assembled pose: flat key above its pocket floor, tab outside the hood."""
    head=key_outline().extrude(KEY_TOP_Z-KEY_FLOOR_Z).translate((0,0,KEY_FLOOR_Z))
    arm=block(0,KEY_END_X+GRIP_LENGTH/2,-KEY_ARM_HALF_Y,KEY_ARM_HALF_Y,
              KEY_FLOOR_Z,KEY_TOP_Z)
    grip=(rounded_block(GRIP_LENGTH,GRIP_DEPTH,KEY_TOP_Z-KEY_FLOOR_Z,
                        KEY_FLOOR_Z,1.0)
          .translate((KEY_END_X+GRIP_LENGTH/2,0,0)))
    return head.union(arm).union(grip).faces('>Z or <Z').edges().chamfer(.15)


def key_print():
    return connector().translate((0,0,-KEY_FLOOR_Z))


def module_centres(number=2):
    return [(i-(number-1)/2)*MODULE_PITCH for i in range(number)]


def end_fixture(end=1):
    """Actual end geometry; local port face at Y=0, original print orientation."""
    if end>0:
        lo,hi=FOOT_DEPTH/2-FIXTURE_DEPTH,FOOT_DEPTH/2+.1
    else:
        lo,hi=-FOOT_DEPTH/2-.1,-FOOT_DEPTH/2+FIXTURE_DEPTH
    part=base().intersect(block(-FOOT_X/2-.1,FOOT_X/2+.1,lo,hi,0,SEAM_Z))
    return part.translate((0,-end*FOOT_DEPTH/2,0))


def print_layout():
    return compound(base().translate(PRINT_ANCHOR),
        hood_print(cap()).translate((PRINT_ANCHOR[0]+HOOD_SHIFT,PRINT_ANCHOR[1],0)),
        key_print().translate(KEY_PRINT_ANCHOR))


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
