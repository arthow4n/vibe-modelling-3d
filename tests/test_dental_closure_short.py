"""A smaller coupon must not silently inherit full-size force evidence."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import closure_short_design as design
import closure_short_verification as verification
from verification import make_plan


def test_short_samples_preserve_interfaces_and_clear_separation_grips():
    rows=verification.cad()['cases']
    assert set(rows)==set(design.KINDS)
    assert all(not row['forces_inherited'] for row in rows.values())


def test_short_force_intent_has_no_inherited_long_fixture_strategy():
    plan=make_plan('research-short-closures')
    plan.validate()
    assert any(r.id=='research.force' for r in plan.requirements)
    assert all(c.id!='research.pull-proxy' for c in plan.checks)
    assert not any('force' in str(c.targets) for c in plan.checks)
    with pytest.raises(ValueError): design.build('shell_broad_typo')
