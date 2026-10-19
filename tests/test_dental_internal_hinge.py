"""Protect whole mini-box motion and print pose, not just a loose latch wall."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import internal_hinge_verification as v


def test_internal_hinge_needs_rear_wall_redesign_and_retains_overtravel_limit():
    v.motion()


def test_complete_captive_box_has_clear_parts_and_both_panels_start_on_bed():
    v.mini_geometry()


def test_c7_keeps_dental_intent_while_declaring_minibox_scope():
    from verification import make_plan
    p=make_plan('hinge-c7-mini');p.validate()
    assert {'brush.fit','closure.secure','hinge.internal','trial.integrated'}<={r.id for r in p.requirements}
