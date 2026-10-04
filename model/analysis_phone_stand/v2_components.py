"""Raised open-easel revision. mm; X across phone, global Y rear, Z up.

Cradle-local Y runs up the phone; +Z faces the screen. Its phone rear is Z=0.
The frame is set back behind the accessory pocket. No exports on import.
"""
import math
from functools import lru_cache
import cadquery as cq

PHONE_WIDTH = 85.0
PHONE_HEIGHT = 170.0
PHONE_THICKNESS = 13.0
LIP_INNER_Z = PHONE_THICKNESS + .8
LIP_THICKNESS = 3.0
PHONE_MASS_KG = 0.30
ANGLES = (50.0, 65.0, 75.0)
FRAME_BACK = -46.0
FRAME_FRONT = -36.0
UPPER_CONTACT_Y = 70.0
CONTACT_X = 37.0
PIVOT_LOCAL_Y = -8.0
PIVOT_LOCAL_Z = -40.0
PIVOT_Y = 42.0
PIVOT_Z = 55.0
PROP_LENGTH = 120.0
FOOT_RADIUS = 4.0
SEAT_VERTEX_Z = 11.5
FOOT_Z = SEAT_VERTEX_Z + FOOT_RADIUS * math.sqrt(2)
AXIAL_CLEARANCE = .25
PROP_INNER_X = 50 + AXIAL_CLEARANCE
PROP_WIDTH = 6.0
PIN_BORE = 5.4
NUT_FLATS = 8.4
NUT_THICKNESS = 4.0
CRADLE_BOSS_INNER_X = 38.0
CRADLE_BOSS_OUTER_X = 50 - AXIAL_CLEARANCE
PIN_LENGTH = 30.0
BASE_FRONT_Y = -35.0
BASE_REAR_Y = 211.0
ROOT_Y = 196.0
LEAF_WIDTH = 1.2
ROOT_X = 104.0
LEAF_Z = 8.0
LEAF_THICKNESS = 4.0
RELEASE_TRAVEL = 7.0
GUIDE_X_PLAY = .20
GUIDE_Z_PLAY = .30
GUIDE_DIAMETER = 8.0
GUIDE_YS = (75.0, 178.0)
GUIDE_POST_TOP = LEAF_Z + LEAF_THICKNESS + GUIDE_Z_PLAY
WASHER_DIAMETER = 14.0
WASHER_THICKNESS = 2.0
M3_BORE = 3.4
M3_NUT_FLATS = 5.9
FOOT_YS = (-20.0, 200.0)
HOOK_UNDERSIDE = FOOT_Z + FOOT_RADIUS + .40


def box(x0, y0, z0, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz, centered=False).translate((x0,y0,z0))


def rounded_plate(x0,y0,z0,dx,dy,dz,r=2):
    return box(x0,y0,z0,dx,dy,dz).edges('|Z').fillet(r)


def cylinder_x(x0,y,z,length,radius):
    return cq.Workplane('YZ',origin=(x0,y,z)).circle(radius).extrude(length)


def hex_x(x0,y,z,length,flats):
    return cq.Workplane('YZ',origin=(x0,y,z)).polygon(6,flats/math.cos(math.pi/6)).extrude(length)


def hex_z(x,y,z,length,flats):
    return cq.Workplane('XY',origin=(x,y,z)).polygon(6,flats/math.cos(math.pi/6)).extrude(length)


def compound(items):
    return cq.Workplane('XY').newObject([cq.Compound.makeCompound([p.val() for p in items])])


def place_cradle(part,angle):
    return part.translate((0,-PIVOT_LOCAL_Y,-PIVOT_LOCAL_Z)).rotate((0,0,0),(1,0,0),angle).translate((0,PIVOT_Y,PIVOT_Z))


def prop_pose(angle):
    theta=math.radians(angle)
    u=UPPER_CONTACT_Y-PIVOT_LOCAL_Y
    hinge_y=PIVOT_Y+u*math.cos(theta)
    hinge_z=PIVOT_Z+u*math.sin(theta)
    dz=hinge_z-FOOT_Z
    if dz >= PROP_LENGTH:
        raise ValueError('Rear prop cannot reach the seat at this angle')
    rear=math.sqrt(PROP_LENGTH**2-dz**2)
    foot_y=hinge_y+rear
    beta=math.degrees(math.atan2(dz,-rear))
    return foot_y,beta


