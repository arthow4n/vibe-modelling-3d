"""Four installation-integrity experiments for the existing 34 mm liner fixture.

All dimensions mm. Explicit variants; no file publication during construction.
A uses closed square-opening loops in wall sections, not solid rib substitutes.
B uses ties separated in tangent and height, plus discrete floor/roof posts.
"""
from dataclasses import dataclass
import cadquery as cq
import design as fixture

PITCH = 4.4
CENTRES = tuple(i * PITCH for i in range(-3, 4))
FLOOR_SKIN = .4
RIM_CAP = .4
FRAME_CROSS_WEB = .6
FLOOR_FRAME_WEB = .5
LABEL_DEPTH = .2
LABEL_SIZE = 12.0
REVISION = "R2"
# A one-layer preload replaces historical 0.1 mm, so all pad Z features lie on
# the agreed 0.2 mm grid. This is deliberate squeeze, not a calibrated fit.
PRELOAD = .2


@dataclass(frozen=True)
class SupportVariant:
    name: str
    topology: str
    thickness: float
    wall_skin: float
    tie_size: float

    @property
    def core(self):
        return self.thickness - 2 * FLOOR_SKIN

    @property
    def wall_core(self):
        return self.thickness - 2 * self.wall_skin

    @property
    def clear(self):
        return fixture.CUP_SIZE - 2 * self.thickness

    @property
    def wall_height(self):
        return fixture.CUP_HEIGHT - self.thickness

    @property
    def pad_size(self):
        return fixture.CUP_SIZE - 2 * self.wall_skin - 2 * fixture.PAD_ALLOWANCE

    @property
    def frame_opening(self):
        return self.wall_core - 2 * self.tie_size


VARIANTS = {
    'A16': SupportVariant('A16', 'frame', 1.6, .5, .2),
    'A20': SupportVariant('A20', 'frame', 2.0, .5, .2),
    'B08': SupportVariant('B08', 'ties', 1.6, .5, .8),
    'B16': SupportVariant('B16', 'ties', 1.6, .5, 1.6),
}
NAMES = tuple(VARIANTS)


def variant_named(name):
    if name not in VARIANTS:
        raise ValueError(f'Unknown support experiment {name!r}; choose {NAMES}')
    return VARIANTS[name]


def block(x, y, z, bottom=0, cx=0, cy=0):
    return fixture.block(x, y, z, bottom).translate((cx, cy, 0))


def compound(parts):
    return cq.Compound.makeCompound([p.val() for p in parts])


def label_cut(name, depth=LABEL_DEPTH):
    variant_named(name)
    main = cq.Workplane('XY').text(name,LABEL_SIZE,depth,
        font='DejaVu Sans Mono',kind='bold',combine=True)
    revision = cq.Workplane('XY').center(0,-11).text(REVISION,8,depth,
        font='DejaVu Sans Mono',kind='bold',combine=True)
    return main.union(revision).mirror('YZ')


def floor_supports(v, length):
    if v.topology == 'ties':
        return compound([block(v.tie_size, v.tie_size, v.core,
                               FLOOR_SKIN, x, y) for x in CENTRES for y in CENTRES])
    # Horizontal skins/rail heights follow the 0.2 mm layer grid; the long
    # vertical cross-webs need ordinary-line-width material, independent of the
    # small rails embedded in the upright skins.
    rail_height = .2
    opening = v.core - 2*rail_height
    width = opening + 2*FLOOR_FRAME_WEB
    loop = block(width,length,v.core,FLOOR_SKIN).cut(
        block(opening,length+1,opening,FLOOR_SKIN+rail_height))
    return compound([loop.translate((x,0,0)) for x in CENTRES])


def tie_heights(v):
    # All tie starts/heights are whole 0.2 mm layers; same centres for both B's.
    return tuple(3.2 + i * PITCH for i in range(7))


def wall_supports(v):
    """Canonical left-wall supports; depth is X and tangent is Y."""
    core_outer = -fixture.CUP_SIZE / 2 + v.wall_skin
    depth_centre = core_outer + v.wall_core / 2
    height = v.wall_height - FLOOR_SKIN - RIM_CAP
    parts = []
    if v.topology == 'ties':
        for y in CENTRES:
            for z in tie_heights(v):
                parts.append(block(v.wall_core, v.tie_size, v.tie_size,
                                   z - v.tie_size / 2, depth_centre, y))
    else:
        # Build each loop as ONE ring. Overlapping, unfused rail boxes are not
        # a valid boolean cutter and previously produced misleading final solids.
        loop = block(v.wall_core,v.frame_opening+2*FRAME_CROSS_WEB,height,FLOOR_SKIN,depth_centre).cut(
            block(v.frame_opening,v.frame_opening,height+2,
                  FLOOR_SKIN-1,depth_centre))
        parts = [loop.translate((0,y,0)) for y in CENTRES]
    return compound(parts)


def cup(name):
    v = variant_named(name)
    # Keep the established external envelope and constant-section insertion path.
    p = block(fixture.CUP_SIZE, fixture.CUP_SIZE, fixture.CUP_HEIGHT)
    p = p.cut(block(v.clear, v.clear, fixture.CUP_HEIGHT, v.thickness))
    pocket = fixture.CUP_SIZE - 2 * v.wall_skin
    p = p.cut(block(pocket, pocket, v.thickness + 1, v.wall_height))
    floor_size = fixture.CUP_SIZE - 2 * v.wall_skin
    floor_void = block(floor_size, floor_size, v.core, FLOOR_SKIN)
    p = p.cut(floor_void.cut(cq.Workplane(obj=floor_supports(v, floor_size))))
    inner_skin_outer = v.clear + 2 * v.wall_skin
    wall_void = block(pocket, pocket, v.wall_height-FLOOR_SKIN-RIM_CAP, FLOOR_SKIN).cut(
        block(inner_skin_outer, inner_skin_outer, fixture.CUP_HEIGHT))
    walls = wall_supports(v)
    supports = cq.Compound.makeCompound([
        walls.rotate((0, 0, 0), (0, 0, 1), angle) for angle in (0, 90, 180, 270)])
    p = p.cut(wall_void.cut(cq.Workplane(obj=supports)))
    # Square bed/rim/contact edges deliberately preserve the thin skins and fit.
    return p.cut(label_cut(name)).clean()


def pad_print(name):
    v = variant_named(name)
    p = block(v.pad_size, v.pad_size, v.thickness + PRELOAD)
    inside = v.pad_size - 2 * v.wall_skin
    void = block(inside, inside, v.core, FLOOR_SKIN + PRELOAD)
    supports = cq.Workplane(obj=floor_supports(v, inside)).translate((0, 0, PRELOAD))
    return p.cut(void.cut(supports)).cut(label_cut(name)).clean()


def pad_closed(name):
    return (pad_print(name).rotate((0, 0, 0), (1, 0, 0), 180)
            .translate((0, 0, fixture.FLOOR + fixture.CUP_HEIGHT + PRELOAD)))


def placements(name):
    variant_named(name)
    return ((f'cup_{name}', 'cup', (20., 20., 0.)),
            (f'pad_{name}', 'pad', (62., 20., 0.)))


def layout(name):
    variant_named(name)
    assembly = cq.Assembly(name=f'support_{name}')
    builders = {'cup': cup, 'pad': pad_print}
    for part, kind, position in placements(name):
        assembly.add(builders[kind](name), name=part, loc=cq.Location(position))
    return assembly
