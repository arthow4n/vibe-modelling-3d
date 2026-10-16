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
