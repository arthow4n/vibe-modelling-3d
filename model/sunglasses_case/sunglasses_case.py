"""Sunglasses case, mm. Evaluate this file with the CadQuery MCP.

PETG, 0.4 mm nozzle. Body prints floor down; lid prints roof down.
Hinge: M3 x 150 mm threaded rod, two washers and two locknuts.
Source builds closed, open and print layouts; exports are derived here.
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
HINGE_RADIUS = 4.5
PIN_HOLE = 3.6  # diameter; M3 hardware, trial fit before assembly
HINGE_GAP = 0.5  # axial gap between knuckles
LATCH_THICKNESS = 1.6
LAYOUT = "closed"  # closed / open / print / body / lid
EXPORT = True

IW = GLASSES_WIDTH + 2 * CLEARANCE
ID = GLASSES_DEPTH + 2 * CLEARANCE
IH = GLASSES_HEIGHT + 2 * CLEARANCE
OW, OD = IW + 2 * WALL, ID + 2 * WALL
HEIGHT = IH + 2 * FLOOR
SEAM = HEIGHT / 2
HY = OD / 2 + HINGE_RADIUS + 0.5
HX = OW / 2 - 19
KN = 20.0
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


def knuckle(x0, x1, upper=False):
    barrel = cq.Workplane("YZ", origin=(x0, HY, SEAM)).circle(HINGE_RADIUS).extrude(x1-x0)
    # Broad accessible web; support below external hinge only when slicing.
    web = block((x0+x1)/2, OD/2+0.8, SEAM+(3 if upper else -3),
                x1-x0, 5.6, 6)
    bore = cq.Workplane("YZ", origin=(x0-0.1, HY, SEAM)).circle(PIN_HOLE/2).extrude(x1-x0+0.2)
    return barrel.union(web).cut(bore)


body = half()
lid = half().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, HEIGHT))
for a, b in [(-HX, -HX+KN), (HX-KN, HX)]:
    body = body.union(knuckle(a, b))
for a, b in [(-HX+KN+HINGE_GAP, -HX+2*KN+HINGE_GAP),
             (HX-2*KN-HINGE_GAP, HX-KN-HINGE_GAP)]:
    lid = lid.union(knuckle(a, b, upper=True))

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

closed = cq.Compound.makeCompound([body.val(), lid.val()])
lid_open = lid.rotate((0, HY, SEAM), (1, HY, SEAM), -110)
opened = cq.Compound.makeCompound([body.val(), lid_open.val()])
lid_print = lid.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, HEIGHT))
print_layout = cq.Compound.makeCompound([body.val(), lid_print.translate((OW+12, 0, 0)).val()])
result = {"closed": closed, "open": opened, "print": print_layout,
          "body": body, "lid": lid_print}[LAYOUT]

# Geometry checks run on every evaluation. Contact at the seam is intended.
assert len(body.solids().vals()) == 1 and body.val().isValid()
assert len(lid.solids().vals()) == 1 and lid.val().isValid()
assert body.intersect(lid).val().Volume() < 0.001, "Closed parts interfere"
fit_envelope = block(0, 0, HEIGHT/2, GLASSES_WIDTH, GLASSES_DEPTH, GLASSES_HEIGHT)
assert body.intersect(fit_envelope).val().Volume() < 0.001
assert lid.intersect(fit_envelope).val().Volume() < 0.001
for angle in range(5, 111, 5):
    # Latch must be manually flexed clear during the first few degrees.
    moving = lid.rotate((0, HY, SEAM), (1, HY, SEAM), -angle)
    if angle >= 20:
        assert body.intersect(moving).val().Volume() < 0.001, "Hinge sweep interferes"

if EXPORT:
    dest = Path(globals().get("__file__", "/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/sunglasses_case.py")).resolve().parent
    cq.exporters.export(closed, str(dest / "sunglasses_case.step"))
    cq.exporters.export(print_layout, str(dest / "sunglasses_case.stl"), tolerance=0.05, angularTolerance=0.1)
    for name, part in [("body", body), ("lid", lid_print)]:
        cq.exporters.export(part, str(dest / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1)
