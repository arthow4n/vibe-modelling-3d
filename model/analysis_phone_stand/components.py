"""Four-part phone stand. Assembly units mm; X across phone, Y back, Z up.

Arm/cradle local Y points toward the top of the phone, local Z toward its screen.
Base is printed as assembled; arm on its X face; cradle upright; latch flat.
"""
import math
import cadquery as cq

BASE_WIDTH=80.0
BASE_DEPTH=125.0
BASE_THICKNESS=4.0
PIVOT_Y=28.0
PIVOT_Z=34.0
ARM_WIDTH=12.0
ARM_THICKNESS=8.0
ARM_LENGTH=130.0
GEAR_ROOT=19.8
GEAR_TIP=22.0
TOOTH_PITCH=15.0
HINGE_DIAMETER=4.5
AXIAL_CLEARANCE=.4
CHEEK_THICKNESS=6.0
CRADLE_WIDTH=74.0
CRADLE_BOTTOM=26.0
CRADLE_TOP=146.0
CRADLE_THICKNESS=4.0
PHONE_THICKNESS=14.0
PHONE_HEIGHT=180.0
PHONE_MASS_KG=.3
CRADLE_BOLT_Y=(65.0,115.0)
LATCH_WIDTH=12.0
LATCH_ROOT_WIDTH=24.0
LATCH_BOLT_X=7.0
LATCH_LENGTH=32.0
LATCH_THICKNESS=3.0
LATCH_TOP=11.6
LATCH_TIP_Y=PIVOT_Y
LATCH_ROOT_Y=LATCH_TIP_Y+LATCH_LENGTH
LATCH_TOOTH_HEIGHT=2.2
LATCH_MOUNT_LENGTH=12.0
RELEASE_TRAVEL=4.7
TOOTH_RELEASE_TRAVEL=2.1
ANGLES=(45,60,75)

# Jula 002837: zinc-plated C-1008 steel pan-head machine screws and plain nuts.
# Jula does not specify head dimensions: these are conservative fit envelopes,
# not measurements of the user's screws. Thread lengths are under-head lengths.
M3_LENGTH=12.0
M3_DIAMETER=3.0
M3_HOLE_DIAMETER=3.4
M3_HEAD_DIAMETER=6.0
M3_HEAD_HEIGHT=2.4
M3_HEAD_POCKET_DIAMETER=6.6
BASE_HEAD_DEPTH=2.8
CRADLE_HEAD_DEPTH=2.6
ARM_NUT_DEPTH=1.0
ARM_NUT_ACCESS_DIAMETER=9.0  # Access for a small 5.5 mm nut socket/spanner.
M3_NUT_FLATS=5.5
M3_NUT_HEIGHT=2.4
M3_PITCH=.5
PIVOT_LENGTH=25.0
PIVOT_DIAMETER=4.0
PIVOT_HEAD_DIAMETER=8.0
PIVOT_HEAD_HEIGHT=3.1
PIVOT_HEAD_POCKET_DIAMETER=8.6
PIVOT_HEAD_DEPTH=3.7
PIVOT_NUT_DEPTH=3.2
PIVOT_NUT_FLATS=7.0
PIVOT_NUT_POCKET_FLATS=7.4
PIVOT_NUT_HEIGHT=3.2
PIVOT_PITCH=.7


def hex_x(y,z,flats,width,x):
    return cq.Workplane('YZ',origin=(x,y,z)).polygon(6,flats/math.cos(math.pi/6)).extrude(width)


def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z))


def side_profile(points,width,x=0):
    return cq.Workplane('YZ',origin=(x,0,0)).polyline(points).close().extrude(width)


def x_cylinder(y,z,r,width,x=0):
    return cq.Workplane('YZ',origin=(x,y,z)).circle(r).extrude(width)


def teardrop_x(y,z,r,width,x):
    # Round bearing below; 45-degree roof above the nominal circular hole.
    circle=x_cylinder(y,z,r,width,x)
    roof=side_profile([(y-r/math.sqrt(2),z+r/math.sqrt(2)),
                       (y,z+r*math.sqrt(2)),(y+r/math.sqrt(2),z+r/math.sqrt(2))],width,x)
    return circle.union(roof)


def gear_profile():
    points=[]
    for i in range(round(360/TOOTH_PITCH)):
        # Valley centered on each pitch angle, flat tooth crown in between.
        for offset,r in ((-4,GEAR_ROOT),(4,GEAR_ROOT),(4,GEAR_TIP),(9.5,GEAR_TIP)):
            a=math.radians(i*TOOTH_PITCH+offset)
            points.append((r*math.cos(a),r*math.sin(a)))
    return points


