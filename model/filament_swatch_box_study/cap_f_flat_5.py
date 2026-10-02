"""F: smooth flush hood exterior, 0.8 mm upper walls, unchanged E mating base.

Lower snap reinforcement is inside the hood. Roof down / base floor down.
"""
from cap_e_thin_5 import (cq,COUNT,WALL,ROOF,ROOF_TOP,ROOF_RADIUS,BAND_WALL,
    BAND_TOP,BAND_TRANSITION,SEAM_Z,BAND_X,FOOT_X,PRINT_ANCHOR,CAP_INNER_X,
    CAP_INNER_RADIUS,ROOF_UNDERSIDE,MOUTH_HEIGHT,MOUTH_EXPANSION,
    GROOVE_DEPTH,STEM_WIDTH,GROOVE_SIDE_CLEARANCE,FIT_GAP,
    MAX_CREST_TRAVEL,MATING_HALF_WIDTH_ERROR,MAX_SEAT_HEIGHT,
    rounded_block,inner_depth,band_depth,base,groove,pad,detent_centres,
    hood_print,hood_shift,compound,contents,slot_y,block,mirrored)

OUTSIDE_X = BAND_X
OUTSIDE_RADIUS = CAP_INNER_RADIUS+BAND_WALL
UPPER_INNER_X = OUTSIDE_X-2*WALL
UPPER_INNER_RADIUS = OUTSIDE_RADIUS-WALL
TRANSITION_START = BAND_TOP-BAND_TRANSITION
BOTTOM_EDGE_ROUND = .2


def cap(count=COUNT,include_pockets=True):
    outer=(rounded_block(OUTSIDE_X,band_depth(count),ROOF_TOP-SEAM_Z,
                         SEAM_Z,OUTSIDE_RADIUS)
           .faces('>Z').edges().fillet(ROOF_RADIUS)
           .faces('<Z').edges().fillet(BOTTOM_EDGE_ROUND))
    lower=rounded_block(CAP_INNER_X,inner_depth(count),BAND_TOP-SEAM_Z+.1,
                        SEAM_Z-.1,CAP_INNER_RADIUS)
    upper=(rounded_block(UPPER_INNER_X,band_depth(count)-2*WALL,
                         ROOF_UNDERSIDE-TRANSITION_START,TRANSITION_START,
                         UPPER_INNER_RADIUS)
           .faces('>Z').edges().fillet(ROOF_RADIUS-WALL)
           .faces('<Z').edges().chamfer(BAND_TRANSITION))
    body=outer.cut(lower.union(upper))
    mouth=(rounded_block(CAP_INNER_X+2*MOUTH_EXPANSION,
                         inner_depth(count)+2*MOUTH_EXPANSION,MOUTH_HEIGHT+.1,
                         SEAM_Z-.1,CAP_INNER_RADIUS+MOUTH_EXPANSION)
           .faces('>Z').edges().chamfer(MOUTH_EXPANSION))
    body=body.cut(mouth)
    if include_pockets:
        for y in detent_centres(count):
            for side in (-1,1):
                body=body.cut(groove(y,side))
    return body


def print_layout(count=COUNT):
    return compound(base(count),hood_print(cap(count)).translate((hood_shift(count),0,0))).translate(PRINT_ANCHOR)


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
