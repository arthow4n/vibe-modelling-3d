"""Two ten-card decks under a hinged cover. mm; fresh product architecture.

Body coordinates are the assembled coordinates. Lid builders return the closed
pose; lid_print() turns its broad exterior roof onto the bed. Inspection entry
points alone add reference cards. No geometry from retired boxes is used.
"""
import cadquery as cq
from functools import lru_cache

CARD_X, CARD_Y, CARD_T = 80., 50., 2.
PER_POCKET = 10
CARD_ALLOWANCE = .7             # on each side, independent of print fit
WALL, FLOOR, DIVIDER = 2.4, 1.6, 1.6
FINGER_BAY, UNDER_CARD = 12., 4.
POCKET_X = CARD_X + 2*CARD_ALLOWANCE
POCKET_Y = CARD_Y + 2*CARD_ALLOWANCE
WIDTH = 2*POCKET_X + DIVIDER + 2*WALL
DEPTH = POCKET_Y + FINGER_BAY + 2*WALL
CARD_BOTTOM = FLOOR + UNDER_CARD
RIM_Z = CARD_BOTTOM + PER_POCKET*CARD_T + 2.4
LIP_H, LIP_T, LIP_INSET = 2., .8, 1.6
LID_WALL, LID_ROOF = 1.2, 1.6
LID_INSIDE = RIM_Z + 3.2
TOTAL_Z = LID_INSIDE + LID_ROOF
CORNER = 4.
HINGE_Y, HINGE_Z = DEPTH/2 + 3., RIM_Z
HINGE_R, HINGE_BORE, HINGE_GAP = 3.2, 3.4, .4
POCKET_CENTERS = (- (POCKET_X+DIVIDER)/2, (POCKET_X+DIVIDER)/2)
CARD_CENTER_Y = FINGER_BAY/2

# One front leaf, bending inward in XY. Keeper passes outside its round bead.
LEAF_ROOT, LEAF_END = -10., 17.
LEAF_T, LEAF_H = 3.2, 8.
LEAF_Z = RIM_Z-LEAF_H
FRONT_Y = -DEPTH/2
BEAD_X0, BEAD_WIDTH, BEAD_R = 7., 4., 1.2
BEAD_Y, BEAD_Z = FRONT_Y, RIM_Z-3.8
TOOTH_FLOOR = BEAD_Z-.5  # positive retaining underside, rounded closing lead-in
KEEPER_Y = BEAD_Y - 1.5
KEEPER_Z = BEAD_Z - 2.1
KEEPER_WIDTH = 2.4 # bears inside wider tooth, allowing rotation/axial tolerance
KEEPER_X0 = BEAD_X0 + (BEAD_WIDTH-KEEPER_WIDTH)/2
RELEASE_TRAVEL = 1.15
PRESS_TRAVEL = 1.35 # actual fingertip stroke; bead travels less than tip
LEAF_STOP_GAP = 2.0
INNER_BARRIER_Y = 6.5  # local bay intrusion leaves spring room; fingers use pocket centers
ROOT_X, ROOT_SIZE = LEAF_ROOT-8., 8.
ROOT_SCREW_X, ROOT_SCREW_Y = ROOT_X+4., FRONT_Y+4.

def block(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z))

def rounded_plate(w,d,h,z=0,r=CORNER):
    return cq.Workplane('XY').rect(w,d).extrude(h).edges('|Z').fillet(r).translate((0,0,z))

def ring(w,d,t,h,z,r=CORNER):
    return rounded_plate(w,d,h,z,r).cut(rounded_plate(w-2*t,d-2*t,h+2,z-1,r-t))

def axial_cylinder(x,y,z,length,r):
    return cq.Workplane('YZ',origin=(x,y,z)).circle(r).extrude(length)

def hinge_lug(x, lid=False):
    lug = axial_cylinder(x,HINGE_Y,HINGE_Z,3.,HINGE_R)
    # Solid web to shell; no unsupported floating barrel.
    if lid:
        web=block(x,DEPTH/2-2,HINGE_Z,3.,5.,LID_INSIDE-HINGE_Z)
    else:
        web=block(x,DEPTH/2-2,HINGE_Z-HINGE_R,3.,5.,HINGE_R)
    lug=lug.union(web)
    # Teardrop roof above nominal clearance bore avoids a round-hole ceiling.
    bore=axial_cylinder(x-.1,HINGE_Y,HINGE_Z,3.2,HINGE_BORE/2)
    up=-1 if lid else 1
    tear=(cq.Workplane('YZ',origin=(x-.1,HINGE_Y,HINGE_Z))
          .polyline([(-1.2,up*1.2),(0,up*2.4),(1.2,up*1.2)]).close().extrude(3.2))
    return lug.cut(bore.union(tear))

