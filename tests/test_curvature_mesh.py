"""Explicit curvature meshing and identity guards; numerical adequacy stays local."""
import json
import pytest
import cadquery as cq
from physical_analysis import AnalysisCase, Material
from physical_analysis.backends.structural import CalculixBackend

MATERIAL = Material('benchmark', 1200, .3, 'Numerical fixture, not measured filament')


def make_case(**controls):
    case = AnalysisCase('curvature')
    case.add_part('body', cq.Workplane('XY').box(2, 2, 2), material=MATERIAL,
                  mesh_size_mm=3, **controls)
    return case


@pytest.mark.parametrize('controls', [
    {'mesh_min_size_mm': .12}, {'mesh_curvature_points': 12},
    {'mesh_min_size_mm': 0, 'mesh_curvature_points': 12},
    {'mesh_min_size_mm': 4, 'mesh_curvature_points': 12},
    {'mesh_min_size_mm': .12, 'mesh_curvature_points': 2},
    {'mesh_min_size_mm': .12, 'mesh_curvature_points': 12.5},
    {'mesh_min_size_mm': .12, 'mesh_curvature_points': True},
])
def test_invalid_curvature_controls_fail_before_native_work(controls):
    with pytest.raises(ValueError):
        make_case(**controls)


def test_controls_serialized_and_change_mesh_identity(tmp_path):
    backend = CalculixBackend()
    requests = []
    for name, controls in (('uniform', {}), ('curved', dict(mesh_min_size_mm=.12, mesh_curvature_points=12)),
                           ('finer', dict(mesh_min_size_mm=.12, mesh_curvature_points=16))):
        directory = tmp_path/name
        directory.mkdir()
        requests.append(backend.prepare_request(make_case(**controls), directory))
    uniform, curved, finer = requests
    assert uniform['parts'][0]['mesh_min_size_mm'] is None
    assert uniform['parts'][0]['mesh_curvature_points'] is None
    assert curved['parts'][0]['mesh_min_size_mm'] == .12
    assert curved['parts'][0]['mesh_curvature_points'] == 12
    assert len({json.dumps(backend.mesh_identity(r), sort_keys=True) for r in requests}) == 3
    # Historical requests without optional fields retain the same default identity.
    del uniform['parts'][0]['mesh_min_size_mm']
    del uniform['parts'][0]['mesh_curvature_points']
    default_request = backend.prepare_request(make_case(), tmp_path/'uniform')
    assert backend.mesh_identity(uniform) == backend.mesh_identity(default_request)


def test_reuse_rejects_changed_curvature_controls_before_copy(tmp_path):
    import hashlib
    backend = CalculixBackend()
    source = tmp_path/'source'
    source.mkdir()
    old = backend.prepare_request(make_case(mesh_min_size_mm=.12, mesh_curvature_points=12), source)
    (source/'case.json').write_text(json.dumps(old))
    (source/'analysis.inp').write_text('native mesh fixture\n')
    provenance = {key: hashlib.sha256((source/name).read_bytes()).hexdigest()
                  for key, name in (('input_sha256', 'analysis.inp'), ('case_sha256', 'case.json'))}
    (source/'result.json').write_text(json.dumps({'provenance': provenance}))
    for changes in ({'mesh_min_size_mm': .10, 'mesh_curvature_points': 12},
                    {'mesh_min_size_mm': .12, 'mesh_curvature_points': 16}, {}):
        destination = tmp_path/f'new_{len(list(tmp_path.iterdir()))}'
        destination.mkdir()
        new = backend.prepare_request(make_case(**changes), destination)
        with pytest.raises(ValueError, match='mesh settings differ'):
            backend.reuse_mesh(new, destination, source)
        assert not (destination/'mesh_source.inp').exists()


def test_native_mesh_logs_join_retained_evidence(tmp_path):
    from physical_analysis.backends.structural import evidence_files
    (tmp_path/'part_0.mesh.log').write_text('Gmsh native progress\n')
    (tmp_path/'part_1.mesh.log').write_text('Gmsh native progress\n')
    files, _ = evidence_files(tmp_path)
    assert files['mesh_logs'] == [('part_0.mesh.log', True), ('part_1.mesh.log', True)]
