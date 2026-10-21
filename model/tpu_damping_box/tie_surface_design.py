"""Seven side-wall slice probes; no full-box variants or print qualification.

44 mm wall length, 34 mm height, 4 mm solid end lands, 1.6 mm solid foot.
Discrete tie pitch/height/waist and 0.6 mm air gap follow approved B08.
Changing skins does not change that gap. W13 separately explores full-height N2.
"""
from dataclasses import dataclass
from math import cos, sin, pi, hypot
import cadquery as cq


@dataclass(frozen=True)
class Variant:
    name: str
    skin: float
    core: float
    joint: str

    @property
    def depth(self):
        return 2 * self.skin + self.core


VARIANTS = (
    Variant('T05', .5, .6, 'straight'),
    Variant('T09', .9, .6, 'straight'),
    Variant('T13', 1.3, .6, 'straight'),
    Variant('R09', .9, .6, 'rounded'),
    Variant('R13', 1.3, .6, 'rounded'),
    Variant('C13', 1.3, .6, 'swept'),
    Variant('W13', 1.3, 2.4, 'continuous'),
    Variant('T08', .8, .6, 'straight'),
    Variant('T12', 1.2, .6, 'straight'),
    Variant('T16', 1.6, .6, 'straight'),
    Variant('R16', 1.6, .6, 'rounded'),
    Variant('K16', 1.6, .6, 'swept'),
)
NAMES = tuple(v.name for v in VARIANTS)
INITIAL_NAMES = NAMES[:7]
REFINED_NAMES = NAMES[7:]
LENGTH, HEIGHT, LAND, FOOT = 44., 34., 4., 1.6
CENTRES = tuple(i * 4.4 for i in range(-3, 4))
TIE_Z = tuple(3.2 + i * 4.4 for i in range(7))


def variant_named(name):
    matches = [v for v in VARIANTS if v.name == name]
    if not matches:
        raise ValueError(f'Unknown variant {name!r}; choose {NAMES}')
    return matches[0]


def placement(name):
    variant_named(name)
    index = NAMES.index(name)
    return 28. + (index % 4) * 56., 20. + (index // 4) * 18.


def strip(points, tangents, width):
    """Constant normal-width polygon around a sampled smooth centreline."""
    left, right = [], []
    for (x, y), (dx, dy) in zip(points, tangents, strict=True):
        scale = width / (2 * hypot(dx, dy))
        left.append((x - dy * scale, y + dx * scale))
        right.append((x + dy * scale, y - dx * scale))
    return cq.Workplane('XY').polyline(left + list(reversed(right))).close()


def tie_profile(v):
    if v.joint == 'straight':
        return cq.Workplane('XY').center(0, v.core / 2).rect(.8, v.core + .2)
    if v.joint == 'rounded':
        # Elliptical shoulders: 1.6 mm root, 0.8 mm waist. Tangent to skins.
        side = []
        for i in range(41):
            a = pi * i / 80
            side.append((.4 + .4 * (1 - sin(a)), v.core / 2 * (1 - cos(a))))
        side += [(x, v.core - y) for x, y in reversed(side[:-1])]
        points = [(.8, -.1)] + side + [(.8, v.core + .1), (-.8, v.core + .1)]
        points += [(-x, y) for x, y in reversed(side)] + [(-.8, -.1)]
        return cq.Workplane('XY').polyline(points).close()
    if v.joint == 'swept':
        # Cubic Bezier centreline: both roots tangent to their skins in XY.
        points, tangents = [], []
        for i in range(97):
            t = i / 96
            x = -1.2 * (1-t)**3 + 1.2 * t**3
            y = v.core * (3*t*t - 2*t*t*t)
            dx = 3.6 * ((1-t)**2 + t*t)
            dy = 6 * v.core * t * (1-t)
            points.append((x, y)); tangents.append((dx, dy))
        return strip(points, tangents, .8)
    raise ValueError(f'{v.joint!r} does not define discrete ties')


def continuous_profile(v):
    points, tangents = [], []
    for i in range(577):
        x = -18 + 36 * i / 576
        a = 2*pi*(x+18)/6
        points.append((x, v.core / 2 * (1-cos(a))))
        tangents.append((1., v.core * pi / 6 * sin(a)))
    return strip(points, tangents, .8)


def check_tie_bridge(v, shape):
    """Check the final body's intended core crossings, not just solid validity."""
    if v.joint == 'continuous':
        witnesses = [(x, v.skin+v.core/2*(1-cos(2*pi*(x+18)/6)), 3.2)
                     for x in (-2.8,-1.5,-.2,.2,1.5,2.8)]
    elif v.joint == 'swept':
        witnesses = [(-1.2*(1-t)**3+1.2*t**3, v.skin+v.core*(3*t*t-2*t*t*t), 3.2)
                     for t in (.05,.5,.95)]
    else:
        witnesses = [(0,v.skin+v.core*f,3.2) for f in (.05,.5,.95)]
    solid = shape.val()
    if not all(solid.isInside(cq.Vector(*p),1e-6) for p in witnesses):
        raise ValueError(f'{v.name}: intended tie/web does not bridge both skins')
    if v.joint != 'continuous':
        for p in ((0,v.skin+v.core/2,4.4),(2.2,v.skin+v.core/2,3.2)):
            if solid.isInside(cq.Vector(*p),1e-6):
                raise ValueError(f'{v.name}: intended discrete-tie air space is filled')


def wall(name):
    v = variant_named(name)
    body = cq.Workplane('XY').box(LENGTH, v.depth, HEIGHT, centered=(True, False, False))
    core = (cq.Workplane('XY').box(LENGTH-2*LAND, v.core, HEIGHT-FOOT,
                                 centered=(True, False, False))
            .translate((0, v.skin, FOOT)))
    if v.joint == 'continuous':
        supports = continuous_profile(v).extrude(HEIGHT-FOOT).translate((0, v.skin, FOOT))
    else:
        one = tie_profile(v).extrude(.8)
        supports = cq.Compound.makeCompound([
            one.val().translate((x, v.skin, z-.4)) for x in CENTRES for z in TIE_Z])
        supports = cq.Workplane(obj=supports)
    result = body.cut(core.cut(supports)).clean()
    check_tie_bridge(v, result)
    return result


def layout(names):
    if not names or len(set(names)) != len(names):
        raise ValueError('Select a nonempty set of distinct variant names')
    selected = tuple(variant_named(name) for name in names)
    assembly = cq.Assembly(name='tie_surface_slice_probes')
    for v in selected:
        x, y = placement(v.name)
        assembly.add(wall(v.name), name=v.name, loc=cq.Location((x, y, 0)))
    return assembly