def latch_leaf():
    leaf=block(LEAF_ROOT,FRONT_Y,LEAF_Z,LEAF_END-LEAF_ROOT,LEAF_T,LEAF_H)
    # Round contact bead; axis X, shared with numerical fixture and coupon.
    bead=tooth()
    return leaf.union(bead)

def tooth():
    t=axial_cylinder(BEAD_X0,BEAD_Y,BEAD_Z,BEAD_WIDTH,BEAD_R).cut(
        block(BEAD_X0-.1,BEAD_Y-BEAD_R-.1,BEAD_Z-BEAD_R-.1,
              BEAD_WIDTH+.2,2*BEAD_R+.2,TOOTH_FLOOR-(BEAD_Z-BEAD_R)+.1))
    # Break the contacted outer retaining edge, preserving a flat underside.
    import math
    outer_y=BEAD_Y-math.sqrt(BEAD_R**2-(BEAD_Z-TOOTH_FLOOR)**2)
    edge=cq.selectors.NearestToPointSelector((BEAD_X0+BEAD_WIDTH/2,outer_y,TOOTH_FLOOR))
    return t.edges(edge).fillet(.2)

def latch():
    root=block(ROOT_X,FRONT_Y,LEAF_Z,ROOT_SIZE,ROOT_SIZE,LEAF_H)
    # XY rounded corners and a radiused beam junction reduce sharp root edges.
    root=root.edges('|Z').fillet(.6)
    s=root.union(latch_leaf())
    # Concave junction at x=root, y=front+thickness; selected by position.
    junction=cq.selectors.NearestToPointSelector((LEAF_ROOT,FRONT_Y+LEAF_T,LEAF_Z+LEAF_H/2))
    s=s.edges(junction).fillet(1.2)
    hole=cq.Workplane('XY').center(ROOT_SCREW_X,ROOT_SCREW_Y).circle(1.7).extrude(LEAF_H+2).translate((0,0,LEAF_Z-1))
    return s.cut(hole)

def latch_print():
    return latch().translate((-ROOT_X,-FRONT_Y, -LEAF_Z))

def keeper():
    bead=axial_cylinder(KEEPER_X0,KEEPER_Y,KEEPER_Z,KEEPER_WIDTH,BEAD_R)
    stem=block(KEEPER_X0,KEEPER_Y-BEAD_R,KEEPER_Z,KEEPER_WIDTH,.8,LID_INSIDE-KEEPER_Z)
    # Roof connection over front edge; a single modest front catch.
    bridge=block(KEEPER_X0,KEEPER_Y-BEAD_R,LID_INSIDE-1.2,KEEPER_WIDTH,
                 FRONT_Y-(KEEPER_Y-BEAD_R)+1.2,1.2)
    gusset=(cq.Workplane('YZ',origin=(KEEPER_X0,0,0)).polyline([
        (FRONT_Y,TOTAL_Z),(KEEPER_Y-BEAD_R,LID_INSIDE-1.2),
        (FRONT_Y,LID_INSIDE-1.2)]).close().extrude(KEEPER_WIDTH))
    return bead.union(stem).union(bridge).union(gusset)

