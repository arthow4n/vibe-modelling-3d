"""Sunglasses case, mm. Evaluate this file with the CadQuery MCP.

PETG, 0.4 mm nozzle; 260 mm build volume confirmed.
Captive bulbed spindle: no separate pin, nuts or assembly.
Print the connected assembly open 180 degrees, hinge axis vertical.
Accessible shell supports may be needed; exclude bearing gaps from supports.
"""
from pathlib import Path
import cadquery as cq

GLASSES_WIDTH = 160.0
GLASSES_DEPTH = 80.0
GLASSES_HEIGHT = 60.0
CLEARANCE = 4.0  # each side, includes allowance for 1 mm soft lining
WALL = 3.0
FLOOR = 3.0
CORNER = 7.0
HINGE_RADIUS = 6.2
AXLE_RADIUS = 2.4
BULB_RADIUS = 4.4
RADIAL_GAP = 0.5  # per side, not diametral
AXIAL_GAP = 0.3  # additional allowance on the conical bearing ends
LATCH_THICKNESS = 1.6
LAYOUT = "closed"  # closed / open / print / coupon / hinge_section
EXPORT = True

IW = GLASSES_WIDTH + 2 * CLEARANCE
ID = GLASSES_DEPTH + 2 * CLEARANCE
IH = GLASSES_HEIGHT + 2 * CLEARANCE
OW, OD = IW + 2 * WALL, ID + 2 * WALL
HEIGHT = IH + 2 * FLOOR
SEAM = HEIGHT / 2
HY = OD / 2 + HINGE_RADIUS + 0.8
BEARING_CENTERS = (-OW/2 + 52, OW/2 - 52)
ANCHOR_END = OW/2 - 10
assert CLEARANCE >= 3 and WALL >= 2.4 and IH >= 40
assert OW > 140 and ID > 60


def block(x, y, z, dx, dy, dz):
    return cq.Workplane("XY").box(dx, dy, dz).translate((x, y, z))


def rounded(w, d, h, z, radius):
    return (cq.Workplane("XY").box(w, d, h, centered=(True, True, False))
            .edges("|Z").fillet(radius).translate((0, 0, z)))


def half():
    outer = rounded(OW, OD, SEAM, 0, CORNER)
    outer = outer.edges("<Z").chamfer(0.6)
    cavity = rounded(IW, ID, SEAM, FLOOR, CORNER - WALL)
    return outer.cut(cavity).edges(">Z").chamfer(0.3)


def turned(profile):
    """Solid of revolution about X, shifted to the hinge axis."""
    return (cq.Workplane("XY").polyline(profile).close()
            .revolve(360, (0, 0), (1, 0)).translate((0, HY, SEAM)))


def ear(start, end, lid_side=False):
    """Bearing exterior with two 45-degree underside cuts in print direction X.

    The ear grows from its shell wall before surrounding the vertical axle.
    This avoids starting a complete annulus in mid-air. Bore is cut afterward.
    """
    side = 1 if lid_side else -1
    wall_y = HY + side * (HINGE_RADIUS + 0.8)
    barrel = cq.Workplane("YZ", origin=(start, HY, SEAM)).circle(HINGE_RADIUS).extrude(end-start)
    web = block((start+end)/2, (HY+wall_y)/2, SEAM-2.5,
                end-start, abs(wall_y-HY)+2, 5)
    part = barrel.union(web)
    m = 500
    slope = -side
    # Remove X < start + slope * (Y - wall_y).
    under_y = (cq.Workplane("XY", origin=(0, 0, -m))
               .polyline([(start+slope*(-m-wall_y), -m),
                          (start+slope*(m-wall_y), m), (-m, m), (-m, -m)])
               .close().extrude(2*m))
    # Also grow the upper half of the circle upward from the web at 45 degrees.
    under_z = (cq.Workplane("XZ", origin=(0, m, 0))
               .polyline([(start-m-(SEAM-5), -m),
                          (start+m-(SEAM-5), m), (-m, m), (-m, -m)])
               .close().extrude(2*m))
    return part.cut(under_y).cut(under_z).edges(">X").chamfer(0.3)


def spindle(start, end, centers):
    profile = [(start, 0), (start, AXLE_RADIUS)]
    for c in centers:
        run = BULB_RADIUS - AXLE_RADIUS  # 45-degree cones in print orientation
        profile += [(c-1-run, AXLE_RADIUS), (c-1, BULB_RADIUS),
                    (c+1, BULB_RADIUS), (c+1+run, AXLE_RADIUS)]
    profile += [(end, AXLE_RADIUS), (end, 0)]
    return turned(profile)


def bearing(c):
    start, end = c-21, c+7
    run = BULB_RADIUS - AXLE_RADIUS
    neck, wide = AXLE_RADIUS+RADIAL_GAP, BULB_RADIUS+RADIAL_GAP
    # Widened internal cavity captures the bulb behind two narrower necks.
    # Both transitions are 45 degrees, with explicit radial and axial gaps.
    bore = turned([(start-0.1, 0), (start-0.1, neck),
                   (c-1-run-AXIAL_GAP, neck), (c-1-AXIAL_GAP, wide),
                   (c+1+AXIAL_GAP, wide), (c+1+run+AXIAL_GAP, neck),
                   (end+0.1, neck), (end+0.1, 0)])
    return ear(start, end, lid_side=True).cut(bore)


