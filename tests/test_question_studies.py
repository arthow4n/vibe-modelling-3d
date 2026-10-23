"""Study orchestration guards; synthetic responses do not qualify mechanics."""
from copy import deepcopy
import json

import pytest

from physical_analysis import AnalysisResult, PETG_SCREEN, QuestionStudy, StructuralQuestion
from physical_analysis.studies import compare_results


@pytest.fixture
def responses(monkeypatch):
    calls = []
    results = {}

    def obtain(question, directory, **kwargs):
        calls.append(str(directory))
        return deepcopy(results[str(directory)])

    monkeypatch.setattr(StructuralQuestion, 'run', obtain)
    monkeypatch.setattr(StructuralQuestion, 'read_evidence', obtain)
    return calls, results


def result(value=1):
    return AnalysisResult('study_fixture', 'completed', completed=True, metrics={
        'force_N': value,
        'question': {'numerical_evidence_adequate': True, 'design_screen_passes': True,
                     'numerical_confidence': dict(increment_sensitivity='not_run',
                         mesh_sensitivity='not_run', contact_parameter_sensitivity='not_run')}})


def study(**kwargs):
    # No geometry is solved: the real question dataclass exercises replacement
    # and the public study entry point with controlled numerical responses.
    question = StructuralQuestion(name='study_fixture', part=None, material=PETG_SCREEN, supports=())
    return QuestionStudy(question, 'Force accuracy for candidate selection', ('force_N',),
                         relative_tolerance=.05, mesh_levels=2, **kwargs)


@pytest.mark.parametrize('value', [None, True, 'unknown', float('nan'), float('inf')])
def test_unavailable_baseline_quantity_stops_before_refinement(responses, value):
    calls, results = responses
    results['saved_baseline'] = result(value)
    answer = study().run(evidence={'baseline': 'saved_baseline'})
    assert calls == ['saved_baseline']
    assert answer.completed and answer.status == 'completed'
    q = answer.metrics['question']
    assert q['baseline_quality_adequate'] is True
    assert q['numerical_evidence_adequate'] is False
    assert q['numerical_confidence']['mesh_sensitivity'] == 'unresolved'
    assert q['study']['unavailable_metrics'] == {'baseline': ['force_N']}


def test_missing_baseline_path_is_unavailable_evidence(responses):
    calls, results = responses
    results['saved_baseline'] = result()
    del results['saved_baseline'].metrics['force_N']
    answer = study().run(evidence={'baseline': 'saved_baseline'})
    assert calls == ['saved_baseline']
    assert answer.metrics['question']['study']['unavailable_metrics'] == {'baseline': ['force_N']}


def test_unavailable_baseline_still_writes_an_honest_study_record(tmp_path, responses):
    calls, results = responses
    results['base'] = result(None)
    study().run(tmp_path/'study', evidence={'baseline': 'base'})
    saved = json.loads((tmp_path/'study/study_result.json').read_text())
    assert calls == ['base']
    assert saved['status'] == 'completed' and saved['completed'] is True
    assert saved['metrics']['question']['numerical_evidence_adequate'] is False
    assert saved['metrics']['question']['study']['unavailable_metrics'] == {'baseline': ['force_N']}
    assert list((tmp_path/'study').iterdir()) == [tmp_path/'study/study_result.json']


def test_bad_evidence_label_fails_before_any_computation(tmp_path, responses):
    calls, _ = responses
    with pytest.raises(ValueError, match='Unknown.*mesh_sensitivty_1'):
        study().run(tmp_path/'new_study', evidence={'mesh_sensitivty_1': 'existing'})
    assert not calls
    assert not (tmp_path/'new_study').exists()


def test_unknown_absolute_tolerance_cannot_be_silently_ignored(responses):
    calls, _ = responses
    with pytest.raises(ValueError, match='Absolute.*force_typo'):
        study(absolute_tolerances={'force_typo': .1}).run()
    assert not calls


@pytest.mark.parametrize('factor', [float('nan'), float('inf')])
def test_nonfinite_contact_factor_fails_before_computation(responses, factor):
    calls, _ = responses
    with pytest.raises(ValueError, match='finite'):
        study(contact_factor=factor).run()
    assert not calls


def test_missing_refined_quantity_stops_later_levels_and_preserves_baseline(responses):
    calls, results = responses
    results.update(base=result(), fine=result(None))
    answer = study().run(evidence={'baseline': 'base', 'mesh_sensitivity_1': 'fine'})
    assert calls == ['base', 'fine']
    q = answer.metrics['question']
    assert q['numerical_confidence']['mesh_sensitivity'] == 'unresolved'
    assert q['study']['unavailable_metrics'] == {'mesh_sensitivity_1': ['force_N']}
    assert q['baseline_quality_adequate'] is True
    assert q['numerical_evidence_adequate'] is False


def test_stable_first_comparison_does_not_request_later_evidence(responses):
    calls, results = responses
    results.update(base=result(), fine=result(1.01))
    answer = study().run(evidence={'baseline': 'base', 'mesh_sensitivity_1': 'fine'})
    assert calls == ['base', 'fine']
    assert answer.metrics['question']['selected_metrics_stable'] is True


def test_absolute_tolerance_remains_effective_near_zero(responses):
    _, results = responses
    results.update(base=result(1e-8), fine=result(0))
    answer = study(absolute_tolerances={'force_N': 1e-7}).run(
        evidence={'baseline': 'base', 'mesh_sensitivity_1': 'fine'})
    assert answer.metrics['question']['selected_metrics_stable'] is True


def test_comparison_checks_each_operand_without_overflowing_their_sum():
    compared = compare_results(result(1e308), result(1e308),
                               metrics=('force_N',), relative_tolerance=.05)
    assert compared['force_N']['passes'] is True


@pytest.mark.parametrize('value', [True, None, 'unknown', float('nan'), float('inf')])
def test_direct_comparison_rejects_unavailable_quantities(value):
    with pytest.raises(ValueError, match='finite scalar'):
        compare_results(result(value), result(), metrics=('force_N',), relative_tolerance=.05)
