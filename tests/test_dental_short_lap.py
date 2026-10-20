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
    assert now['closure.side-hit'].acceptance_criteria == ('Knocks and bumps inside a travel bag',)
    assert not any(rid == 'closure.side-hit' for check in plan.checks
                   if check.id in ('short-lap.CAD','short-lap.side','short-lap.comparison')
                   for rid,qid in check.targets), (
        'Static bearing stiffness and centered-pull screens cannot qualify lateral-impact retention')
    assert not any(target in physical for check in plan.checks for target in check.targets)
    assert not plan.retained, 'Old sample print results cannot qualify this full prototype'


def test_bad_overlap_fails_before_cad_construction():
    with pytest.raises(ValueError,match='Undeclared overlap'):
        design.build(2.4)
    with pytest.raises(ValueError,match='Unknown variant'):
        make_plan('slim-short-lap-typo')


@pytest.mark.parametrize('axis,index', [('x',0),('y',1)])
def test_lateral_fixture_does_not_hold_the_cap_closed_axially(axis,index):
    from short_lap_lateral import question
    q = question(axis,mesh=2.5,increment=.02,penalty=20000.)
    assert q.motion.displacement_mm[index] == 8.
    assert q.motion.displacement_mm[2] is None
    assert all(s.displacement_mm[2] is None for s in q.supports)
    assert all(f.force_N[2] == -.05 for f in q.forces)
    assert q.mating_parts[0].motion is None, 'Both mating shells must deform'
    assert q.mating_parts[0].material == q.material


def test_lateral_fixture_rejects_undeclared_axis():
    from short_lap_lateral import question
    with pytest.raises(ValueError):
        question('diagonal',mesh=2.5,increment=.02,penalty=20000.)


@pytest.mark.parametrize('axis,normal', [('x',1),('y',0)])
def test_seated_half_fixture_preserves_free_axial_motion_and_force_scaling(axis,normal):
    from short_lap_lateral import seated_question
    q = seated_question(axis,mesh=2.5,increment=.02,penalty=20000.)
    assert q.motion.progress == ((0.,0.),(.1,0.),(1.,1.))
    assert q.motion.displacement_mm[2] is None
    assert all(s.displacement_mm[2] is None for s in q.supports)
    assert q.supports[0].displacement_mm[normal] == 0
    assert q.forces[0].force_N == (0.,0.,-.025)
    assert len(q.mating_parts[0].supports) == 2
    if axis == 'y':
        assert not any(name.endswith('_negative') for name in q.observations)


@pytest.mark.parametrize('axis,index', [('x',0),('y',1)])
def test_pickup_pose_moves_cap_loading_regions_together_without_axial_restraint(axis,index):
    from short_lap_lateral import pickup_question,seated_question
    before = seated_question(axis,mesh=2.5,increment=.02,penalty=20000.)
    after = pickup_question(axis,mesh=2.5,increment=.02,penalty=20000.)
    assert after.motion.region.lower[index]-before.motion.region.lower[index] == pytest.approx(.1)
    assert after.forces[0].region == after.motion.region
    assert after.motion.displacement_mm[2] is None
    assert all(s.displacement_mm[2] is None for s in after.supports)
    assert after.forces[0].force_N == before.forces[0].force_N


def test_unconverged_native_attempt_is_not_an_accepted_snapshot(tmp_path):
    from short_lap_lateral_view import accepted_times
    sta = tmp_path/'analysis.sta'
    sta.write_text(' 1 6 1U 60 .10 .10 .02\n 1 6 2 38 .12 .12 .02\n')
    assert accepted_times(sta) == [.12]


def test_partial_contact_snapshots_do_not_pass_coupled_release_obligation():
    from product_verification import Status
    plan = make_plan('slim-short-lap')
    check = next(c for c in plan.checks if c.id == 'short-lap.lateral-release')
    assert check.targets == (('closure.side-hit','coupled-release'),)
    assert all(e.status == Status.INCONCLUSIVE for e in check.run())
