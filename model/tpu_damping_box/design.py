"""Six-face nut impact study; mm. Builders have no publication side effects."""
from dataclasses import dataclass
from math import sqrt
import cadquery as cq

# Primary experimental dimensions; all variants share the impact envelope.
CLEAR = 26.0
ZONE = 4.0
BACKING = 0.8
CUP_SIZE = CLEAR + 2 * ZONE
CUP_HEIGHT = CLEAR + 2 * ZONE
INSERT_ALLOWANCE = 0.2  # per side, cup to PETG
PAD_ALLOWANCE = 0.2  # per side, pad to cup's upper backing
PAD_PRELOAD = 0.2  # deliberate axial squeeze; physical fit is unqualified
FLOOR = 2.4
OUTSIDE = 48.0
BODY_HEIGHT = FLOOR + CUP_HEIGHT
LID_THICKNESS = 3.2
RIB_PITCH = 3.6
RIB_CENTRES = tuple((i - 3.5) * RIB_PITCH for i in range(8))
SCREW_CENTRES = ((-19.5, -19.5), (19.5, 19.5))
SCREW_CLEARANCE = 3.4
NUT_AF = 5.8  # M3 pocket incl. allowance; verify actual stock fit
NUT_SLOT_HEIGHT = 2.8
NUT_ROOF = 2.6
@dataclass(frozen=True)
class Variant:
    label: str
    core: str
    rib_wall: float
    skin: float = 0.8

VARIANTS = {
    'A': Variant('A', 'solid', 0.0),
    'B': Variant('B', 'straight', 1.2),
    'C': Variant('C', 'straight', 0.8),
    'D': Variant('D', 'inclined', 0.8),
    'E': Variant('E', 'chevron', 0.8),
    'F': Variant('F', 'straight', 0.8, skin=0.6),
}


def variant_named(name):
    if name not in VARIANTS:
        raise ValueError(f'Unknown liner {name!r}; choose {tuple(VARIANTS)}')
    return VARIANTS[name]


def block(x, y, z, bottom=0):
    return cq.Workplane('XY').box(x, y, z, centered=(True, True, False)).translate((0, 0, bottom))


def outline(size, height):
    return block(size, size, height).edges('|Z').fillet(4.5)


def body():
    p = outline(OUTSIDE, BODY_HEIGHT).edges('<Z').chamfer(1.2)
    cavity = CUP_SIZE + 2 * INSERT_ALLOWANCE
    p = p.cut(block(cavity, cavity, CUP_HEIGHT + 1, FLOOR))
    # Side-loaded hex nuts bear against pocket roofs: tightening clamps the lid
    # onto the body. Fasteners never enter the lined test chamber.
    for x, y in SCREW_CENTRES:
        hole = cq.Workplane('XY').center(x, y).circle(SCREW_CLEARANCE / 2).extrude(11.5).translate((0, 0, BODY_HEIGHT - 11.5))
        slot_bottom = BODY_HEIGHT - NUT_ROOF - NUT_SLOT_HEIGHT
        hexagon = cq.Workplane('XY').center(x, y).polygon(6, 2 * NUT_AF / sqrt(3)).extrude(NUT_SLOT_HEIGHT).translate((0, 0, slot_bottom))
        # Nut flats parallel X; lateral entrance opens towards nearest X edge.
        sign = 1 if x > 0 else -1
        entry = block(5.0, NUT_AF, NUT_SLOT_HEIGHT, slot_bottom).translate((x + sign * 2.5, y, 0))
        p = p.cut(hole).cut(hexagon.union(entry))
    return p


def lid_print():
    # Outer face on bed; mating face upward. No floating lip or trapped support.
    p = outline(OUTSIDE, LID_THICKNESS).edges('<Z').chamfer(1.2)
    for x, y in SCREW_CENTRES:
        p = p.cut(cq.Workplane('XY').center(x, y).circle(SCREW_CLEARANCE / 2).extrude(LID_THICKNESS))
    return p


def lid_closed():
    # Flipping about the diagonal preserves the diagonal screw-hole pair.
    return lid_print().rotate((0, 0, 0), (1, 1, 0), 180).translate((0, 0, BODY_HEIGHT + LID_THICKNESS))


def web_segment(x0, z0, x1, z1, thickness, length):
    # Horizontal half-width corresponding to shortest normal wall thickness.
    half = thickness * sqrt(1 + ((x1-x0)/(z1-z0))**2) / 2
    points = [(x0-half,z0), (x0+half,z0), (x1+half,z1), (x1-half,z1)]
    return cq.Workplane('XZ').polyline(points).close().extrude(length).translate((0,length/2,0))


