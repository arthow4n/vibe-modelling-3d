"""50 x 25 mm scalloped screw jar. Millimetres; result is print placement."""
import cadquery as cq
import math

OUTER_DIAMETER = 50.0
CLOSED_HEIGHT = 25.0
BASE_HEIGHT = 15.0
FLOOR = 2.0
LID_ROOF = 2.0
NECK_RADIUS = 21.0
OPENING_RADIUS = 19.0
RADIAL_CLEARANCE = 0.30
AXIAL_CLEARANCE = 0.25
THREAD_PITCH = 3.0
THREAD_DEPTH = 1.0
THREAD_HALF_WIDTH = 1.0
THREAD_START = 16.6
THREAD_TRAVEL = 4.5
GRIP_COUNT = 12
GRIP_CUT_RADIUS = 7.0
GRIP_DEPTH = 1.5
EDGE_RADIUS = 0.65
PART_SPACING = 58.0


def grip(height):
    body = cq.Workplane('XY').circle(OUTER_DIAMETER / 2).extrude(height)
    centres = [( (OUTER_DIAMETER/2 + GRIP_CUT_RADIUS-GRIP_DEPTH)*math.cos(i*2*math.pi/GRIP_COUNT),
                 (OUTER_DIAMETER/2 + GRIP_CUT_RADIUS-GRIP_DEPTH)*math.sin(i*2*math.pi/GRIP_COUNT)) for i in range(GRIP_COUNT)]
    body = body.cut(cq.Workplane('XY').pushPoints(centres).circle(GRIP_CUT_RADIUS).extrude(height))
    body = body.edges('|Z').fillet(1.0)
    body = body.faces('>Z').edges().fillet(EDGE_RADIUS)
    return body.faces('<Z').edges().chamfer(0.35)


def thread(clearance=False):
    # Symmetric 45-degree flanks; wider cutter provides radial and axial fit.
    extra = RADIAL_CLEARANCE if clearance else 0.0
    half = THREAD_HALF_WIDTH + (AXIAL_CLEARANCE + extra if clearance else 0)
    root = NECK_RADIUS - 0.12
    tip = NECK_RADIUS + THREAD_DEPTH + extra
    lead = THREAD_PITCH if clearance else 0.0
    path = cq.Wire.makeHelix(THREAD_PITCH, THREAD_TRAVEL + lead, NECK_RADIUS)
    profile = cq.Workplane('XZ').polyline([(root,-half),(tip,0),(root,half)]).close()
    return profile.sweep(cq.Workplane(obj=path), isFrenet=True).translate((0,0,THREAD_START-lead))


def build():
    assert CLOSED_HEIGHT > BASE_HEIGHT + LID_ROOF + THREAD_PITCH
    neck_top = CLOSED_HEIGHT-LID_ROOF-0.25
    base = grip(BASE_HEIGHT)
    neck = cq.Workplane('XY').workplane(offset=BASE_HEIGHT-0.1).circle(NECK_RADIUS).extrude(neck_top-BASE_HEIGHT+0.1)
    neck = neck.faces('>Z').edges().chamfer(0.4)
    base = base.union(neck).union(thread())
    pocket = cq.Workplane('XY').workplane(offset=FLOOR).circle(OPENING_RADIUS).extrude(CLOSED_HEIGHT)
    pocket = pocket.faces('<Z').edges().fillet(2.0)
    base = base.cut(pocket)
    # Round the mouth edge selected by radius and height.
    mouth = [e for e in base.val().Edges() if e.geomType() == 'CIRCLE' and abs(e.Center().z-neck_top)<0.01 and abs(e.radius()-OPENING_RADIUS)<0.01]
    base = base.newObject(mouth).fillet(0.45)
    lid = grip(CLOSED_HEIGHT-BASE_HEIGHT).translate((0,0,BASE_HEIGHT))
    bore = cq.Workplane('XY').workplane(offset=BASE_HEIGHT-1).circle(NECK_RADIUS+RADIAL_CLEARANCE).extrude(CLOSED_HEIGHT-LID_ROOF-BASE_HEIGHT+1)
    lid = lid.cut(bore).cut(thread(True))
    assert len(base.solids().vals()) == len(lid.solids().vals()) == 1
    assert base.val().isValid() and lid.val().isValid()
    return base, lid

base, lid = build()
print_lid = lid.rotate((0,0,0),(1,0,0),180).translate((PART_SPACING,0,CLOSED_HEIGHT))
result = cq.Compound.makeCompound([base.val(), print_lid.val()])
