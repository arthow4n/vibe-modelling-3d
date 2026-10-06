"""Real migrations, preserved exports, retained history and meaningful mutations."""
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import pytest
from product_verification import Status, UserRequirement

ROOT=Path(__file__).resolve().parents[1]


@contextmanager
def product(name):
    directory=ROOT/'model'/name
    old={n:sys.modules.pop(n,None) for n in ('assembly_checks','components')}
    sys.path.insert(0,str(directory))
    try:
        spec=importlib.util.spec_from_file_location(name+'_verification',directory/'verification.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        yield m
    finally:
        sys.path.remove(str(directory))
        for n,mod in old.items():
            sys.modules.pop(n,None)
            if mod is not None:
                sys.modules[n]=mod


def fingerprints(name):
    root=ROOT/'model'/name
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for ext in ('*.step','*.stl') for p in root.glob(ext)}


def statuses(report,rid):
    return {q['id']:q['status'] for r in report['requirements'] if r['id']==rid for q in r['questions']}


@pytest.mark.parametrize('name,variant,user_ids',[
    ('sunglasses_case','accepted-e',{'case.cavity','case.operation'}),
    ('vaseline_container','accepted-thread',{'jar.envelope','jar.use'}),
    ('book_reading_plate','accepted-plate',{'plate.use'}),
    ('filament_swatch_box_study','q1f',{'swatch.storage','swatch.open','swatch.join','swatch.quiet','swatch.appearance','swatch.upper-fit'})])
def test_replacement_retains_user_intent_reports_unknown_and_keeps_historical_evidence(name,variant,user_ids):
    with product(name) as m:
        assert {r.id for r in m.REQUIREMENTS if isinstance(r,UserRequirement)}==user_ids
        report=m.make_plan('replacement-fixture').evaluate()
        assert {r['id'] for r in report['requirements'] if r['kind']=='user'}==user_ids
        assert all(q['status']=='UNKNOWN' for r in report['requirements'] if r['kind']=='user' for q in r['questions'])
        assert report['evidence']
        for r in report['requirements']:
            if r['non_applicable']:
                assert all(q['status'] is None for q in r['questions'])


@pytest.mark.parametrize('name,variant,physical_rid,physical_qid',[
    ('sunglasses_case','accepted-e','case.operation','use'),
    ('vaseline_container','accepted-thread','jar.use','print-use'),
    ('book_reading_plate','accepted-plate','plate.use','finish')])
def test_printed_products_computed_and_scoped_physical_success_with_unknowns(name,variant,physical_rid,physical_qid):
    before=fingerprints(name)
    with product(name) as m:
        report=m.make_plan(variant).evaluate()
        assert statuses(report,physical_rid)[physical_qid]=='PASS'
        assert all(q['status']=='PASS' for r in report['requirements'] for q in r['questions']
                   if q['mode'] in ('CAD','analytical'))
        assert any(q['status']=='UNKNOWN' for r in report['requirements'] for q in r['questions'])
        assert report['scope']['sources']=='migration-reviewed'
    assert fingerprints(name)==before


def test_sunglasses_material_change_loses_physical_qualification_while_nominal_cad_can_pass():
    with product('sunglasses_case') as m:
        report=m.make_plan('tpu-fixture').evaluate([])
        assert statuses(report,'case.operation')['use']=='UNKNOWN'
        r=next(r for r in report['requirements'] if r['id']=='case.operation')
        assert next(q for q in r['questions'] if q['id']=='use')['out_of_scope']==['case.full-print','case.sample-D','case.sample-E']


@pytest.mark.parametrize('variant',['q1','q1f'])
def test_quiet_migrated_checks_legacy_outcomes_placements_and_three_real_mutations(variant,monkeypatch):
    before=fingerprints('filament_swatch_box_study')
    with product('filament_swatch_box_study') as m:
        import check_quiet_q1 as shared
        from check_quiet_q1_flush import local_checks
        from check_quiet_assembly import qualify
        captured={}
        # Capture the actual product-run traversals once; compose their unchanged
        # outputs into the historical main report for comparison, without a
        # second expensive path traversal. This is local test data, not a cache.
        for name in ('closed_checks','card_checks','hood_checks','insert_checks','landing_checks','joining_checks'):
            original=getattr(shared,name)
            def wrapper(model,evidence,original=original,name=name):
                if name in captured:
                    evidence.extend(captured[name][1])
                    return captured[name][2]
                start=len(evidence)
                result=original(model,evidence)
                captured[name]=(model,evidence[start:].copy(),result)
                return result
            monkeypatch.setattr(shared,name,wrapper)
        report=m.make_plan(variant).evaluate()
        assert statuses(report,'swatch.storage')['seating']=='PASS'
        assert statuses(report,'swatch.open')['path-retention']=='PASS'
        assert statuses(report,'swatch.join')['geometry']=='PASS'
        assert statuses(report,'swatch.quiet')['sound']==('FAIL' if variant=='q1f' else 'UNKNOWN')
        assert statuses(report,'swatch.join')['use']==('PASS' if variant=='q1f' else 'UNKNOWN')
        model=captured['hood_checks'][0]
        legacy=shared.main(model.model,None,model=model,
            extra=local_checks(model) if variant=='q1f' else None)
        qualified=qualify(model,legacy)
        assert len(qualified['negatives'])==3
        assert all(n['status']=='failed' for n in qualified['negatives'])
        assert qualified['native_pose_and_print_selection_regressions']
        if variant=='q1':
            assert statuses(report,'swatch.insert-connected')['topology'] is None
        else:
            assert statuses(report,'swatch.insert-connected')['topology']=='PASS'
    assert fingerprints('filament_swatch_box_study')==before


