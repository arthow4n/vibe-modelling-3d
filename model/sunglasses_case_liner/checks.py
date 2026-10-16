"""Targeted accessory checks against the unchanged complete accepted case."""
import cadquery as cq
from assembly_geometry import PairRequirement, check_pair
import design as d

FREE = PairRequirement('Liner clears rigid components and other insert',max_overlap_mm3=.001)


def free(a,b):
    check_pair(a,b,FREE).require_passed()


def check_profile():
    p = d.cup()
    length,width,height,radius = d.dimensions()
    # These are explicit profile/coverage checks, not generic export audits.
    assert (d.BACKING,d.CORE,d.SKIN,d.WEB,d.PITCH)==(.4,.8,.4,.9,4.4), 'S16 local profile changed'
    assert len(p.solids().vals())==1, 'Insert must remain connected'
    air = d.block(2.8,10,.6,2.2,z=.5)
    free(p,air)
    for z in (.05,1.25):
        skin = d.block(10,10,.3,z=z)
        assert skin.cut(p).val().Volume()<.001, 'Continuous floor skin missing'
    for sign in (-1,1):
        # Long walls: continuous skins and an open channel halfway between ribs.
        for depth in (.05,1.25):
            skin = d.block(10,.3,10,0,sign*(width/2-depth-.15),5)
            assert skin.cut(p).val().Volume()<.001, 'Continuous side skin missing'
        air = d.block(2.8,.6,10,2.2,sign*(width/2-.8),5)
        free(p,air)
    # Rounded residual contents envelope excludes TPU, including corner transitions.
    cavity = d.rounded(length-2*d.THICKNESS,width-2*d.THICKNESS,
                       height,radius-d.THICKNESS,d.THICKNESS)
    free(p,cavity)


def check_fit():
    m = d.case()
    body,lid = d.installed(180)
    for liner in (body,lid):
        for rigid in (m['body'],m['lid'],m['keeper']):
            free(liner,rigid)
    free(body,lid)
    # Straight drop into each open half: includes its complete shell/mechanisms.
    open_body,open_lid = d.installed(0)
    for shift in (0, .5, 5, 20, 35):
        for liner in (open_body,open_lid):
            for rigid in (m['body'],m['open_lid'],m['keeper']):
                free(liner.translate((0,0,shift)),rigid)


def check_motion():
    m = d.case()
    body,_ = d.installed(0)
    for angle in range(0,181,10):
        _,lid = d.installed(angle)
        free(lid,body)
        for rigid in (m['body'],m['keeper']):
            free(lid,rigid)
        free(body,m['close'](m['open_lid'],angle))
    # Deliberately displaced insert must trip the same shell-clearance criterion.
    bad = body.translate((1,0,0))
    assert check_pair(bad,m['body'],FREE).status=='failed', 'Missing collision sensitivity'


def require_corner_coverage(part):
    """Sample air, both skins and radial ribs at every bend and three heights."""
    from math import cos, sin, radians
    _,_,height,radius = d.dimensions()
    core_radius = radius-d.BACKING-d.CORE/2
    for sx,sy,cx,cy in d.corner_locations():
        for z in (2.,15.,height-.6):
            for angle in (15,45,75):
                co,si=cos(radians(angle)),sin(radians(angle))
                air = cq.Workplane('XY').sphere(.1).translate((
                    cx+sx*core_radius*co,cy+sy*core_radius*si,z))
                assert air.intersect(part).val().Volume()<1e-6, (
                    'Required corner air core is solid',sx,sy,angle,z)
                for r in (radius-d.BACKING/2,radius-d.THICKNESS+d.SKIN/2):
                    skin=cq.Workplane('XY').sphere(.1).translate((cx+sx*r*co,cy+sy*r*si,z))
                    assert skin.cut(part).val().Volume()<1e-6, 'Corner skin missing'
            for angle in (30,60):
                rib=cq.Workplane('XY').sphere(.1).translate((
                    cx+sx*core_radius*cos(radians(angle)),
                    cy+sy*core_radius*sin(radians(angle)),z))
                assert rib.cut(part).val().Volume()<1e-6, 'Corner rib missing'


def check_corner_coverage():
    require_corner_coverage(d.cup())
    try:
        require_corner_coverage(d.solid_corner_cup())
    except AssertionError as exc:
        assert 'Required corner air core is solid' in str(exc), 'Wrong negative-control failure'
    else:
        raise AssertionError('Original solid corner must fail coverage')
