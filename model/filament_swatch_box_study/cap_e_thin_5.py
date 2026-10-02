"""E: 0.8 mm PETG hood, seated rim and integral base-mounted detents.

Print the matching two-part layout: base floor down, hood roof down. Units mm.
Earlier swatch guides and broad clips are reused; closure leaves are separate.
"""
import cadquery as cq
from cap_common import (DEFAULT_COUNT, OUTER_WIDTH, TOP_Z, outer_depth, slot_y,
                        rounded_base, rounded_block, contents, compound,
                        CAP_INNER_X, CAP_INNER_RADIUS, FIT_GAP,
                        ROOF_UNDERSIDE, MAX_SEAT_HEIGHT)

COUNT = DEFAULT_COUNT
WALL = .8
ROOF = .8
ROOF_TOP = ROOF_UNDERSIDE+ROOF
ROOF_RADIUS = 3.0
BAND_WALL = 1.6
BAND_TOP = 24.0
BAND_TRANSITION = .8
SEAM_Z = 5.0
OUTSIDE_X = CAP_INNER_X+2*WALL
BAND_X = CAP_INNER_X+2*BAND_WALL
FOOT_X = BAND_X+.4
FOOT_OVERHANG = .2
FOOT_RADIUS = 6.0
FOOT_TOP_ROUND = .6
FOOT_BOTTOM_CHAMFER = .8
MOUTH_HEIGHT = 1.2
MOUTH_EXPANSION = .4
STEM_THICKNESS = 1.2
STEM_WIDTH = 12.0
ROOT_Z = 5.0
CONTACT_Z = 19.8
FLEX_LENGTH = CONTACT_Z-ROOT_Z
TIP_BOTTOM_Z = 18.2
TIP_LOWER_Z = 19.6
TIP_TOP_Z = 21.2
TIP_X = CAP_INNER_X/2+.8
TIP_EDGE_RADIUS = .15
BACK_RELIEF = 2.0
SIDE_RELIEF = .8
ROOT_BLEND = .6
GROOVE_DEPTH = .65
GROOVE_BOTTOM_Z = 17.95
GROOVE_LOWER_Z = 19.35
GROOVE_UPPER_Z = 20.05
GROOVE_TOP_Z = 21.45
GROOVE_SIDE_CLEARANCE = .4
MATING_HALF_WIDTH_ERROR = .2  # Provisional, not measured print error.
NOMINAL_CREST_TRAVEL = TIP_X-CAP_INNER_X/2
MAX_CREST_TRAVEL = NOMINAL_CREST_TRAVEL+FIT_GAP+MATING_HALF_WIDTH_ERROR
PRINT_ANCHOR = (80,135,0)


def inner_depth(count=COUNT):
    return outer_depth(count)+2*FIT_GAP


def band_depth(count=COUNT):
    return inner_depth(count)+2*BAND_WALL


def detent_centres(count=COUNT):
    if count<5:
        raise ValueError('This four-detent layout requires at least five positions')
    return (-outer_depth(count)/2+13, outer_depth(count)/2-13)


def block(x0,x1,y0,y1,z0,z1):
    return (cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,
                                 centered=(False,False,False)).translate((x0,y0,z0)))


def mirrored(shape,side):
    return shape if side>0 else shape.mirror('YZ')


def pad(y,side=1):
    face=OUTER_WIDTH/2
    points=[(face,TIP_BOTTOM_Z),(TIP_X,TIP_LOWER_Z),
            (TIP_X,CONTACT_Z),(face,TIP_TOP_Z)]
    p=(cq.Workplane('XZ',origin=(0,y+STEM_WIDTH/2,0))
       .polyline(points).close().extrude(STEM_WIDTH)
       .edges('|Y').fillet(TIP_EDGE_RADIUS))
    return mirrored(p,side)


def leaf(y,side=1,include_pad=True):
    face=OUTER_WIDTH/2
    stem=block(face-STEM_THICKNESS,face,y-STEM_WIDTH/2,y+STEM_WIDTH/2,
               ROOT_Z-.1,TIP_TOP_Z)
    stem=mirrored(stem,side)
    return stem.union(pad(y,side)) if include_pad else stem


