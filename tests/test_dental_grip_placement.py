"""Decision-relevant layout failures and preservation of the user's intent."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
from grip_placement import GripLayout,LAYOUTS,describe,dimensions,selected_layout
from verification import make_plan
from product_verification import Status


def test_selected_layout_keeps_functional_regions_free_through_cap_lift():
    result=selected_layout();m=result['metrics']
    assert result['accepted']
    assert m['cap_extent_mm']==(45.,65.)
    assert m['body_extent_mm']==(-40.,-20.)
    assert m['cap_backing_gap_mm']==6.
    assert m['cap_closed_end_gap_mm']==25.
    assert m['cap_end_round_gap_mm']==21.
    assert [p['axial_band_gap_mm'] for p in result['travel']]==[65.,71.,95.,155.]
    assert all(p['body_center_mm']==-30. for p in result['travel'])


def test_layout_rejects_backing_overlap_without_rejecting_usable_alternatives():
    d=dimensions();near=describe(LAYOUTS['near'],d)
    assert not near['accepted']
    assert near['metrics']['cap_backing_gap_mm']==-9.
    assert not near['checks']['cap_beyond_backing']
    # No invented 5 mm minimum merely to make the previous position fail.
    assert describe(LAYOUTS['previous'],d)['accepted']
    assert describe(LAYOUTS['far'],d)['accepted']


@pytest.mark.parametrize('layout,failed',[
    (GripLayout(85.,-30.,20.,.7),'cap_before_end_round'),
    (GripLayout(55.,0.,20.,.7),'body_below_seam'),
    (GripLayout(55.,-170.,20.,.7),'body_above_bottom_round'),
])
def test_real_layout_conflicts_change_the_decision(layout,failed):
    result=describe(layout,dimensions())
    assert not result['accepted']
    assert not result['checks'][failed]


def test_replacing_strategy_preserves_intent_and_does_not_depend_on_native_search(monkeypatch):
    import grip_human_verification as native
    def unexpected(*args):raise AssertionError('Optional diagnostic cannot gate the layout')
    monkeypatch.setattr(native,'evaluate',unexpected)
    parent=make_plan('slim-short-lap-three-line')
    plan=make_plan('grip-band-placement');plan.validate()
    assert plan.requirements[:-1]==parent.requirements
    requirement=plan.requirements[-1]
    assert requirement.id=='form.grip-placement'
    assert requirement.text=='Provide useful exterior grips for separating cap/body while holding the case upright or diagonal'
    questions=[q for q in plan.questions if q.requirement_id==requirement.id]
    assert {(q.id,q.mode) for q in questions}=={('layout','dimensional'),('use','physical')}
    assert any(d.id=='grip.upright' for d in plan.directives)
    assert len(plan.checks)==1
    evidence=plan.checks[0].run()[0]
    assert evidence.status==Status.PASS
    assert evidence.targets==(('form.grip-placement','layout'),)
