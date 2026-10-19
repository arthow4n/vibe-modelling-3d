"""C6 needs positive shoulder capture and a trial tied to the shorter loop."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import clamshell_design as d
import clamshell_verification as v


def test_short_loop_rail_has_real_flat_capture_not_just_radial_overlap():
    a=v.cad()['hypotheses']['screw_pin']
    assert a['retaining_faces']['loop_normal']==[0,0,1]
    assert a['retaining_faces']['keeper_normal']==[0,0,-1]
    assert a['retaining_faces']['projected_contact_area_mm2']==pytest.approx(19.8)


def test_matching_trial_includes_the_entire_actual_shortened_loop():
    from c6_latch_test import sample
    p=d.build('screw_pin');coupon=sample()
    assert p['loop'].cut(coupon['lid']).val().Volume()<1e-5
    assert coupon['body'].cut(p['body']).val().Volume()<1e-5
    with pytest.raises(ValueError):d.build('unselected_hinge')


def test_architecture_supersession_preserves_active_secure_closure_intent():
    from verification import make_plan
    plan=make_plan('clamshell-c6');plan.validate()
    req={r.id:r for r in plan.requirements}
    assert 'closure.secure' in req and not plan.non_applicable
    assert req['closure.secure'].source.reference=='notes/clamshell_exploration.md'
