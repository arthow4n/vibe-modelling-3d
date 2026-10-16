"""S16 TPU accessory for the existing accepted E case; all dimensions in mm."""
from functools import cache
from math import asin, cos, sin, radians, degrees
from pathlib import Path
import runpy
import cadquery as cq

CASE_SOURCE = Path(__file__).resolve().parents[1] / 'sunglasses_case/sunglasses_case.py'
# Local S16 dimensions deliberately preserved, not scaled with shell size.
BACKING = .4
CORE = .8
SKIN = .4
THICKNESS = BACKING + CORE + SKIN
WEB = .9
PITCH = 4.4
SIDE_ALLOWANCE = .2
TAPE_ALLOWANCE = .2
SEAM_ALLOWANCE = .5
LAYOUT_GAP = 6.


@cache
def case():
    return runpy.run_path(str(CASE_SOURCE), init_globals={'VERIFY': False})


def dimensions():
    m = case()
    return (m['INNER_LENGTH'] - 2*SIDE_ALLOWANCE,
            m['INNER_WIDTH'] - 2*SIDE_ALLOWANCE,
            m['SEAM'] - m['FLOOR'] - TAPE_ALLOWANCE - SEAM_ALLOWANCE,
            m['CORNER'] - m['WALL'] - SIDE_ALLOWANCE)


def rounded(length, width, height, radius, z=0):
    return (cq.Workplane('XY').box(length, width, height, centered=(True, True, False))
            .edges('|Z').fillet(radius).translate((0, 0, z)))


def block(length, width, height, x=0, y=0, z=0):
    return cq.Workplane('XY').box(length, width, height, centered=(True, True, False)).translate((x,y,z))


def channels(half_span):
    """Full inter-rib gaps only; the short end remainder remains solid."""
    n = int(half_span // PITCH) + 1
    return tuple((i*PITCH + WEB/2, (i+1)*PITCH - WEB/2)
                 for i in range(-n, n)
                 if i*PITCH + WEB/2 >= -half_span and (i+1)*PITCH - WEB/2 <= half_span)


@cache
def solid_corner_cup():
    length, width, height, radius = dimensions()
    p = rounded(length,width,height,radius).cut(
        rounded(length-2*THICKNESS,width-2*THICKNESS,height,radius-THICKNESS,THICKNESS))
    # TPU opening: rounded outer/inner lips, flat backing retained for adhesion.
    p = p.edges('>Z').fillet(.2)
    floor_mask = rounded(length-2*BACKING,width-2*BACKING,CORE,radius-BACKING,BACKING)
    cuts = []
    for lo, hi in channels(length/2-BACKING):
        cuts.append(block(hi-lo,width,CORE,(lo+hi)/2,z=BACKING).intersect(floor_mask).val())
    # Retained pre-correction baseline, also the starting envelope for the
    # current cup. The current builder below adds the corner core.
    wall_z = THICKNESS
    wall_height = height-SKIN-wall_z
    for lo, hi in channels(length/2-radius):
        for sign in (-1,1):
            cuts.append(block(hi-lo,CORE,wall_height,(lo+hi)/2,
                              sign*(width/2-BACKING-CORE/2),wall_z).val())
    for lo, hi in channels(width/2-radius):
        for sign in (-1,1):
            cuts.append(block(CORE,hi-lo,wall_height,
                              sign*(length/2-BACKING-CORE/2),(lo+hi)/2,wall_z).val())
    return p.cut(cq.Compound.makeCompound(cuts)).clean()


def corner_locations():
    length,width,_,radius = dimensions()
    return tuple((sx,sy,sx*(length/2-radius),sy*(width/2-radius))
                 for sx in (-1,1) for sy in (-1,1))


def quarter_slots():
    _,_,height,radius = dimensions()
    inner = radius-BACKING-CORE
    outer = radius-BACKING
    # At the inner core radius, two adjacent half-ribs retain 0.9 mm minimum
    # chord width. Three sectors keep corner spacing below the 4.4 mm S16 pitch.
    half_rib_angle = degrees(asin(WEB/(2*inner)))
    ring = (cq.Workplane('XY').circle(outer).circle(inner)
            .extrude(height-THICKNESS-SKIN).translate((0,0,THICKNESS)))
    slots=[]
    for low in (0,30,60):
        lo,hi = radians(low+half_rib_angle),radians(low+30-half_rib_angle)
        reach = 2*radius
        wedge = (cq.Workplane('XY').polyline([(0,0),
                 (reach*cos(lo),reach*sin(lo)),(reach*cos(hi),reach*sin(hi))])
                 .close().extrude(height))
        slots.append(ring.intersect(wedge).val())
    return cq.Workplane(obj=cq.Compound.makeCompound(slots))


@cache
def cup():
    slots = quarter_slots()
    cuts=[]
    for sx,sy,x,y in corner_locations():
        local=slots
        if sx<0: local=local.mirror('YZ')
        if sy<0: local=local.mirror('XZ')
        cuts.append(local.translate((x,y,0)).val())
    return solid_corner_cup().cut(cq.Compound.makeCompound(cuts)).clean()



def layout():
    _, width, _, _ = dimensions()
    part = cup()
    return (cq.Assembly(name='S16_sunglasses_liner')
            .add(part,name='body_insert')
            .add(part,name='lid_insert',loc=cq.Location((0,width+LAYOUT_GAP,0))))


def installed(angle):
    """Actual case coordinates; angle 0 is fully open, 180 closed."""
    m = case()
    body = cup().translate((0,0,m['FLOOR']+TAPE_ALLOWANCE))
    lid_open = body.translate((0,2*m['HY'],0))
    return body, m['close'](lid_open,angle)
