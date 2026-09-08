"""Five-finger folding glove insert. Millimetres; one four-part kit per glove.
Two slotted hand skeletons separate through the thickness of every digit.
Evaluate this source with CadQuery MCP for the print layout.
"""
import math
from pathlib import Path
import cadquery as cq

# General adult/size-8 starting fit; deliberately narrow fingers, not an anatomical cast.
HAND_SCALE = 1.0                    # scales only the hand outline, not hinge/clearance
FINGER_LENGTH_SCALE = 1.0          # independently lengthen all finger branches
FINGER_WIDTH_SCALE = 1.0
OPEN_HALF_ANGLE = 1.0               # 2 degrees between the panels
THICKNESS = 3.2
RAIL = 5.0
FINGER_RAIL = 2.6
CUFF_START = 12.0
CUFF_END = 24.0
BRACE_START = 34.0
BRACE_END = 42.0
HINGE_RADIUS = 5.0
HINGE_HALF_WIDTH = 18.0
HINGE_INNER = 10.0
AXIAL_GAP = 0.4
BORE_RADIUS = 2.5
PIN_RADIUS = 2.1
PIN_SPLIT = 1.1
EDGE_BREAK = .35
SPREADER_THICKNESS = 4.0
SLOT_CLEARANCE = .3
SNAP_OVERLAP = .1
# Start/end centerlines and widths. Thumb is a separate angled branch.
DIGITS = {
    'index': ((-27.,101.),(-28.,192.),12.),
    'middle': ((-9.,112.),(-9.,204.),13.),
    'ring': ((9.,110.),(11.,193.),12.),
    'little': ((27.,94.),(32.,166.),10.5),
    'thumb': ((-29.,60.),(-65.,121.),12.),
}
HERE=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/glove_drying_insert.py')).resolve().parent


def box(x,y,z,at):
    return cq.Workplane('XY').box(x,y,z,centered=(True,True,False)).translate(at)


def capsule(start,end,width):
    dx,dy=end[0]-start[0],end[1]-start[1]
    length=math.hypot(dx,dy)
    return cq.Workplane('XY').center((start[0]+end[0])/2,(start[1]+end[1])/2).slot2D(length+width,width,math.degrees(math.atan2(dy,dx))).extrude(THICKNESS)


def digit_dimensions():
    result={}
    for name,(root,tip,w) in DIGITS.items():
        start=tuple(v*HAND_SCALE for v in root)
        end=tuple((root[i]+(tip[i]-root[i])*FINGER_LENGTH_SCALE)*HAND_SCALE for i in (0,1))
        result[name]=(start,end,w*FINGER_WIDTH_SCALE)
    return result


def hand_outline():
    assert .85 <= HAND_SCALE <= 1.1
    assert .85 <= FINGER_LENGTH_SCALE <= 1.15
    assert .85 <= FINGER_WIDTH_SCALE <= 1.15
    assert .5 <= OPEN_HALF_ANGLE <= 1.7
    outline=[(-25,12),(25,12),(36,92),(30,104),(11,118),(-10,121),(-32,111),(-36,88)]
    outline=[(x*HAND_SCALE,max(CUFF_START,y*HAND_SCALE)) for x,y in outline]
    p=cq.Workplane('XY').polyline(outline).close().extrude(THICKNESS).edges('|Z').fillet(4)
    # A continuous open palm; two struts at its sides carry the five branches.
    inner=[(-19,CUFF_END),(19,CUFF_END),(29,86),(22,95),(-22,99),(-29,82)]
    inner=[(x*HAND_SCALE,y if y==CUFF_END else y*HAND_SCALE) for x,y in inner]
    window=cq.Workplane('XY').polyline(inner).close().extrude(THICKNESS).edges('|Z').fillet(4)
    p=p.cut(window).edges('#Z').chamfer(EDGE_BREAK)
    crossbar=box(52*HAND_SCALE,BRACE_END-BRACE_START,THICKNESS,(0,(BRACE_START+BRACE_END)/2,0)).edges('|Z').fillet(1).edges('#Z').chamfer(EDGE_BREAK)
    p=p.union(crossbar)
    for start,end,width in digit_dimensions().values():
        assert width > 2*FINGER_RAIL+2
        finger=capsule(start,end,width).cut(capsule(start,end,width-2*FINGER_RAIL))
        finger=finger.edges('#Z').chamfer(EDGE_BREAK)
        p=p.union(finger)
    for x in (-15,15):
        p=p.cut(cq.Workplane('XY').center(x,18).circle(2.5).extrude(THICKNESS))
    return p


def frame(outer_knuckles=True):
    p=hand_outline()
    # The second print is mirrored so flipping it produces aligned thumb/fingers.
    if not outer_knuckles:
        p=p.mirror('YZ',union=False)
    spans=[(-18,-10),(10,18)] if outer_knuckles else [(-HINGE_INNER+AXIAL_GAP,HINGE_INNER-AXIAL_GAP)]
    for lo,hi in spans:
        barrel=cq.Workplane('YZ',origin=(lo,0,HINGE_RADIUS)).circle(HINGE_RADIUS).extrude(hi-lo)
        foot=cq.Workplane('YZ',origin=(lo,0,0)).polyline([(-3,0),(3,0),(5,5),(-5,5)]).close().extrude(hi-lo)
        web=box(hi-lo,15,THICKNESS,((lo+hi)/2,7.5,0))
        p=p.union(barrel).union(foot).union(web)
    bore=cq.Workplane('YZ',origin=(-19,0,HINGE_RADIUS)).circle(BORE_RADIUS).extrude(38)
    r=BORE_RADIUS
    roof=cq.Workplane('YZ',origin=(-19,0,HINGE_RADIUS)).polyline([(-r/2**.5,r/2**.5),(0,r*2**.5),(r/2**.5,r/2**.5)]).close().extrude(38)
    return p.cut(bore.union(roof))


