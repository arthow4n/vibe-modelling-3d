"""One-piece postcard easel. X across card, +Y rearward, +Z up; mm.
Print result as supplied, feet on the bed. Card references are not exported.
"""
import math
import cadquery as cq

FOOT_SPACING = 56.0
FOOT_WIDTH = 8.0
FRONT_Y = -2.0
REAR_Y = 38.0
BASE_HEIGHT = 1.6
BACK_HEIGHT = 55.0  # above the card's bottom edge
LEAN_DEG = 12.0
RIB_WIDTH = 3.2
TOP_DEPTH = 2.4
SLOT_GAP = 1.2  # horizontal clearance at the bottom, not a friction fit
LIP_HEIGHT = 1.4
LIP_THICKNESS = 1.2
CONNECTOR_Y = 22.0
CONNECTOR_DEPTH = 5.0
CORNER_RADIUS = 1.0
EDGE_BREAK = 0.25
SLOPE = math.tan(math.radians(LEAN_DEG))

assert SLOT_GAP >= 1.0 and LIP_THICKNESS >= 1.2
assert SLOT_GAP + BACK_HEIGHT * SLOPE + TOP_DEPTH < REAR_Y
assert FOOT_WIDTH > RIB_WIDTH and BACK_HEIGHT > LIP_HEIGHT


def foot(x):
    pad = (cq.Workplane('XY').center(x, (FRONT_Y + REAR_Y)/2)
           .rect(FOOT_WIDTH, REAR_Y-FRONT_Y).extrude(BASE_HEIGHT)
           .edges('|Z').fillet(CORNER_RADIUS))
    # Broad triangular side gusset: no bridge, tall unsupported mast or rear leg joint.
    profile = [(SLOT_GAP, BASE_HEIGHT),
               (SLOT_GAP + BACK_HEIGHT*SLOPE, BASE_HEIGHT+BACK_HEIGHT),
               (SLOT_GAP + BACK_HEIGHT*SLOPE+TOP_DEPTH, BASE_HEIGHT+BACK_HEIGHT),
               (REAR_Y-1.0, BASE_HEIGHT),]
    rib = (cq.Workplane('YZ', origin=(x-RIB_WIDTH/2,0,0))
           .polyline(profile).close().extrude(RIB_WIDTH)
           .edges('|X').fillet(0.6))
    # Overlap the base by 0.4 mm so rounding cannot disconnect the gusset.
    root = (cq.Workplane('XY').box(RIB_WIDTH, REAR_Y-1-SLOT_GAP-0.8, 0.8,
                                  centered=(True,False,False))
            .translate((x,SLOT_GAP+0.8,BASE_HEIGHT-0.4)))
    lip = (cq.Workplane('XY').box(FOOT_WIDTH-1, LIP_THICKNESS,
                                 LIP_HEIGHT+0.4, centered=(True,False,False))
           .translate((x,-LIP_THICKNESS,BASE_HEIGHT-0.4))
           .edges('|Z').fillet(0.35).edges('>Z').chamfer(EDGE_BREAK))
    return pad.union(rib).union(root).union(lip)


def build():
    connector = (cq.Workplane('XY').box(FOOT_SPACING, CONNECTOR_DEPTH, BASE_HEIGHT,
                                       centered=(True,True,False))
                 .translate((0,CONNECTOR_Y,0)).edges('|Z').fillet(CORNER_RADIUS))
    return connector.union(foot(-FOOT_SPACING/2)).union(foot(FOOT_SPACING/2)).clean()


result = build()
