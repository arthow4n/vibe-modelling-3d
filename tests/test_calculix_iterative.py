"""The lower-memory linear solver must retain real contact and open-gap behavior."""
import json
import pytest
from physical_analysis.backends.structural import CalculixBackend
from model.dental_travel_case.retention_solver_qualification import make_case


def test_unknown_linear_solver_rejected():
    for invalid in ('cholesky', 'typo', None):
        with pytest.raises(ValueError, match='linear_solver'):
            CalculixBackend(linear_solver=invalid)


@pytest.mark.parametrize('solver', ('iterative_scaling', 'iterative_cholesky'))
def test_iterative_contact_matches_direct_and_preserves_open_gap(tmp_path, solver):
    source = tmp_path/'direct'
    direct = make_case(.02).run(source).require_completed()
    backend = CalculixBackend(linear_solver=solver)
    iterative = make_case(.02).run(tmp_path/'iterative', backend=backend,
                                  mesh_from=source).require_completed()
    assert 'calculix' not in json.loads((source/'case.json').read_text())
    assert json.loads((tmp_path/'iterative/case.json').read_text())['calculix'] == {
        'linear_solver': solver}
    assert iterative.provenance['linear_solver'] == solver
    assert iterative.provenance['iterative_cholesky_fallback_to_scaling'] is False
    assert ('*STATIC,SOLVER='+solver.replace('_', ' ').upper()) in (tmp_path/'iterative/analysis.inp').read_text()
    for result in (direct, iterative):
        assert result.metrics['contact_detected'] is True
        assert result.metrics['peak_reaction_force_N']['BC2'] == pytest.approx(12, rel=.02)
        assert result.metrics['max_force_balance_relative'] < 1e-4
    for key in ('max_abs_principal_strain', 'max_penetration_mm'):
        assert iterative.metrics[key] == pytest.approx(direct.metrics[key], rel=1e-4)
    assert [h['load_fraction'] for h in direct.history] == [h['load_fraction'] for h in iterative.history]
    for left, right in zip(direct.history, iterative.history):
        assert right['reactions_N']['BC2'][2] == pytest.approx(left['reactions_N']['BC2'][2], rel=1e-4, abs=1e-4)
    opened = make_case(.005).run(tmp_path/'open', backend=backend,
                                 mesh_from=source).require_completed()
    assert opened.metrics['contact_detected'] is False
    assert opened.metrics['peak_reaction_force_N']['BC2'] < 1e-4