def face_core(v, length):
    """CAD webs spanning two flat skins; canonical depth axis is Z."""
    h = ZONE - BACKING - v.skin
    if v.core == 'straight':
        rib = web_segment(0,0,0,h,v.rib_wall,length)
    elif v.core == 'inclined':
        rib = web_segment(-0.6,0,0.6,h,v.rib_wall,length)
    elif v.core == 'chevron':
        rib = web_segment(-0.5,0,0.5,h/2,v.rib_wall,length).union(
              web_segment(0.5,h/2,-0.5,h,v.rib_wall,length))
    else:
        raise ValueError(f'No cellular core for {v.core!r}')
    return cq.Compound.makeCompound([rib.translate((x,0,0)).val() for x in RIB_CENTRES])


def label_cut(letter, depth):
    # Read from the exterior underside (-Z), rather than through the part.
    return cq.Workplane('XY').text(letter, 6, depth, font='DejaVu Sans', kind='bold', combine=True).mirror('YZ')


def cup(name):
    v = variant_named(name)
    inner = CUP_SIZE - 2 * BACKING
    # Solid control establishes exactly flat inner faces and the roof pad seat.
    p = block(CUP_SIZE,CUP_SIZE,CUP_HEIGHT).cut(block(CLEAR,CLEAR,CUP_HEIGHT,ZONE))
    p = p.cut(block(inner,inner,ZONE+1,ZONE+CLEAR))
    if v.core != 'solid':
        h = ZONE - BACKING - v.skin
        # Floor core and four-wall core are separate voids, so the flat inside
        # corner retains skin thickness. No stored object enters the channels.
        p = p.cut(block(inner,inner,h,BACKING))
        inner_skin_outer = CLEAR + 2*v.skin
        wall_void = block(inner,inner,CLEAR+ZONE-BACKING,BACKING).cut(
                    block(inner_skin_outer,inner_skin_outer,CLEAR+ZONE+1))
        p = p.cut(wall_void)
        p = p.union(cq.Workplane(obj=face_core(v,inner)).translate((0,0,BACKING)))
        # Canonical axes x->y, y->z, z->x. Trim away from adjacent wall cores.
        wall = cq.Workplane(obj=face_core(v,CLEAR+ZONE)).rotate((0,0,0),(1,1,1),120)
        wall = wall.translate((-inner/2,0,(CLEAR+ZONE)/2))
        core_mask = block(h,inner_skin_outer,CLEAR+ZONE).translate((-inner/2+h/2,0,0))
        wall = wall.intersect(core_mask)
        for angle in (0,90,180,270):
            p = p.union(wall.rotate((0,0,0),(0,0,1),angle))
    return p.cut(label_cut(v.label,0.3)).clean()


def pad_print(name):
    v = variant_named(name)
    size = CUP_SIZE - 2*BACKING - 2*PAD_ALLOWANCE
    p = block(size,size,ZONE+PAD_PRELOAD)
    if v.core != 'solid':
        h = ZONE - BACKING - v.skin
        # Perimeter frame joins both skins. Maximum floor/roof web spacing is
        # 3.6 mm; F uses three 0.2-mm layers for its inner face instead of four.
        void_size = size - 2*BACKING
        p = p.cut(block(void_size,void_size,h,BACKING+PAD_PRELOAD))
        core = cq.Workplane(obj=face_core(v,void_size)).translate((0,0,BACKING+PAD_PRELOAD))
        p = p.union(core)
    return p.cut(label_cut(v.label,0.3)).clean()


def pad_closed(name):
    # The extra 0.2 mm lies above the lid seat before elastic compression.
    return pad_print(name).rotate((0,0,0), (1,0,0), 180).translate((0,0,FLOOR+CUP_HEIGHT+PAD_PRELOAD))


def petg_layout():
    return cq.Assembly(name='petg').add(body(), name='body', loc=cq.Location((28,28,0))).add(lid_print(), name='lid', loc=cq.Location((80,28,0)))


def liner_layout(names):
    if not names or len(set(names)) != len(names):
        raise ValueError('Supply distinct explicit liner names')
    a = cq.Assembly(name='tpu')
    for i, name in enumerate(names):
        variant_named(name)
        x = 20 + (i % 3) * 42
        y = (i // 3) * 84
        a.add(cup(name), name=f'cup_{name}', loc=cq.Location((x,20+y,0)))
        a.add(pad_print(name), name=f'pad_{name}', loc=cq.Location((x,61+y,0)))
    return a


def assembled(name):
    variant_named(name)
    return (cq.Assembly(name=f'closed_{name}').add(body(), name='body')
            .add(lid_closed(), name='lid').add(cup(name), name='cup', loc=cq.Location((0,0,FLOOR)))
            .add(pad_closed(name), name='pad'))
