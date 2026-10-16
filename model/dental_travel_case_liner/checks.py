"""Application checks; physical installation and quietness stay unqualified."""
import math
import cadquery as cq
from assembly_geometry import PairRequirement, check_pair
import design as d
from model.dental_travel_case.m1_design import tongue, mirrored

FREE=PairRequirement('No interference with rigid shell, catches or other liner',max_overlap_mm3=.001)


def free(a,b):
    check_pair(a,b,FREE).require_passed()


def check_fit():
    rigid=d.rigid()
    body,cap=d.cup('body'),d.cup('cap')
    for liner in (body,cap):
        for shell in (rigid['body'],rigid['cap']):
            free(liner,shell)
    free(body,cap)
    for displacement in (0,d.D.release/2,d.D.release):
        for sign in (-1,1):
            leaf=mirrored(tongue(d.D,displacement),sign)
            free(body,leaf)
            free(cap,leaf)
    # The cap's normal axial removal must not snag the body liner.
    for lift in (.4,2,6,12,25,80):
        free(body,rigid['cap'].translate((0,0,lift)))
        free(body,cap.translate((0,0,lift)))
    assert check_pair(body.translate((1,0,0)),rigid['body'],FREE).status=='failed', 'Collision guard insensitive'


def inside(shape,point):
    return any(s.isInside(point,1e-6) for s in shape.Solids())


def check_profile():
    assert (d.BACKING,d.CORE,d.SKIN,d.WEB,d.PITCH)==(.4,.8,.4,.9,4.4)
    for part in ('body','cap'):
        p=d.cup(part).val()
        assert len(p.Solids())==1,'Cup must remain connected'
        z=d.D.floor+d.END_GAP if part=='body' else d.D.length-d.D.floor-d.END_GAP-d.THICKNESS
        for x in (-4.4,0,4.4):
            for depth in (.1,1.5):
                assert inside(p,(x,0,z+depth)),'Floor skin missing'
        assert not inside(p,(2.2,0,z+.8)),'Floor core filled'


def check_perimeters():
    """Test skins, voids and supporting ribs through flat and curved regions.

    The wire-based normal witnesses cover the ordinary rounded bends and the
    two concave notches. Transition zones have separately stated print limits.
    """
    counts={}
    for part,samples in (('body',(10.,150.,180.)),('cap',(190.,220.))):
        p=d.cup(part).val()
        for z in samples:
            wire=d.section_wire(d.envelope(part,.8),z)
            n=math.ceil(wire.Length()/d.PITCH)
            gaps=0
            for i in range(n):
                q=wire.positionAt((i+.5)/n)
                # Some short corner remainders are shared by adjacent normal
                # ribs. Require sampled air in every arc as well as on flats.
                if not inside(p,(q.x,q.y,z)):
                    gaps+=1
            assert gaps>=n*.7,('Excessive solid perimeter coverage',part,z,gaps,n)
            for edge in wire.Edges():
                if edge.geomType()!='CIRCLE':
                    continue
                air=[]
                for t in (.2,.4,.6,.8):
                    q=edge.positionAt(t)
                    air.append(not inside(p,(q.x,q.y,z)))
                assert any(air),('Rounded bend has no core',part,z,edge.Center().toTuple())
            counts[f'{part}:{z}']={'air_samples':gaps,'total':n}
    return counts
