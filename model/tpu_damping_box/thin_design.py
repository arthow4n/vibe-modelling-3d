"""Thinner derivatives of approved I; original design.py is intentionally retained."""
from dataclasses import dataclass
import cadquery as cq
import design as base


@dataclass(frozen=True)
class ThinVariant:
    label: str
    thickness: float
    backing: float
    skin: float
    web: float

    @property
    def core(self):
        return self.thickness - self.backing - self.skin

    @property
    def clear(self):
        return base.CUP_SIZE - 2*self.thickness

    @property
    def amplitude(self):
        # Preserve I's centreline slope, rather than create steeper overhangs.
        return .5*self.core/2.6

    @property
    def pad_size(self):
        return base.CUP_SIZE - 2*self.backing - 2*base.PAD_ALLOWANCE


VARIANTS = {
    'I30': ThinVariant('I30', 3.0, .6, .6, .5),
    'I24': ThinVariant('I24', 2.4, .4, .6, .4),
    'I20': ThinVariant('I20', 2.0, .4, .4, .4),
}
SELECTED_NAMES = ('I30', 'I24', 'I20')
LABEL_DEPTH = .2
LABEL_SIZE = 12.0  # font em size; actual capital height is font-dependent
LABEL_FONT = 'DejaVu Sans Mono'


def variant_named(name):
    if name not in VARIANTS:
        raise ValueError(f'Unknown thin liner {name!r}; choose {tuple(VARIANTS)}')
    return VARIANTS[name]


def label_cut(name, depth):
    variant_named(name)
    # Wide bold strokes and a barred I distinguish the common prefix from 1.
    # Read from exterior underside; preserve the thin backing above the recess.
    return cq.Workplane('XY').text(name,LABEL_SIZE,depth,font=LABEL_FONT,
        kind='bold',combine=True).mirror('YZ')


def shift(v, depth):
    return -v.amplitude + 4*v.amplitude*min(depth/v.core, 1-depth/v.core)


def face_core(v, length):
    a, h = v.amplitude, v.core
    rib = base.web_segment(-a, 0, a, h/2, v.web, length).union(
          base.web_segment(a, h/2, -a, h, v.web, length))
    return cq.Compound.makeCompound([rib.translate((x,0,0)).val() for x in base.RIB_CENTRES])


def cup(name):
    v = variant_named(name)
    inner = base.CUP_SIZE - 2*v.backing
    wall_height = base.CUP_HEIGHT - v.thickness
    p = base.block(base.CUP_SIZE,base.CUP_SIZE,base.CUP_HEIGHT).cut(
        base.block(v.clear,v.clear,base.CUP_HEIGHT,v.thickness))
    p = p.cut(base.block(inner,inner,v.thickness+1,wall_height))
    p = p.cut(base.block(inner,inner,v.core,v.backing))
    inner_skin_outer = v.clear + 2*v.skin
    wall_void = base.block(inner,inner,wall_height-v.backing,v.backing).cut(
        base.block(inner_skin_outer,inner_skin_outer,wall_height+1))
    p = p.cut(wall_void)
    p = p.union(cq.Workplane(obj=face_core(v,inner)).translate((0,0,v.backing)))
    wall = cq.Workplane(obj=face_core(v,wall_height)).rotate((0,0,0),(1,1,1),120)
    wall = wall.translate((-inner/2,0,wall_height/2))
    mask = base.block(v.core,inner_skin_outer,wall_height).translate((-inner/2+v.core/2,0,0))
    wall = wall.intersect(mask)
    for angle in (0,90,180,270):
        p = p.union(wall.rotate((0,0,0),(0,0,1),angle))
    return p.cut(label_cut(name,LABEL_DEPTH)).clean()


def pad_print(name):
    v = variant_named(name)
    p = base.block(v.pad_size,v.pad_size,v.thickness+base.PAD_PRELOAD)
    void_size = v.pad_size - 2*v.backing
    p = p.cut(base.block(void_size,void_size,v.core,v.backing+base.PAD_PRELOAD))
    core = cq.Workplane(obj=face_core(v,void_size)).translate((0,0,v.backing+base.PAD_PRELOAD))
    return p.union(core).cut(label_cut(name,LABEL_DEPTH)).clean()


def pad_closed(name):
    return pad_print(name).rotate((0,0,0),(1,0,0),180).translate(
        (0,0,base.FLOOR+base.CUP_HEIGHT+base.PAD_PRELOAD))


def placements():
    # Three cup/pad pairs in one 118 x 75 mm plate; preserve bridge direction.
    return tuple(row for i,name in enumerate(SELECTED_NAMES) for row in (
        (f'cup_{name}','cup',name,(20+42*i,20,0)),
        (f'pad_{name}','pad',name,(20+42*i,61,0))))


def layout():
    a = cq.Assembly(name='thin_I')
    builders = {'cup':cup,'pad':pad_print}
    for part,kind,name,position in placements():
        a.add(builders[kind](name),name=part,loc=cq.Location(position))
    return a
