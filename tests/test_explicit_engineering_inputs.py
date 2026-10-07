"""Consequential engineering choices cannot be supplied by omitted inputs."""
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest
from product_verification import Question
from physical_analysis import AnalysisCase, ContactQuestion, ManufacturingAssumption, QuestionStudy
from physical_analysis.studies import compare_results

ROOT = Path(__file__).resolve().parents[1]


def test_evidence_category_is_required_even_for_a_plausible_physical_question():
    with pytest.raises(TypeError, match='mode'):
        Question('feel', 'fixture.use', 'Comfortable opening')
    assert Question('feel', 'fixture.use', 'Comfortable opening', 'physical').mode == 'physical'
    for mode in (None, True, 12, ''):
        with pytest.raises(ValueError, match='evidence category'):
            Question('feel', 'fixture.use', 'Comfortable opening', mode)


def test_comparison_requires_and_retains_the_actual_acceptance_threshold():
    coarse = SimpleNamespace(metrics={'force': 100}, require_completed=lambda: None)
    refined = SimpleNamespace(metrics={'force': 104}, require_completed=lambda: None)
    with pytest.raises(TypeError, match='relative_tolerance'):
        compare_results(coarse, refined, metrics=['force'])
    for limit, expected in ((.05, True), (.02, False)):
        answer = compare_results(coarse, refined, metrics=['force'], relative_tolerance=limit)['force']
        assert answer['passes'] is expected
        assert answer['relative_tolerance'] == limit
    with pytest.raises(TypeError, match='relative_tolerance'):
        QuestionStudy(object(), 'Force accuracy changes the decision', ('force',))


def test_section_acceptance_requires_a_limit_before_reading_paths(tmp_path):
    assert ManufacturingAssumption('Unmeasured process').review()['local_solid_paths_established'] is None
    with pytest.raises(ValueError, match='explicit uncovered width limit'):
        ManufacturingAssumption('Section acceptance', tmp_path/'missing.gcode', ((0, .2, (-1, 1)),)).review()


def test_contact_apis_cannot_choose_different_implicit_quality_limits():
    with pytest.raises(TypeError, match='penetration_limit_mm'):
        AnalysisCase('contact', nonlinear=True).contact('a', None, 'b', penalty_N_mm3=1000)
    with pytest.raises(TypeError, match='penetration_limit_mm'):
        ContactQuestion(name='contact', part=object(), material=object(), supports=(),
                        contact_region=object(), mating_parts=(), penalty_N_mm3=1000)


def test_direct_slice_review_requires_setup_and_placement():
    from evaluate_model import review
    with pytest.raises(TypeError, match='printer'):
        review('missing.stl')
    with pytest.raises(TypeError, match='placement'):
        review('missing.stl', 'printer.json', 'process.json', 'filament.json')


def test_legacy_assembly_selectors_reject_omission_and_unknown_designs(monkeypatch):
    directory = ROOT/'model/filament_swatch_box_study'
    monkeypatch.syspath_prepend(str(directory))
    checker = runpy.run_path(str(directory/'check_quiet_assembly.py'))
    with pytest.raises(TypeError, match='variant'):
        checker['run']()
    with pytest.raises(ValueError, match='Unknown assembly variant'):
        checker['run']('typo')
    with pytest.raises(TypeError, match='model'):
        checker['QuietAssembly']()
    with pytest.raises(TypeError, match='q'):
        checker['main']()
