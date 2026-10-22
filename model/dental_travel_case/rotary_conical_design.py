"""Matched printable wheel recess and flush socket-head shoulder axle.

Local screw Z runs inward from the historical external-hex face. The new face
extends 0.3 mm outward; the successful thread, shoulder seat and nut stay put.
"""
from math import cos,radians
import cadquery as cq
import m1_design as base
from rotary_printed_fastener_design import printed_axle as old_axle,TIP,HEAD_HEIGHT

FACE_EXTENSION=.3
HEAD_RADIUS=6.
JOURNAL_RADIUS=4.
HEAD_DEPTH=2.
RADIAL_SEAM=.2
KEY_AF=3.
SOCKET_AF=3.2
SOCKET_DEPTH=2.2
SOCKET_ROOF=1.9


def printed_axle():
    """Blind drive ends before the thread; the complete thread core is solid."""
    old=old_axle()
    shaft=old.intersect(base.box(0,0,(HEAD_HEIGHT+TIP)/2,14,14,TIP-HEAD_HEIGHT))
    head=(cq.Workplane('XY',origin=(0,0,-FACE_EXTENSION)).circle(HEAD_RADIUS)
          .workplane(offset=HEAD_DEPTH).circle(JOURNAL_RADIUS).loft(ruled=True))
    neck=(cq.Workplane('XY',origin=(0,0,HEAD_DEPTH-FACE_EXTENSION-.05))
          .circle(JOURNAL_RADIUS).extrude(HEAD_HEIGHT-HEAD_DEPTH+FACE_EXTENSION+.10))
    socket=(cq.Workplane('XY',origin=(0,0,-FACE_EXTENSION-.01))
            .polygon(6,SOCKET_AF/cos(radians(30))).extrude(SOCKET_DEPTH+.01))
    roof=(cq.Workplane('XY',origin=(0,0,SOCKET_DEPTH-FACE_EXTENSION))
          .polygon(6,SOCKET_AF/cos(radians(30)))
          .workplane(offset=SOCKET_ROOF).polygon(6,.04).loft(ruled=True))
    return shaft.union(neck).union(head).cut(socket.union(roof)).clean()


def wheel_recess(d):
    """Face-down hole shrinks 0.2 mm in radius per 0.2 mm layer (45 degrees)."""
    return cq.Workplane(obj=cq.Solid.makeCone(HEAD_RADIUS+RADIAL_SEAM,
        JOURNAL_RADIUS+RADIAL_SEAM,HEAD_DEPTH,
        cq.Vector(0,d.wheel_front,d.pivot),cq.Vector(0,-1,0)))


def screw_print_pose(part):
    """Broad head down; tapered blind-socket roof closes without a flat ceiling."""
    return part.translate((0,0,FACE_EXTENSION))
