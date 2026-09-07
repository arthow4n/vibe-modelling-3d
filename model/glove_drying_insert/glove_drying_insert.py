"""One glove: two folding frames, a snap-retained axle, and a cuff spreader.
Millimetres. Evaluate this file for the print layout; inspect.py for working pose.
"""
import math
from pathlib import Path
import cadquery as cq

# Fit starting points, NOT measured size-8 glove dimensions.
FRAME_LENGTH = 120.0                 # cuff edge to hinge axis
CUFF_WIDTH = 62.0
PALM_WIDTH = 44.0
RAIL = 6.0
CUFF_BAR = 12.0
THICKNESS = 3.2
OPEN_HALF_ANGLE = 11.0               # each frame; 22 degrees total
HINGE_RADIUS = 5.0
HINGE_HALF_WIDTH = 18.0
HINGE_INNER = 10.0
AXIAL_GAP = 0.4                     # each knuckle interface
BORE_RADIUS = 2.5
PIN_RADIUS = 2.1
PIN_SPLIT = 1.1
EDGE_BREAK = 0.4
SPREADER_THICKNESS = 4.0
SLOT_CLEARANCE = 0.3                # each face of frame
SNAP_OVERLAP = 0.10                 # per slot face at entry lips
HERE = Path(globals().get('__file__', '/home/hevar/git/vibe-modelling-3d/model/glove_drying_insert/glove_drying_insert.py')).resolve().parent


def box(x, y, z, at):
    return cq.Workplane('XY').box(x, y, z, centered=(True, True, False)).translate(at)


def frame(outer_knuckles=True):
    assert CUFF_WIDTH > 2*RAIL+20 and PALM_WIDTH >= 2*HINGE_HALF_WIDTH+6
    assert FRAME_LENGTH > 80 and THICKNESS > 2*EDGE_BREAK
    outline = [(-CUFF_WIDTH/2,0),(CUFF_WIDTH/2,0),(PALM_WIDTH/2,FRAME_LENGTH-8),(-PALM_WIDTH/2,FRAME_LENGTH-8)]
    p = cq.Workplane('XY').polyline(outline).close().extrude(THICKNESS).edges('|Z').fillet(3)
    inner = [(-CUFF_WIDTH/2+RAIL,CUFF_BAR),(CUFF_WIDTH/2-RAIL,CUFF_BAR),
             (PALM_WIDTH/2-RAIL,FRAME_LENGTH-16),(-PALM_WIDTH/2+RAIL,FRAME_LENGTH-16)]
    cut = cq.Workplane('XY').polyline(inner).close().extrude(THICKNESS).edges('|Z').fillet(3)
    p = p.cut(cut).edges('#Z').chamfer(EDGE_BREAK)
    for x in (-CUFF_WIDTH/2+12, CUFF_WIDTH/2-12):
        p = p.cut(cq.Workplane('XY').center(x,6).circle(2.5).extrude(THICKNESS))
    spans = [(-HINGE_HALF_WIDTH,-HINGE_INNER),(HINGE_INNER,HINGE_HALF_WIDTH)] if outer_knuckles else [(-HINGE_INNER+AXIAL_GAP,HINGE_INNER-AXIAL_GAP)]
    for lo,hi in spans:
        barrel = cq.Workplane('YZ',origin=(lo,FRAME_LENGTH,HINGE_RADIUS)).circle(HINGE_RADIUS).extrude(hi-lo)
        foot=cq.Workplane('YZ',origin=(lo,FRAME_LENGTH,0)).polyline([(-3,0),(3,0),(5,5),(-5,5)]).close().extrude(hi-lo)
        barrel=barrel.union(foot)
        web = box(hi-lo,12,THICKNESS,((lo+hi)/2,FRAME_LENGTH-6,0))
        p = p.union(barrel).union(web)
    # Circular bearing with a 45-degree roof: no horizontal bore ceiling.
    bore = cq.Workplane('YZ',origin=(-HINGE_HALF_WIDTH-1,FRAME_LENGTH,HINGE_RADIUS)).circle(BORE_RADIUS).extrude(2*HINGE_HALF_WIDTH+2)
    r=BORE_RADIUS
    roof = cq.Workplane('YZ',origin=(-HINGE_HALF_WIDTH-1,FRAME_LENGTH,HINGE_RADIUS)).polyline([(-r/2**.5,r/2**.5),(0,r*2**.5),(r/2**.5,r/2**.5)]).close().extrude(2*HINGE_HALF_WIDTH+2)
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