SEAT_YS=tuple(prop_pose(a)[0] for a in ANGLES)
SPINE_FRONT=min(GUIDE_YS)-10
SPINE_REAR=ROOT_Y+6


@lru_cache(None)
def base():
    p=rounded_plate(-65,BASE_FRONT_Y,0,18,BASE_REAR_Y-BASE_FRONT_Y,8)
    p=p.union(rounded_plate(47,BASE_FRONT_Y,0,18,BASE_REAR_Y-BASE_FRONT_Y,8))
    # Bridges behind the cable exit; the front is an open charging bay.
    for y in GUIDE_YS:
        p=p.union(rounded_plate(-65,y-7,0,130,14,8))
    p=p.union(rounded_plate(-ROOT_X-8,ROOT_Y-7,0,2*(ROOT_X+8),14,8))
    for x in (-ROOT_X,ROOT_X):
        p=p.union(rounded_plate(x-8,ROOT_Y-9,0,16,18,8))
        # M3 x 10 root bolts: nuts recessed above the desk, 0.5 mm thread beyond.
        p=p.cut(hex_z(x,ROOT_Y,-.1,5.0,M3_NUT_FLATS))
        p=p.cut(cq.Workplane('XY',origin=(x,ROOT_Y,-.1)).circle(M3_BORE/2).extrude(12))
    for x0 in (-56,50):
        outline=[(PIVOT_Y-14,8),(PIVOT_Y-8,PIVOT_Z),(PIVOT_Y+8,PIVOT_Z),(PIVOT_Y+30,8)]
        cheek=cq.Workplane('YZ',origin=(x0,0,0)).polyline(outline).close().extrude(6)
        cheek=cheek.union(cylinder_x(x0,PIVOT_Y,PIVOT_Z,6,9))
        cheek=cheek.cut(cylinder_x(x0-.1,PIVOT_Y,PIVOT_Z,6.2,PIN_BORE/2))
        p=p.union(cheek)
    # Two load-bearing 90-degree V seats per angle, with flared entry above them.
    for y in SEAT_YS:
        for x0 in (-65,47):
            block=rounded_plate(x0,y-11,0,18,22,19,1.5)
            cut=cq.Workplane('YZ',origin=(x0-.1,0,0)).polyline(
                [(y,SEAT_VERTEX_Z),(y-11,SEAT_VERTEX_Z+11),(y+11,SEAT_VERTEX_Z+11)]).close().extrude(18.2)
            p=p.union(block.cut(cut))
    # Guide posts establish slider clearance independently of screw tightening.
    for y in GUIDE_YS:
        post=cq.Workplane('XY',origin=(0,y,8)).circle(GUIDE_DIAMETER/2).extrude(GUIDE_POST_TOP-8)
        p=p.union(post)
        p=p.cut(cq.Workplane('XY',origin=(0,y,-.1)).circle(M3_BORE/2).extrude(18))
        p=p.cut(hex_z(0,y,-.1,5.3,M3_NUT_FLATS))
    # Optional compliant pads insert from below; recess supplies location/capture.
    for x in (-56,56):
        for y in FOOT_YS:
            mouth=rounded_plate(x-7,y-5,-.1,14,10,1.3,1)
            well=rounded_plate(x-7.4,y-5.4,1.2,14.8,10.8,2,1)
            p=p.cut(mouth.union(well))
    return p


def cradle_boss(side,u):
    x0=CRADLE_BOSS_INNER_X if side>0 else -CRADLE_BOSS_OUTER_X
    length=CRADLE_BOSS_OUTER_X-CRADLE_BOSS_INNER_X
    p=cylinder_x(x0,u,PIVOT_LOCAL_Z,length,8)
    collar_x=34.5 if side>0 else -38
    p=p.union(cylinder_x(collar_x,u,PIVOT_LOCAL_Z,3.5,7))
    p=p.intersect(box(-100,-30,FRAME_BACK,200,130,70))
    p=p.cut(cylinder_x(x0-5,u,PIVOT_LOCAL_Z,length+10,PIN_BORE/2))
    p=p.cut(hex_x(collar_x-.1,u,PIVOT_LOCAL_Z,3.7,NUT_FLATS))
    return p


