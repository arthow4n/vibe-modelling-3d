"""Archive behavior checks need files, not another numerical solve."""
import gzip
import json
import pytest
from physical_analysis import AnalysisResult
from physical_analysis.evidence import retain_run


def test_retention_preserves_evidence_and_all_fixture_parts(tmp_path):
    run = tmp_path/'run'
    run.mkdir()
    payload = AnalysisResult('archive', 'completed_with_warnings', completed=True,
        metrics={'peak_force_N': .4}, history=[{'load_fraction': 1, 'strain': .01}],
        assumptions=['Uncalibrated elastic material'], warnings=['Example notice'],
        provenance={'backend': 'CalculiX', 'input_sha256': 'original'},
        artifacts={'directory': str(run), 'raw_results': 'analysis.dat'})
    payload.write(run/'result.json')
    contents = {'case.json': '{}\n', 'analysis.inp': '*HEADING\narchive\n',
                'solver.log': 'Job finished\n', 'worker.log': '',
                'analysis.sta': 'increments\n', 'regions.json': '{}\n'}
    contents.update({f'part_{i}.brep': f'fixture {i}\n' for i in range(3)})
    for name, content in contents.items():
        (run/name).write_text(content)
    (run/'analysis.dat').write_text('bulky raw fields')
    before = {p.name: p.read_bytes() for p in run.iterdir()}
    target = retain_run(run, tmp_path/'archive')
    archived = json.loads((target/'result.json').read_text())
    for key, value in payload.to_dict().items():
        if key != 'artifacts':
            assert archived[key] == value
    links = archived['artifacts']
    assert len(links['fixture_geometry']) == 3
    assert links['raw_fields_retained'] is False
    assert not (target/'analysis.dat').exists()
    for role in ('case', 'input', 'solver_log', 'worker_log', 'increments', 'regions', 'fixture_geometry'):
        names = links[role] if isinstance(links[role], list) else [links[role]]
        for name in names:
            content = gzip.decompress((target/name).read_bytes()) if name.endswith('.gz') else (target/name).read_bytes()
            assert content == before[name.removesuffix('.gz')]
    assert {p.name: p.read_bytes() for p in run.iterdir()} == before
    # Stable compressed output and no accidental replacement of existing evidence.
    second = retain_run(run, tmp_path/'second')
    assert (second/'analysis.inp.gz').read_bytes() == (target/'analysis.inp.gz').read_bytes()
    with pytest.raises(FileExistsError):
        retain_run(run, target)
    assert json.loads((target/'result.json').read_text()) == archived


def test_partial_failure_lists_only_existing_artifacts(tmp_path):
    run = tmp_path/'failure'
    run.mkdir()
    AnalysisResult('failed', 'timeout', errors=['Exceeded time budget']).write(run/'result.json')
    (run/'worker.log').write_text('partial run\n')
    archived = retain_run(run, tmp_path/'retained_failure')
    result = json.loads((archived/'result.json').read_text())
    assert result['status'] == 'timeout' and not result['completed']
    assert result['errors'] == ['Exceeded time budget']
    assert result['artifacts'] == {'worker_log': 'worker.log.gz', 'raw_fields_retained': False}


def test_invalid_run_does_not_create_archive(tmp_path):
    run = tmp_path/'invalid'
    run.mkdir()
    (run/'result.json').write_text('{broken')
    destination = tmp_path/'unused'
    with pytest.raises(json.JSONDecodeError):
        retain_run(run, destination)
    assert not destination.exists()
