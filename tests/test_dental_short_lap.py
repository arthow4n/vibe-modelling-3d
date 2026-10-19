"""Protect current intent and keep unprinted retention separate from CAD evidence."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import short_lap_design as design
from verification import make_plan
from closure_short_verification import make_short_plan
from verification import REQUIREMENTS


def test_current_direction_preserves_intent_with_explicit_smaller_bite_supersession():
    plan = make_plan('slim-short-lap')
    plan.validate()
    old = {r.id:r for r in make_short_plan('research-short-closures',REQUIREMENTS).requirements}
    now = {r.id:r for r in plan.requirements}
    assert set(old) <= set(now)
    for id in set(old)-{'closure.end-retention'}:
        assert old[id] == now[id]
    assert now['closure.end-retention'].source.reference.startswith('notes/short_lap.md')
    assert any(d.id == 'hinge.abandoned' for d in plan.directives)
    physical = {(q.requirement_id,q.id) for q in plan.questions if q.mode == 'physical'}
    assert ('closure.secure','physical') in physical
    assert ('closure.side-hit','physical') in physical
    assert not any(rid == 'closure.side-hit' for check in plan.checks for rid,qid in check.targets), (
        'Static bearing stiffness and centered-pull screens cannot qualify lateral-impact retention')
    assert not any(target in physical for check in plan.checks for target in check.targets)
    assert not plan.retained, 'Old sample print results cannot qualify this full prototype'


def test_bad_overlap_fails_before_cad_construction():
    with pytest.raises(ValueError,match='Undeclared overlap'):
        design.build(2.4)
    with pytest.raises(ValueError,match='Unknown variant'):
        make_plan('slim-short-lap-typo')
