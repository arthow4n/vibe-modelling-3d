"""Physical limiting cases: detect absent preload before printing a friction-only grip."""
import pytest
from physical_analysis.screening import elastic_friction_grip


@pytest.mark.parametrize('interference', [-.2, 0])
def test_clearance_or_touching_without_preload_cannot_hold(interference):
    answer = elastic_friction_grip(interference_mm=interference, contact_count=4)
    assert answer['normal_force_N'] == answer['friction_retention_N'] == 0
    assert answer['retention_screen_passes'] is False


def test_preload_with_unknown_material_is_not_a_holding_force_pass():
    answer = elastic_friction_grip(interference_mm=.2, contact_count=4)
    assert answer['preload_present'] and answer['spring_travel_mm'] == .2
    assert answer['normal_force_N'] is answer['friction_retention_N'] is answer['retention_screen_passes'] is None


def test_linear_contacts_and_coulomb_limit():
    # Four independently loaded 10 N/mm springs each displaced .2 mm.
    answer = elastic_friction_grip(interference_mm=.2, contact_count=4,
                                   stiffness_N_mm=10, friction_coefficient=.25,
                                   required_retention_N=1.5)
    assert answer['normal_force_N'] == pytest.approx(8)
    assert answer['friction_retention_N'] == pytest.approx(2)
    assert answer['retention_screen_passes'] is True
    assert elastic_friction_grip(interference_mm=.2, stiffness_N_mm=10,
                                 friction_coefficient=.25, required_retention_N=1)['retention_screen_passes'] is False


def test_frictionless_preloaded_contact_has_no_friction_capacity():
    answer = elastic_friction_grip(interference_mm=.2, friction_coefficient=0)
    assert answer['preload_present'] and answer['friction_retention_N'] == 0
    assert answer['retention_screen_passes'] is False


@pytest.mark.parametrize('kwargs', [dict(interference_mm=float('nan')),
    dict(interference_mm=.1, contact_count=0), dict(interference_mm=.1, contact_count=True),
    dict(interference_mm=.1, stiffness_N_mm=-1), dict(interference_mm=.1, friction_coefficient=-.1),
    dict(interference_mm=.1, friction_coefficient=float('inf'))])
def test_invalid_inputs_do_not_produce_a_grip_claim(kwargs):
    with pytest.raises(ValueError):
        elastic_friction_grip(**kwargs)


def test_actual_key_print_entry_rejects_gap_only_revision_before_building(monkeypatch):
    from pathlib import Path
    import importlib
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'model/filament_swatch_box_study'))
    keys=importlib.import_module('cap_i_grip_keys')
    # A proposed edit removes compression. The ordinary evaluator entry point
    # must stop before constructing/exporting a useless friction-grip layout.
    monkeypatch.setattr(keys,'PROJECTIONS',(.2,.2,.2))
    with pytest.raises(ValueError,match='actual seated preload'):
        keys.print_layout()


def test_actual_key_print_entry_checks_preload_after_seam_closes(monkeypatch):
    from pathlib import Path
    import importlib
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'model/filament_swatch_box_study'))
    keys=importlib.import_module('cap_i_grip_keys')
    monkeypatch.setattr(keys,'KEY_SEAM_GAP',.3)
    assert keys.PROJECTIONS[0]-keys.h.KEY_FIT_GAP>0  # nominal preload looks adequate
    assert keys.seated_interference(keys.PROJECTIONS[0])<0  # lost when blocks butt
    with pytest.raises(ValueError,match='actual seated preload'):
        keys.print_layout()