def arm():
    wheel=side_profile(gear_profile(),ARM_WIDTH,-ARM_WIDTH/2)
    spine=box(-ARM_WIDTH/2,0,-ARM_THICKNESS,ARM_WIDTH,ARM_LENGTH,ARM_THICKNESS)
    result=wheel.union(spine)
    # Round the profile corners, including tooth roots, along the extrusion.
    result=result.edges('|X').fillet(.35)
    result=result.cut(x_cylinder(0,0,HINGE_DIAMETER/2,ARM_WIDTH+2,-ARM_WIDTH/2-1))
    for y in CRADLE_BOLT_Y:
        hole=cq.Workplane('XY',origin=(0,y,-ARM_THICKNESS-1)).circle(M3_HOLE_DIAMETER/2).extrude(ARM_THICKNESS+2)
        result=result.cut(hole)
        # Partial nut recess shortens the grip while leaving socket access.
        pocket=cq.Workplane('XY',origin=(0,y,-ARM_THICKNESS-1)).circle(ARM_NUT_ACCESS_DIAMETER/2).extrude(ARM_NUT_DEPTH+1)
        result=result.cut(pocket)
    return result


def cradle():
    # Rounded, broad backing; cable notch is open through the seat and lip.
    backing=box(-CRADLE_WIDTH/2,CRADLE_BOTTOM,0,CRADLE_WIDTH,CRADLE_TOP-CRADLE_BOTTOM,CRADLE_THICKNESS)
    backing=backing.edges('|Z').fillet(5)
    seat_y=CRADLE_BOTTOM+6
    seat=box(-CRADLE_WIDTH/2,seat_y-6,CRADLE_THICKNESS,CRADLE_WIDTH,6,PHONE_THICKNESS+4)
    lip=box(-CRADLE_WIDTH/2,seat_y,CRADLE_THICKNESS+PHONE_THICKNESS+2,CRADLE_WIDTH,8,2)
    result=backing.union(seat).union(lip)
    result=result.cut(box(-10,CRADLE_BOTTOM-1,CRADLE_THICKNESS,20,16,PHONE_THICKNESS+10))
    result=result.edges('|Z').fillet(.7)
    for y in CRADLE_BOLT_Y:
        hole=cq.Workplane('XY',origin=(0,y,-1)).circle(M3_HOLE_DIAMETER/2).extrude(CRADLE_THICKNESS+2)
        head=cq.Workplane('XY',origin=(0,y,CRADLE_THICKNESS-CRADLE_HEAD_DEPTH)).circle(M3_HEAD_POCKET_DIAMETER/2).extrude(CRADLE_HEAD_DEPTH+1)
        result=result.cut(hole).cut(head)
    return result


def latch():
    x=-LATCH_WIDTH/2
    root=box(-LATCH_ROOT_WIDTH/2,LATCH_ROOT_Y,LATCH_TOP-LATCH_THICKNESS,LATCH_ROOT_WIDTH,LATCH_MOUNT_LENGTH,LATCH_THICKNESS)
    outline=[(-6,LATCH_TIP_Y-14),(6,LATCH_TIP_Y-14),(6,PIVOT_Y+10),
             (LATCH_ROOT_WIDTH/2,PIVOT_Y+16),(LATCH_ROOT_WIDTH/2,LATCH_ROOT_Y+1),
             (-LATCH_ROOT_WIDTH/2,LATCH_ROOT_Y+1),(-LATCH_ROOT_WIDTH/2,PIVOT_Y+16),(-6,PIVOT_Y+10)]
    leaf=cq.Workplane('XY',origin=(0,0,LATCH_TOP-LATCH_THICKNESS)).polyline(outline).close().extrude(LATCH_THICKNESS)
    leaf=leaf.edges('|Z').fillet(1.5)
    # A steep holding face and chamfered entry; press the forward tab to adjust.
    tooth=side_profile([(PIVOT_Y-1.7,LATCH_TOP-.1),(PIVOT_Y-1.1,LATCH_TOP+LATCH_TOOTH_HEIGHT),
                        (PIVOT_Y+1.1,LATCH_TOP+LATCH_TOOTH_HEIGHT),(PIVOT_Y+1.1,LATCH_TOP-.1)],LATCH_WIDTH,x)
    tab=box(-12,PIVOT_Y-16,LATCH_TOP-LATCH_THICKNESS,24,8,LATCH_THICKNESS)
    tab=tab.edges('|Z').fillet(2)
    result=root.union(leaf).union(tooth).union(tab)
    for x in (-LATCH_BOLT_X,LATCH_BOLT_X):
        hole=cq.Workplane('XY',origin=(x,LATCH_ROOT_Y+7,0)).circle(M3_HOLE_DIAMETER/2).extrude(12)
        result=result.cut(hole)
    return result


