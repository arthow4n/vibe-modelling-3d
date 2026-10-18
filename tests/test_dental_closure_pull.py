"""The force reduction must distinguish stored energy from opening resistance."""
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
from closure_research_pull import spring_path, cap_question, section_segments, profile_retraction, required_retraction
import closure_research_design as design


def test_constant_compression_has_energy_but_no_frictionless_holding_force():
    travel = np.linspace(0, 2, 21)
    row = spring_path(travel, np.full(21, .5), .2, 2)
    assert row['barrier_Nmm'] > 0
    assert max(abs(v) for v in row['force_N']) < 1e-12
    empty = spring_path(travel, np.zeros(21), .2, 2)
    assert empty['peak_force_N'] == 0 and empty['barrier_Nmm'] == 0


def test_deformable_receiver_and_lost_catch_reduce_the_same_barrier():
    travel = np.linspace(0, 1, 101)
    rigid_cap = spring_path(travel, .5*travel, .2, 2)
    flexible_cap = spring_path(travel, .5*travel, .4, 2)
    one_catch = spring_path(travel, .5*travel, .4, 1)
    assert flexible_cap['peak_force_N'] == pytest.approx(rigid_cap['peak_force_N']/2)
    assert one_catch['barrier_Nmm'] == pytest.approx(flexible_cap['barrier_Nmm']/2)
    assert flexible_cap['force_N'][-2] == pytest.approx(2*.5**2*.99/.4)


def test_free_play_reduces_undamped_deadweight_threshold_without_changing_ramp():
    travel = np.linspace(0, 3, 301)
    no_slack = spring_path(travel, np.minimum(travel,1)*.5, .4, 2)
    slack = spring_path(travel, np.clip(travel-1,0,1)*.5, .4, 2)
    assert slack['peak_force_N'] == pytest.approx(no_slack['peak_force_N'])
    assert slack['undamped_seated_release_force_N'] < no_slack['undamped_seated_release_force_N']
    assert slack['undamped_seated_release_force_N'] < slack['peak_force_N']


def test_cap_selection_rejects_unanalysed_ring_instead_of_inheriting_force():
    with pytest.raises(ValueError):
        cap_question('perimeter_bead')


def test_actual_profile_agrees_with_3D_clearance_and_excess_gap_removes_barrier():
    parts = design.build('shell_broad')
    radius = design.D.sleeve_depth/2
    bump = design.local_bump(radius, design.D.latch_z, design.D.bump_width, design.D.detent).val()
    cap = parts['cap'].val()
    tooth = section_segments(bump, 1, radius)
    receiver = section_segments(cap, 1, radius)
    for travel in (0., 1., 2., 3., 6.):
        estimate = profile_retraction(tooth, receiver, travel, 0.)
        assert estimate == pytest.approx(required_retraction(cap, bump, travel, 1, 0.), abs=.001)
        assert profile_retraction(tooth, receiver, travel, .65) == 0.
    assert profile_retraction(tooth, receiver, 2., 0.) > 0
    assert profile_retraction(tooth, receiver, 6., 0.) == 0
