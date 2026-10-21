"""Full T08/T16 B-derived cups with small M1 labels; mm, no publication on import."""
from dataclasses import dataclass
from math import atan2, degrees, hypot
import cadquery as cq
import design as fixture
import support_design as baseline

NAMES = ('T08', 'T16')
FLOOR_SKIN, FLOOR_CORE, FLOOR_TOTAL = .4, .8, 1.6
PRELOAD, RIM_CAP, WALL_GAP, TIE, LAND = .2, .4, .6, .8, 4.
LABEL_DEPTH, STROKE = .2, .8
LABEL_PATCH = (10., 6.5)  # 9 x 5.5 reserved zone plus 1 mm outer-edge setback.
CENTRES = baseline.CENTRES
WALL_CENTRES = tuple(x for x in CENTRES if abs(x)+TIE/2 < fixture.CUP_SIZE/2-LAND)
TIE_Z = tuple(3.2+i*4.4 for i in range(7))
# Paths in the SVG's downward-positive glyph coordinates, before exterior mirroring.
GLYPHS = {
 'T': (((0,0),(1.6,0)), ((.8,0),(.8,3.2))),
 '0': (((0,0),(1.6,0),(1.6,3.2),(0,3.2),(0,0)),),
 '8': (((0,0),(1.6,0),(1.6,3.2),(0,3.2),(0,0)), ((0,1.6),(1.6,1.6))),
 '1': (((.3,.4),(.8,0),(.8,3.2)), ((.2,3.2),(1.4,3.2))),
 '6': (((1.6,0),(0,0),(0,3.2),(1.6,3.2),(1.6,1.6),(0,1.6)),),
}

@dataclass(frozen=True)
class Variant:
    name: str
    skin: float

    @property
    def wall(self): return 2*self.skin+WALL_GAP
    @property
    def clear(self): return fixture.CUP_SIZE-2*self.wall
    @property
    def pocket(self): return fixture.CUP_SIZE-2*self.skin
    @property
    def pad_size(self): return self.pocket-2*fixture.PAD_ALLOWANCE


def variant_named(name):
    if name not in NAMES: raise ValueError(f'Unknown T skin pair {name!r}; choose {NAMES}')
    return Variant(name, {'T08':.8,'T16':1.6}[name])


def block(x,y,z,bottom=0,cx=0,cy=0):
    return baseline.block(x,y,z,bottom,cx,cy)


def corner_lands(size, height, bottom):
    return cq.Workplane(obj=cq.Compound.makeCompound([
        block(LAND,LAND,height,bottom,sx*(size-LAND)/2,sy*(size-LAND)/2).val()
        for sx in (-1,1) for sy in (-1,1)]))


def label_backing(size,height,bottom=0):
    x,y=LABEL_PATCH
    return block(x,y,height,bottom,(size-x)/2,-(size-y)/2)


def label_cut(name,size,depth):
    variant_named(name)
    strokes=[]
    for index,char in enumerate(name):
        for chain in GLYPHS[char]:
            for (ax,ay),(bx,by) in zip(chain,chain[1:]):
                # Exterior reading coordinates; all transforms on finished solids.
                x1,y1=-size/2+1.7+index*3.0+ax,-size/2+2.15+3.2-ay
                x2,y2=-size/2+1.7+index*3.0+bx,-size/2+2.15+3.2-by
                stroke=(cq.Workplane('XY').slot2D(hypot(x2-x1,y2-y1)+STROKE,STROKE,
                         degrees(atan2(y2-y1,x2-x1))).extrude(depth)
                         .translate(((x1+x2)/2,(y1+y2)/2,0)))
                strokes.append(stroke)
    result=strokes[0]
    for stroke in strokes[1:]: result=result.union(stroke)
    return result.clean().mirror('YZ')


def horizontal_void(v,size,bottom):
    air=block(size-2*v.skin,size-2*v.skin,FLOOR_CORE,bottom)
    posts=cq.Workplane(obj=cq.Compound.makeCompound([
        block(TIE,TIE,FLOOR_CORE,bottom,x,y).val() for x in CENTRES for y in CENTRES]))
    # Solid corner treatment and label seat are explicit, local changes from B.
    return air.cut(posts).cut(corner_lands(size,FLOOR_CORE,bottom)).cut(label_backing(size,FLOOR_CORE,bottom))


def cup(name):
    v=variant_named(name)
    p=block(34,34,34).cut(block(v.clear,v.clear,34,FLOOR_TOTAL))
    p=p.cut(block(v.pocket,v.pocket,FLOOR_TOTAL+1,34-FLOOR_TOTAL))
    p=p.cut(horizontal_void(v,34,FLOOR_SKIN))
    wall_height=34-FLOOR_TOTAL-RIM_CAP-FLOOR_SKIN
    nx=-17+v.skin+WALL_GAP/2
    channel=block(WALL_GAP,34-2*LAND,wall_height,FLOOR_SKIN,nx)
    ties=cq.Workplane(obj=cq.Compound.makeCompound([
        block(WALL_GAP+.2,TIE,TIE,z-TIE/2,nx,y).val()
        for y in WALL_CENTRES for z in TIE_Z]))
    for angle in (0,90,180,270):
        p=p.cut(channel.cut(ties).rotate((0,0,0),(0,0,1),angle))
    # Core subtraction never reaches the label seat, including wall/floor overlap.
    p=p.union(label_backing(34,FLOOR_TOTAL)).cut(label_cut(name,34,LABEL_DEPTH))
    return p.clean()


def pad_print(name):
    v=variant_named(name)
    p=block(v.pad_size,v.pad_size,FLOOR_TOTAL+PRELOAD)
    p=p.cut(horizontal_void(v,v.pad_size,FLOOR_SKIN+PRELOAD))
    return p.cut(label_cut(name,v.pad_size,LABEL_DEPTH)).clean()


def pad_closed(name):
    return (pad_print(name).rotate((0,0,0),(1,0,0),180)
            .translate((0,0,fixture.FLOOR+34+PRELOAD)))


def placements(name):
    variant_named(name)
    return ((f'cup_{name}','cup',(60.,60.,0.)),(f'pad_{name}','pad',(102.,60.,0.)))


def layout(name):
    variant_named(name)
    assembly=cq.Assembly(name=f'{name}_M1_pair')
    for part,kind,position in placements(name):
        assembly.add({'cup':cup,'pad':pad_print}[kind](name),name=part,loc=cq.Location(position))
    return assembly
