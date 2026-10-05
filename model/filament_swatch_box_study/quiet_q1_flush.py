"""Q1F: recessed TPU 95A jacket within accepted A/G exterior dimensions.

New PETG base and separate TPU insert; exact existing G hood and I3 key.
Millimetres, assembly floor Z0. Print each material separately. Unprinted.
"""
import cadquery as cq
import quiet_q1 as original

archive, g, h = original.archive, original.g, original.h
keys, grips, ref = original.keys, original.grips, original.ref
rounded, block, loft = original.rounded, original.block, original.loft
cards = original.cards

JACKET_WALL = .80
JACKET_FIT = .10  # Per-side assembly cavity allowance, not a friction anchor.
RUNNER_PROJECTION = .20
RUNNER_WIDTH = 3.20
JACKET_X = g.OUTER_WIDTH-2*RUNNER_PROJECTION
JACKET_Y = g.BODY_DEPTH-2*RUNNER_PROJECTION
JACKET_R = 5.0-RUNNER_PROJECTION
CORE_X = JACKET_X-2*(JACKET_WALL+JACKET_FIT)
CORE_Y = JACKET_Y-2*(JACKET_WALL+JACKET_FIT)
CORE_R = JACKET_R-JACKET_WALL-JACKET_FIT
CORE_TOP = archive.TOP
JACKET_TOP = CORE_TOP+.80
FOOT_X, FOOT_Y = g.FOOT_X, g.FOOT_DEPTH
HOOD_X, HOOD_Y, HOOD_R = g.OUTSIDE_X, g.OUTSIDE_DEPTH, g.OUTSIDE_RADIUS
HOOD_INNER_X = g.CAP_INNER_X
SEAT_THICKNESS = .80
SEAT_TOP = g.SEAM_Z
FOOT_TOP = SEAT_TOP-SEAT_THICKNESS  # Recessed support underneath the soft ring.
SEAT_RECESS_GAP = .10
BEAD_Y = g.detent_centres(g.COUNT)
BEAD_WIDTH = 8.0
BEAD_BOTTOM, BEAD_LOWER = 18.2,19.6
BEAD_UPPER, BEAD_TOP = 19.8,21.2
BEAD_ENGAGEMENT = .30
BEAD_TIP_X = HOOD_INNER_X/2+BEAD_ENGAGEMENT
FLEX_CLEARANCE = .80
ANCHOR_DEPTH = .65
ANCHOR_BOTTOM, ANCHOR_TOP = 6.4,9.0
ANCHOR_GROOVE_DEPTH = .80
PRINT_CENTRE = original.PRINT_CENTRE
KEY_ENTRY_EXTRA = .50  # Above foot only, room for comfortable rounded mouths.
PORT_BYPASS_WIDTH, PORT_BYPASS_DEPTH, PORT_BYPASS_Y = 22.,5.2,20.5
RIM_RADIUS = .40  # Both top edges; retain >=.8 mm at the flared corner crest.
ACCESS_EDGE_BREAK = .20

assert CORE_X-(archive.r1.POCKET_WIDTH+2*archive.ENTRY_EXPANSION) > 4.0
assert CORE_Y-(archive.r1.POCKET_DEPTH+2*archive.ENTRY_EXPANSION) > 4.0


def socket(end):
    # Original port plus its actual taller-wall installation route.
    cy=end*g.MODULE_PITCH/2
    reach=g.MODULE_GAP/2+h.KEY_EMBED+h.KEY_FIT_GAP
    entry=block(-h.KEY_HEAD_HALF_X-h.KEY_FIT_GAP,
                h.KEY_HEAD_HALF_X+h.KEY_FIT_GAP,cy-reach-KEY_ENTRY_EXTRA,cy+reach+KEY_ENTRY_EXTRA,
                g.SEAM_Z,JACKET_TOP+1)
    return h.socket(end).union(entry)


