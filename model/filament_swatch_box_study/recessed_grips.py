"""J4/K4: upper-open pockets in the original foot, no outward additions.

Side entry under the closed G hood; press the rounded upward floor down while
lifting the hood. Reference finger volumes are inspection-only assumptions.
"""
import math
import cap_g_module_5 as g
from upward_grips import restore_foot

INNER_X=g.FOOT_X/2-2.2
LENGTH_Y=18.0
FLOOR_Z=2.0
PLAN_ROUND=1.0
ROOT_ROUND=.6
CONTACT_EDGE_ROUND=.35
NOSE_X=INNER_X+.85
NOSE_THICKNESS=2.6
NOSE_WIDTH=12.0
FINGER_BODY_X=g.FOOT_X/2+.5


def pocket(side=1):
    outer=g.FOOT_X/2+2
    root_x=INNER_X+ROOT_ROUND
    root_z=FLOOR_Z+ROOT_ROUND
    edge_x=g.FOOT_X/2-CONTACT_EDGE_ROUND
    edge_z=FLOOR_Z-CONTACT_EDGE_ROUND
    q=math.sqrt(2)
    # Concave inner root and convex exposed floor edge are explicit arcs.
    # This avoids a fragile post-boolean fillet where three cut faces meet.
    profile=(g.cq.Workplane('XZ',origin=(0,LENGTH_Y/2,0))
        .moveTo(INNER_X,g.SEAM_Z+.1).lineTo(INNER_X,root_z)
        .threePointArc((root_x-ROOT_ROUND/q,root_z-ROOT_ROUND/q),(root_x,FLOOR_Z))
        .lineTo(edge_x,FLOOR_Z)
        .threePointArc((edge_x+CONTACT_EDGE_ROUND/q,edge_z+CONTACT_EDGE_ROUND/q),
                       (g.FOOT_X/2,edge_z))
        .lineTo(outer,edge_z).lineTo(outer,g.SEAM_Z+.1).close().extrude(LENGTH_Y))
    plan=(g.rounded_block(outer-INNER_X,LENGTH_Y,g.SEAM_Z+.2,0,PLAN_ROUND)
          .translate(((outer+INNER_X)/2,0,0)))
    tool=profile.intersect(plan)
    return g.mirrored(tool,side)


def revise(previous):
    return previous.union(restore_foot()).cut(pocket()).cut(pocket(-1))


def changed_region():
    box=g.block(INNER_X-.05,g.FOOT_X/2+.1,-LENGTH_Y/2-.1,LENGTH_Y/2+.1,
                -.1,g.SEAM_Z+.11)
    return box.union(box.mirror('YZ'))


def finger(side=1,withdrawal=0,press=0):
    """Assumed 2.6 mm distal pad/nail edge, not a simulated anatomical finger.

    Side insertion keeps the thicker outside body beyond the hood; the 12 mm
    wide contact nose enters the 3 mm high recess. Comfort/compressibility and
    user reach remain physical questions. Positive withdrawal is outward.
    """
    tip=g.block(NOSE_X,FINGER_BODY_X+2,-NOSE_WIDTH/2,NOSE_WIDTH/2,
                FLOOR_Z-press,FLOOR_Z+NOSE_THICKNESS-press)
    body=(g.rounded_block(25,16,8,FLOOR_Z-press,2)
          .translate((FINGER_BODY_X+12.5,0,0)).faces('>Z').edges().fillet(1))
    return g.mirrored(tip.union(body).translate((withdrawal,0,0)),side)
