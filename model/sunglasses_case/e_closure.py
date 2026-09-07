"""Accepted E interfaces in their original coupon coordinates (mm).

Side-effect-free production component module. Original reference: the E export
from bca684e, preserved in keeper_latch_trials.py. Keep flexure lengths and fits
unchanged when placing these features: translate them, do not scale them.
Reference front wall Y=-20, open lid front Y=77.439..., seam Z=30.
"""
import math
import cadquery as cq

REFERENCE_SEAM = 30.0
REFERENCE_DEPTH = 40.0
REFERENCE_HY = 20.0 + 5.6*math.sqrt(2) + 0.8
LOOP_THICKNESS = 2.8
LOOP_WIDTH = 18.0
LEAF_WIDTH = 3.0
LOOP_WALL_GAP = 3.9
RELEASE_TRAVEL = 3.2
SEATED_GAP = 0.2
KEY_ENTRY_CLEARANCE = 0.16
KEY_SEATED_CLEARANCE = -0.04
RAIL_HEIGHT = 3.0

def profile(x, points, width):
    return cq.Workplane('YZ',origin=(x,0,0)).polyline(points).close().extrude(width)

def outward_profile(x, points, width):
    return profile(x,[(-REFERENCE_DEPTH/2-r,z) for r,z in points],width)

def receiver():
    boss=outward_profile(-5.5,[(-0.3,19),(3.5,22.8),(3.5,30),(-0.3,30)],12)
    diamond=outward_profile(-5.6,[(0.6,25),(1.8,23.2),(3.0,25),(1.8,26.8)],11.3)
    slit=outward_profile(-5.6,[(1.8,24.3),(3.6,26.1),(3.6,27.5),(1.8,25.7)],11.3)
    return boss.cut(diamond.union(slit))

def keeper():
    def key_points(gap):
        return [(-REFERENCE_DEPTH/2-r,z) for r,z in
                [(0.6+gap,25),(1.8,23.2+gap),(3.0-gap,25),(1.8,26.8-gap)]]
    key=(cq.Workplane('YZ',origin=(-5.5,0,0)).polyline(key_points(KEY_SEATED_CLEARANCE)).close()
         .workplane(offset=11).polyline(key_points(KEY_ENTRY_CLEARANCE)).close().loft(ruled=True))
    neck=outward_profile(-5.5,[(1.8,24.5),(3.8,26.5),(3.8,27.5),(1.8,25.5)],11)
    reach=LOOP_WALL_GAP+RELEASE_TRAVEL
    tooth=outward_profile(-5.5,[(3.5,REFERENCE_SEAM-6+SEATED_GAP),
        (reach,REFERENCE_SEAM-6+SEATED_GAP),(reach,25.8),(3.5,29.4)],11)
    return key.union(neck).union(tooth)

def loop(thickness=LOOP_THICKNESS):
    front=2*REFERENCE_HY+REFERENCE_DEPTH/2
    inner=LOOP_WALL_GAP; outer=inner+thickness
    def out(x, points, width):
        return profile(x,[(front+r,z) for r,z in points],width)
    rail_z=REFERENCE_SEAM+6
    latch=None
    for x in (-LOOP_WIDTH/2,LOOP_WIDTH/2-LEAF_WIDTH):
        root=out(x,[(-0.6,1.5),(outer,1.5+outer+0.6),
                    (outer,REFERENCE_SEAM-18.5),(-0.6,REFERENCE_SEAM-18.5)],LEAF_WIDTH)
        leaf=out(x,[(inner,REFERENCE_SEAM-20),(outer,REFERENCE_SEAM-20),
                    (outer,rail_z+RAIL_HEIGHT),(inner,rail_z+RAIL_HEIGHT)],LEAF_WIDTH)
        part=root.union(leaf)
        part=part.edges(cq.selectors.NearestToPointSelector(
            (x+LEAF_WIDTH/2,front+inner,REFERENCE_SEAM-18.5))).fillet(0.8)
        latch=part if latch is None else latch.union(part)
    rail=out(-LOOP_WIDTH/2,[(inner,rail_z),(outer,rail_z),
                           (outer,rail_z+RAIL_HEIGHT),(inner,rail_z+RAIL_HEIGHT)],LOOP_WIDTH)
    grip=out(-4,[(outer-0.1,rail_z+1),(outer+0.8,rail_z+1.9),
                 (outer+0.8,rail_z+2.8),(outer-0.1,rail_z+2.8)],8)
    return latch.union(rail).union(grip)
