"""Real products are immutable regression subjects, not redesign opportunities."""
from contextlib import contextmanager
from dataclasses import replace
import hashlib
import importlib.util
from pathlib import Path
import sys
import cadquery as cq
import pytest

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def consumer(object_name):
    directory = ROOT/'model'/object_name
    # The book uses its established sibling-module imports. Isolate that name
    # from other products' components modules in this test process.
    old = sys.modules.pop('components', None)
    sys.path.insert(0, str(directory))
    try:
        spec = importlib.util.spec_from_file_location(object_name+'_checks', directory/'assembly_checks.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        sys.path.remove(str(directory))
        sys.modules.pop('components', None)
        if old is not None:
            sys.modules['components'] = old


def difference(a, b):
    from assembly_geometry.configuration import geometry
    a, b = geometry(a), geometry(b)
    return a.cut(b).Volume()+b.cut(a).Volume()


def fingerprints(name):
    directory = ROOT/'model'/name
    # This protects accepted artifact bytes, rather than re-auditing their meshes.
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for ext in ('*.step', '*.stl') for p in directory.glob(ext)}


def test_sunglasses_production_configs_motion_retention_and_layout(monkeypatch):
    def forbidden_write(*args, **kwargs):
        pytest.fail('Geometry loading/inspection must not publish exports or rewrite evidence')
    monkeypatch.setattr(cq.exporters, 'export', forbidden_write)
    monkeypatch.setattr(Path, 'write_text', forbidden_write)
    before = fingerprints('sunglasses_case')
    with consumer('sunglasses_case') as m:
        data = m.load()  # includes original production assertions without publishing
        config = m.configuration(data)
        assert config.names == ('body', 'lid', 'keeper')
        assert difference(config.shape('lid'), data['lid']) < .001
        assert difference(config.assembly().toCompound(), data['closed']) < .001
        printed = m.configuration(data, name='print', print_layout=True)
        assert printed.kind == 'print'
        assert difference(printed.assembly().toCompound(), data['print_layout']) < .001
        report = m.verify(data)
        assert len(report['hinge']['samples']) == 37
        assert report['hinge']['status'] == report['release']['status'] == 'passed'
        assert report['checks'][-1]['overlap_mm3'] > .01
    assert fingerprints('sunglasses_case') == before


def test_sunglasses_loader_rejects_unsupported_overrides_before_building(monkeypatch):
    with consumer('sunglasses_case') as m:
        calls = []
        monkeypatch.setattr(m.runpy, 'run_path', lambda path, **kw: calls.append(kw) or kw)
        for dimensions in ({'INNER_HEIGTH': 70}, {'WALL': 4}, {'VERIFY': False}):
            with pytest.raises(TypeError, match='unexpected keyword'):
                m.load(**dimensions)
        assert not calls
        m.load(verify=False, INNER_HEIGHT=70)
        assert calls == [{'init_globals': {'VERIFY': False, 'INNER_HEIGHT': 70}}]


def test_book_repeated_screws_native_placement_print_jobs_and_parameters():
    before = fingerprints('book_reading_plate')
    with consumer('book_reading_plate') as m:
        parts = m.build()
        explicit = m.configuration(parts)
        resolved = m.configuration(parts, constrained=True)
        assert len(explicit.names) == 6
        assert all(r['status'] == 'passed' for r in m.verify(explicit)+m.verify(resolved))
        for i, station in enumerate(m.c.stations()):
            original = m.c.posed(parts[2], *station)
            assert difference(explicit.shape(f'screw_{i}'), original) < 1e-5
            assert difference(resolved.shape(f'screw_{i}'), original) < 1e-5
        jobs = m.print_jobs(parts)
        assert all(c.kind == 'print' for c in jobs.values())
        expected = cq.Compound.makeCompound([m.c.print_screw().translate((i*26, 0, 0)).val() for i in range(4)])
        assert difference(jobs['screws'].assembly().toCompound(), expected) < 1e-5
        assert difference(jobs['left'].shape('left'), m.c.print_half(parts[0], True)) < 1e-5
        assert difference(jobs['right'].shape('right'), m.c.print_half(parts[1], False)) < 1e-5
        # Ordinary candidate study: original builder parameters and same criteria;
        # no alternative scheduler/cache or optimization machinery.
        p = replace(m.c.P, width=360, inner_height=230)
        candidate = m.build(p)
        altered = m.configuration(candidate, p)
        assert all(r['status'] == 'passed' for r in m.verify(altered, p))
        assert altered.parameters['width'] == 360
        for i, station in enumerate(m.c.stations(p)):
            assert altered.location(f'screw_{i}').toTuple()[0] == pytest.approx(station[:3])
        # Actual positioned product geometry feeds the existing question API.
        from physical_analysis import StructuralQuestion, Support, Region, SurfaceForce, PETG_SCREEN, QuestionStudy
        q = StructuralQuestion(name='left_fixture', part=explicit.shape('left'), material=PETG_SCREEN,
            supports=(Support(Region.plane('x', -m.c.P.width/2)),),
            forces=(SurfaceForce(Region.plane('x', m.c.P.overlap_half), (0, 0, -1)),), mesh_size_mm=10)
        case = q.build_case()  # fixture construction only; no load rating inferred
        assert difference(next(iter(case.parts.values())).shape, explicit.shape('left')) < 1e-5
        assert QuestionStudy(q, decision='Example fixture refinement', metrics=('max_displacement_mm',),
                            relative_tolerance=.1, mesh_levels=1).question is q
    assert fingerprints('book_reading_plate') == before


def test_jar_thread_transfers_same_queries_and_keeps_print_geometry():
    before = fingerprints('vaseline_container')
    with consumer('vaseline_container') as m:
        data = m.load()
        config = m.configuration(data)
        assert difference(config.shape('lid'), data['lid']) < 1e-5
        printed = m.configuration(data, print_layout=True)
        assert difference(printed.assembly().toCompound(), data['result']) < 1e-5
        opened = m.configuration(data, opening_deg=180)
        original = data['lid'].rotate((0, 0, 0), (0, 0, 1), 180).translate((0, 0, data['THREAD_PITCH']/2))
        assert difference(opened.shape('lid'), original) < 1e-5
        report = m.verify(data)
        assert len(report['withdrawal']['samples']) == 37
        assert report['withdrawal']['status'] == report['retention']['status'] == 'passed'
        assert report['retention']['maximum_sampled_overlap']['mm3'] > 1
    assert fingerprints('vaseline_container') == before