def test_all_tpu_history_remains_failed_noise_unknown_appearance_and_discontinued():
    with product('filament_swatch_box_study') as m:
        report=m.make_plan('q1f-tpu-hood').evaluate()
        assert statuses(report,'swatch.quiet')['sound']=='FAIL'
        assert statuses(report,'swatch.appearance')['appearance']=='UNKNOWN'
        assert statuses(report,'swatch.join')['use']=='UNKNOWN'
        assert report['directives'][0]['id']=='swatch.stop'
        assert report['hypotheses'][0]['id']=='swatch.layers'
        assert len(report['evidence'])==7


@pytest.mark.parametrize('defect',['missing','stale','invalid','nonfinite','criterion-failed'])
def test_plate_retained_evidence_missing_stale_invalid_and_failure_are_distinct(defect,tmp_path,monkeypatch):
    with product('book_reading_plate') as m:
        original=m.make_plan().evaluate(['plate.analytical'])
        assert statuses(original,'plate.joint')['screen']=='PASS'
        fake=tmp_path/'plate';(fake/'notes').mkdir(parents=True)
        for name in ('components.py','measure_structure.py','load_checks.py','notes/sections.json','notes/verification_sources.json'):
            (fake/name).write_bytes((m.ROOT/name).read_bytes())
        record=json.loads((m.ROOT/'notes/load_checks.json').read_text())
        if defect=='stale':
            (fake/'components.py').write_text('changed geometry')
        elif defect=='invalid':
            del record['checks']
        elif defect=='nonfinite':
            record['minimum_margin']=float('nan')
        elif defect=='criterion-failed':
            item=next(iter(record['checks'].values()))
            item['stress_MPa']=2*item['allowable_MPa'];item['margin']=.5;item['passes']=False
            record['minimum_margin']=.5
        if defect!='missing':
            (fake/'notes/load_checks.json').write_text(json.dumps(record))
        monkeypatch.setattr(m,'ROOT',fake)
        report=m.make_plan().evaluate(['plate.analytical'])
        expected={'missing':'UNKNOWN','stale':'UNKNOWN','invalid':'INCONCLUSIVE',
                  'nonfinite':'INCONCLUSIVE','criterion-failed':'FAIL'}[defect]
        assert statuses(report,'plate.joint')['screen']==expected


@pytest.mark.parametrize('variant',['q1','q1f'])
def test_actual_swatch_fixture_cannot_shrink_and_silently_qualify_fifteen_cards(variant):
    from types import SimpleNamespace
    from product_verification import assertion_check
    with product('filament_swatch_box_study'):
        import quiet_q1, quiet_q1_flush
        from check_quiet_q1 import require_card_fixture, card_checks
        q=quiet_q1_flush if variant=='q1f' else quiet_q1
        # Actual unchanged source-card population, not an invented test solid.
        actual=q.cards()
        assert len(actual)==15
        require_card_fixture(SimpleNamespace(cards=actual))
        incomplete=SimpleNamespace(cards=actual[:-1])
        evidence=assertion_check('quiet.cards',(('swatch.storage','seating'),),
            lambda:card_checks(incomplete,[]),'check_quiet_q1.py',{'design':variant}).run()[0]
        assert evidence.status is Status.INCONCLUSIVE
        assert '15-card' in evidence.summary


def test_quiet_composed_check_isolates_hood_failure_from_insert_capture(monkeypatch):
    with product('filament_swatch_box_study') as m:
        import check_quiet_q1 as shared
        import quiet_assembly
        calls=[]
        candidate=object()
        def build(model):
            calls.append('build')
            return candidate
        def bad_path(model,evidence):
            assert model is candidate
            raise AssertionError('Hood path defect')
        def good_insert(model,evidence):
            assert model is candidate
            calls.append('insert')
        monkeypatch.setattr(quiet_assembly,'QuietAssembly',build)
        monkeypatch.setattr(shared,'hood_checks',bad_path)
        monkeypatch.setattr(shared,'insert_checks',good_insert)
        monkeypatch.setattr(shared,'landing_checks',lambda model,evidence:None)
        report=m.make_plan('q1f').evaluate(['quiet.hood'])
        assert statuses(report,'swatch.open')['path-retention']=='FAIL'
        assert statuses(report,'swatch.insert-anchored')['capture']=='PASS'
        assert calls==['build','insert']
        assert {e['id'] for e in report['evidence']} >= {'quiet.hood.path','quiet.hood.insert'}


def test_quiet_landing_defect_cannot_falsely_fail_joining(monkeypatch):
    with product('filament_swatch_box_study') as m:
        import check_quiet_q1 as shared
        import quiet_assembly
        monkeypatch.setattr(quiet_assembly,'QuietAssembly',lambda model:object())
        def failed_landing(model,evidence):
            raise AssertionError('Missing soft-seat contact')
        monkeypatch.setattr(shared,'landing_checks',failed_landing)
        for fn in ('hood_checks','insert_checks','joining_checks'):
            monkeypatch.setattr(shared,fn,lambda model,evidence:None)
        report=m.make_plan('q1f').evaluate(['quiet.hood','quiet.join'])
        assert statuses(report,'swatch.landing-access')['roles']=='FAIL'
        assert statuses(report,'swatch.join')['geometry']=='PASS'
        assert statuses(report,'swatch.open')['path-retention']=='PASS'
