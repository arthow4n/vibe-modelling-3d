"""Full S16 retrofit for the printed narrow M1. Millimetres; Z follows brush.

Nested cavity envelopes preserve skins around the sleeve and fixed catch guards.
Perimeter-normal ribs follow curved and concave boundaries as well as flat walls.
No rigid-box geometry is changed. Builders have no publication side effects.
"""
from functools import cache
import math
import cadquery as cq
from model.dental_travel_case.m1_design import D, rounded_wire, build

BACKING, CORE, SKIN = .4, .8, .4
THICKNESS = BACKING + CORE + SKIN
WEB, PITCH = .9, 4.4
ALLOWANCE = .2
END_GAP = .2
SLEEVE_LINER_RADIUS = 3.0  # enlarge inside the shell to keep a real corner core
BODY_TOP = D.seam + D.lap - .4
CAP_START = D.seam + D.lap + .4
GUARD_X = D.beam_outer-D.beam_thickness-(D.release+.3)-1.2
GUARD_Y = D.beam_width/2+2.8
GUARD_START = D.beam_root-10
GUARD_END = D.beam_root-2


def box(x, y, z, w, h, depth):
    return cq.Workplane('XY').box(w,h,depth,centered=(True,True,False)).translate((x,y,z))


def profile(w,h,r,z):
    return rounded_wire(w,h,max(.15,r),z)


def loft(rows):
    return cq.Workplane(obj=cq.Solid.makeLoft([profile(*row) for row in rows],ruled=True))


def guard(inset):
    """Conservative clearance from the complete ramp and closed leaf guards."""
    # Extend the diagonal keep-out along its normal; the liner grows inward
    # gradually in print Z, rather than starting a floating horizontal shelf.
    slope=(D.width/2-D.wall-GUARD_X)/(GUARD_END-GUARD_START)
    normal_factor=math.sqrt(1+slope*slope)
    start=GUARD_START-10
    # Extend the SAME diagonal until it is outside the complete cavity.
    # Starting an offset cutter at an interior X creates an abrupt shelf and
    # a new inner-skin extrusion with no layer underneath it.
    x0=GUARD_X+slope*(GUARD_END-start)-(ALLOWANCE+inset)*normal_factor
    x1=GUARD_X-ALLOWANCE-inset
    end=GUARD_END-(ALLOWANCE+inset)*(normal_factor-1)/slope
    cuts=[]
    for sign in (-1,1):
        cut=(cq.Workplane('XZ',origin=(0,GUARD_Y+ALLOWANCE+inset,0))
             .polyline([(x0,start),(50,start),(50,BODY_TOP+5),
                        (x1,BODY_TOP+5),(x1,end)])
             .close().extrude(2*(GUARD_Y+ALLOWANCE+inset)))
        cuts.append((cut if sign==1 else cut.mirror('YZ')).val())
    return cq.Workplane(obj=cq.Compound.makeCompound(cuts))


def envelope(part, inset):
    """Filled contents-side envelope, not printable geometry."""
    if part == 'body':
        w,h,r = D.width-2*D.wall-2*ALLOWANCE,D.depth-2*D.wall-2*ALLOWANCE,D.corner-D.wall-ALLOWANCE
        upper = (D.sleeve_width-2*D.lap_wall-2*ALLOWANCE,
                 D.sleeve_depth-2*D.lap_wall-2*ALLOWANCE,
                 max(SLEEVE_LINER_RADIUS,D.sleeve_corner-D.lap_wall-ALLOWANCE))
        rows=[(w-4-2*inset,h-4-2*inset,r-2-inset,D.floor+END_GAP+inset),
              (w-2*inset,h-2*inset,r-inset,D.floor+END_GAP+2+inset),
              (w-2*inset,h-2*inset,r-inset,D.seam-6),
              (upper[0]-2*inset,upper[1]-2*inset,upper[2]-inset,D.seam),
              (upper[0]-2*inset,upper[1]-2*inset,upper[2]-inset,BODY_TOP+1)]
        return loft(rows).cut(guard(inset))
    if part == 'cap':
        # Coordinates remain assembled, then flip for printing.
        w,h,r=D.width-2*D.wall-2*ALLOWANCE,D.depth-2*D.wall-2*ALLOWANCE,D.corner-D.wall-ALLOWANCE
        wr,hr,rr=D.width-2*D.receiver_wall-2*ALLOWANCE,D.depth-2*D.receiver_wall-2*ALLOWANCE,D.corner-D.receiver_wall-ALLOWANCE
        return loft([(wr-2*inset,hr-2*inset,rr-inset,CAP_START-1),
                     (wr-2*inset,hr-2*inset,rr-inset,D.seam+20),
                     (w-2*inset,h-2*inset,r-inset,D.seam+24),
                     (w-2*inset,h-2*inset,r-inset,D.length-D.floor-END_GAP-2-inset),
                     (w-4-2*inset,h-4-2*inset,r-2-inset,D.length-D.floor-END_GAP-inset)])
    raise ValueError(part)