def anchor_core():
    d=ANCHOR_GROOVE_DEPTH
    return loft([(ANCHOR_BOTTOM,CORE_X,CORE_Y,CORE_R),
                 (ANCHOR_BOTTOM+d,CORE_X-2*d,CORE_Y-2*d,CORE_R-d),
                 (ANCHOR_TOP-d,CORE_X-2*d,CORE_Y-2*d,CORE_R-d),
                 (ANCHOR_TOP,CORE_X,CORE_Y,CORE_R)])


def flex_recess(y,side):
    face=CORE_X/2
    profile=[(face-FLEX_CLEARANCE,BEAD_BOTTOM-.8),
             (face+2,BEAD_BOTTOM-.8),(face+2,BEAD_TOP+2.8),
             (face,BEAD_TOP+.8+FLEX_CLEARANCE),
             (face-FLEX_CLEARANCE,BEAD_TOP+.8)]
    tool=(cq.Workplane('XZ',origin=(0,y+BEAD_WIDTH/2+.6,0))
          .polyline(profile).close().extrude(BEAD_WIDTH+1.2))
    return g.mirrored(tool,side)


def seating_ring(extra=0,height=SEAT_THICKNESS,z=FOOT_TOP):
    outer=rounded(HOOD_X+2*extra,HOOD_Y+2*extra,height,z,HOOD_R+extra)
    inner=rounded(CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,
                  height+.02,z-.01,CORE_R+JACKET_FIT)
    ring=outer.cut(inner)
    # Detour inside each key port, across the solid end wall below the card rim.
    # Cutting the ports then leaves one connected insert, with open key routes.
    for end in (-1,1):
        bypass=rounded(PORT_BYPASS_WIDTH+2*extra,PORT_BYPASS_DEPTH+2*extra,
                       height,z,1.+extra).translate((0,end*PORT_BYPASS_Y,0))
        ring=ring.union(bypass.intersect(outer))
    return ring


def port_bypass_access(end):
    # Open channel above each inward band so it can descend to its seat.
    # The card-side end wall remains continuous; no change to the card pocket.
    x,y,r=(PORT_BYPASS_WIDTH+2*SEAT_RECESS_GAP,
           PORT_BYPASS_DEPTH+2*SEAT_RECESS_GAP,1.+SEAT_RECESS_GAP)
    e=ACCESS_EDGE_BREAK
    # Open the cutter at the rim, breaking the newly exposed access-channel lip.
    return loft([(SEAT_TOP,x,y,r),(CORE_TOP-e,x,y,r),
                 (CORE_TOP,x+2*e,y+2*e,r+e),
                 (JACKET_TOP+1,x+2*e,y+2*e,r+e)]).translate((0,end*PORT_BYPASS_Y,0))


def base():
    body=(rounded(CORE_X,CORE_Y,CORE_TOP,0,CORE_R).cut(archive.pocket())
          .faces('>Z').edges().fillet(RIM_RADIUS))
    foot=(rounded(FOOT_X,FOOT_Y,g.SEAM_Z,0,g.FOOT_RADIUS)
          .faces('<Z').edges().chamfer(g.FOOT_BOTTOM_CHAMFER)
          .faces('>Z').edges().fillet(g.FOOT_TOP_ROUND)
          .cut(archive.pocket()))
    body=body.union(foot).cut(seating_ring(SEAT_RECESS_GAP,
        SEAT_THICKNESS+.1,FOOT_TOP))
    outer=rounded(CORE_X+4,CORE_Y+4,ANCHOR_TOP-ANCHOR_BOTTOM,
                  ANCHOR_BOTTOM,CORE_R+2)
    body=body.cut(outer.cut(anchor_core()))
    for y in BEAD_Y:
        for side in (-1,1):
            body=body.cut(flex_recess(y,side))
    for side in (-1,1):
        body=body.cut(grips.pocket(side)).cut(socket(side)).cut(port_bypass_access(side))
    # The widened access channel's plan corners are rounded in its cutter.
    return body


