"""Source-coordinate swatch reference, then ONE proper notch-up rotation.

The SCAD front is +Z. After rotation it faces +Y; source +X becomes holder
+Z and source +Y becomes holder +X. Surface engraving is omitted; contact
checks must avoid its source area. This reference is never printable output.
"""
import cadquery as cq
from study import swatch_dimension
from card_base_test import FLOOR

WIDTH=swatch_dimension('card_width')
HEIGHT=swatch_dimension('card_height')
THICKNESS=swatch_dimension('base_thickness')
DOME_SOURCE=(WIDTH-66,9,THICKNESS+6)
DOME_RADIUS=8.0


def block(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))


def source_card(thickness=THICKNESS):
    r=swatch_dimension('right_corner_radius')
    c=swatch_dimension('left_chamfer_size')
    body=(cq.Workplane('XY').moveTo(c,0).lineTo(WIDTH-r,0)
          .radiusArc((WIDTH,r),-r).lineTo(WIDTH,HEIGHT-r)
          .radiusArc((WIDTH-r,HEIGHT),-r).lineTo(c,HEIGHT)
          .lineTo(0,HEIGHT-c).lineTo(0,c).close().extrude(thickness))
    body=body.cut(cq.Workplane('XY').center(WIDTH,HEIGHT/2).circle(8).extrude(thickness+2,both=True))
    body=body.cut(cq.Workplane('XY').sphere(DOME_RADIUS).translate(
        (DOME_SOURCE[0],DOME_SOURCE[1],thickness+6)))
    for n in range(5):
        body=body.cut(block(WIDTH-15-10*n,WIDTH-5-10*n,5,13,.2*(n+1),thickness+.1))
    edge=swatch_dimension('top_edge_chamfer')
    body=body.cut(cq.Workplane('YZ',origin=(-1,0,0)).polyline(
        [(HEIGHT,thickness-edge),(HEIGHT,thickness),(HEIGHT-edge,thickness)]).close().extrude(WIDTH+2))
    radius=swatch_dimension('bottom_edge_fillet')
    offset=thickness-radius
    cutter=block(-1,WIDTH+1,0,radius+.1,offset,thickness+.1).cut(
        cq.Workplane('YZ',origin=(-1,radius,offset)).circle(radius).extrude(WIDTH+2))
    return body.cut(cutter)


def upright(shape,back_y):
    # Rotation determinant +1. Do not reflect or reconstruct recesses after it.
    return shape.rotate((0,0,0),(1,1,1),-120).translate((-HEIGHT/2,back_y,FLOOR))


def card(back_y,thickness=THICKNESS):
    return upright(source_card(thickness),back_y)


def point(source_xyz,back_y):
    x,y,z=source_xyz
    return (y-HEIGHT/2,back_y+z,FLOOR+x)


def dome_ball(back_y,thickness=THICKNESS):
    return upright(cq.Workplane('XY').sphere(DOME_RADIUS).translate(
        (DOME_SOURCE[0],DOME_SOURCE[1],thickness+6)),back_y)
