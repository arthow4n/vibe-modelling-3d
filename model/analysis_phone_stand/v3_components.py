"""Compact fully printed pedestal. Assembly X across, Y rear, Z up; mm.

Cradle coordinates use the pivot as origin, local Y up the phone and +Z screenward.
"""
import math
from functools import lru_cache
import cadquery as cq

BASE_WIDTH=105.0
BASE_DEPTH=140.0
BASE_HEIGHT=10.0
PHONE_WIDTH=85.0
PHONE_HEIGHT=170.0
PHONE_THICKNESS=13.0
PHONE_MASS=.30
ANGLES=(45.,60.,75.)
PIVOT_Y=38.0
PIVOT_Z=26.0
PHONE_U=28.0
PHONE_V=40.0
FRAME_BACK=-16.0
FRAME_FRONT=4.0
FRAME_THICKNESS=FRAME_FRONT-FRAME_BACK
ROTOR_R=18.0
ROTOR_WIDTH=16.0
HOOD_R=22.0
HOOD_WIDTH=32.0
ROTATION_GAP=.25
PIN_D=8.0
PIN_BORE=8.3
PIN_LENGTH=113.0
LOCK_THICKNESS=2.0
LOCK_GAP=.12
LOCK_DEPTH=2.0
RELEASE=3.0
SLIDER_Z=18.0
RAIL_INNER=10.0
RAIL_WIDTH=4.0
ROOT_X=43.0
ROOT_Y=38.0
LEAF_WIDTH=.8
LEAF_HEIGHT=4.0
FOOT_X=43.5
FOOT_YS=(10.,130.)


def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z))


def rounded(x,y,z,dx,dy,dz,r=1):
    return box(x,y,z,dx,dy,dz).edges('|Z').fillet(r)


def cyl_x(x,y,z,length,r):
    return cq.Workplane('YZ',origin=(x,y,z)).circle(r).extrude(length)


def compound(parts):
    return cq.Workplane('XY').newObject([cq.Compound.makeCompound([p.val() for p in parts])])


def place_cradle(p,angle):
    return p.rotate((0,0,0),(1,0,0),angle).translate((0,PIVOT_Y,PIVOT_Z))


def rail_profile(x0,width=4,z0=SLIDER_Z,clearance=0):
    # Flat bearing lands; narrow accessible channel roofs are slice-reviewed.
    return box(x0-clearance,14,z0-clearance,width+2*clearance,62,4+2*clearance)


@lru_cache(None)
def return_leaf(side=1):
    w=LEAF_WIDTH
    # Three serial leaves fold into the low shoulder; only the last meets the rail.
    leaf=box(12,ROOT_Y+16-w/2,SLIDER_Z,24+w/2,w,LEAF_HEIGHT)
    for x,y,dx,dy in ((36-w/2,10-w/2,w,6+w),
                      (17-w/2,10-w/2,19+w,w),
                      (17-w/2,4-w/2,w,6+w),
                      (17-w/2,4-w/2,23+w/2,w)):
        leaf=leaf.union(box(x,ROOT_Y+y,SLIDER_Z,dx,dy,LEAF_HEIGHT))
    leaf=leaf.union(box(10,ROOT_Y+14,SLIDER_Z,5.5,4,LEAF_HEIGHT))
    leaf=leaf.edges('|Z').fillet(.3)
    pad=rounded(ROOT_X-5,ROOT_Y-5,SLIDER_Z,10,10,13,.8)
    p=leaf.union(pad).cut(cyl_x(ROOT_X-6,ROOT_Y,PIVOT_Z,12,PIN_BORE/2))
    return p if side>0 else p.mirror('YZ')


@lru_cache(None)
def slider():
    p=rail_profile(10).union(rail_profile(-14))
    p=p.union(rounded(-14,10,SLIDER_Z,28,10,4,.7))
    p=p.union(rounded(-8,16,SLIDER_Z+2.5,16,4,8,.6))
    p=p.union(box(-8,PIVOT_Y-ROTOR_R-.2,PIVOT_Z-LOCK_THICKNESS/2,
                  16,LOCK_DEPTH+.2,LOCK_THICKNESS))
    p=p.union(rounded(-14,68,SLIDER_Z,28,8,9,1.5))
    # The already-needed pin also limits release travel, avoiding assembly-blocking
    # stop posts in the rear insertion path. Slots are open through each rail boss.
    for x0 in (-14,10):
        boss=rounded(x0,33,SLIDER_Z,4,14,13,.5)
        slot=cyl_x(x0-.1,PIVOT_Y,PIVOT_Z,4.2,PIN_BORE/2).union(
             cyl_x(x0-.1,PIVOT_Y+RELEASE,PIVOT_Z,4.2,PIN_BORE/2))
        slot=slot.union(box(x0-.1,PIVOT_Y,PIVOT_Z-PIN_BORE/2,4.2,RELEASE,PIN_BORE))
        p=p.union(boss.cut(slot))
    for side in (-1,1):p=p.union(return_leaf(side))
    sel=cq.selectors.BoxSelector((-8.2,16.5,21.9),(8.2,19.5,22.1))
    p=p.edges(sel).fillet(1.2)
    return p.cut(cyl_x(-54,PIVOT_Y,PIVOT_Z,108,PIN_BORE/2))


def local_lock_blank():
    return box(-ROTOR_WIDTH/2-.1,-ROTOR_R-3,-(LOCK_THICKNESS+LOCK_GAP)/2,
               ROTOR_WIDTH+.2,3+LOCK_DEPTH+.15,LOCK_THICKNESS+LOCK_GAP)