@lru_cache(None)
def cradle():
    p=rounded_plate(-50,-16,FRAME_BACK,8,110,10,2)
    p=p.union(rounded_plate(42,-16,FRAME_BACK,8,110,10,2))
    # Crossbars clear a complete axial driver approach to the inner jam nuts.
    for y in (PIVOT_LOCAL_Y+10,UPPER_CONTACT_Y+10):
        p=p.union(rounded_plate(-50,y,FRAME_BACK,100,8,10,2))
    for side in (-1,1):
        x=side*CONTACT_X
        # Lower ledges carry the case; two lips leave the centre charging port free.
        ledge=rounded_plate(x-6,-5,FRAME_BACK,12,5,-FRAME_BACK+LIP_INNER_Z+2.2,1.5)
        lip=rounded_plate(x-6,-1,LIP_INNER_Z,12,8,LIP_THICKNESS,1.5)
        lower_pad=rounded_plate(x-5,4,FRAME_BACK,10,4,-FRAME_BACK,1)
        upper_pad=rounded_plate(x-5,UPPER_CONTACT_Y-4,FRAME_BACK,10,8,-FRAME_BACK,1.5)
        p=p.union(ledge).union(lip).union(lower_pad).union(upper_pad)
        p=p.union(cradle_boss(side,PIVOT_LOCAL_Y)).union(cradle_boss(side,UPPER_CONTACT_Y))
    # Cut after the frame unions: crossbars must not refill a pin or captive nut.
    for u in (PIVOT_LOCAL_Y,UPPER_CONTACT_Y):
        p=p.cut(cylinder_x(-60,u,PIVOT_LOCAL_Z,120,PIN_BORE/2))
        for side in (-1,1):
            collar_x=34.5 if side>0 else -38
            p=p.cut(hex_x(collar_x-.1,u,PIVOT_LOCAL_Z,3.7,NUT_FLATS))
            # Open counterbore for the second plain nut and a small socket.
            start=29.5 if side>0 else -34.5
            p=p.cut(cylinder_x(start,u,PIVOT_LOCAL_Z,5,6.5))
    return p


@lru_cache(None)
def prop():
    # Local Y runs from the common round foot bar toward the upper pivot.
    p=cylinder_x(-PROP_INNER_X-PROP_WIDTH,0,0,2*(PROP_INNER_X+PROP_WIDTH),FOOT_RADIUS)
    for side in (-1,1):
        x0=PROP_INNER_X if side>0 else -PROP_INNER_X-PROP_WIDTH
        arm=box(x0,0,-4,PROP_WIDTH,PROP_LENGTH,8)
        boss=cylinder_x(x0,PROP_LENGTH,0,PROP_WIDTH,8).intersect(box(-100,-10,-4,200,150,20))
        arm=arm.union(boss).cut(cylinder_x(x0-.1,PROP_LENGTH,0,PROP_WIDTH+.2,PIN_BORE/2))
        p=p.union(arm)
    return p


def place_prop(part,angle):
    y,beta=prop_pose(angle)
    return part.rotate((0,0,0),(1,0,0),beta).translate((0,y,FOOT_Z))


def leaf(side):
    # Wider ends soften the spring/root transitions without thickening its span.
    coords=[(8,-5),(12,-5),(16,-LEAF_WIDTH/2),(ROOT_X-7,-LEAF_WIDTH/2),
            (ROOT_X-3,-5),(ROOT_X+8,-5),(ROOT_X+8,5),(ROOT_X-3,5),(ROOT_X-7,LEAF_WIDTH/2),
            (16,LEAF_WIDTH/2),(12,5),(8,5)]
    if side<0:
        coords=[(-x,y) for x,y in reversed(coords)]
    p=cq.Workplane('XY',origin=(0,ROOT_Y,LEAF_Z)).polyline(coords).close().extrude(LEAF_THICKNESS)
    p=p.edges('|Z').fillet(.6)
    x=side*ROOT_X
    p=p.cut(cq.Workplane('XY',origin=(x,ROOT_Y,LEAF_Z-.1)).circle(M3_BORE/2).extrude(4.2))
    return p


