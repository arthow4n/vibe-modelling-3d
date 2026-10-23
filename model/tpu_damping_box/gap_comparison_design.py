"""G08/G16 exploratory cups: 0.8mm skins, uniform selected core on all faces.

The selected L20 standard and dental model stay unchanged. Dimensions in mm.
"""
from dataclasses import dataclass
from math import hypot,atan2,degrees
import cadquery as cq
from model.tpu_damping_box import design as fixture
from model.tpu_damping_box.l20_standard import SKIN,TIE,PITCH,LAND,RIM_CAP,centres
from t_skin_design import GLYPHS as BASE_GLYPHS,label_backing

SIZE=34.
PAD_SIZE=SIZE-2*SKIN-2*fixture.PAD_ALLOWANCE
GLYPHS={**BASE_GLYPHS,'G':(((1.6,0),(0,0),(0,3.2),(1.6,3.2),(1.6,1.6),(.8,1.6)),)}

@dataclass(frozen=True)
class Variant:
    name:str
    gap:float
    @property
    def total(self):return 2*SKIN+self.gap
    @property
    def clear(self):return SIZE-2*self.total


def variant_named(name):
    if name not in ('G08','G16'):raise ValueError(name)
    return Variant(name,{'G08':.8,'G16':1.6}[name])


def block(w,h,depth,*,x=0.,y=0.,z=0.):
    return cq.Workplane('XY').box(w,h,depth,centered=(True,True,False)).translate((x,y,z))


def floor_void(name,size):
    v=variant_named(name)
    air=block(size-2*LAND,size-2*LAND,v.gap,z=SKIN)
    posts=cq.Compound.makeCompound([block(TIE,TIE,v.gap,x=x,y=y,z=SKIN).val()
        for x in centres(size,end_margin=LAND) for y in centres(size,end_margin=LAND)])
    return air.cut(posts)


def label(name,size):
    variant_named(name);strokes=[]
    for i,char in enumerate(name):
        for chain in GLYPHS[char]:
            for (ax,ay),(bx,by) in zip(chain,chain[1:]):
                x1,y1=-size/2+1.7+i*3+ax,-size/2+5.35-ay
                x2,y2=-size/2+1.7+i*3+bx,-size/2+5.35-by
                strokes.append(cq.Workplane('XY').slot2D(hypot(x2-x1,y2-y1)+.8,.8,
                    degrees(atan2(y2-y1,x2-x1))).extrude(.2).translate(((x1+x2)/2,(y1+y2)/2,0)))
    result=strokes[0]
    for stroke in strokes[1:]:result=result.union(stroke)
    return result.clean().mirror('YZ')


def wall_rows(name):
    v=variant_named(name);low=SKIN;high=SIZE-v.total-RIM_CAP
    return tuple((low+high)/2+z for z in centres(high-low,end_margin=1.))


def cup(name):
    v=variant_named(name)
    p=block(SIZE,SIZE,SIZE).cut(block(v.clear,v.clear,SIZE,z=v.total))
    p=p.cut(block(SIZE-2*SKIN,SIZE-2*SKIN,v.total+1,z=SIZE-v.total))
    p=p.cut(floor_void(name,SIZE))
    low=SKIN;high=SIZE-v.total-RIM_CAP;normal=-SIZE/2+SKIN+v.gap/2
    channel=block(v.gap,SIZE-2*LAND,high-low,x=normal,z=low)
    ties=cq.Compound.makeCompound([block(v.gap+.2,TIE,TIE,x=normal,y=a,z=z-TIE/2).val()
        for a in centres(SIZE,end_margin=LAND) for z in wall_rows(name)])
    for angle in (0,90,180,270):p=p.cut(channel.cut(ties).rotate((0,0,0),(0,0,1),angle))
    return p.union(label_backing(SIZE,v.total)).cut(label(name,SIZE)).clean()


def pad_print(name):
    v=variant_named(name)
    return (block(PAD_SIZE,PAD_SIZE,v.total).cut(floor_void(name,PAD_SIZE))
            .union(label_backing(PAD_SIZE,v.total)).cut(label(name,PAD_SIZE)).clean())


def pad_closed(name):
    return pad_print(name).rotate((0,0,0),(1,0,0),180).translate((0,0,fixture.FLOOR+SIZE))


def layout(name):
    variant_named(name)
    return (cq.Assembly(name=name+'_cup_and_matching_pad')
        .add(cup(name),name=name+'_cup',loc=cq.Location((60,60,0)))
        .add(pad_print(name),name=name+'_pad',loc=cq.Location((102,60,0))))