def base(count=COUNT,include_detents=True):
    body=rounded_base(count)
    foot=(rounded_block(FOOT_X,band_depth(count)+.4,SEAM_Z,0,FOOT_RADIUS)
          .faces('<Z').edges().chamfer(FOOT_BOTTOM_CHAMFER)
          .faces('>Z').edges().fillet(FOOT_TOP_ROUND))
    # Wide underside purchase, returning at 45 degrees in the print direction.
    grip=(cq.Workplane('XZ',origin=(0,9,0))
          .polyline([(FOOT_X/2-2,-.1),(FOOT_X/2-2,1.0),
                     (FOOT_X/2+.5,3.5),(FOOT_X/2+2,3.5),
                     (FOOT_X/2+2,-.1)]).close().extrude(18)
          .edges('|Y').fillet(.35))
    foot=foot.cut(grip).cut(grip.mirror('YZ'))
    # Add the foot around the existing base, never fill its card slots/seats.
    foot=foot.cut(rounded_block(OUTER_WIDTH-.4,outer_depth(count)-.4,
                               SEAM_Z+.2,-.1,5.0-.2))
    body=body.union(foot)
    face=OUTER_WIDTH/2
    for y in detent_centres(count):
        outer=block(face-STEM_THICKNESS,face+1.5,
                    y-STEM_WIDTH/2-SIDE_RELIEF,y+STEM_WIDTH/2+SIDE_RELIEF,
                    ROOT_Z,TIP_TOP_Z+.5)
        rear=block(face-STEM_THICKNESS-BACK_RELIEF,face-STEM_THICKNESS,
                   y-STEM_WIDTH/2,y+STEM_WIDTH/2,ROOT_Z,TIP_TOP_Z+.5)
        rear=rear.edges('|Y and <Z').fillet(ROOT_BLEND)
        for side in (-1,1):
            body=body.cut(mirrored(outer,side)).cut(mirrored(rear,side))
            for edge in (-1,1):
                y0,y1=sorted((y+edge*STEM_WIDTH/2,
                              y+edge*(STEM_WIDTH/2+SIDE_RELIEF)))
                gap=block(face-STEM_THICKNESS-BACK_RELIEF,face+1.5,
                          y0,y1,ROOT_Z,TIP_TOP_Z+.5)
                body=body.cut(mirrored(gap,side))
            body=body.union(leaf(y,side,include_detents))
    return body


def groove(y,side=1):
    x=CAP_INNER_X/2
    points=[(x-.1,GROOVE_BOTTOM_Z),(x,GROOVE_BOTTOM_Z),
            (x+GROOVE_DEPTH,GROOVE_LOWER_Z),
            (x+GROOVE_DEPTH,GROOVE_UPPER_Z),(x,GROOVE_TOP_Z),
            (x-.1,GROOVE_TOP_Z)]
    cut=(cq.Workplane('XZ',origin=(0,y+STEM_WIDTH/2+GROOVE_SIDE_CLEARANCE,0))
         .polyline(points).close().extrude(STEM_WIDTH+2*GROOVE_SIDE_CLEARANCE))
    return mirrored(cut,side)


def cap(count=COUNT,include_pockets=True):
    depth=inner_depth(count)
    outer=(rounded_block(OUTSIDE_X,depth+2*WALL,ROOF_TOP-SEAM_Z,SEAM_Z,
                         CAP_INNER_RADIUS+WALL)
           .faces('>Z').edges().fillet(ROOF_RADIUS))
    band=(rounded_block(BAND_X,band_depth(count),BAND_TOP-SEAM_Z,SEAM_Z,
                        CAP_INNER_RADIUS+BAND_WALL)
          .faces('>Z').edges().chamfer(BAND_TRANSITION)
          .faces('<Z').edges().fillet(.2))
    outer=outer.union(band)
    inner=(rounded_block(CAP_INNER_X,depth,ROOF_UNDERSIDE-SEAM_Z+.1,SEAM_Z-.1,
                         CAP_INNER_RADIUS)
           .faces('>Z').edges().fillet(ROOF_RADIUS-WALL))
    body=outer.cut(inner)
    # A rounded, four-sided lead-in. Expands the cavity, retaining >=1.2 mm rim.
    mouth=(rounded_block(CAP_INNER_X+2*MOUTH_EXPANSION,
                         depth+2*MOUTH_EXPANSION,MOUTH_HEIGHT+.1,SEAM_Z-.1,
                         CAP_INNER_RADIUS+MOUTH_EXPANSION)
           .faces('>Z').edges().chamfer(MOUTH_EXPANSION))
    body=body.cut(mouth)
    if include_pockets:
        for y in detent_centres(count):
            for side in (-1,1):
                body=body.cut(groove(y,side))
    return body


def hood_print(shape):
    return shape.rotate((0,0,0),(1,0,0),180).translate((0,0,ROOF_TOP))


def hood_shift(count=COUNT):
    return FOOT_X/2+BAND_X/2+10


def print_layout(count=COUNT):
    return compound(base(count),hood_print(cap(count)).translate((hood_shift(count),0,0))).translate(PRINT_ANCHOR)


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
