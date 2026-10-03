"""Object-only revision: upward-facing finger ledges below the closed hood.

Hold the base down on the ledges while the other hand lifts the hood. J2/K2
card geometry, Z=5 seating, closure springs and I sockets are preserved.
"""
import cadquery as cq
import cap_g_module_5 as g

EXTENSION=7.0
ROOT_OVERLAP=1.2
LENGTH_Y=24.0
HEIGHT=2.4
CORNER_RADIUS=2.0
TOP_ROUND=.6
BOTTOM_CHAMFER=.6
RESTORE_HEIGHT=3.6
CONTACT_X=g.FOOT_X/2+4.5
FINGER_HALF_Y=10.0
FINGER_HALF_Z=4.0
FINGER_NOSE=4.0
FINGER_LENGTH=25.0


def ledge(side=1):
    lo=g.FOOT_X/2-ROOT_OVERLAP
    hi=g.FOOT_X/2+EXTENSION
    pad=(g.rounded_block(hi-lo,LENGTH_Y,HEIGHT,0,CORNER_RADIUS)
         .translate(((lo+hi)/2,0,0)).faces('>Z').edges().fillet(TOP_ROUND)
         .faces('<Z').edges().chamfer(BOTTOM_CHAMFER))
    return g.mirrored(pad,side)


def restore_foot():
    # Restrict restoration to the OLD cutouts, below all spring/seat interfaces.
    original=(g.rounded_block(g.FOOT_X,g.FOOT_DEPTH,g.SEAM_Z,0,g.FOOT_RADIUS)
              .faces('<Z').edges().chamfer(g.FOOT_BOTTOM_CHAMFER)
              .faces('>Z').edges().fillet(g.FOOT_TOP_ROUND))
    region=g.block(g.FOOT_X/2-2.05,g.FOOT_X/2+.1,-9.05,9.05,0,RESTORE_HEIGHT)
    patch=original.intersect(region)
    return patch.union(patch.mirror('YZ'))


def revise(previous):
    return previous.union(restore_foot()).union(ledge(1)).union(ledge(-1))


def changed_region():
    box=g.block(g.FOOT_X/2-2.1,g.FOOT_X/2+EXTENSION+.1,
                -LENGTH_Y/2-.1,LENGTH_Y/2+.1,-.1,RESTORE_HEIGHT+.01)
    return box.union(box.mirror('YZ'))


def finger(side=1,lift=0):
    """Inspection-only distal finger envelope, not a human grasp simulation.

    Assumed 20 mm width/8 mm thickness; rounded bounding envelope, outward body.
    A vertical approach stays outside the largest hood outline. Contact is
    deliberate at the ledge top; skin deformation/comfort are physical unknowns.
    """
    lo=CONTACT_X-FINGER_NOSE
    hi=CONTACT_X+FINGER_LENGTH
    body=(g.rounded_block(hi-lo,2*FINGER_HALF_Y,2*FINGER_HALF_Z,HEIGHT+lift,3)
          .translate(((lo+hi)/2,0,0)).faces('>Z or <Z').edges().fillet(1))
    return g.mirrored(body,side)
