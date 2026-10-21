"""L20/L18 reduce only T08's upright air gap; approved T08 builder stays frozen."""
from dataclasses import dataclass
from math import atan2,degrees,hypot
import cadquery as cq
import t_skin_design as base

NAMES=('L20','L18')
GLYPHS={**base.GLYPHS,
 'L': (((0,0),(0,3.2),(1.6,3.2)),),
 '2': (((0,0),(1.6,0),(1.6,1.6),(0,1.6),(0,3.2),(1.6,3.2)),),
}

@dataclass(frozen=True)
class Variant:
    name:str
    gap:float
    skin:float=.8
    @property
    def wall(self):return 2*self.skin+self.gap
    @property
    def clear(self):return 34-2*self.wall
    @property
    def pocket(self):return 34-2*self.skin
    @property
    def pad_size(self):return self.pocket-2*base.fixture.PAD_ALLOWANCE


def variant_named(name):
    if name not in NAMES:raise ValueError(f'Unknown thinner-gap pair {name!r}; choose {NAMES}')
    return Variant(name,{'L20':.4,'L18':.2}[name])


def label_cut(name,size,depth):
    variant_named(name)
    strokes=[]
    for index,char in enumerate(name):
        for chain in GLYPHS[char]:
            for (ax,ay),(bx,by) in zip(chain,chain[1:]):
                x1,y1=-size/2+1.7+index*3+ax,-size/2+5.35-ay
                x2,y2=-size/2+1.7+index*3+bx,-size/2+5.35-by
                strokes.append((cq.Workplane('XY').slot2D(hypot(x2-x1,y2-y1)+base.STROKE,
                    base.STROKE,degrees(atan2(y2-y1,x2-x1))).extrude(depth)
                    .translate(((x1+x2)/2,(y1+y2)/2,0))))
    result=strokes[0]
    for stroke in strokes[1:]:result=result.union(stroke)
    return result.clean().mirror('YZ')


def cup(name):
    v=variant_named(name)
    p=base.block(34,34,34).cut(base.block(v.clear,v.clear,34,base.FLOOR_TOTAL))
    p=p.cut(base.block(v.pocket,v.pocket,base.FLOOR_TOTAL+1,34-base.FLOOR_TOTAL))
    p=p.cut(base.horizontal_void(base.variant_named('T08'),34,base.FLOOR_SKIN))
    height=34-base.FLOOR_TOTAL-base.RIM_CAP-base.FLOOR_SKIN
    nx=-17+v.skin+v.gap/2
    channel=base.block(v.gap,34-2*base.LAND,height,base.FLOOR_SKIN,nx)
    ties=cq.Workplane(obj=cq.Compound.makeCompound([
        base.block(v.gap+.2,base.TIE,base.TIE,z-base.TIE/2,nx,y).val()
        for y in base.WALL_CENTRES for z in base.TIE_Z]))
    for angle in (0,90,180,270):p=p.cut(channel.cut(ties).rotate((0,0,0),(0,0,1),angle))
    return p.union(base.label_backing(34,base.FLOOR_TOTAL)).cut(label_cut(name,34,base.LABEL_DEPTH)).clean()


def pad_print(name):
    v=variant_named(name)
    # Reuse the actual approved pad, refilling only its solid label seat before recoding.
    return (base.pad_print('T08').union(base.label_backing(v.pad_size,base.FLOOR_TOTAL+base.PRELOAD))
            .cut(label_cut(name,v.pad_size,base.LABEL_DEPTH)).clean())


def pad_closed(name):
    return pad_print(name).rotate((0,0,0),(1,0,0),180).translate((0,0,base.fixture.FLOOR+34+base.PRELOAD))


def placements(name):
    variant_named(name)
    return ((f'cup_{name}','cup',(60.,60.,0.)),(f'pad_{name}','pad',(102.,60.,0.)))


def layout(name):
    variant_named(name)
    assembly=cq.Assembly(name=f'{name}_M1_thinner_pair')
    for part,kind,pos in placements(name):
        assembly.add({'cup':cup,'pad':pad_print}[kind](name),name=part,loc=cq.Location(pos))
    return assembly