def base():
    result=box(-BASE_WIDTH/2,0,0,BASE_WIDTH,BASE_DEPTH,BASE_THICKNESS).edges('|Z').fillet(6)
    inside=ARM_WIDTH/2+AXIAL_CLEARANCE
    for x in (-inside-CHEEK_THICKNESS,inside):
        cheek=side_profile([(PIVOT_Y-7,BASE_THICKNESS-.1),(PIVOT_Y+7,BASE_THICKNESS-.1),
                            (PIVOT_Y+7,PIVOT_Z),(PIVOT_Y-7,PIVOT_Z)],CHEEK_THICKNESS,x)
        cheek=cheek.union(x_cylinder(PIVOT_Y,PIVOT_Z,7,CHEEK_THICKNESS,x))
        cheek=cheek.cut(teardrop_x(PIVOT_Y,PIVOT_Z,HINGE_DIAMETER/2,CHEEK_THICKNESS+2,x-1))
        if x<0:
            # Roof retains the head's round clearance without a horizontal ceiling.
            cheek=cheek.cut(teardrop_x(PIVOT_Y,PIVOT_Z,PIVOT_HEAD_POCKET_DIAMETER/2,PIVOT_HEAD_DEPTH+1,x-1))
        else:
            # One plain nut is held by the hex; another jams against it outside.
            cheek=cheek.cut(hex_x(PIVOT_Y,PIVOT_Z,PIVOT_NUT_POCKET_FLATS,PIVOT_NUT_DEPTH+1,x+CHEEK_THICKNESS-PIVOT_NUT_DEPTH))
        result=result.union(cheek)
    # Spring deflection well, open from above; at full release leaf remains >1 mm above floor.
    well=box(-15,PIVOT_Y-19,1,30,11.5,BASE_THICKNESS)
    well=well.union(box(-6.2,PIVOT_Y-7.5,1,12.4,15,BASE_THICKNESS))
    well=well.union(box(-15,PIVOT_Y+7.5,1,30,LATCH_LENGTH-7.5,BASE_THICKNESS))
    result=result.cut(well)
    # Positive thumb stop limits nominal release travel, avoiding needless root strain.
    stop_top=LATCH_TOP-LATCH_THICKNESS-RELEASE_TRAVEL
    result=result.union(box(-8,PIVOT_Y-16,1,16,5,stop_top-1))
    result=result.union(box(-LATCH_ROOT_WIDTH/2,LATCH_ROOT_Y,BASE_THICKNESS-.1,LATCH_ROOT_WIDTH,LATCH_MOUNT_LENGTH,LATCH_TOP-LATCH_THICKNESS-BASE_THICKNESS+.1))
    for x in (-LATCH_BOLT_X,LATCH_BOLT_X):
        hole=cq.Workplane('XY',origin=(x,LATCH_ROOT_Y+7,-1)).circle(M3_HOLE_DIAMETER/2).extrude(15)
        # Recess the pan head above the bed plane; plain nut clamps the latch.
        head=cq.Workplane('XY',origin=(x,LATCH_ROOT_Y+7,-1)).circle(M3_HEAD_POCKET_DIAMETER/2).extrude(BASE_HEAD_DEPTH+1)
        result=result.cut(hole).cut(head)
    assert len(result.val().Solids())==1, 'Spring well must not sever the pivot cheeks from the base'
    return result


def placed(part,angle):
    return part.rotate((0,0,0),(1,0,0),angle).translate((0,PIVOT_Y,PIVOT_Z))


def assembled(angle=60):
    return dict(base=base(),arm=placed(arm(),angle),cradle=placed(cradle(),angle),latch=latch())


def printable_parts():
    # Arm's +X face goes down; cradle stands on its bottom edge; latch lies flat.
    a=arm().rotate((0,0,0),(0,1,0),90).translate((0,0,ARM_WIDTH/2))
    l=latch().translate((0,0,-LATCH_TOP+LATCH_THICKNESS))
    c=cradle().translate((0,-CRADLE_BOTTOM,0)).rotate((0,0,0),(1,0,0),90)
    return dict(base=base(),arm=a,cradle=c,latch=l)
