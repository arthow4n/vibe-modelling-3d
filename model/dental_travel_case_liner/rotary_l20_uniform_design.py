"""Current dental cups: identical L20 section in walls and both floors."""
from contextlib import contextmanager
from functools import cache
from pathlib import Path
import sys
import cadquery as cq
from model.dental_travel_case.m1_design import rounded_wire

from model.tpu_damping_box.l20_standard import (
    SKIN, CORE, TOTAL, TIE, PITCH, LAND, RIM_CAP, centres, floor_void)

WALL = FLOOR_TOTAL = TOTAL
FLOOR_SKIN = SKIN
FLOOR_CORE = CORE
ALLOWANCE, END_GAP, RIM_GAP = .3, .3, .8
PAD_PROJECTION=.4
PAD_INTERFERENCE=PAD_PROJECTION-ALLOWANCE
PRINT_CENTRES = {'body':(60.,60.,0.), 'cap':(142.,60.,0.)}
CASE_DIR=Path(__file__).resolve().parents[1]/'dental_travel_case'


@contextmanager
def case_imports():
    """Scope the existing case's flat sibling imports; restore caller paths."""
    before=sys.path[:]
    sys.path.insert(0,str(CASE_DIR))
    try:
        yield
    finally:
        sys.path[:]=before


with case_imports():
    from rotary_case_design import CURRENT as D
    import rotary_case_design as _case_module
    if Path(_case_module.__file__).resolve().parent!=CASE_DIR:
        raise ImportError('Rotary case module belongs to another object')

BODY_BOTTOM=2.+END_GAP
BODY_TOP=D.seam+D.lap-RIM_GAP/2
CAP_BOTTOM=D.seam+D.lap+RIM_GAP/2
CAP_TOP=D.length-2.-END_GAP


def block(w,h,height,*,x=0.,y=0.,z=0.):
    return cq.Workplane('XY').box(w,h,height,centered=(True,True,False)).translate((x,y,z))


def loft(rows):
    return cq.Workplane(obj=cq.Solid.makeLoft([
        rounded_wire(w,h,r,z) for z,w,h,r in rows],ruled=True))


def height(part):
    if part=='body':return BODY_TOP-BODY_BOTTOM
    if part=='cap':return CAP_TOP-CAP_BOTTOM
    raise ValueError(part)


def outer_rows(part):
    height(part)
    if part=='body':
        upper=(67.2-2*ALLOWANCE,44.2-2*ALLOWANCE,2.-ALLOWANCE)
        lower=(71.8-2*ALLOWANCE,48.8-2*ALLOWANCE,4.-ALLOWANCE)
        # The floor itself fits through the sleeve mouth; the thicker, wider
        # lower walls still need gentle elastic compression during insertion.
        return [(0.,*upper[:2],2.5),(FLOOR_TOTAL,*upper[:2],2.5),
                (FLOOR_TOTAL+6.,*lower),
                (D.seam-6.-BODY_BOTTOM,*lower),
                (D.seam-BODY_BOTTOM,*upper),(height(part),*upper)]
    return [(0.,71.2+2*D.guide_clearance-2*ALLOWANCE,
             48.2+2*D.guide_clearance-2*ALLOWANCE,4.+D.guide_clearance-ALLOWANCE),
            (height(part),71.2+2*D.guide_clearance-2*ALLOWANCE,
             48.2+2*D.guide_clearance-2*ALLOWANCE,4.+D.guide_clearance-ALLOWANCE)]


def profile_at(part,z):
    rows=outer_rows(part)
    for a,b in zip(rows,rows[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0])
            return tuple(a[i]+t*(b[i]-a[i]) for i in (1,2,3))
    raise ValueError((part,z))


def inner_rows(part):
    rows=[(FLOOR_TOTAL,*profile_at(part,FLOOR_TOTAL))]
    rows.extend(row for row in outer_rows(part) if row[0]>FLOOR_TOTAL)
    rows.append((height(part)+1.,*rows[-1][1:]))
    return [(z,w-2*WALL,h-2*WALL,max(1.2,r-WALL)) for z,w,h,r in rows]


