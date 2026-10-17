"""30 mm closed-core finish coupons; dimensions in mm, no publication on import."""
from dataclasses import dataclass
import cadquery as cq
from skin_design import variant_named as closed_variant

SIZE = 30.0
FRAME = 1.2
LABEL_BAND = 10.0
FIELD_X = SIZE - 2 * FRAME
FIELD_Y = SIZE - FRAME - LABEL_BAND
FIELD_CY = (LABEL_BAND - FRAME) / 2
BASE = closed_variant('S16')
CORE = BASE.core
BACKING = BASE.backing
WEB = BASE.web
LABEL_DEPTH = .2
LABEL_SIZE = 11.0


@dataclass(frozen=True)
class SurfaceVariant:
    name: str
    skin: float
    pitch: float
    pattern: str

    @property
    def thickness(self):
        return BACKING + CORE + self.skin


VARIANTS = {
    'F0': SurfaceVariant('F0', BASE.skin, 4.4, 'straight'),
    'F1': SurfaceVariant('F1', .6, 4.4, 'straight'),
    'F2': SurfaceVariant('F2', .8, 4.4, 'straight'),
    'F3': SurfaceVariant('F3', BASE.skin, 3.2, 'straight'),
    'F4': SurfaceVariant('F4', BASE.skin, 2.4, 'straight'),
    'F5': SurfaceVariant('F5', BASE.skin, 4.4, 'grid'),
    'F6': SurfaceVariant('F6', BASE.skin, 4.4, 'shoulders'),
    'F7': SurfaceVariant('F7', BASE.skin, 4.4, 'solid'),
}
NAMES = tuple(VARIANTS)


def variant_named(name):
    if name not in VARIANTS:
        raise ValueError(f'Unknown surface coupon {name!r}; choose {NAMES}')
    return VARIANTS[name]


def block(x, y, height, z=0, cx=0, cy=0):
    return cq.Workplane('XY').box(x, y, height, centered=(True, True, False)).translate((cx, cy, z))


def centres(length, pitch):
    n = int((length / 2 - WEB / 2) / pitch)
    return tuple(i * pitch for i in range(-n, n + 1))


def label_cut(name):
    v = variant_named(name)
    return (cq.Workplane('XY').text(name, LABEL_SIZE, LABEL_DEPTH,
            font='DejaVu Sans Mono', kind='bold', combine=True)
            .translate((0, -SIZE / 2 + LABEL_BAND / 2, v.thickness - LABEL_DEPTH)))


def coupon(name):
    v = variant_named(name)
    # Only the vertical outside corners are rounded: full flat bed/top contact.
    p = block(SIZE, SIZE, v.thickness).edges('|Z').fillet(.6)
    if v.pattern != 'solid':
        void = block(FIELD_X, FIELD_Y, CORE, BACKING, cy=FIELD_CY)
        ribs = None
        for x in centres(FIELD_X, v.pitch):
            if v.pattern == 'shoulders':
                # Upper 0.6 mm grows 0.6 mm per side (45 degrees), reducing
                # the final roof span without adding an exposed outer ledge.
                section = [(-WEB/2, 0), (WEB/2, 0), (WEB/2, .2),
                           (WEB/2+.6, CORE), (-WEB/2-.6, CORE), (-WEB/2, .2)]
                r = (cq.Workplane('XZ').polyline(section).close()
                     .extrude(FIELD_Y / 2, both=True)
                     .translate((x, FIELD_CY, BACKING)))
            else:
                r = block(WEB, FIELD_Y, CORE, BACKING, x, FIELD_CY)
            ribs = r if ribs is None else ribs.union(r)
        if v.pattern == 'grid':
            for y in centres(FIELD_Y, v.pitch):
                ribs = ribs.union(block(FIELD_X, WEB, CORE, BACKING, cy=FIELD_CY+y))
        # Subtract only air; ribs remain connected to backing, roof and frame.
        p = p.cut(void.cut(ribs))
    return p.cut(label_cut(name)).clean()


def placements():
    return tuple((name, (18 + (i % 4) * 36, 18 + (i // 4) * 36, 0))
                 for i, name in enumerate(NAMES))


def layout():
    a = cq.Assembly(name='surface_coupons')
    for name, position in placements():
        a.add(coupon(name), name=name, loc=cq.Location(position))
    return a
