"""Shared cap exploration dimensions; historical printed sources stay intact."""
import cadquery as cq
from card_base_corner_seat_5 import build_base as seating_base
from card_base_test import OUTER_WIDTH, TOP_Z, outer_depth, slot_y
from study import UPRIGHT_HEIGHT, FLOOR, card_reference

DEFAULT_COUNT = 5
FULL_COUNT = 20
CAP_WALL = 2.4
FIT_GAP = 0.4  # Per coordinate side, provisional PETG printed clearance.
BASE_CORNER = 5.0
BASE_RIM_RADIUS = 1.0
LEGACY_CORNER = 3.0  # Cavity accommodates both old and newly rounded base.
HEADROOM = 4.0
MAX_SEAT_HEIGHT = FLOOR+0.4
ROOF_UNDERSIDE = MAX_SEAT_HEIGHT+UPRIGHT_HEIGHT+HEADROOM
ROOF_TOP = ROOF_UNDERSIDE+CAP_WALL
HOOD_BOTTOM = TOP_Z-12.0
CAP_INNER_X = OUTER_WIDTH+2*FIT_GAP
CAP_OUTER_X = CAP_INNER_X+2*CAP_WALL
CAP_INNER_RADIUS = LEGACY_CORNER+FIT_GAP
CAP_OUTER_RADIUS = CAP_INNER_RADIUS+CAP_WALL


def rounded_block(width, depth, height, z=0, radius=3):
    return (cq.Workplane('XY').box(width,depth,height,centered=(True,True,False))
            .translate((0,0,z)).edges('|Z').fillet(radius))


def rounded_base(count=DEFAULT_COUNT, include_leaves=True):
    envelope=(rounded_block(OUTER_WIDTH,outer_depth(count),TOP_Z,radius=BASE_CORNER)
              .faces('<Z').edges().chamfer(.4)
              .faces('>Z').edges().fillet(BASE_RIM_RADIUS))
    # Changes exterior only: slots, ramps, leaves and their gaps are preserved.
    return seating_base(count,include_leaves=include_leaves).intersect(envelope)


def contents(count=DEFAULT_COUNT, sparse=False):
    indices=range(count) if not sparse else sorted({0,count//2,count-1})
    return [card_reference().translate((0,slot_y(i,count)-.4,0)).val() for i in indices]


def cap_depth(count=DEFAULT_COUNT):
    return outer_depth(count)+2*FIT_GAP+2*CAP_WALL


def hood_shell(count=DEFAULT_COUNT):
    inner_depth=outer_depth(count)+2*FIT_GAP
    shell=(rounded_block(CAP_OUTER_X,cap_depth(count),ROOF_TOP-HOOD_BOTTOM,
                         HOOD_BOTTOM,CAP_OUTER_RADIUS)
           .faces('>Z').edges().fillet(1.2)
           .faces('<Z').edges().chamfer(.3))
    cavity=rounded_block(CAP_INNER_X,inner_depth,
                         ROOF_UNDERSIDE-HOOD_BOTTOM+.1,HOOD_BOTTOM-.1,CAP_INNER_RADIUS)
    shell=shell.cut(cavity)
    # Lead the skirt onto the base from every side without opening the roof.
    mouth=(cq.Workplane('XY',origin=(0,0,HOOD_BOTTOM-.1))
           .rect(CAP_INNER_X+1.2,inner_depth+1.2)
           .workplane(offset=1.7).rect(CAP_INNER_X,inner_depth).loft(ruled=True))
    # Restrict the square loft to its intended small rounded corner footprint.
    mouth=mouth.intersect(rounded_block(CAP_INNER_X+1.2,inner_depth+1.2,1.8,
                                        HOOD_BOTTOM-.1,CAP_INNER_RADIUS+.6))
    return shell.cut(mouth)


def stop_pads(count=DEFAULT_COUNT):
    """Four internal pads seat on the base rim, independently of the cards.

In roof-down print placement the pads grow inward from the skirt on a ramp.
"""
    pads=[]
    inside=OUTER_WIDTH/2-1.3
    outside=CAP_OUTER_X/2
    for side in (-1,1):
        points=[(side*inside,TOP_Z),(side*outside,TOP_Z),
                (side*outside,TOP_Z+3.6),(side*CAP_INNER_X/2,TOP_Z+3.6)]
        for y in (-outer_depth(count)/2+10,outer_depth(count)/2-10):
            pads.append(cq.Workplane('XZ',origin=(0,y+3,0))
                        .polyline(points).close().extrude(6))
    result=pads[0]
    for pad in pads[1:]: result=result.union(pad)
    return result


def side_grips(count=DEFAULT_COUNT):
    grips=[]
    length=min(24,cap_depth(count)-16)
    for side in (-1,1):
        x=CAP_OUTER_X/2
        points=[(side*(x-.1),40),(side*(x+.8),41),
                (side*(x+.8),43),(side*(x-.1),44)]
        grips.append(cq.Workplane('XZ',origin=(0,length/2,0))
                     .polyline(points).close().extrude(length).edges('|Y').fillet(.25))
    return grips[0].union(grips[1])


def hood_print(hood):
    return hood.rotate((0,0,0),(1,0,0),180).translate((0,0,ROOF_TOP))


def compound(*parts):
    return cq.Compound.makeCompound([p.val() if isinstance(p,cq.Workplane) else p for p in parts])
