"""C: fixed rear wall, roof-height hinge, printed axle and loose tapered key.

Five-card exploratory prototype. All geometry uses the current seating builder;
the printed lower-section history remains separate. Clearances are provisional.
"""
import math
import cadquery as cq
from cap_common import *

FRAME_WIDTH = CAP_OUTER_X+3.6
AXLE_RADIUS = 2.5
BEARING_GAP = .2
DIAMOND_RADIUS = (AXLE_RADIUS+BEARING_GAP)*math.sqrt(2)
HINGE_Z = ROOF_TOP-5.2
MOVING_HALF_WIDTH = 6.0
EAR_GAP = .6
EAR_OUTSIDE = 13.6
KEY_X = 17.2
KEY_THICKNESS = 1.6
KEY_TIP_WIDTH = 2.8
KEY_ROOT_WIDTH = 3.1
REAR_FOOT_REACH = 40.0  # From rear edge of card base; open-lid stability footprint.
OPEN_STOP_ANGLE = 180


def end_y(count):
    return outer_depth(count)/2


def hinge_y(count):
    return end_y(count)+7.7


def block(x0,x1,y0,y1,z0,z1):
    return (cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=(False,False,False))
            .translate((x0,y0,z0)))


def bore(count,x0,x1):
    r=DIAMOND_RADIUS
    return (cq.Workplane('YZ',origin=(x0,hinge_y(count),HINGE_Z))
            .polyline([(0,-r),(r,0),(0,r),(-r,0)]).close().extrude(x1-x0))


def frame(count=DEFAULT_COUNT):
    """Rear wall stays upright; external ears are joined all the way to the floor."""
    end=end_y(count)
    wall=block(-FRAME_WIDTH/2,FRAME_WIDTH/2,end-.2,end+2.4,0,ROOF_UNDERSIDE)
    # Returns cover the moving side/rear seams with an exterior overlap.
    for side in (-1,1):
        x0,x1=sorted((side*(CAP_OUTER_X/2+.2),side*FRAME_WIDTH/2))
        wall=wall.union(block(x0,x1,end-2,end+2.4,0,ROOF_UNDERSIDE))
    # Opening clearance at the front upper corner of the fixed rear wall.
    relief=(cq.Workplane('YZ',origin=(-FRAME_WIDTH/2-.1,0,0))
            .polyline([(end-.3,ROOF_UNDERSIDE+.01),
                       (end+.8,ROOF_UNDERSIDE+.01),
                       (end-.3,ROOF_UNDERSIDE-1.09)]).close().extrude(FRAME_WIDTH+.2))
    wall=wall.cut(relief)
    hy=hinge_y(count)
    # Bevel the ear crowns so the roof tail clears on its over-centre travel.
    profile=[(end+2.3,0),(hy+5,0),(hy+5,HINGE_Z+1.2),
             (hy+1.2,HINGE_Z+5),(hy-1.2,HINGE_Z+5),
             (hy-5,HINGE_Z+1.2),(hy-5,76),(end+2.3,75.6)]
    for x0,x1 in ((-EAR_OUTSIDE,-MOVING_HALF_WIDTH-EAR_GAP),
                   (MOVING_HALF_WIDTH+EAR_GAP,EAR_OUTSIDE)):
        ear=(cq.Workplane('YZ',origin=(x0,0,0)).polyline(profile).close()
             .extrude(x1-x0))
        wall=wall.union(ear)
        # Inversion exposes the roof's outer surface to these open-stop shelves.
        stop=(cq.Workplane('YZ',origin=(x0,0,0))
              .polyline([(hy+4.8,HINGE_Z-8.4),(hy+8,HINGE_Z-5.2),
                         (hy+4.8,HINGE_Z-5.2)]).close().extrude(x1-x0))
        wall=wall.union(stop)
    wall=wall.cut(bore(count,-EAR_OUTSIDE-.1,EAR_OUTSIDE+.1))
    reach=REAR_FOOT_REACH-2.3
    foot=rounded_block(50,reach,CAP_WALL,radius=3).translate((0,end+2.3+reach/2,0))
    wall=wall.union(foot)
    return rounded_base(count).union(wall)


