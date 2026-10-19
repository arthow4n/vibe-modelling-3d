"""Reject spatially poor hinges despite nominal motion/capture success."""
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import spine_design as d
import spine_verification as v


def test_full_and_mini_cavities_clear_through_flat_opening_with_negative_reference():
    v.motion()


def test_flush_mount_needs_actual_heads_and_keeps_flat_open_floor_pose():
    v.mounting_geometry()


def test_spine_plan_keeps_original_intent_and_explicit_new_spatial_requirements():
    from verification import make_plan
    p=make_plan('spine-c8-mini');p.validate()
    assert {'brush.fit','closure.secure','hinge.clear-cavity','hinge.flat-open'}<={r.id for r in p.requirements}
    with pytest.raises(ValueError):d.build('unselected',size=d.MINI)
