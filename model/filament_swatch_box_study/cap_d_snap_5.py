"""D: plain push-on / pull-off hood with four hidden PETG detents.

Print the matching base and cap together. Existing ungrooved bases are not mates.
Coordinates describe the closed assembly; printable output flips the hood.
"""
import cadquery as cq
from cap_common import *

COUNT = DEFAULT_COUNT
SKIRT_BOTTOM = 6.4  # Exposed lower base band plus underside provide a pull grip.
STEM_THICKNESS = 1.2
STEM_WIDTH = 16.0
BACK_RELIEF = 2.4
SIDE_RELIEF = .8
BACK_WALL = 2.4
SHELL_WALL = STEM_THICKNESS+BACK_RELIEF+BACK_WALL
OUTSIDE_X = CAP_INNER_X+2*SHELL_WALL
OUTSIDE_RADIUS = CAP_INNER_RADIUS+SHELL_WALL
CONTACT_Z = 15.2
FLEX_LENGTH = 16.2
ROOT_Z = CONTACT_Z+FLEX_LENGTH
TIP_BOTTOM_Z = 13.2
TIP_LOWER_Z = 14.8
TIP_UPPER_Z = CONTACT_Z
TIP_TOP_Z = 16.8
GROOVE_DEPTH = .8
TIP_EXTRA_REACH = .15  # Beyond groove floor; crest offset also adds preload.
TIP_X = OUTER_WIDTH/2-GROOVE_DEPTH-TIP_EXTRA_REACH
GROOVE_LOWER_Z = 13.0
GROOVE_FLOOR_LOWER_Z = 14.6
GROOVE_FLOOR_UPPER_Z = 15.0
GROOVE_UPPER_Z = 15.8  # Upper return is a 45-degree printable shoulder.
GROOVE_EXTRA_LENGTH = .8
TIP_EDGE_RADIUS = .15
RELIEF_ROOT_RADIUS = .6
PRINT_ANCHOR = (80,135,0)  # Known Q2C coordinates for retained stem-path review.
MATING_HALF_WIDTH_ERROR = .2  # Screening assumption, not measured print error.
NOMINAL_CREST_TRAVEL = OUTER_WIDTH/2-TIP_X
MAX_CREST_TRAVEL = NOMINAL_CREST_TRAVEL+MATING_HALF_WIDTH_ERROR+FIT_GAP


def detent_centres(count=COUNT):
    if count<5: raise ValueError('This four-detent layout needs at least five card positions')
    return (-outer_depth(count)/2+13,outer_depth(count)/2-13)


def outside_depth(count=COUNT):
    return outer_depth(count)+2*FIT_GAP+2*SHELL_WALL


def box_between(x0,x1,y0,y1,z0,z1):
    return (cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=(False,False,False))
            .translate((x0,y0,z0)))


def mirrored(shape,side):
    return shape if side>0 else shape.mirror('YZ')


def groove(y,side=1):
    face=OUTER_WIDTH/2
    profile=[(face-GROOVE_DEPTH,GROOVE_FLOOR_LOWER_Z),
             (face-GROOVE_DEPTH,GROOVE_FLOOR_UPPER_Z),
             (face,GROOVE_UPPER_Z),(face+1,GROOVE_UPPER_Z),
             (face+1,GROOVE_LOWER_Z),(face,GROOVE_LOWER_Z)]
    cut=(cq.Workplane('XZ',origin=(0,y+(STEM_WIDTH+GROOVE_EXTRA_LENGTH)/2,0))
         .polyline(profile).close().extrude(STEM_WIDTH+GROOVE_EXTRA_LENGTH))
    return mirrored(cut,side)


def base(count=COUNT):
    body=rounded_base(count)
    for y in detent_centres(count):
        for side in (-1,1): body=body.cut(groove(y,side))
    return body


