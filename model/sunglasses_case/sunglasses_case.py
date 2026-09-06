"""Sunglasses case, mm. Evaluate this file with the CadQuery MCP.

PETG, 0.4 mm nozzle; 260 mm build volume confirmed.
Opposing conical pivots: no separate pin, nuts or assembly.
Print open 180 degrees with both broad exterior faces on the bed.
No supports; short pivots and socket roofs grow on 45-degree surfaces.
"""
from pathlib import Path
import cadquery as cq

GLASSES_WIDTH = 160.0
GLASSES_DEPTH = 80.0
GLASSES_HEIGHT = 60.0
CLEARANCE = 4.0  # each side, includes allowance for 1 mm soft lining
WALL = 3.0
FLOOR = 3.0
CORNER = 10.0
EXTERIOR_BEVEL = 2.0
RIM_ROUND = 0.6
HINGE_RADIUS = 5.6  # round crown with tangent 45-degree printable underside
PIVOT_RADIUS = 3.5
PIVOT_TIP_OFFSET = 1.0  # tips stop either side of bearing centre
CONE_CLEARANCE = 0.6  # radial at fixed X; normal cone gap = value / sqrt(2)
END_CLEARANCE = 0.5  # axial gap between fixed and moving ears
EAR_OUTER_OFFSET = 10.0
LATCH_THICKNESS = 1.6
LAYOUT = "closed"  # closed / open / print / coupon / hinge_section
EXPORT = True

IW = GLASSES_WIDTH + 2 * CLEARANCE
ID = GLASSES_DEPTH + 2 * CLEARANCE
IH = GLASSES_HEIGHT + 2 * CLEARANCE
OW, OD = IW + 2 * WALL, ID + 2 * WALL
HEIGHT = IH + 2 * FLOOR
SEAM = HEIGHT / 2
HY = OD / 2 + HINGE_RADIUS * 2**0.5 + 0.8
BEARING_CENTERS = (-OW/2 + 52, OW/2 - 52)
PIVOT_ROOT = PIVOT_TIP_OFFSET + PIVOT_RADIUS
RECEIVER_HALF = PIVOT_ROOT - END_CLEARANCE
assert CLEARANCE >= 3 and WALL >= 2.4 and IH >= 40
assert OW > 140 and ID > 60


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


body = half()
open_lid = half().translate((0, 2*HY, 0))
for c in BEARING_CENTERS:
    left, right, receiver = hinge(c)
    body = body.union(left).union(right)
    open_lid = open_lid.union(receiver)
front = -OD/2
keeper = (cq.Workplane("YZ", origin=(-8, 0, 0))
          .polyline([(front+0.2, SEAM-5.6), (front-1.4, SEAM-4),
                     (front+0.2, SEAM-2.4)]).close().extrude(16))
body = body.union(keeper)
open_lid = open_lid.union(front_latch())
lid = open_lid.rotate((0, HY, SEAM), (1, HY, SEAM), 180)


def compound(*parts):
    return cq.Compound.makeCompound([p.val() for p in parts])


def opening(angle):
    return lid.rotate((0, HY, SEAM), (1, HY, SEAM), -angle)


def hinge_coupon():
    # Exact production hinge on short wall sections, same bed and axis heights.
    fixed = block(0, OD/2-1.5, SEAM/2, 32, 3, SEAM)
    moving = block(0, 2*HY-OD/2+1.5, SEAM/2, 32, 3, SEAM)
    fixed = fixed.union(block(0, OD/2-6, FLOOR/2, 32, 12, FLOOR))
    moving = moving.union(block(0, 2*HY-OD/2+6, FLOOR/2, 32, 12, FLOOR))
    left, right, receiver = hinge(0)
    fixed = fixed.union(left).union(right)
    moving = moving.union(receiver)
    assert len(fixed.solids().vals()) == len(moving.solids().vals()) == 1
    assert fixed.val().isValid() and moving.val().isValid()
    for angle in range(0, 181, 15):
        rotated = moving.rotate((0, HY, SEAM), (1, HY, SEAM), angle)
        assert fixed.intersect(rotated).val().Volume() < 0.001, f"Coupon interference {angle}"
    # Translation meets opposing ears/cones before either tip can disengage.
    for shift in (-1.0, 1.0):
        assert fixed.intersect(moving.translate((shift, 0, 0))).val().Volume() > 0.001
    return compound(fixed, moving)


closed = compound(body, lid)
opened = compound(body, opening(110))
print_body, print_lid = body, open_lid
print_layout = compound(body, open_lid)
coupon = hinge_coupon()
hinge_section = cq.Workplane(obj=coupon).intersect(block(0, HY, SEAM-15, 40, 70, 30))
result = {"closed": closed, "open": opened, "print": print_layout,
          "coupon": coupon, "hinge_section": hinge_section}[LAYOUT]

assert len(body.solids().vals()) == 1 and body.val().isValid()
assert len(lid.solids().vals()) == 1 and lid.val().isValid()
assert body.intersect(lid).val().Volume() < 0.001, "Closed parts interfere"
fit_envelope = block(0, 0, HEIGHT/2, GLASSES_WIDTH, GLASSES_DEPTH, GLASSES_HEIGHT)
assert body.intersect(fit_envelope).val().Volume() < 0.001
assert lid.intersect(fit_envelope).val().Volume() < 0.001
for angle in range(20, 181, 5):
    assert body.intersect(opening(angle)).val().Volume() < 0.001, "Hinge sweep interferes"
assert PIVOT_RADIUS-END_CLEARANCE > END_CLEARANCE
assert HINGE_RADIUS - (PIVOT_RADIUS+CONE_CLEARANCE-END_CLEARANCE) >= 1.5
assert abs(print_body.val().BoundingBox().zmin) < 0.02
assert abs(print_lid.val().BoundingBox().zmin) < 0.02
assert max(print_layout.BoundingBox().xlen, print_layout.BoundingBox().ylen,
           print_layout.BoundingBox().zlen) < 260

if EXPORT:
    dest = Path(globals().get("__file__", "/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/sunglasses_case.py")).resolve().parent
    cq.exporters.export(closed, str(dest / "sunglasses_case.step"))
    cq.exporters.export(print_layout, str(dest / "sunglasses_case.stl"), tolerance=0.035, angularTolerance=0.1)
    cq.exporters.export(coupon, str(dest / "hinge_test.stl"), tolerance=0.035, angularTolerance=0.1)