@lru_cache(None)
def keeper():
    p=rounded_plate(-10,SPINE_FRONT,LEAF_Z,20,SPINE_REAR-SPINE_FRONT,4,2)
    p=p.union(leaf(-1)).union(leaf(1))
    for y in SEAT_YS:
        # Horizontal underside blocks lifting; upper ramp permits downward seating.
        outline=[(y-10,LEAF_Z),(y-6,LEAF_Z),(y-6,HOOK_UNDERSIDE),
                 (y-1,HOOK_UNDERSIDE),(y-1,HOOK_UNDERSIDE+2),
                 (y-6,HOOK_UNDERSIDE+7),(y-10,HOOK_UNDERSIDE+7)]
        hook=cq.Workplane('YZ',origin=(-10,0,0)).polyline(outline).close().extrude(20)
        p=p.union(hook)
    for y in GUIDE_YS:
        # Slot permits exactly the release travel; front/rear stop faces remain rigid.
        slot=cq.Workplane('XY',origin=(0,y+RELEASE_TRAVEL/2,LEAF_Z-.1)).slot2D(
            GUIDE_DIAMETER+2*GUIDE_X_PLAY+RELEASE_TRAVEL,GUIDE_DIAMETER+2*GUIDE_X_PLAY,90).extrude(4.2)
        p=p.cut(slot)
    # Rear button: push toward the phone, then let the flexures return the keeper.
    p=p.union(rounded_plate(-15,ROOT_Y+1,LEAF_Z,30,13,8,3))
    return p


def washer():
    return cq.Workplane('XY').circle(WASHER_DIAMETER/2).circle(M3_BORE/2).extrude(WASHER_THICKNESS)


def soft_foot():
    """TPU only: modest 0.1 mm/side neck interference, weight bears on broad pad."""
    pad=rounded_plate(-11,-8,0,22,16,2.5,3)
    neck=rounded_plate(-7.1,-5.1,2.5,14.2,10.2,1.2,1)
    cap=rounded_plate(-7.3,-5.3,3.7,14.6,10.6,1.8,1)
    # 0.2-mm rounded entry removes sharp insertion corners, not a material model.
    cap=cap.edges('>Z').fillet(.2)
    return pad.union(neck).union(cap)


def guide_cage(y):
    post=cq.Workplane('XY',origin=(0,y,0)).circle(GUIDE_DIAMETER/2).extrude(GUIDE_POST_TOP)
    cap=cq.Workplane('XY',origin=(0,y,GUIDE_POST_TOP)).circle(WASHER_DIAMETER/2).extrude(2)
    return post.union(cap)


def assembly(angle=65):
    items=[base(),place_cradle(cradle(),angle),place_prop(prop(),angle),keeper()]
    items.extend(washer().translate((0,y,GUIDE_POST_TOP)) for y in GUIDE_YS)
    return compound(items)


def phone_reference(angle=65,landscape=False):
    width,height=(PHONE_HEIGHT,PHONE_WIDTH) if landscape else (PHONE_WIDTH,PHONE_HEIGHT)
    p=box(-width/2,0,0,width,height,PHONE_THICKNESS).edges('|Z').fillet(4)
    return place_cradle(p,angle)


def accessory_reference(angle=65,landscape=False):
    if landscape:
        # Covers both sideways offsets; lateral outline is deliberately broad.
        p=box(-85,10,-33,170,50,33)
    else:
        p=box(-30,10,-33,60,115,33)
    return place_cradle(p,angle)


def mechanism_layout():
    return compound([
        cradle().translate((192,16,46)),
        prop().translate((75,8,4)),
        keeper().translate((146,50,-LEAF_Z)),
        washer().translate((197,163,0)),washer().translate((221,163,0)),
    ])