def cap(count=DEFAULT_COUNT):
    end=end_y(count)
    lid=hood_shell(count).union(stop_pads(count)).union(side_grips(count))
    # Replace the rear skirt with the fixed wall. The roof overlaps that wall.
    lid=lid.cut(block(-100,100,end-.6,end+40,0,ROOF_UNDERSIDE))
    # The original four-wall hood's inner rear fillets would catch the base
    # during opening. Open that internal corner into a straight U cavity.
    lid=lid.cut(block(-CAP_INNER_X/2,CAP_INNER_X/2,end-4,end+40,0,ROOF_UNDERSIDE))
    lid=lid.cut(block(-100,100,end+2.3,end+40,0,ROOF_TOP+1))
    web=block(-MOVING_HALF_WIDTH,MOVING_HALF_WIDTH,end+1.2,hinge_y(count),
              ROOF_UNDERSIDE+.4,ROOF_TOP)
    # Compact octagonal boss: unlike a square, it keeps its full rotation
    # inside the clearance to the fixed rear wall. Crown grows at 45 degrees.
    b=4.9; c=1.0
    boss=(cq.Workplane('YZ',origin=(-MOVING_HALF_WIDTH,hinge_y(count),HINGE_Z))
          .polyline([(-c,-b),(c,-b),(b,-c),(b,c),(c,b),(-c,b),(-b,c),(-b,-c)])
          .close().extrude(2*MOVING_HALF_WIDTH))
    lid=lid.union(web).union(boss)
    return lid.cut(bore(count,-MOVING_HALF_WIDTH-.1,MOVING_HALF_WIDTH+.1))


def axle(count=DEFAULT_COUNT):
    axis=(hinge_y(count),HINGE_Z)
    pin=cq.Workplane('YZ',origin=(-14,*axis)).circle(AXLE_RADIUS).extrude(36)
    head=cq.Workplane('YZ',origin=(-16,*axis)).circle(4).extrude(2)
    pin=pin.union(head)
    # A diamond-ended cross slot has 45-degree roofs in the vertical pin print.
    slot=(cq.Workplane('XZ',origin=(KEY_X,hinge_y(count)+3.5,HINGE_Z))
          .polyline([(-2.6,0),(-1,-1.6),(1,-1.6),(2.6,0),(1,1.6),(-1,1.6)])
          .close().extrude(7))
    return pin.cut(slot)


def key(count=DEFAULT_COUNT):
    # Loose tapered key: axial retention is conditional on the key staying in.
    # No calibrated interference or spring-retention claim is made.
    hy=hinge_y(count)
    points=[(hy-4,HINGE_Z-KEY_TIP_WIDTH/2),
            (hy+4,HINGE_Z-KEY_ROOT_WIDTH/2),(hy+4,HINGE_Z-3.5),
            (hy+6,HINGE_Z-3.5),(hy+6,HINGE_Z+3.5),
            (hy+4,HINGE_Z+3.5),(hy+4,HINGE_Z+KEY_ROOT_WIDTH/2),
            (hy-4,HINGE_Z+KEY_TIP_WIDTH/2)]
    return (cq.Workplane('YZ',origin=(KEY_X-KEY_THICKNESS/2,0,0))
            .polyline(points).close().extrude(KEY_THICKNESS))


def opened(lid,count,angle=110):
    return lid.rotate((0,hinge_y(count),HINGE_Z),(1,hinge_y(count),HINGE_Z),-angle)


def axle_print(count=DEFAULT_COUNT):
    return (axle(count).translate((0,-hinge_y(count),-HINGE_Z))
            .rotate((0,0,0),(0,1,0),-90).translate((0,0,16)))


def key_print(count=DEFAULT_COUNT):
    return (key(count).translate((-KEY_X+KEY_THICKNESS/2,-hinge_y(count),-HINGE_Z))
            .rotate((0,0,0),(0,1,0),-90))


def print_layout(count=DEFAULT_COUNT):
    return compound(frame(count),hood_print(cap(count)).translate((78,0,0)),
                    axle_print(count).translate((126,-8,0)),
                    key_print(count).translate((126,10,0)))


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