@lru_cache(None)
def cradle():
    p=cyl_x(-8,0,0,16,ROTOR_R)
    for angle in ANGLES:p=p.cut(local_lock_blank().rotate((0,0,0),(1,0,0),-angle))
    p=p.union(rounded(-8,0,FRAME_BACK,16,32,FRAME_THICKNESS,1))
    p=p.union(rounded(-50,24,FRAME_BACK,100,8,FRAME_THICKNESS,1.5))
    for x0 in (-50,42):p=p.union(rounded(x0,24,FRAME_BACK,8,96,FRAME_THICKNESS,1.5))
    for x in (-37,37):
        p=p.union(rounded(x-6,PHONE_U-5,FRAME_BACK,12,5,PHONE_V+PHONE_THICKNESS+2.5-FRAME_BACK,1))
        p=p.union(rounded(x-6,PHONE_U-1,PHONE_V+PHONE_THICKNESS+.8,12,8,3,1))
        for u,dy in ((PHONE_U,8),(PHONE_U+66,12)):
            p=p.union(rounded(x-5,u,FRAME_BACK,10,dy,PHONE_V-FRAME_BACK,1))
    p=p.cut(cyl_x(-9,0,0,18,PIN_BORE/2))
    return p


@lru_cache(None)
def base():
    p=rounded(-BASE_WIDTH/2,0,0,BASE_WIDTH,BASE_DEPTH,BASE_HEIGHT,7)
    hood=cyl_x(-HOOD_WIDTH/2,PIVOT_Y,PIVOT_Z,HOOD_WIDTH,HOOD_R)
    p=p.union(hood)
    # Low shoulders enclose most of the short transverse return springs.
    for side in (-1,1):
        x0=16 if side>0 else -52.5
        wing=rounded(x0,30,10,36.5,28,23,.8)
        wing=wing.cut(box(x0-.1,29.9,17.7,36.7,29,6.3))
        wing=wing.cut(box(37.75 if side>0 else -48.25,32.75,17.7,10.5,25.6,13.6))
        p=p.union(wing)
    p=p.cut(cyl_x(-8-ROTATION_GAP,PIVOT_Y,PIVOT_Z,16+2*ROTATION_GAP,ROTOR_R+.3))
    # Swept neck opening through the upper annular shell, not the side cheeks.
    rays=[(0,0),(45*math.cos(math.radians(-18)),45*math.sin(math.radians(-18))),
          (45*math.cos(math.radians(88)),45*math.sin(math.radians(88)))]
    opening=cq.Workplane('YZ',origin=(-8.25,PIVOT_Y,PIVOT_Z)).polyline(rays).close().extrude(16.5)
    p=p.cut(opening)
    # Front tooth chamber and rear-accessible guide channels, below the rotor.
    p=p.cut(box(-9.5,13.7,17.7,19,46.6,11.6))
    p=p.cut(box(-14.2,4.7,17.7,28.4,53.6,4.4))
    p=p.cut(box(-36.2,29.7,17.7,72.4,34.6,4.4))
    for x0 in (-14,10):p=p.cut(rail_profile(x0,clearance=.1))
    # Keep an unobstructed external release button and roots' insertion path.
    p=p.cut(box(-14.2,60,17.7,28.4,18,11))
    for x0 in (-14.2,9.5):p=p.cut(box(x0,29.9,17.7,4.7,47,13.6))
    p=p.cut(cyl_x(-54,PIVOT_Y,PIVOT_Z,108,PIN_BORE/2))
    for x in (-FOOT_X,FOOT_X):
        for y in FOOT_YS:
            mouth=rounded(x-5.9,y-3.9,-.1,11.8,7.8,1.3,.8)
            well=rounded(x-6.3,y-4.3,1.2,12.6,8.6,2,.8)
            p=p.cut(mouth.union(well))
    return p


@lru_cache(None)
def pin():
    p=cyl_x(0,0,0,3,6).union(cyl_x(3,0,0,PIN_LENGTH-3,4))
    barb=cq.Workplane('YZ',origin=(108.5,0,0)).circle(4.6).workplane(offset=4.5).circle(3.9).loft()
    p=p.union(barb).cut(box(90,-.55,-8,24,1.1,16))
    p=p.intersect(box(-1,-8,-3.8,116,16,14))
    return p


def place_pin(p):return p.translate((-55.5,PIVOT_Y,PIVOT_Z))


def foot():
    p=rounded(-9,-7,0,18,14,2.5,2)
    p=p.union(rounded(-6,-4,2.5,12,8,1.2,.8))
    cap=rounded(-6.2,-4.2,3.7,12.4,8.4,1.8,.8).edges('>Z').fillet(.2)
    return p.union(cap)


def phone(angle,landscape=False):
    w,h=(PHONE_HEIGHT,PHONE_WIDTH) if landscape else (PHONE_WIDTH,PHONE_HEIGHT)
    return place_cradle(rounded(-w/2,PHONE_U,PHONE_V,w,h,PHONE_THICKNESS,3),angle)


def ring(angle,landscape=False):
    x0,width,dy=(-85,170,50) if landscape else (-30,60,115)
    return place_cradle(box(x0,PHONE_U+10,PHONE_V-33,width,dy,33),angle)


def assembly(angle=60):return compound([base(),place_cradle(cradle(),angle),slider(),place_pin(pin())])


def print_layout():
    return compound([base().translate((66,20,0)),
        cradle().rotate((0,0,0),(0,1,0),90).translate((183,24,50)),
        slider().translate((205,151,-SLIDER_Z)),
        pin().translate((20,225,3.8))])
