"""N2 cavity-root comparison with native spline edges, not polygonal facets."""
from math import sin, cos, pi, hypot
import cadquery as cq
import tie_surface_design as study

NAMES = ('WN13', 'WF13')


def position(name):
    if name not in NAMES:
        raise ValueError(f'Unknown N2 case {name!r}; choose {NAMES}')
    return (28. + 56*NAMES.index(name), 20.)


def wall(name):
    position(name)
    v = study.variant_named('W13')
    left, right = [], []
    for i in range(241):
        x = -18 + 36*i/240
        a = 2*pi*(x+18)/6
        y = v.core/2*(1-cos(a))
        dy = v.core*pi/6*sin(a)
        normal_scale = .4/hypot(1.,dy)
        left.append((x-dy*normal_scale, y+normal_scale))
        right.append((x+dy*normal_scale, y-normal_scale))
    profile = (cq.Workplane('XY').spline(left).lineTo(*right[-1])
               .spline(list(reversed(right[:-1])),includeCurrent=True).close())
    web = profile.extrude(study.HEIGHT-study.FOOT).translate((0,v.skin,study.FOOT))
    body = cq.Workplane('XY').box(study.LENGTH,v.depth,study.HEIGHT,centered=(True,False,False))
    core = (cq.Workplane('XY').box(study.LENGTH-2*study.LAND,v.core,study.HEIGHT-study.FOOT,
                                  centered=(True,False,False)).translate((0,v.skin,study.FOOT)))
    body = body.cut(core.cut(web)).clean()
    if name == 'WN13':
        return body
    roots = [e for e in body.edges().vals()
             if abs(e.endPoint().x-e.startPoint().x)<1e-6
             and abs(e.endPoint().y-e.startPoint().y)<1e-6
             and abs(e.Center().x) < study.LENGTH/2-study.LAND-1e-6
             and abs(e.Length()-(study.HEIGHT-study.FOOT)) < 1e-5
             and min(abs(e.Center().y-v.skin),abs(e.Center().y-v.skin-v.core)) < 1e-6]
    if not roots:
        raise ValueError('N2 root selection found no full-height core-plane junctions')
    return body.newObject(roots).fillet(.25)


def layout():
    assembly = cq.Assembly(name='N2_native_root_comparison')
    for name in NAMES:
        x,y = position(name)
        assembly.add(wall(name), name=name, loc=cq.Location((x,y,0)))
    return assembly
