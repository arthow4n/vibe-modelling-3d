"""Rounded R2/C candidate: pure builders, millimetres, independent hinge joints.

Shells print separately, exterior panel down. Closed body stays at Z=0;
lid is the mirrored cup. Link angles run from 101.31 (closed) to 0 (flat open).
The wide link is also a recessed rear hatch, rather than an exposed barrel.
"""
import math
import cadquery as cq
from components import compound
from mechanisms import block

LENGTH = 263.8
WIDTH = 132.0
HEIGHT = 66.0
FLOOR = 2.4
WALL = 3.2
HALF_HEIGHT = HEIGHT/2
RIM = HALF_HEIGHT-.3
BASE_HALF = 50.0
AXIS_Y = 49.5
AXIS_Z = 8.0
LID_AXIS_Y = 39.5
LINK_SPACING = math.hypot(HEIGHT-2*AXIS_Z,LID_AXIS_Y-AXIS_Y)
CLOSED_LINK_ANGLE = math.degrees(math.atan2(HEIGHT-2*AXIS_Z,LID_AXIS_Y-AXIS_Y))
STATIONS = (-110.0, 110.0)
LINK_THICKNESS = 7.4
SLOT_WIDTH = 8.0
PIN_RADIUS = 3.0
BEARING_RADIUS = 3.2
BRUSH_Y = -36.0
BRUSH_Z = 33.0
TUBE_LENGTH = 180.0
TUBE_Y = 18.0


def half_width(z):
    return WIDTH/2-(WIDTH/2-BASE_HALF)*(1-min(z,HALF_HEIGHT)/HALF_HEIGHT)**1.5


def profile(z, inset):
    # End shaping is deliberately shallow to preserve the 255 mm long brush.
    a = LENGTH/2 - 2*(1-min(z,HALF_HEIGHT)/HALF_HEIGHT)**1.5 - inset
    b = half_width(z)-inset
    r = 6+8*min(z,HALF_HEIGHT)/HALF_HEIGHT-inset
    rear_r = 6+22*min(z,HALF_HEIGHT)/HALF_HEIGHT-inset
    return (cq.Workplane('XY', origin=(0,0,z)).moveTo(-a+r,-b)
            .lineTo(a-r,-b).radiusArc((a,-b+r),-r)
            .lineTo(a,b-rear_r).radiusArc((a-rear_r,b),-rear_r)
            .lineTo(-a+rear_r,b).radiusArc((-a,b-rear_r),-rear_r)
            .lineTo(-a,-b+r).radiusArc((-a+r,-b),-r).close().val())


def cup():
    levels = (0,FLOOR,5,9,14,20,25,RIM)
    outer = cq.Solid.makeLoft([profile(z,0) for z in levels])
    inner = cq.Solid.makeLoft([profile(z,WALL) for z in levels[1:]]+
                             [profile(RIM+1,WALL)])
    return cq.Workplane(obj=outer.cut(inner)).edges('>Z').fillet(.4)


def bearing():
    # Vertical teardrop roof gives an open 45-degree crown above a round seat.
    hole = (cq.Workplane('YZ',origin=(-12,AXIS_Y,AXIS_Z))
            .circle(BEARING_RADIUS).extrude(24))
    roof = (cq.Workplane('YZ',origin=(-12,0,0))
            .polyline([(AXIS_Y-BEARING_RADIUS/math.sqrt(2),AXIS_Z+BEARING_RADIUS/math.sqrt(2)),
                       (AXIS_Y,AXIS_Z+BEARING_RADIUS*math.sqrt(2)),
                       (AXIS_Y+BEARING_RADIUS/math.sqrt(2),AXIS_Z+BEARING_RADIUS/math.sqrt(2))])
            .close().extrude(24))
    post = (cq.Workplane('YZ',origin=(-1.9,0,0))
            .polyline([(42,FLOOR),(57,FLOOR),(54.5,15),(44.5,15)])
            .close().extrude(3.8))
    return post.cut(hole).cut(roof)


