"""B: upright-card drawer inside a fixed five-sided printed enclosure.

Print layout: tray floor down; enclosure back down with open front facing up.
No hardware, latch or travel-retention claim. Units millimetres.
"""
import cadquery as cq
from cap_common import *
from card_base_petg_5 import block

DOOR_THICKNESS = CAP_WALL
DOOR_RADIUS = 3.6
LIP_DEPTH = 3.0
LIP_THICKNESS = 1.6
LIP_TOP = ROOF_UNDERSIDE-FIT_GAP


def front_y(count): return -outer_depth(count)/2-FIT_GAP
def back_y(count): return outer_depth(count)/2+FIT_GAP+CAP_WALL


def housing(count=DEFAULT_COUNT):
    front,back=front_y(count),back_y(count)
    shell=(cq.Workplane('XY').box(CAP_OUTER_X,back-front,ROOF_TOP+CAP_WALL,
                                  centered=(True,True,False))
           .translate((0,(front+back)/2,-CAP_WALL))
           .edges('|Y').fillet(DOOR_RADIUS)
           .faces('<Y').edges().chamfer(.3))
    cavity=block(-CAP_INNER_X/2,CAP_INNER_X/2,
                 front-.1,back-CAP_WALL,0,ROOF_UNDERSIDE)
    return shell.cut(cavity)


def front_structure(count=DEFAULT_COUNT):
    front=front_y(count)
    panel=(cq.Workplane('XZ',origin=(0,front,ROOF_TOP/2))
           .rect(CAP_OUTER_X,ROOF_TOP).extrude(DOOR_THICKNESS)
           .edges('|Y').fillet(DOOR_RADIUS))
    neck=block(-OUTER_WIDTH/2+1,OUTER_WIDTH/2-1,
               front-.1,-outer_depth(count)/2+.3,0,2.4)
    result=panel.union(neck)
    # Side lips grow rearward from the front panel, above the base's top edge.
    side_profile=[(front-.1,TOP_Z+.2),(front-.1,LIP_TOP),
                  (front+LIP_DEPTH,LIP_TOP),(front+LIP_DEPTH,TOP_Z+.2+LIP_DEPTH)]
    for x in (-OUTER_WIDTH/2,OUTER_WIDTH/2-LIP_THICKNESS):
        lip=(cq.Workplane('YZ',origin=(x,0,0)).polyline(side_profile).close()
             .extrude(LIP_THICKNESS))
        result=result.union(lip)
    # Top lip also grows on a slope, avoiding an unsupported flat first layer.
    top_profile=[(front-.1,LIP_TOP-5),(front-.1,LIP_TOP),
                 (front+LIP_DEPTH,LIP_TOP),(front+LIP_DEPTH,LIP_TOP-2)]
    top=(cq.Workplane('YZ',origin=(-OUTER_WIDTH/2,0,0))
         .polyline(top_profile).close().extrude(OUTER_WIDTH))
    result=result.union(top)
    grip_profile=[(front-DOOR_THICKNESS+.1,48),
                  (front-DOOR_THICKNESS-1.2,49.3),
                  (front-DOOR_THICKNESS-1.2,52.7),
                  (front-DOOR_THICKNESS+.1,54)]
    grip=(cq.Workplane('YZ',origin=(-12,0,0)).polyline(grip_profile).close()
          .extrude(24).edges('|X').fillet(.3))
    return result.union(grip)


def drawer(count=DEFAULT_COUNT):
    return rounded_base(count).union(front_structure(count))


def housing_print(count=DEFAULT_COUNT):
    return (housing(count).rotate((0,0,0),(1,0,0),-90)
            .translate((0,0,back_y(count)))
            .faces('<Z').edges().chamfer(.4))


def print_layout(count=DEFAULT_COUNT):
    return compound(drawer(count),housing_print(count).translate((CAP_OUTER_X+10,0,0)))


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
