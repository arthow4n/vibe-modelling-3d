"""Solid C controls, mm; same fixture and pad interface as the R2 support pairs.

No core subtraction or generated cellular structure. Print with 100% fill.
"""
from dataclasses import dataclass
import cadquery as cq
import design as fixture
import support_design as support


@dataclass(frozen=True)
class SolidVariant:
    name: str
    thickness: float

    @property
    def clear(self):
        return fixture.CUP_SIZE - 2*self.thickness

    @property
    def wall_height(self):
        return fixture.CUP_HEIGHT - self.thickness

    @property
    def pocket(self):
        # Preserve the R2 rim/pad interface, independent of lining thickness.
        return fixture.CUP_SIZE - 2*support.VARIANTS['B16'].wall_skin

    @property
    def pad_size(self):
        return self.pocket - 2*fixture.PAD_ALLOWANCE


VARIANTS = {'C12': SolidVariant('C12', 1.2), 'C16': SolidVariant('C16', 1.6)}
NAMES = tuple(VARIANTS)


def variant_named(name):
    if name not in VARIANTS:
        raise ValueError(f'Unknown solid control {name!r}; choose {NAMES}')
    return VARIANTS[name]


def label_cut(name, depth=support.LABEL_DEPTH):
    variant_named(name)
    main = cq.Workplane('XY').text(name, support.LABEL_SIZE, depth,
        font='DejaVu Sans Mono', kind='bold', combine=True)
    subtitle = cq.Workplane('XY').center(0, -11).text('SOLID', 6, depth,
        font='DejaVu Sans Mono', kind='bold', combine=True)
    return main.union(subtitle).mirror('YZ')


def cup(name):
    v = variant_named(name)
    p = fixture.block(fixture.CUP_SIZE, fixture.CUP_SIZE, fixture.CUP_HEIGHT)
    p = p.cut(fixture.block(v.clear, v.clear, fixture.CUP_HEIGHT, v.thickness))
    p = p.cut(fixture.block(v.pocket, v.pocket, v.thickness+1, v.wall_height))
    # Flat square interfaces preserve the R2 fit and the controlled comparison.
    return p.cut(label_cut(name)).clean()


def pad_print(name):
    v = variant_named(name)
    return fixture.block(v.pad_size, v.pad_size, v.thickness+support.PRELOAD).cut(label_cut(name)).clean()


def pad_closed(name):
    return (pad_print(name).rotate((0,0,0), (1,0,0), 180)
            .translate((0,0,fixture.FLOOR+fixture.CUP_HEIGHT+support.PRELOAD)))


def layout(name):
    variant_named(name)
    assembly = cq.Assembly(name=f'solid_{name}')
    builders = {'cup': cup, 'pad': pad_print}
    for part, kind, position in support.placements('B16'):
        assembly.add(builders[kind](name), name=part.replace('B16',name),
                     loc=cq.Location(position))
    return assembly