def rear_half(*, lid_side):
    part=cup()
    ear=bearing()
    for x in STATIONS:
        # The curved rear wall is interrupted only at each narrow hatch station.
        part=part.cut(block(x,65,20,SLOT_WIDTH,44,36))
        for sign in (-1,1):
            part=part.union(ear.translate((x+sign*6,LID_AXIS_Y-AXIS_Y if lid_side else 0,0)))
        centre_y=LID_AXIS_Y if lid_side else AXIS_Y
        bore=cq.Workplane('YZ',origin=(x-12,centre_y,AXIS_Z)).circle(BEARING_RADIUS).extrude(24)
        crown=(cq.Workplane('YZ',origin=(x-12,0,0))
               .polyline([(centre_y-BEARING_RADIUS/math.sqrt(2),AXIS_Z+BEARING_RADIUS/math.sqrt(2)),
                          (centre_y,AXIS_Z+BEARING_RADIUS*math.sqrt(2)),
                          (centre_y+BEARING_RADIUS/math.sqrt(2),AXIS_Z+BEARING_RADIUS/math.sqrt(2))])
               .close().extrude(24))
        part=part.cut(bore).cut(crown)
    if lid_side:
        for x in STATIONS:
            for side in (-1,1):
                part=part.cut(block(x+side*13.2,52.5,(FLOOR+RIM+1)/2,
                                    3.2,39,RIM+1-FLOOR))
    else:
        whole_levels=(0,FLOOR,5,9,14,20,25,HALF_HEIGHT,
                      HEIGHT-25,HEIGHT-20,HEIGHT-14,HEIGHT-9,HEIGHT-5,HEIGHT-FLOOR,HEIGHT)
        wires=[]
        for z in whole_levels:
            wire=profile(min(z,HEIGHT-z),0)
            wires.append(wire.translate((0,0,z-min(z,HEIGHT-z))))
        envelope=cq.Workplane(obj=cq.Solid.makeLoft(wires))
        for x in STATIONS:
            pocket_top=HEIGHT-FLOOR-.6
            front=block(x,29.0,(FLOOR+pocket_top)/2,28.8,2.4,pocket_top-FLOOR)
            front=front.edges('>Z').fillet(.4)
            part=part.union(front)
            for side in (-1,1):
                wall=block(x+side*13.2,49,(FLOOR+pocket_top)/2,2.4,41,pocket_top-FLOOR)
                part=part.union(wall.intersect(envelope))
            # Outer end access is covered by the recessed lower pin head.
            direction=-1 if x>0 else 1
            # Rounded shell is shallow at the lower axis. Grow a small enclosed
            # recess from the bed, rather than let the pin head cut a thin wall.
            shroud=(cq.Workplane('YZ',origin=(x-direction*18.3,0,0))
                    .polyline([(43,0),(50,0),(57,8),(55,18),(43,18)])
                    .close().extrude(direction*4.1))
            part=part.union(shroud)
            head_space=(cq.Workplane('YZ',origin=(x-direction*50,AXIS_Y,AXIS_Z))
                        .circle(5.0).extrude(direction*35.6))
            head_roof=(cq.Workplane('YZ',origin=(x-direction*50,0,0))
                       .polyline([(AXIS_Y-5/math.sqrt(2),AXIS_Z+5/math.sqrt(2)),
                                  (AXIS_Y,AXIS_Z+5*math.sqrt(2)),
                                  (AXIS_Y+5/math.sqrt(2),AXIS_Z+5/math.sqrt(2))])
                       .close().extrude(direction*35.6))
            part=part.cut(head_space).cut(head_roof)
            port=cq.Workplane('YZ',origin=(x-direction*50,AXIS_Y,AXIS_Z)).circle(BEARING_RADIUS).extrude(direction*41)
            roof=(cq.Workplane('YZ',origin=(x-direction*50,0,0))
                  .polyline([(AXIS_Y-BEARING_RADIUS/math.sqrt(2),AXIS_Z+BEARING_RADIUS/math.sqrt(2)),
                             (AXIS_Y,AXIS_Z+BEARING_RADIUS*math.sqrt(2)),
                             (AXIS_Y+BEARING_RADIUS/math.sqrt(2),AXIS_Z+BEARING_RADIUS/math.sqrt(2))])
                  .close().extrude(direction*41))
            part=part.cut(port).cut(roof)
            # The far snap barb expands beyond the ear into this local recess.
            barb_space=cq.Workplane('YZ',origin=(x+direction*8,AXIS_Y,AXIS_Z)).circle(3.8).extrude(direction*2.5)
            part=part.cut(barb_space)
    return part


def link():
    p=(cq.Workplane('YZ',origin=(-LINK_THICKNESS/2,0,0))
       .center((AXIS_Y+LID_AXIS_Y)/2,HEIGHT/2)
       .slot2D(LINK_SPACING+10,10,angle=CLOSED_LINK_ANGLE).extrude(LINK_THICKNESS))
    for y,z in ((AXIS_Y,AXIS_Z),(LID_AXIS_Y,HEIGHT-AXIS_Z)):
        p=p.cut(cq.Workplane('YZ',origin=(-8,y,z)).circle(BEARING_RADIUS).extrude(16))
    return p


def lid_pose(lid,phi,theta):
    pivot=(0,LID_AXIS_Y,HEIGHT-AXIS_Z)
    endpoint=(AXIS_Y+LINK_SPACING*math.cos(math.radians(theta)),
              AXIS_Z+LINK_SPACING*math.sin(math.radians(theta)))
    return lid.rotate(pivot,(1,*pivot[1:]),-phi).translate(
        (0,endpoint[0]-pivot[1],endpoint[1]-pivot[2]))


def link_pose(part,theta):
    return part.rotate((0,AXIS_Y,AXIS_Z),(1,AXIS_Y,AXIS_Z),theta-CLOSED_LINK_ANGLE)


def rough():
    body=rear_half(lid_side=False)
    lid_print=rear_half(lid_side=True)
    lid=lid_print.rotate((0,0,HEIGHT/2),(1,0,HEIGHT/2),180).mirror('XZ')
    # Rotation plus Y mirror leaves the closed lid directly above the body.
    links=[link().translate((x,0,0)) for x in STATIONS]
    assembly=cq.Assembly(name='rounded_C_candidate')
    assembly.add(body,name='body',color=cq.Color(.2,.5,.65))
    assembly.add(lid,name='lid',color=cq.Color(.5,.75,.8,.55))
    for i,p in enumerate(links):
        assembly.add(p,name=f'rear_hatch_{i+1}',color=cq.Color(.4,.65,.35))
    return dict(body=body,lid=lid,links=links,assembly=assembly)
