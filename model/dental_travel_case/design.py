"""Production builders; construction has no exports or report writes.

Coordinates: brush head at negative X, butt at positive X; Z is print-up.
Lid prints open at positive Y and closes about the X-directed hinge axis.
"""
import cadquery as cq
from parameters import *
from mechanisms import block, half, hinge, front_latch
from components import compound, clip, socket

def shells():
    body=half()
    open_lid=half().translate((0,2*HY,0))
    for c in BEARING_CENTERS:
        left,right,receiver=hinge(c)
        body=body.union(left).union(right)
        open_lid=open_lid.union(receiver)
    # Continuous partition reaches near the closed roof, protecting the head
    # even when the case is inverted. Rounded top for handling and cleaning.
    partition=block(0,PARTITION_Y,(FLOOR+HEIGHT-FLOOR-0.6)/2,
                    IW-1.2,WALL,IH-0.6)
    partition=partition.edges('|Y and >Z').fillet(PARTITION_CORNER_RADIUS)
    partition=partition.edges('|X').fillet(PARTITION_EDGE_RADIUS)
    body=body.union(partition)
    for x in CLIP_POSITIONS:
        body=body.union(socket().translate((x,BRUSH_Y,FLOOR)))
    front=-OD/2
    keeper=(cq.Workplane('YZ',origin=(-8,0,0))
            .polyline([(front+0.2,SEAM-5.6),(front-1.4,SEAM-4),
                       (front+0.2,SEAM-2.4)]).close().extrude(16))
    body=body.union(keeper)
    open_lid=open_lid.union(front_latch())
    # Side vents adjacent to head, vertical slots with arched ends. No floor holes.
    for x in (-IW/2+16,-IW/2+24,-IW/2+32):
        vent=(cq.Workplane('XZ',origin=(x,-OD/2+WALL+1,14))
              .slot2D(10,2.4,angle=90).extrude(WALL+2))
        body=body.cut(vent)
    lid=open_lid.rotate((0,HY,SEAM),(1,HY,SEAM),180)
    return body,open_lid,lid



def build():
    body, open_lid, lid = shells()
    cartridge = clip()
    clips = [cartridge.translate((x, BRUSH_Y, FLOOR+CRADLE_LIFT)) for x in CLIP_POSITIONS]
    closed = cq.Assembly(name="dental_case")
    closed.add(body, name="body")
    closed.add(lid, name="lid")
    for i, c in enumerate(clips):
        closed.add(c, name=f"brush_clip_{i+1}")
    opened = cq.Assembly(name="open_case")
    opened.add(body, name="body")
    opened.add(lid.rotate((0,HY,SEAM),(1,HY,SEAM),-110), name="lid")
    for i, c in enumerate(clips):
        opened.add(c, name=f"brush_clip_{i+1}")
    return dict(body=body, open_lid=open_lid, lid=lid, installed_clips=clips,
                result=compound(body,open_lid), accessories=compound(cartridge,cartridge.translate((32,0,0))),
                closed=closed.toCompound(), opened=opened.toCompound(), assembly=closed)