@lru_cache(None)
def body(retention=True):
    b=rounded_plate(WIDTH,DEPTH,RIM_Z)
    b=b.cut(rounded_plate(WIDTH-2*WALL,DEPTH-2*WALL,RIM_Z,FLOOR,CORNER-WALL))
    # Low central divider and four side ledges locate/support two card packets.
    b=b.union(block(-DIVIDER/2,-DEPTH/2+WALL,FLOOR,DIVIDER,
                    DEPTH-2*WALL,RIM_Z-FLOOR))
    for cx in POCKET_CENTERS:
        for sx in (-1,1):
            x=cx+sx*(CARD_X/2-3)-2
            b=b.union(block(x,CARD_CENTER_Y-CARD_Y/2+2,FLOOR,4.,CARD_Y-4,UNDER_CARD))
    # Three short lip segments guide/align; the rear stays clear of hinge sweep.
    lip=ring(WIDTH-2*LIP_INSET,DEPTH-2*LIP_INSET,LIP_T,LIP_H,RIM_Z,CORNER-LIP_INSET)
    lip=lip.cut(block(-WIDTH,-0+DEPTH/2-12,RIM_Z-1,2*WIDTH,20,LIP_H+2))
    lip=lip.faces('>Z').edges().chamfer(.2)
    b=b.union(lip)
    for x in (-74.,71.):
        b=b.union(hinge_lug(x))
    for x in (-70.6,67.6):
        b=b.cut(axial_cylinder(x-.2,HINGE_Y,HINGE_Z,3.4,HINGE_R+.3))
    for x in (-67.6,64.9):
        b=b.cut(axial_cylinder(x,HINGE_Y,HINGE_Z,2.7,3.5))
    if retention:
        # Clearance behind and below the cantilever, with a continuous inner
        # wall keeping the contents away. Leaf is not a guide, seat or support.
        b=b.cut(block(ROOT_X-.2,FRONT_Y-.1,LEAF_Z-1.2,
                      LEAF_END-ROOT_X+1.2,ROOT_SIZE+.3,LEAF_H+LIP_H+2.))
        b=b.union(block(LEAF_ROOT+.2,FRONT_Y+INNER_BARRIER_Y,FLOOR,
                        LEAF_END-LEAF_ROOT+1.8,1.2,RIM_Z-FLOOR))
        # Rounded root reaches the full-height left shell with a generous pad.
        # Full-depth screw seat attached to shell; keyed corners restrain twist.
        seat=block(ROOT_X-1.4,FRONT_Y,LEAF_Z-1.2,10.8,9.6,1.2)
        key=block(ROOT_X-1.4,FRONT_Y,LEAF_Z-1.2,10.8,9.6,3.2)
        key=key.cut(block(ROOT_X-.2,FRONT_Y-.1,LEAF_Z,8.4,8.3,3))
        key=key.cut(block(LEAF_ROOT-.2,FRONT_Y-.1,LEAF_Z,1.7,LEAF_T+1.7,3))
        b=b.union(seat).union(key)
        # 45-degree underside supports the keyed screw perch from the wall.
        perch_gusset=(cq.Workplane('YZ',origin=(ROOT_X-1.4,0,0)).polyline([
            (FRONT_Y+WALL,LEAF_Z-1.2-(9.6-WALL)),
            (FRONT_Y+9.6,LEAF_Z-1.2),(FRONT_Y+WALL,LEAF_Z-1.2)])
            .close().extrude(10.8))
        b=b.union(perch_gusset)
        b=b.union(block(LEAF_END-1,FRONT_Y+LEAF_T+LEAF_STOP_GAP,FLOOR,
                        2.,INNER_BARRIER_Y-(LEAF_T+LEAF_STOP_GAP)+1.2,RIM_Z-FLOOR))
        hole=cq.Workplane('XY').center(ROOT_SCREW_X,ROOT_SCREW_Y).circle(1.7).extrude(7).translate((0,0,LEAF_Z-5))
        b=b.cut(hole)
        nut_well=(cq.Workplane('XY').center(ROOT_SCREW_X,ROOT_SCREW_Y)
                  .polygon(6,6.93).extrude(2.6).translate((0,0,LEAF_Z-3.8)))
        nut_access=block(ROOT_SCREW_X-3.4,ROOT_SCREW_Y,LEAF_Z-3.8,6.8,9.,2.6)
        b=b.cut(nut_well.union(nut_access))
        # Retain the front lip over the slot using the independent inner wall.
        b=b.cut(block(LEAF_ROOT+.8,FRONT_Y+1.6,RIM_Z-.01,
                      LEAF_END-LEAF_ROOT+.2,2.,LIP_H+.1))
    return b

@lru_cache(None)
def lid(retention=True):
    l=rounded_plate(WIDTH,DEPTH,LID_ROOF,LID_INSIDE).faces('>Z').edges().chamfer(.3)
    l=l.union(ring(WIDTH,DEPTH,LID_WALL,LID_INSIDE-RIM_Z,RIM_Z))
    for x in (-70.6,67.6):
        l=l.union(hinge_lug(x,True))
    for x in (-74.,71.):
        l=l.cut(axial_cylinder(x-.2,HINGE_Y,HINGE_Z,3.4,HINGE_R+.3))
    for x in (-67.6,64.9):
        l=l.cut(axial_cylinder(x,HINGE_Y,HINGE_Z,2.7,3.5))
    if retention:
        l=l.union(keeper())
        # Pan-head clearance above catch root; does not carry or guide catch.
        l=l.cut(block(ROOT_SCREW_X-3.3,FRONT_Y+.8,RIM_Z,6.6,.6,LID_INSIDE-RIM_Z))
    return l