body = half()
# Build both halves open, sharing the same floor level, then close the lid.
open_lid = half().translate((0, 2*HY, 0))
body = body.union(ear(-ANCHOR_END, -ANCHOR_END+16))
body = body.union(ear(ANCHOR_END-16, ANCHOR_END))
body = body.union(spindle(-ANCHOR_END+14, ANCHOR_END-2, BEARING_CENTERS))
for center in BEARING_CENTERS:
    open_lid = open_lid.union(bearing(center))
lid = open_lid.rotate((0, HY, SEAM), (1, HY, SEAM), 180)

# Front keeper: horizontal underside carries opening load; sloped top cams
# the latch outward during closing. Y is negative on the front of the case.
front = -OD/2
keeper = (cq.Workplane("YZ", origin=(-8, 0, 0))
          .polyline([(front+0.3, SEAM-5), (front-1.8, SEAM-5),
                     (front-1.8, SEAM-3.5), (front, SEAM-1)])
          .close().extrude(16))
body = body.union(keeper)

# Long PETG leaf: lift the bottom tab outward, then lift the lid.
inner = front - 2.4
leaf_bottom, leaf_top = SEAM-10, SEAM+15
leaf = block(0, inner-LATCH_THICKNESS/2, (leaf_bottom+leaf_top)/2,
             20, LATCH_THICKNESS, leaf_top-leaf_bottom).edges("|Y").fillet(0.7)
root = block(0, front-1.2, leaf_top-1.6, 20, 5.6, 3.2).edges("|Z").fillet(0.6)
hook = (cq.Workplane("YZ", origin=(-7, 0, 0))
        .polyline([(inner-0.2, SEAM-8.8), (front-0.4, SEAM-5.6),
                   (inner-0.2, SEAM-5.6)]).close().extrude(14))
grip = block(0, inner-LATCH_THICKNESS-0.6, leaf_bottom+1.4,
             18, 1.8, 2.8).edges("|X").fillet(0.6)
lid = lid.union(leaf).union(root).union(hook).union(grip)

def compound(*parts):
    return cq.Compound.makeCompound([p.val() for p in parts])


def opening(angle):
    return lid.rotate((0, HY, SEAM), (1, HY, SEAM), -angle)


def standing(part):
    # X becomes print Z; short end X=-OW/2 is on the bed.
    return part.rotate((0, 0, 0), (0, 1, 0), -90).translate((SEAM, OD/2, OW/2))


closed = compound(body, lid)
opened = compound(body, opening(110))
print_body, print_lid = standing(body), standing(opening(180))
print_layout = compound(print_body, print_lid)
# Small print-in-place clearance coupon using the exact same bearing profile.
# Separate feet provide bed contact; neither foot bridges the moving clearance.
def hinge_coupon():
    low, high = -37.0, 26.0
    fixed_wall_y, moving_wall_y = OD/2-1.5, 2*HY-OD/2+1.5
    fixed = block((low+high)/2, fixed_wall_y, SEAM-3, high-low, 3, 6)
    moving = block((low+high)/2, moving_wall_y, SEAM-3, high-low, 3, 6)
    fixed = fixed.union(block(low+1.5, fixed_wall_y-1, SEAM-5.5, 3, 8, 9))
    moving = moving.union(block(low+1.5, moving_wall_y+1, SEAM-5.5, 3, 8, 9))
    pin = spindle(low+14, high-2, (0,))
    fixed = fixed.union(ear(low, low+16)).union(ear(high-16, high)).union(pin)
    moving = moving.union(bearing(0))
    assert len(fixed.solids().vals()) == len(moving.solids().vals()) == 1, "Coupon disconnected"
    assert fixed.val().isValid() and moving.val().isValid(), "Coupon invalid"
    assert fixed.intersect(moving).val().Volume() < 0.001, "Coupon initial interference"
    for angle in range(0, 181, 15):
        rotated = moving.rotate((0, HY, SEAM), (1, HY, SEAM), angle)
        assert fixed.intersect(rotated).val().Volume() < 0.001, f"Coupon sweep interference {angle}"
    # Verify both cone shoulders prevent the bearing sliding along the spindle.
    for shift in (-1.5, 1.5):
        assert pin.intersect(bearing(0).translate((shift, 0, 0))).val().Volume() > 0.01, "Coupon not captive"
    parts = [part.rotate((0, 0, 0), (0, 1, 0), -90)
             .translate((SEAM, -HY, -low)) for part in (fixed, moving)]
    return compound(*parts)


coupon = hinge_coupon()
hinge_section = cq.Workplane(obj=coupon).intersect(block(10, 0, 31.5, 20, 60, 80))
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
# Enlarged bulbs cannot pass through either end of the bearing bores.
assert BULB_RADIUS > AXLE_RADIUS + RADIAL_GAP + 1.0
assert HINGE_RADIUS - (BULB_RADIUS+RADIAL_GAP) >= 1.2
assert abs(print_body.val().BoundingBox().zmin) < 0.02
assert abs(print_lid.val().BoundingBox().zmin) < 0.02
assert max(print_layout.BoundingBox().xlen, print_layout.BoundingBox().ylen,
           print_layout.BoundingBox().zlen) < 260

if EXPORT:
    dest = Path(globals().get("__file__", "/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/sunglasses_case.py")).resolve().parent
    cq.exporters.export(closed, str(dest / "sunglasses_case.step"))
    cq.exporters.export(print_layout, str(dest / "sunglasses_case.stl"), tolerance=0.035, angularTolerance=0.1)
    cq.exporters.export(coupon, str(dest / "hinge_test.stl"), tolerance=0.035, angularTolerance=0.1)