def wall_zones(part):
    height(part)
    if part=='body':
        return ((FLOOR_TOTAL+6.+RIM_CAP,D.seam-6.-BODY_BOTTOM-RIM_CAP),
                (D.seam-BODY_BOTTOM+RIM_CAP,height(part)-RIM_CAP))
    return ((FLOOR_SKIN,height(part)-RIM_CAP),)


def wall_spec(part,zone,axis,sign):
    """Pure pattern coordinates, shared by construction and path inspection."""
    if axis not in ('x','y') or sign not in (-1,1):raise ValueError((axis,sign))
    bottom,top=zone;w,h,_=profile_at(part,(bottom+top)/2)
    span,depth=(w,h) if axis=='y' else (h,w)
    along=centres(span,end_margin=LAND)
    vertical=centres(top-bottom,end_margin=1.)
    vertical=tuple((bottom+top)/2+z for z in vertical)
    radial=sign*(depth/2-SKIN-CORE/2)
    return dict(axis=axis,sign=sign,span=span,depth=depth,
        bottom=bottom,top=top,along=along,vertical=vertical,radial=radial)


def wall_pattern(part,zone,axis,sign):
    """A flat air channel interrupted by complete discrete square ties."""
    p=wall_spec(part,zone,axis,sign)
    span,radial,bottom,top=(p[k] for k in ('span','radial','bottom','top'))
    def brick(a,b,wide,tall,high,z):
        return (block(wide,tall,high,x=a,y=b,z=z) if axis=='y'
                else block(tall,wide,high,x=b,y=a,z=z))
    air=brick(0.,radial,span-2*LAND,CORE,top-bottom,bottom)
    ties=cq.Compound.makeCompound([
        brick(a,radial,TIE,CORE+.2,TIE,z-TIE/2).val()
        for a in p['along'] for z in p['vertical']])
    return air.cut(ties),p


def floor_spec(part):
    w,h,_=profile_at(part,0.)
    return dict(x=centres(w,end_margin=LAND),y=centres(h,end_margin=LAND),width=w,depth=h)


def floor_pattern(part):
    p=floor_spec(part)
    return floor_void(p['width'],p['depth']),p


def cap_pads():
    """Four shallow ramped TPU pads: local 0.1mm intended shell interference."""
    w,h,_=profile_at('cap',8.)
    pads=[]
    for axis,depth in (('y',h),('x',w)):
        peak=(PAD_PROJECTION+.2,.2,(PAD_PROJECTION-.2)/2)
        wires=[rounded_wire(4.,thickness,r,z).translate((0,depth/2+offset,0))
            for z,thickness,r,offset in ((6.,.2,.08,-.1),(7.,*peak),
                                         (9.,*peak),(10.,.2,.08,-.1))]
        pad=cq.Workplane(obj=cq.Solid.makeLoft(wires,ruled=True))
        if axis=='x':pad=pad.rotate((0,0,0),(0,0,1),-90)
        pads.extend([pad.val(),pad.mirror('XZ' if axis=='y' else 'YZ').val()])
    return cq.Workplane(obj=cq.Compound.makeCompound(pads))


@cache
def cup(part):
    height(part)
    solid=loft(outer_rows(part)).cut(loft(inner_rows(part)))
    voids=[floor_pattern(part)[0].val()]
    for zone in wall_zones(part):
        for axis in ('x','y'):
            for sign in (-1,1):voids.append(wall_pattern(part,zone,axis,sign)[0].val())
    solid=solid.cut(cq.Compound.makeCompound(voids))
    if part=='cap':solid=solid.union(cap_pads())
    return solid.clean()


def installed(part):
    p=cup(part)
    if part=='body':return p.translate((0,0,BODY_BOTTOM))
    if part=='cap':return p.rotate((0,0,0),(1,0,0),180).translate((0,0,CAP_TOP))
    raise ValueError(part)


def layout():
    a=cq.Assembly(name='rotary_uniform_L20_TPU_liners')
    for part in ('body','cap'):
        a.add(cup(part),name=part+'_liner',loc=cq.Location(PRINT_CENTRES[part]))
    return a


@cache
def rigid():
    # Build the authoritative latest covered box in its own import context;
    # this includes the softened seating stops and complete outside mechanism.
    with case_imports():
        from rotary_covered_design import covered_case
        return covered_case()
