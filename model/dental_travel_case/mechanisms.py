"""Case shell and conical hinge/latch builders, adapted from repository sunglasses case.
Dimensions are imported from this object only; no build/export on import.
"""
import cadquery as cq
from parameters import *

def block(x, y, z, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz).translate((x, y, z))


def rounded(w, d, h, z, radius):
    return (cq.Workplane("XY").box(w, d, h, centered=(True, True, False))
            .edges("|Z").fillet(radius).translate((0, 0, z)))


def half():
    outer = rounded(OW, OD, SEAM, 0, CORNER)
    outer = outer.edges("<Z").chamfer(EXTERIOR_BEVEL)
    cavity = rounded(IW, ID, SEAM, FLOOR, CORNER - WALL)
    return outer.cut(cavity).edges(">Z").fillet(RIM_ROUND)


def hinge_ear(x0, x1, lid_side=False):
    """Round crown, tangent 45-degree underside and web in flat print pose."""
    side = 1 if lid_side else -1
    wall_y = HY + side * (HINGE_RADIUS*2**0.5 + 1.8)
    r = HINGE_RADIUS
    t = r/2**0.5
    barrel = (cq.Workplane("YZ", origin=(x0, HY, SEAM))
              .moveTo(0, -r*2**0.5).lineTo(t, -t)
              .threePointArc((r, 0), (0, r))
              .threePointArc((-r, 0), (-t, -t)).close().extrude(x1-x0))
    barrel = barrel.edges(cq.selectors.NearestToPointSelector(
        ((x0+x1)/2, HY, SEAM-r*2**0.5))).fillet(0.8)
    web_low = SEAM-r*2**0.5-abs(wall_y-HY)
    web = (cq.Workplane("YZ", origin=(x0, 0, 0))
           .polyline([(wall_y, web_low), (HY, SEAM-r*2**0.5),
                      (HY, SEAM), (wall_y, SEAM)]).close().extrude(x1-x0))
    return barrel.union(web)


def cone(x, radius, direction):
    # Blunt the mathematical apex by 0.12 mm to avoid degenerate STL facets.
    # Male and socket cones retain the same 45-degree mating surfaces.
    return cq.Workplane(obj=cq.Solid.makeCone(radius, 0.12, radius-0.12,
        cq.Vector(x, HY, SEAM), cq.Vector(direction, 0, 0)))


def hinge(c):
    """Two fixed cones enter opposite ends of a captive rotating socket.

    Each cone extends from an attached ear at 45 degrees instead of beginning
    as a floating horizontal rod. The conical socket roofs are also 45 degrees.
    """
    left = hinge_ear(c-EAR_OUTER_OFFSET, c-PIVOT_ROOT)
    right = hinge_ear(c+PIVOT_ROOT, c+EAR_OUTER_OFFSET)
    left = left.union(cone(c-PIVOT_ROOT, PIVOT_RADIUS, 1))
    right = right.union(cone(c+PIVOT_ROOT, PIVOT_RADIUS, -1))
    receiver = hinge_ear(c-RECEIVER_HALF, c+RECEIVER_HALF, lid_side=True)
    receiver = receiver.cut(cone(c-PIVOT_ROOT, PIVOT_RADIUS+CONE_CLEARANCE, 1))
    receiver = receiver.cut(cone(c+PIVOT_ROOT, PIVOT_RADIUS+CONE_CLEARANCE, -1))
    return left, right, receiver


def front_latch():
    """Ramp-rooted PETG spring on the lid, built in the OPEN print pose.

    Two-sided 45-degree detents replace the unprintable square undercut.
    Pull the tab outward before lifting. Retention is elastic, not a deadbolt.
    """
    front = 2*HY + OD/2
    inner, outer = front+2.4, front+2.4+LATCH_THICKNESS
    base, top = SEAM-15, SEAM+10
    leaf_start = base + (outer-front) + 0.4
    root = (cq.Workplane("YZ", origin=(-10, 0, 0))
            .polyline([(front-0.5, base), (outer, leaf_start),
                       (outer, leaf_start+2.6), (front-0.5, leaf_start+2.6)])
            .close().extrude(20))
    leaf = block(0, (inner+outer)/2, (leaf_start+top)/2,
                 20, LATCH_THICKNESS, top-leaf_start).edges("|Z").fillet(0.4).edges(">Z").chamfer(0.3)
    tooth = (cq.Workplane("YZ", origin=(-7, 0, 0))
             .polyline([(inner+0.2, SEAM+3.0), (front+0.4, SEAM+5.2),
                        (inner+0.2, SEAM+7.4)]).close().extrude(14))
    grip = (cq.Workplane("YZ", origin=(-9, 0, 0))
            .polyline([(outer-0.2, top-3), (outer+1.2, top-1.6),
                       (outer+1.2, top-0.4), (outer-0.2, top-0.4)])
            .close().extrude(18).edges("|X").fillet(0.3))
    return root.union(leaf).union(tooth).union(grip)
