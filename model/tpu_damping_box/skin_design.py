"""Closed-skin S16/S12 experiments; preserve the physically accepted I22 builders."""
from dataclasses import dataclass
import cadquery as cq
import design as b


@dataclass(frozen=True)
class SkinVariant:
    label: str
    thickness: float
    backing: float = .4
    skin: float = .4
    web: float = .9
    preload: float = .1

    @property
    def core(self):
        return self.thickness-self.backing-self.skin

    @property
    def clear(self):
        return b.CUP_SIZE-2*self.thickness

    @property
    def pad_size(self):
        return b.CUP_SIZE-2*self.backing-2*b.PAD_ALLOWANCE


VARIANTS={'S16':SkinVariant('S16',1.6),'S12':SkinVariant('S12',1.2)}
SELECTED_NAMES=('S16','S12')
PITCH=4.4
RIB_CENTRES=tuple(i*PITCH for i in range(-3,4))
LABEL_SIZE=12.
LABEL_DEPTH=.1


def variant_named(name):
    if name not in VARIANTS:
        raise ValueError(f'Unknown closed-skin variant {name!r}; choose {tuple(VARIANTS)}')
    return VARIANTS[name]


def label_cut(name,depth):
    variant_named(name)
    return cq.Workplane('XY').text(name,LABEL_SIZE,depth,font='DejaVu Sans Mono',
        kind='bold',combine=True).mirror('YZ')


def face_core(v,length):
    # Straight supports have no closely returning chevron legs. Both skins
    # remain joined, but the nominal inter-rib channel widens to 3.5 mm.
    rib=b.web_segment(0,0,0,v.core,v.web,length)
    return cq.Compound.makeCompound([rib.translate((x,0,0)).val() for x in RIB_CENTRES])


def cup(name):
    v=variant_named(name)
    inner=b.CUP_SIZE-2*v.backing
    wall_height=b.CUP_HEIGHT-v.thickness
    p=b.block(b.CUP_SIZE,b.CUP_SIZE,b.CUP_HEIGHT).cut(
        b.block(v.clear,v.clear,b.CUP_HEIGHT,v.thickness))
    p=p.cut(b.block(inner,inner,v.thickness+1,wall_height))
    p=p.cut(b.block(inner,inner,v.core,v.backing))
    skin_outer=v.clear+2*v.skin
    void=b.block(inner,inner,wall_height-v.backing,v.backing).cut(
        b.block(skin_outer,skin_outer,wall_height+1))
    p=p.cut(void).union(cq.Workplane(obj=face_core(v,inner)).translate((0,0,v.backing)))
    wall=cq.Workplane(obj=face_core(v,wall_height)).rotate((0,0,0),(1,1,1),120)
    wall=wall.translate((-inner/2,0,wall_height/2))
    mask=b.block(v.core,skin_outer,wall_height).translate((-inner/2+v.core/2,0,0))
    wall=wall.intersect(mask)
    for angle in (0,90,180,270):
        p=p.union(wall.rotate((0,0,0),(0,0,1),angle))
    return p.cut(label_cut(name,LABEL_DEPTH)).clean()


def pad_print(name):
    v=variant_named(name)
    p=b.block(v.pad_size,v.pad_size,v.thickness+v.preload)
    size=v.pad_size-2*v.backing
    p=p.cut(b.block(size,size,v.core,v.backing+v.preload))
    core=cq.Workplane(obj=face_core(v,size)).translate((0,0,v.backing+v.preload))
    return p.union(core).cut(label_cut(name,LABEL_DEPTH)).clean()


def pad_closed(name):
    v=variant_named(name)
    return pad_print(name).rotate((0,0,0),(1,0,0),180).translate((0,0,b.FLOOR+b.CUP_HEIGHT+v.preload))


def placements():
    return tuple(row for i,name in enumerate(SELECTED_NAMES) for row in (
        (f'cup_{name}','cup',name,(20+42*i,20,0)),
        (f'pad_{name}','pad',name,(20+42*i,61,0))))


def layout():
    a=cq.Assembly(name='closed_skin_followup')
    builders={'cup':cup,'pad':pad_print}
    for part,kind,name,position in placements():
        a.add(builders[kind](name),name=part,loc=cq.Location(position))
    return a
