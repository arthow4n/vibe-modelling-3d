"""Thread motion, simple packing and construction, not crush or wet-grip ratings."""
import cadquery as cq
from assembly_geometry import Configuration,PairRequirement,sample_motion,check_pair
from cylinder_design import *


def construction(case):
    for name in ('base','lid'):
        p=case[name]
        assert p.val().isValid(),name
        assert len(p.solids().vals())==1,name
    assert thread_test(case).isValid()
    assert BODY_RADIUS-FLUTE_DEPTH-INNER_RADIUS>=2.0
    assert COLLAR_RADIUS-FLUTE_DEPTH-(NECK_RADIUS+THREAD_DEPTH+RADIAL_CLEARANCE)>=2.0
    assert HEIGHT-2*FLOOR >= 255+4
    assert NECK_TOP<256 and HEIGHT-SEAM<256


def packing(case):
    items=references()
    for name,p in items.items():
        for host in (case['base'],case['lid']):
            check_pair(host,p,PairRequirement('Plain cavity clears '+name,max_overlap_mm3=1e-5)).require_passed()
    check_pair(items['handle'],items['tube'],PairRequirement('Brush and conservative tube have separation',min_gap_mm=.49)).require_passed()


def thread_motion(case):
    config=Configuration.explicit(assembly(case,opening_degrees=0,loaded=False),name='closed')
    sweep=sample_motion(config,'upper_half','lower_half',PairRequirement(
        'Prescribed helical opening clears threads',max_overlap_mm3=1e-5),
        samples=range(0,1801,30),transform=lambda angle:
            cq.Location((0,0,PITCH*angle/360))*cq.Location((0,0,0),(0,0,angle)),
        parameter='opening',units='degrees')
    if not sweep.calculation_completed:
        from product_verification import CalculationInconclusive
        raise CalculationInconclusive(str(sweep.to_dict()['first_failure']))
    assert sweep.status=='passed',('Thread path',sweep.to_dict()['first_failure'])
    sample_motion(config,'upper_half','lower_half',PairRequirement(
        'Unturned axial pull meets thread flanks',min_overlap_mm3=1),
        samples=(.8,),transform=lambda z:cq.Location((0,0,z)),parameter='axial_pull',units='mm').require_passed()
    # Once threads disengage, a straight lift clears the full attached brush.
    raised=case['lid'].rotate((0,0,0),(0,0,1),1080).translate((0,0,9))
    contents=list(references().values())
    for z in (0,3,8,16,32,64,96,128,140):
        p=raised.translate((0,0,z))
        check_pair(p,case['base'],PairRequirement('Cap lift after disengagement',max_overlap_mm3=1e-5)).require_passed()
        for item in contents:
            check_pair(p,item,PairRequirement('Plain cap clears loaded contents during lift',max_overlap_mm3=1e-5)).require_passed()
    return sweep.to_dict()


if __name__=='__main__':
    case=build()
    construction(case);print('Cylinder construction pass',flush=True)
    packing(case);print('Cylinder packing pass',flush=True)
    thread_motion(case);print('Cylinder thread/lift checks pass',flush=True)