def axle():
    """Horizontal print: split tip flexes in XY, along continuous filament paths."""
    h=HINGE_HALF_WIDTH
    z=1.7
    p=cq.Workplane('YZ',origin=(-h-1,0,z)).circle(PIN_RADIUS).extrude(2*h+2)
    head=cq.Workplane('YZ',origin=(-h-4,0,z)).circle(3.4).extrude(3)
    # Rounded planar arrow, shoulder outside the last bearing.
    pts=[(h-8,-PIN_RADIUS),(h+1,-PIN_RADIUS),(h+1,-2.8),(h+2,-2.8),(h+9,-1.2),
         (h+9,1.2),(h+2,2.8),(h+1,2.8),(h+1,PIN_RADIUS),(h-8,PIN_RADIUS)]
    tip=cq.Workplane('XY').polyline(pts).close().extrude(3.4).faces('>Z or <Z').edges().chamfer(.8)
    p=p.union(head).union(tip)
    p=p.intersect(box(120,30,10,(0,0,0)))
    split=box(20,PIN_SPLIT,10,(h+3,0,-1))
    # Round the slit root to reduce its stress concentration.
    split=split.union(cq.Workplane('XY').center(h-7,0).circle(PIN_SPLIT/2).extrude(8))
    envelope=cq.Workplane('YZ',origin=(-h-1,0,z)).circle(PIN_RADIUS).extrude(2*h+1.5)
    envelope=envelope.union(box(20,20,10,(h+10.5,0,0))).union(box(10,20,10,(-h-6,0,0)))
    return p.cut(split).intersect(envelope)


def placed_frames(angle=None):
    if angle is None: angle=OPEN_HALF_ANGLE
    a=frame(True).translate((0,0,-HINGE_RADIUS)).rotate((0,0,0),(1,0,0),-angle)
    b=frame(False).rotate((0,0,HINGE_RADIUS),(0,1,HINGE_RADIUS),180).translate((0,0,-HINGE_RADIUS)).rotate((0,0,0),(1,0,0),angle)
    return a,b


def spreader():
    """Cuff-accessible slotted brace; its lips catch the far edge of both cuff bars."""
    t=math.radians(OPEN_HALF_ANGLE)
    lower=lambda y: -y*math.tan(t)+(THICKNESS/2-HINGE_RADIUS)/math.cos(t)
    pocket_end=BRACE_END*math.cos(t)-(HINGE_RADIUS-THICKNESS)*math.sin(t)+.45
    mouth_end=pocket_end+4
    start=BRACE_START-4
    reach=abs(lower(mouth_end))+4.5
    p=cq.Workplane('YZ',origin=(-SPREADER_THICKNESS/2,(start+mouth_end)/2,0)).rect(mouth_end-start,2*reach).extrude(SPREADER_THICKNESS).edges('|X').fillet(1.5)
    for sign in (-1,1):
        ys=[BRACE_START-1,pocket_end,pocket_end,pocket_end+1.4,mouth_end+.5]
        widths=[THICKNESS/2+SLOT_CLEARANCE,THICKNESS/2+SLOT_CLEARANCE,THICKNESS/2-SNAP_OVERLAP,THICKNESS/2-SNAP_OVERLAP,THICKNESS/2+1]
        top=[(y,sign*lower(y)+w/math.cos(t)) for y,w in zip(ys,widths)]
        bottom=[(y,sign*lower(y)-w/math.cos(t)) for y,w in reversed(list(zip(ys,widths)))]
        p=p.cut(cq.Workplane('YZ',origin=(-4,0,0)).polyline(top+bottom).close().extrude(8))
    # Small tether eye through the central web between the two slots.
    p=p.cut(cq.Workplane('YZ',origin=(-4,BRACE_START-2,0)).circle(1.2).extrude(8))
    return p.faces('>X or <X').edges().chamfer(.2)


def bed(shape):
    return shape.translate((0,0,-shape.val().BoundingBox().zmin))


def print_parts():
    a=frame(True)
    b=frame(False)
    ab=a.val().BoundingBox();bb=b.val().BoundingBox()
    b=b.translate((ab.xmax-bb.xmin+12,0,0))
    pin=axle().translate((0,-17,0))
    s=bed(spreader().rotate((0,0,0),(0,1,0),90)).translate((55,-55,0))
    return [a,b,pin,s]


def compound(parts):
    return cq.Compound.makeCompound([p.val() for p in parts])


def assembled(angle=None,with_spreader=True):
    a,b=placed_frames(angle)
    parts=[a,b,axle().translate((0,0,-1.7))]
    if with_spreader: parts.append(spreader())
    return parts


result=compound(print_parts())