def placed_frames(angle=OPEN_HALF_ANGLE):
    a=frame(True).translate((0,0,-HINGE_RADIUS)).rotate((0,FRAME_LENGTH,0),(1,FRAME_LENGTH,0),angle)
    b=frame(False).rotate((0,0,HINGE_RADIUS),(0,1,HINGE_RADIUS),180).translate((0,0,-HINGE_RADIUS)).rotate((0,FRAME_LENGTH,0),(1,FRAME_LENGTH,0),-angle)
    return a,b


def spreader():
    """Built in working YZ pose. Twin slots snap over the cuff crossbars.
    Pull toward negative Y to remove; lips flex during installation/removal.
    """
    t=math.radians(OPEN_HALF_ANGLE)
    # Mid-plane of the lower frame as a function of working Y.
    def lower(y):
        return (y-FRAME_LENGTH)*math.tan(t)+(THICKNESS/2-HINGE_RADIUS)/math.cos(t)
    reach=abs(lower(-5))+6
    pocket_end=FRAME_LENGTH+(CUFF_BAR-FRAME_LENGTH)*math.cos(t)+HINGE_RADIUS*math.sin(t)+.45
    mouth_end=pocket_end+4
    p=cq.Workplane('YZ',origin=(-SPREADER_THICKNESS/2,(mouth_end-6)/2,0)).rect(mouth_end+6,2*reach).extrude(SPREADER_THICKNESS).edges('|X').fillet(2)
    for sign in (-1,1):
        # Wider pocket behind narrow flexible lips; flared entry guides the bar.
        ys=[-1,pocket_end,pocket_end,pocket_end+1.4,mouth_end+.5]
        widths=[THICKNESS/2+SLOT_CLEARANCE,THICKNESS/2+SLOT_CLEARANCE,
                THICKNESS/2-SNAP_OVERLAP,THICKNESS/2-SNAP_OVERLAP,THICKNESS/2+1.0]
        center=lambda y: sign*lower(y)
        top=[(y,center(y)+w/math.cos(t)) for y,w in zip(ys,widths)]
        bottom=[(y,center(y)-w/math.cos(t)) for y,w in reversed(list(zip(ys,widths)))]
        tool=cq.Workplane('YZ',origin=(-4,0,0)).polyline(top+bottom).close().extrude(8)
        p=p.cut(tool)
    # Tether hole: optional cord can keep the removable part with a frame.
    p=p.cut(cq.Workplane('YZ',origin=(-4,-2,0)).circle(2).extrude(8))
    return p.faces('>X or <X').edges().chamfer(.25)


def bed(shape):
    b=shape.val().BoundingBox()
    return shape.translate((0,0,-b.zmin))


def print_parts():
    a=frame(True)
    b=frame(False).translate((CUFF_WIDTH+12,0,0))
    pin=axle().translate((10,-14,0))
    s=bed(spreader().rotate((0,0,0),(0,1,0),90)).translate((CUFF_WIDTH+12,-30,0))
    return [a,b,pin,s]


def compound(parts):
    return cq.Compound.makeCompound([p.val() for p in parts])


def assembled(angle=OPEN_HALF_ANGLE, with_spreader=True):
    a,b=placed_frames(angle)
    pin=axle().translate((0,FRAME_LENGTH,-1.7))
    parts=[a,b,pin]
    if with_spreader:
        parts.append(spreader())
    return parts


result=compound(print_parts())