def bead(y,side):
    face=JACKET_X/2
    profile=[(face-.15,BEAD_BOTTOM),(face,BEAD_BOTTOM),
             (BEAD_TIP_X,BEAD_LOWER),(BEAD_TIP_X,BEAD_UPPER),
             (face,BEAD_TOP),(face-.15,BEAD_TOP)]
    part=(cq.Workplane('XZ',origin=(0,y+BEAD_WIDTH/2,0))
          .polyline(profile).close().extrude(BEAD_WIDTH)
          .edges('|Y').filter(lambda e:e.Center().x>face+.1).fillet(.15))
    return g.mirrored(part,side)


def jacket(include_beads=True):
    outer=rounded(JACKET_X,JACKET_Y,JACKET_TOP-SEAT_TOP,SEAT_TOP,JACKET_R)
    inner=loft([(SEAT_TOP-.01,CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,CORE_R+JACKET_FIT),
                (CORE_TOP,CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,CORE_R+JACKET_FIT),
                (JACKET_TOP+.01,CORE_X-1,CORE_Y-1,CORE_R-.5)])
    part=outer.cut(inner).union(seating_ring())
    d=ANCHOR_DEPTH
    anchor_outer=rounded(JACKET_X,JACKET_Y,ANCHOR_TOP-ANCHOR_BOTTOM,
                         ANCHOR_BOTTOM,JACKET_R)
    x,y,r=CORE_X+2*JACKET_FIT,CORE_Y+2*JACKET_FIT,CORE_R+JACKET_FIT
    anchor_inner=loft([(ANCHOR_BOTTOM,x,y,r),
                       (ANCHOR_BOTTOM+d,x-2*d,y-2*d,r-d),
                       (ANCHOR_TOP-d,x-2*d,y-2*d,r-d),
                       (ANCHOR_TOP,x,y,r)])
    part=part.union(anchor_outer.cut(anchor_inner))
    length=CORE_TOP-SEAT_TOP
    for side in (-1,1):
        for x in (-20.,0.,20.):
            # .2 mm outward lead, .2 mm embedded root; no single-line thin sheet.
            runner=(rounded(RUNNER_WIDTH,.60,length,SEAT_TOP,.25)
                    .faces('>Z').edges().fillet(.18)
                    .translate((x,side*(JACKET_Y/2-.10),0)))
            part=part.union(runner)
        runner=(rounded(.60,RUNNER_WIDTH,length,SEAT_TOP,.25)
                .faces('>Z').edges().fillet(.18)
                .translate((side*(JACKET_X/2-.10),0,0)))
        part=part.union(runner)
        if include_beads:
            for y in BEAD_Y:
                part=part.union(bead(y,side))
    part=part.cut(socket(1)).cut(socket(-1))
    # Preserve the accepted grip path through the recessed soft seat too.
    return part.cut(grips.pocket(1)).cut(grips.pocket(-1))


def hood():
    return g.cap()  # Exact G hood; exterior and internal grooves are unchanged.


def finger(side):
    return grips.finger(side)


def print_base():
    return base().translate(PRINT_CENTRE)


def print_jacket():
    return jacket().translate((PRINT_CENTRE[0],PRINT_CENTRE[1],-FOOT_TOP))


def installation_envelopes(jacket,expansion):
    """Independent access envelopes, not a connected elastic deformation pose."""
    upper=jacket.intersect(block(-40,40,-30,30,SEAT_TOP,JACKET_TOP+1).val())
    upper=upper.scale(expansion).translate((0,0,-SEAT_TOP*(expansion-1)))
    seat=jacket.intersect(block(-40,40,-30,30,FOOT_TOP,SEAT_TOP).val())
    return [('expanded upper sleeve',upper),('unexpanded port-bypass seat',seat)]
