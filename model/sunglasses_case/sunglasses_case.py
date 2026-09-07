"""Sunglasses case, mm. Evaluate this file with the CadQuery MCP.

PETG, 0.4 mm nozzle; safe build volume 260 x 260 x 250 mm (XYZ) confirmed.
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
EXPORT = globals().get("EXPORT", True)

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


def hinge_ear(x0, x1, lid_side=False, hy=HY):
    """Round crown, tangent 45-degree underside and web in flat print pose."""
    side = 1 if lid_side else -1
    wall_y = hy + side * (HINGE_RADIUS*2**0.5 + 1.8)
    r = HINGE_RADIUS
    t = r/2**0.5
    barrel = (cq.Workplane("YZ", origin=(x0, hy, SEAM))
              .moveTo(0, -r*2**0.5).lineTo(t, -t)
              .threePointArc((r, 0), (0, r))
              .threePointArc((-r, 0), (-t, -t)).close().extrude(x1-x0))
    barrel = barrel.edges(cq.selectors.NearestToPointSelector(
        ((x0+x1)/2, hy, SEAM-r*2**0.5))).fillet(0.8)
    web_low = SEAM-r*2**0.5-abs(wall_y-hy)
    web = (cq.Workplane("YZ", origin=(x0, 0, 0))
           .polyline([(wall_y, web_low), (hy, SEAM-r*2**0.5),
                      (hy, SEAM), (wall_y, SEAM)]).close().extrude(x1-x0))
    return barrel.union(web)


def cone(x, radius, direction, hy=HY):
    # Blunt the mathematical apex by 0.12 mm to avoid degenerate STL facets.
    # Male and socket cones retain the same 45-degree mating surfaces.
    return cq.Workplane(obj=cq.Solid.makeCone(radius, 0.12, radius-0.12,
        cq.Vector(x, hy, SEAM), cq.Vector(direction, 0, 0)))


def hinge(c, cone_clearance=CONE_CLEARANCE, end_clearance=END_CLEARANCE, hy=HY):
    """Two fixed cones enter opposite ends of a captive rotating socket.

    Each cone extends from an attached ear at 45 degrees instead of beginning
    as a floating horizontal rod. The conical socket roofs are also 45 degrees.
    """
    left = hinge_ear(c-EAR_OUTER_OFFSET, c-PIVOT_ROOT, hy=hy)
    right = hinge_ear(c+PIVOT_ROOT, c+EAR_OUTER_OFFSET, hy=hy)
    left = left.union(cone(c-PIVOT_ROOT, PIVOT_RADIUS, 1, hy))
    right = right.union(cone(c+PIVOT_ROOT, PIVOT_RADIUS, -1, hy))
    receiver_half = PIVOT_ROOT - end_clearance
    receiver = hinge_ear(c-receiver_half, c+receiver_half, lid_side=True, hy=hy)
    receiver = receiver.cut(cone(c-PIVOT_ROOT, PIVOT_RADIUS+cone_clearance, 1, hy))
    receiver = receiver.cut(cone(c+PIVOT_ROOT, PIVOT_RADIUS+cone_clearance, -1, hy))
    return left, right, receiver


def front_latch(tooth_shift=0.0, hy=HY, od=OD):
    """Ramp-rooted PETG spring on the lid, built in the OPEN print pose.

    Two-sided 45-degree detents replace the unprintable square undercut.
    Pull the tab outward before lifting. Retention is elastic, not a deadbolt.
    """
    front = 2*hy + od/2
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
             .polyline([(inner+0.2+tooth_shift, SEAM+3.0),
                        (front+0.4+tooth_shift, SEAM+5.2),
                        (inner+0.2+tooth_shift, SEAM+7.4)]).close().extrude(14))
    grip = (cq.Workplane("YZ", origin=(-9, 0, 0))
            .polyline([(outer-0.2, top-3), (outer+1.2, top-1.6),
                       (outer+1.2, top-0.4), (outer-0.2, top-0.4)])
            .close().extrude(18).edges("|X").fillet(0.3))
    return root.union(leaf).union(tooth).union(grip)


def front_keeper(depth=1.4, front=None):
    """Fixed triangular keeper; depth is the outward engagement reach."""
    if front is None:
        front = -OD/2
    return (cq.Workplane("YZ", origin=(-8, 0, 0))
            .polyline([(front+0.2, SEAM-5.6), (front-depth, SEAM-4),
                       (front+0.2, SEAM-2.4)]).close().extrude(16))


body = half()
open_lid = half().translate((0, 2*HY, 0))
for c in BEARING_CENTERS:
    left, right, receiver = hinge(c)
    body = body.union(left).union(right)
    open_lid = open_lid.union(receiver)
body = body.union(front_keeper())
open_lid = open_lid.union(front_latch())
lid = open_lid.rotate((0, HY, SEAM), (1, HY, SEAM), 180)


def compound(*parts):
    return cq.Compound.makeCompound([p.val() for p in parts])


def opening(angle):
    return lid.rotate((0, HY, SEAM), (1, HY, SEAM), -angle)


def hinge_coupon(cone_clearance=CONE_CLEARANCE, end_clearance=END_CLEARANCE):
    # Exact production hinge on short wall sections, same bed and axis heights.
    fixed = block(0, OD/2-1.5, SEAM/2, 32, 3, SEAM)
    moving = block(0, 2*HY-OD/2+1.5, SEAM/2, 32, 3, SEAM)
    fixed = fixed.union(block(0, OD/2-6, FLOOR/2, 32, 12, FLOOR))
    moving = moving.union(block(0, 2*HY-OD/2+6, FLOOR/2, 32, 12, FLOOR))
    left, right, receiver = hinge(0, cone_clearance, end_clearance)
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


def mechanism_coupon(cone_clearance, end_clearance, tooth_shift=0.0,
                     keeper_depth=1.4):
    """Narrow full-depth box slice with one production hinge and latch.

    The 32 mm width keeps the production hinge and latch geometry in a short
    40 mm-deep box slice. It tests local engagement and movement, but does not
    represent the full case's bending stiffness. It prints open and flat, so
    both halves remain captive and support-free.
    """
    width = 32.0
    test_od = 40.0
    test_hy = test_od/2 + HINGE_RADIUS*2**0.5 + 0.8
    body_floor = block(0, 0, FLOOR/2, width, test_od, FLOOR)
    lid_floor = block(0, 2*test_hy, FLOOR/2, width, test_od, FLOOR)
    body_front = block(0, -test_od/2+1.5, SEAM/2, width, 3, SEAM)
    body_rear = block(0, test_od/2-1.5, SEAM/2, width, 3, SEAM)
    lid_front = block(0, 2*test_hy-test_od/2+1.5, SEAM/2, width, 3, SEAM)
    lid_rear = block(0, 2*test_hy+test_od/2-1.5, SEAM/2, width, 3, SEAM)
    fixed = body_floor.union(body_front).union(body_rear)
    moving = lid_floor.union(lid_front).union(lid_rear)
    left, right, receiver = hinge(0, cone_clearance, end_clearance, test_hy)
    fixed = fixed.union(left).union(right).union(
        front_keeper(keeper_depth, front=-test_od/2))
    moving = moving.union(receiver).union(
        front_latch(tooth_shift, test_hy, test_od))
    assert len(fixed.solids().vals()) == 1 and len(moving.solids().vals()) == 1
    assert fixed.val().isValid() and moving.val().isValid()
    for angle in range(0, 181, 15):
        rotated = moving.rotate((0, test_hy, SEAM), (1, test_hy, SEAM), angle)
        assert fixed.intersect(rotated).val().Volume() < 0.001, \
            f"Mechanism coupon interference {angle}"
    return compound(fixed, moving)


# Superseded tolerance samples are preserved at commit 1c6b8c3.
# Evaluate closure_trials.py for the current small closure experiments.


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
assert print_layout.BoundingBox().xlen < 260
assert print_layout.BoundingBox().ylen < 260
assert print_layout.BoundingBox().zlen < 250

if EXPORT:
    dest = Path(globals().get("__file__", "/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/sunglasses_case.py")).resolve().parent
    cq.exporters.export(print_layout, str(dest / "sunglasses_case.step"))
    cq.exporters.export(print_layout, str(dest / "sunglasses_case.stl"), tolerance=0.035, angularTolerance=0.1)