def section_wire(shape,z):
    section=shape.section(z).val()
    wires=section.Wires()
    if len(wires)!=1:
        raise ValueError(f'Expected one envelope perimeter at {z}: {len(wires)}')
    return wires[0]


def rib_mask(wire, bottom, top):
    """Short normal ribs at <=4.4 mm pitch, including every rounded bend.

    Equal perimeter spacing slightly tightens pitch to avoid an oversized last
    gap. Rib strips project through the .8 mm core and are clipped by it.
    """
    length=wire.Length()
    count=math.ceil(length/PITCH)
    ribs=[]
    for i in range(count):
        p=wire.positionAt(i/count)
        t=wire.tangentAt(i/count)
        angle=math.degrees(math.atan2(t.y,t.x))
        rib=box(0,0,bottom,WEB,6,top-bottom).rotate((0,0,0),(0,0,1),angle).translate((p.x,p.y,0))
        ribs.append(rib.val())
    return cq.Workplane(obj=cq.Compound.makeCompound(ribs))


@cache
def cup(part):
    if part not in ('body','cap'):
        raise ValueError(part)
    outer=envelope(part,0)
    inner=envelope(part,THICKNESS)
    if part=='body':
        lo,hi=D.floor+END_GAP,BODY_TOP
        zones=((6.,GUARD_START-.4,10.),
               (GUARD_START-.4,GUARD_END+.4,137.),
               (GUARD_END+.4,D.seam-6,150.),
               (D.seam-6,D.seam,170.),
               (D.seam,BODY_TOP-SKIN,180.))
    else:
        lo,hi=CAP_START,D.length-D.floor-END_GAP
        zones=((CAP_START+SKIN,D.seam+20,190.),
               (D.seam+20,D.seam+24,196.),
               (D.seam+24,hi-4,220.))
    crop=box(0,0,lo,100,80,hi-lo)
    solid=outer.cut(inner).intersect(crop)
    ring=envelope(part,BACKING).cut(envelope(part,BACKING+CORE))
    cuts=[]
    for bottom,top,sample in zones:
        # A .4 mm solid transition ring separates differing rib patterns.
        # Avoid point-connected core boundaries at the loft stations; the
        # channels close with short, supported roofs rather than sliver faces.
        bottom+=.2
        top-=.2
        # The actual core perimeter owns ribs, so concave guard corners also
        # receive channels rather than a deliberately solid corner block.
        wire=section_wire(envelope(part,BACKING+CORE/2),sample)
        cut=ring.intersect(box(0,0,bottom,100,80,top-bottom)).cut(rib_mask(wire,bottom,top))
        cuts.extend(cut.val().Solids())
    # Floor channels stop short of the sloped end-to-wall transition. Both
    # backing and contact skin remain intact; ribs run across the short axis.
    floor_z=lo+BACKING if part=='body' else hi-BACKING-CORE
    for i in range(-7,7):
        x=(i+.5)*PITCH
        mask=box(x,0,floor_z,PITCH-WEB,100,CORE)
        floor=envelope(part,0).intersect(mask)
        # Keep a 2 mm perimeter/root frame clear of the end taper.
        floor=floor.intersect(box(0,0,floor_z,56,33,CORE))
        cuts.extend(floor.val().Solids())
    return solid.cut(cq.Compound.makeCompound(cuts)).clean()


def print_part(part):
    p=cup(part)
    if part=='body':
        return p.translate((0,0,-D.floor-END_GAP))
    return p.rotate((0,0,0),(1,0,0),180).translate((82,0,D.length-D.floor-END_GAP))


def layout():
    return (cq.Assembly(name='dental_S16_print')
            .add(print_part('body'),name='body_liner')
            .add(print_part('cap'),name='cap_liner'))


@cache
def rigid():
    return build(D)
