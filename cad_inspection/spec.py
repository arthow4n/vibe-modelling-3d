"""Object-owned, resolved inspection recipes. Coordinates and lengths are mm."""
from dataclasses import asdict, dataclass
import math
import re

import cadquery as cq


PRESETS = {
    'isometric': (1, -1, 1), 'isometric_back': (-1, 1, 1),
    'front': (0, -1, 0), 'back': (0, 1, 0),
    'left': (-1, 0, 0), 'right': (1, 0, 0),
    'top': (0, 0, 1), 'bottom': (0, 0, -1),
}


def vector(value):
    value = tuple(value)
    if len(value) != 3 or any(not math.isfinite(x) for x in value):
        raise ValueError('Expected three finite coordinates')
    return cq.Vector(*value)


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise ValueError('Colors must be #RRGGBB')
    return value


def safe_name(value):
    if not isinstance(value, str) or value in ('sheet', 'all') or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', value):
        raise ValueError('Inspection names require letters, digits, underscores or hyphens')
    return value


@dataclass(frozen=True)
class Camera:
    """Direction FROM the subject toward the viewer; up is a world reference."""
    direction: tuple
    up: tuple = (0, 0, 1)

    def __post_init__(self):
        d, u = vector(self.direction), vector(self.up)
        if d.Length == 0 or u.Length == 0 or u.normalized().cross(d.normalized()).Length < 1e-10:
            raise ValueError('Camera direction/up must be nonzero and nonparallel')
        object.__setattr__(self, 'direction', d.toTuple())
        object.__setattr__(self, 'up', u.toTuple())

    @classmethod
    def named(cls, name):
        return cls(PRESETS[name], (0, 1, 0) if name in ('top', 'bottom') else (0, 0, 1))

    @classmethod
    def look_at(cls, eye, target, *, up=(0, 0, 1)):
        return cls((vector(eye)-vector(target)).toTuple(), up)

    @property
    def axes(self):
        d = vector(self.direction).normalized()
        right = vector(self.up).cross(d).normalized()
        return right, d.cross(right).normalized(), d

    def project(self, point):
        p = vector(point)
        return tuple(axis.dot(p) for axis in self.axes)

    def matrix(self):
        from OCP.gp import gp_Trsf
        trsf = gp_Trsf()
        trsf.SetValues(*[v for axis in self.axes for v in (*axis.toTuple(), 0)])
        return cq.Matrix(trsf)


@dataclass(frozen=True)
class Anchor:
    """Point in a named component's authored geometry frame, before its Location."""
    component: str
    point: tuple

    def __post_init__(self):
        if not isinstance(self.component, str) or not self.component:
            raise ValueError('Anchor requires an exact component path')
        object.__setattr__(self, 'point', vector(self.point).toTuple())


def point(value):
    return value if isinstance(value, Anchor) else vector(value).toTuple()


@dataclass(frozen=True)
class Region:
    minimum: tuple
    maximum: tuple
    component: str | None = None

    def __post_init__(self):
        object.__setattr__(self, 'minimum', vector(self.minimum).toTuple())
        object.__setattr__(self, 'maximum', vector(self.maximum).toTuple())
        if any(a >= b for a, b in zip(self.minimum, self.maximum)):
            raise ValueError('Region needs positive extent on every axis')
        if self.component is not None and (not isinstance(self.component, str) or not self.component):
            raise ValueError('Region component must be an exact component path')

    @classmethod
    def around(cls, center, size):
        c, s = vector(center.point if isinstance(center, Anchor) else center), vector(size)
        return cls((c-s/2).toTuple(), (c+s/2).toTuple(),
                   center.component if isinstance(center, Anchor) else None)

    def corners(self):
        from itertools import product
        values = tuple(product(*zip(self.minimum, self.maximum)))
        return tuple(Anchor(self.component, p) for p in values) if self.component else values


@dataclass(frozen=True)
class Frame:
    region: Region | None = None
    margin_mm: float = 2

    def __post_init__(self):
        if self.region is not None and not isinstance(self.region, Region):
            raise TypeError('Frame region must be Region')
        if not math.isfinite(self.margin_mm) or self.margin_mm < 0:
            raise ValueError('Frame margin must be finite and nonnegative')


@dataclass(frozen=True)
class Section:
    origin: tuple
    normal: tuple
    mode: str  # planar or cutaway
    keep: str = 'negative'

    def __post_init__(self):
        object.__setattr__(self, 'origin', vector(self.origin).toTuple())
        object.__setattr__(self, 'normal', vector(self.normal).toTuple())
        if vector(self.normal).Length == 0:
            raise ValueError('Section normal must be nonzero')
        if self.mode not in ('planar', 'cutaway') or self.keep not in ('negative', 'positive'):
            raise ValueError('Section needs planar/cutaway mode and negative/positive retained side')