def lid_pose(angle=0, retention=True):
    return lid(retention).rotate((0,HINGE_Y,HINGE_Z),(1,HINGE_Y,HINGE_Z),-angle)

def lid_print():
    return lid().rotate((0,0,0),(1,0,0),180).translate((0,0,TOTAL_Z))

@lru_cache(None)
def reference_card():
    """Representative source geometry; conservative envelope for fit.

    Faithfully includes notch, asymmetrical corners, recess and thin steps.
    Text omitted (subtractive); fit checks separately use full 80x50x2 blocks.
    This is inspection geometry, not a replacement/export of the SCAD swatch.
    """
    c=(cq.Workplane('XY').moveTo(4,0).lineTo(77,0).radiusArc((80,3),-3)
       .lineTo(80,47).radiusArc((77,50),-3).lineTo(4,50).lineTo(0,46)
       .lineTo(0,4).close().extrude(CARD_T))
    c=c.cut(cq.Workplane('XY').center(80,25).circle(8).extrude(4).translate((0,0,-1)))
    c=c.cut(cq.Workplane('XY').sphere(8).translate((14,9,8)))
    for x,z in ((65,.2),(55,.4),(45,.6),(35,.8),(25,1.)):
        c=c.cut(block(x,5,z,10,8,2))
    top=(cq.Workplane('YZ',origin=(-1,0,0)).polyline([(48,2),(50,0),(50,2)])
         .close().extrude(82))
    c=c.cut(top)
    fillet_cutter=block(-1,0,0,82,2.1,2.1).cut(axial_cylinder(-2,2,0,84,2))
    c=c.cut(fillet_cutter)
    test=block(25,13,2,10,2,2).rotate((25,13,2),(26,13,2),45)
    c=c.cut(test)
    return c.translate((-CARD_X/2,-CARD_Y/2,0))

def cards(access=False):
    shapes=[]
    for pocket,cx in enumerate(POCKET_CENTERS):
        for i in range(PER_POCKET):
            s=reference_card().translate((cx,CARD_CENTER_Y,CARD_BOTTOM+i*CARD_T))
            if access and pocket==0:
                # Whole packet lifted from its finger bay; top card separates.
                s=s.translate((0,-15,26))
                s=s.rotate((cx,CARD_CENTER_Y-15,CARD_BOTTOM+26),
                           (cx,CARD_CENTER_Y-15,CARD_BOTTOM+27),i*4)
                if i==PER_POCKET-1:
                    s=s.translate((-8,-10,12))
            shapes.append(s.val())
    return cq.Compound.makeCompound(shapes)

def hardware():
    """Nominal M3 hardware envelopes for assembly views, never printed."""
    parts=[]
    for sign in (-1,1):
        shaft=axial_cylinder(-74,HINGE_Y,HINGE_Z,12,1.5)
        head=axial_cylinder(-77,HINGE_Y,HINGE_Z,3,2.75)
        nut=cq.Workplane('YZ',origin=(-67.6,HINGE_Y,HINGE_Z)).polygon(6,6.35).extrude(2.4)
        nut=nut.cut(axial_cylinder(-67.7,HINGE_Y,HINGE_Z,2.6,1.5))
        for s in (shaft,head,nut):
            if sign==1: s=s.mirror('YZ')
            parts.append(s.val())
    parts.append(cq.Workplane('XY',origin=(ROOT_SCREW_X,ROOT_SCREW_Y,LEAF_Z-4)).circle(1.5).extrude(12).val())
    parts.append(cq.Workplane('XY',origin=(ROOT_SCREW_X,ROOT_SCREW_Y,RIM_Z)).circle(2.75).extrude(2.4).val())
    nut=cq.Workplane('XY',origin=(ROOT_SCREW_X,ROOT_SCREW_Y,LEAF_Z-3.6)).polygon(6,6.35).extrude(2.4)
    nut=nut.cut(cq.Workplane('XY',origin=(ROOT_SCREW_X,ROOT_SCREW_Y,LEAF_Z-3.7)).circle(1.5).extrude(2.6))
    parts.append(nut.val())
    return cq.Compound.makeCompound(parts)

def print_layout():
    layout=cq.Compound.makeCompound([body().val(),lid_print().translate((0,DEPTH+12,0)).val(),
                                    latch_print().translate((-WIDTH/2,DEPTH+DEPTH/2+20,0)).val()])
    # Explicit positive bed placement registers the catch for local path review.
    return layout.translate((WIDTH/2+20,DEPTH/2+20,0))

if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