def shell(count=COUNT):
    depth=outer_depth(count)+2*FIT_GAP
    body=(rounded_block(OUTSIDE_X,outside_depth(count),ROOF_TOP-SKIRT_BOTTOM,
                        SKIRT_BOTTOM,OUTSIDE_RADIUS)
          .faces('>Z').edges().fillet(1.6)
          .faces('<Z').edges().chamfer(.3))
    void=rounded_block(CAP_INNER_X,depth,ROOF_UNDERSIDE-SKIRT_BOTTOM+.1,
                       SKIRT_BOTTOM-.1,CAP_INNER_RADIUS)
    body=body.cut(void)
    mouth=(cq.Workplane('XY',origin=(0,0,SKIRT_BOTTOM-.1))
           .rect(CAP_INNER_X+1.2,depth+1.2).workplane(offset=1.7)
           .rect(CAP_INNER_X,depth).loft(ruled=True))
    mouth=mouth.intersect(rounded_block(CAP_INNER_X+1.2,depth+1.2,1.8,
                                        SKIRT_BOTTOM-.1,CAP_INNER_RADIUS+.6))
    return body.cut(mouth)


def seat_stops(count=COUNT):
    # Put seating pads at the ends, clear of the long-side flexures.
    pads=[]
    for end in (-1,1):
        inward=outer_depth(count)/2-1.3
        outward=outside_depth(count)/2
        points=[(end*inward,TOP_Z),(end*outward,TOP_Z),
                (end*outward,TOP_Z+3.6),
                (end*(outer_depth(count)/2+FIT_GAP),TOP_Z+3.6)]
        for x in (-18,18):
            pads.append(cq.Workplane('YZ',origin=(x-3,0,0))
                        .polyline(points).close().extrude(6))
    return cq.Workplane('XY').newObject([compound(*pads)])


def pad(y,side=1):
    x=CAP_INNER_X/2
    points=[(x,TIP_BOTTOM_Z),(TIP_X,TIP_LOWER_Z),(TIP_X,TIP_UPPER_Z),
            (x,TIP_TOP_Z),(x+STEM_THICKNESS,TIP_TOP_Z),
            (x+STEM_THICKNESS,TIP_BOTTOM_Z)]
    p=(cq.Workplane('XZ',origin=(0,y+STEM_WIDTH/2,0))
       .polyline(points).close().extrude(STEM_WIDTH).edges('|Y').fillet(TIP_EDGE_RADIUS))
    return mirrored(p,side)


def leaf(y,side=1):
    x=CAP_INNER_X/2
    stem=box_between(x,x+STEM_THICKNESS,y-STEM_WIDTH/2,y+STEM_WIDTH/2,
                     TIP_BOTTOM_Z,ROOT_Z)
    return mirrored(stem,side).union(pad(y,side))


def cap(count=COUNT,include_detents=True):
    body=shell(count).union(seat_stops(count))
    x=CAP_INNER_X/2
    for y in detent_centres(count):
        rear=box_between(x+STEM_THICKNESS,x+STEM_THICKNESS+BACK_RELIEF,
                         y-STEM_WIDTH/2,y+STEM_WIDTH/2,SKIRT_BOTTOM-.1,ROOT_Z)
        rear=rear.edges('|Y and >Z').fillet(RELIEF_ROOT_RADIUS)
        for side in (-1,1):
            body=body.cut(mirrored(rear,side))
            for edge in (-1,1):
                y0,y1=sorted((y+edge*STEM_WIDTH/2,y+edge*(STEM_WIDTH/2+SIDE_RELIEF)))
                gap=box_between(x-.1,x+STEM_THICKNESS+BACK_RELIEF,y0,y1,
                                SKIRT_BOTTOM-.1,ROOT_Z)
                body=body.cut(mirrored(gap,side))
            bottom=box_between(x-.1,x+STEM_THICKNESS+BACK_RELIEF,
                               y-STEM_WIDTH/2,y+STEM_WIDTH/2,
                               SKIRT_BOTTOM-.1,TIP_BOTTOM_Z)
            body=body.cut(mirrored(bottom,side))
            if include_detents: body=body.union(pad(y,side))
            else:
                stem=box_between(x-.1,x+STEM_THICKNESS,
                                 y-STEM_WIDTH/2,y+STEM_WIDTH/2,
                                 TIP_BOTTOM_Z,ROOT_Z)
                body=body.cut(mirrored(stem,side))
    return body


def print_layout(count=COUNT):
    shift=OUTER_WIDTH/2+OUTSIDE_X/2+10
    return compound(base(count),hood_print(cap(count)).translate((shift,0,0))).translate(PRINT_ANCHOR)


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