@dataclass(frozen=True)
class Label:
    point: tuple | Anchor
    text: str
    offset_px: tuple = (18, -18)
    color: str = '#943b28'

    def __post_init__(self):
        object.__setattr__(self, 'point', point(self.point))
        object.__setattr__(self, 'offset_px', tuple(self.offset_px))
        color(self.color)
        if not isinstance(self.text, str) or not self.text:
            raise ValueError('Label text required')
        if len(self.offset_px) != 2 or any(not math.isfinite(v) for v in self.offset_px):
            raise ValueError('Label offset needs two finite pixel coordinates')


@dataclass(frozen=True)
class Arrow:
    start: tuple | Anchor
    end: tuple | Anchor
    text: str = ''
    color: str = '#943b28'

    def __post_init__(self):
        object.__setattr__(self, 'start', point(self.start))
        object.__setattr__(self, 'end', point(self.end))
        color(self.color)
        if not isinstance(self.text, str):
            raise TypeError('Arrow text must be a string')


@dataclass(frozen=True)
class Highlight:
    region: Region
    text: str = ''
    color: str = '#943b28'

    def __post_init__(self):
        if not isinstance(self.region, Region):
            raise TypeError('Highlight requires Region')
        color(self.color)
        if not isinstance(self.text, str):
            raise TypeError('Highlight text must be a string')


@dataclass(frozen=True)
class View:
    camera: Camera
    frame: Frame = Frame()
    section: Section | None = None
    components: tuple = ()  # empty means whole subject
    colors: tuple = ()  # (exact component path, #RRGGBB) pairs
    annotations: tuple = ()
    show_hidden: bool = False

    def __post_init__(self):
        object.__setattr__(self, 'components', tuple(self.components))
        object.__setattr__(self, 'colors', tuple(tuple(pair) for pair in self.colors))
        object.__setattr__(self, 'annotations', tuple(self.annotations))
        if not isinstance(self.camera, Camera) or not isinstance(self.frame, Frame):
            raise TypeError('View requires Camera and Frame')
        if self.section is not None and not isinstance(self.section, Section):
            raise TypeError('Expected Section')
        if len(set(self.components)) != len(self.components):
            raise ValueError('Duplicate component selection')
        if len(dict(self.colors)) != len(self.colors):
            raise ValueError('Duplicate component color')
        for name, value in self.colors:
            if not isinstance(name, str):
                raise TypeError('Color component path must be a string')
            color(value)
        if any(not isinstance(a, (Label, Arrow, Highlight)) for a in self.annotations):
            raise TypeError('Unknown annotation')
        if not isinstance(self.show_hidden, bool):
            raise TypeError('show_hidden must be boolean')


@dataclass(frozen=True)
class Inspection:
    subject: object
    view: View
    purpose: str
    title: str = ''
    question_ids: tuple = ()

    def __post_init__(self):
        object.__setattr__(self, 'question_ids', tuple(self.question_ids))
        if not isinstance(self.view, View) or not isinstance(self.purpose, str) or not self.purpose:
            raise ValueError('Inspection needs a View and explicit purpose')
        if not isinstance(self.title, str) or any(not isinstance(q, str) or not q for q in self.question_ids):
            raise ValueError('Title and question IDs must be strings')


def view_to_dict(view):
    """JSON-compatible recipe, including explicit annotation discriminators."""
    result = asdict(view)
    kinds = {Label: 'label', Arrow: 'arrow', Highlight: 'highlight'}
    result['annotations'] = [dict(kind=kinds[type(a)], **asdict(a)) for a in view.annotations]
    return result


def view_from_dict(data):
    """Strict JSON boundary for quick views, using the same recipe primitives."""
    data = dict(data)
    if isinstance(data.get('camera'), str):
        data['camera'] = Camera.named(data['camera'])
    else:
        data['camera'] = Camera(**data['camera'])
    if 'frame' in data:
        frame = dict(data['frame'])
        if frame.get('region') is not None:
            frame['region'] = Region(**frame['region'])
        data['frame'] = Frame(**frame)
    if data.get('section') is not None:
        data['section'] = Section(**data['section'])
    annotations = []
    for raw in data.pop('annotations', ()):
        raw = dict(raw); kind = raw.pop('kind')
        for key in ('point', 'start', 'end'):
            if isinstance(raw.get(key), dict):
                raw[key] = Anchor(**raw[key])
        if kind == 'highlight':
            raw['region'] = Region(**raw['region'])
        annotations.append({'label': Label, 'arrow': Arrow, 'highlight': Highlight}[kind](**raw))
    data['annotations'] = tuple(annotations)
    data['components'] = tuple(data.get('components', ()))
    data['colors'] = tuple(dict(data.get('colors', {})).items())
    return View(**data)
