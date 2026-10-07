"""Requirements constrain claims, not exploration or mechanism choice."""
from dataclasses import replace
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from product_verification import (Status as T, Question as Q, UserRequirement as U,
    DerivedRequirement as D, UserSource as S, DesignDecision, Hypothesis, Directive,
    Evidence as E, Check, Plan, CalculationInconclusive, assertion_check,
    engineering_evidence, protect_user_requirements, protect_recorded_intent,
    recorded_design_scope, human_report)

REQ=U('fixture.retain','Cover stays retained',S('README.md#intent','User requests retained cover'))
QUESTIONS=(Q('obstruction',REQ.id,'Attempted removal meets retaining material', mode='CAD'),
           Q('feel',REQ.id,'Comfortable opening','physical'))
SCOPE={'design':'beads','material':'PETG','sources':'reviewed'}
TARGET=(('fixture.retain','obstruction'),)


def ev(id='cad',status=T.PASS,targets=TARGET,scope=None):
    return E(id,targets,status,'Criterion evaluated','fixture.py',scope or SCOPE)


def row(report,rid='fixture.retain',qid='obstruction'):
    r=next(r for r in report['requirements'] if r['id']==rid)
    return next(q for q in r['questions'] if q['id']==qid)


def test_uncovered_requirement_and_physical_unknown_despite_all_implemented_checks_passing():
    report=Plan('beads',(REQ,),SCOPE,(Check('cad',TARGET,lambda:(ev(),)),), questions=QUESTIONS).evaluate()
    assert row(report)['status']=='PASS'
    assert row(report,qid='feel')['status']=='UNKNOWN'
    assert row(report,qid='feel')['coverage']=='uncovered'
    assert 'source: README.md#intent' in human_report(report)
    replacement=Plan('thread',(REQ,),{'design':'thread','material':'PETG'}, questions=QUESTIONS).evaluate()
    assert row(replacement)['status']=='UNKNOWN'
    assert 'UNKNOWN' in human_report(replacement)
    assert 'overall' not in report


def test_distinct_provenance_no_decision_promotion_no_user_demotion():
    decision=DesignDecision('fixture.retain','Use four beads','agent notes')
    with pytest.raises(TypeError):
        U('fake','Use four beads',decision)
    with pytest.raises(TypeError):
        Plan('x',(decision,),SCOPE, questions=QUESTIONS).evaluate()
    with pytest.raises(ValueError,match='decision'):
        Plan('x',(REQ,),SCOPE,decisions=(decision,), questions=QUESTIONS).evaluate()
    with pytest.raises(ValueError,match='user instruction'):
        protect_user_requirements((REQ,),(decision,))
    with pytest.raises(ValueError):
        protect_user_requirements((REQ,),())
    with pytest.raises(ValueError,match='reclassify'):
        protect_user_requirements((REQ,),(D(REQ.id,REQ.text,('other',),'Agent demotion'),))
    with pytest.raises(ValueError):
        protect_user_requirements((REQ,),(replace(REQ,text='Loose cover acceptable'),))
    with pytest.raises(ValueError):
        protect_user_requirements((REQ,),(replace(REQ,text='Improve human wording'),))
    protect_user_requirements((REQ,),(),changes={REQ.id:S('later user message','User cancels cover requirement')})


def test_derived_parent_and_explicit_architecture_non_applicability():
    insert=D('fixture.insert','Insert connected',(REQ.id,),'Separate insert architecture')
    insert_questions=QUESTIONS+(Q('connected',insert.id,'one solid', mode='CAD'),)
    report=Plan('thread',(REQ,insert),SCOPE,questions=insert_questions,non_applicable={insert.id:'Thread architecture has no insert'}).evaluate()
    r=next(x for x in report['requirements'] if x['id']==insert.id)
    assert r['provenance']['parents']==(REQ.id,)
    assert r['questions'][0]['status'] is None
    assert r['questions'][0]['coverage']=='non_applicable'
    assert 'derived from: fixture.retain' in human_report(report)
    with pytest.raises(ValueError,match='parents'):
        Plan('x',(replace(insert,parents=('absent',)),),SCOPE, questions=QUESTIONS).evaluate()
    with pytest.raises(ValueError):
        Plan('x',(REQ,),SCOPE,non_applicable={REQ.id:''}, questions=QUESTIONS).evaluate()


def test_variant_non_applicability_cannot_hide_protected_user_intent_or_its_failure():
    # The catalog is unchanged, so the intent audit alone cannot catch this.
    protect_user_requirements((REQ,),(REQ,))
    with pytest.raises(ValueError,match='cannot exclude user intent'):
        Plan('replacement',(REQ,),SCOPE,retained=(ev('physical-failure',T.FAIL),),
             non_applicable={REQ.id:'New architecture abandons the cover'}, questions=QUESTIONS).evaluate()


def test_derivations_cannot_circularly_supply_each_others_provenance():
    a=D('a','A',('b',),'Claimed consequence')
    b=D('b','B',('a',),'Claimed consequence')
    with pytest.raises(ValueError,match='circular requirement derivation'):
        Plan('x',(a,b),SCOPE).evaluate()
    # A normal chain remains rooted in user intent without a new graph API.
    Plan('x',(REQ,replace(a,parents=(REQ.id,)),b),SCOPE, questions=QUESTIONS).evaluate()


def test_one_traversal_many_targets_and_multiple_sources_no_overwrite():
    other=U('fixture.access','Access contents',S('README.md','User asks access'))
    other_questions=QUESTIONS+(Q('path',other.id,'clear path', mode='CAD'),)
    targets=TARGET+(('fixture.access','path'),)
    calls=[]
    def traverse():
        calls.append(True)
        return (ev(targets=targets),)
    report=Plan('beads',(REQ,other),SCOPE,(Check('traverse',targets,traverse),),
        questions=other_questions,retained=(ev('printed',T.FAIL,(('fixture.retain','feel'),)),)).evaluate()
    assert calls==[True]
    assert row(report)['status']==row(report,'fixture.access','path')['status']=='PASS'
    assert row(report,qid='feel')['status']=='FAIL'
    # A contrary source for the same question also cannot overwrite failure.
    report=Plan('x',(REQ,),SCOPE,retained=(ev('yes'),ev('no',T.FAIL)), questions=QUESTIONS).evaluate()
    assert row(report)['status']=='FAIL' and len(report['evidence'])==2


def test_same_requirement_different_callable_strategy():
    def beads():
        return (ev('bead-contact'),)
    def thread():
        return (ev('thread-engagement',scope={**SCOPE,'design':'threads'}),)
    for architecture,check in [('beads',beads),('threads',thread)]:
        report=Plan(architecture,(REQ,),{**SCOPE,'design':architecture},
                    (Check(architecture,TARGET,check),), questions=QUESTIONS).evaluate()
        assert row(report)['status']=='PASS'
        assert row(report)['strategies']==[architecture]


def test_design_failure_calculation_inconclusive_and_independent_continuation():
    def fail():
        assert False,'Missing retaining feature'
    def invalid():
        raise CalculationInconclusive('Invalid Boolean')
    checks=tuple(assertion_check(id,TARGET,fn,'fixture.py',SCOPE)
                 for id,fn in [('failure',fail),('invalid',invalid),('independent',lambda:None)])
    report=Plan('x',(REQ,),SCOPE,checks, questions=QUESTIONS).evaluate()
    assert [e['status'] for e in report['evidence']]==[T.FAIL,T.INCONCLUSIVE,T.PASS]
    assert row(report)['status']=='FAIL'
    only_invalid=Plan('x',(REQ,),SCOPE,(checks[1],), questions=QUESTIONS).evaluate()
    assert row(only_invalid)['status']=='INCONCLUSIVE'
    def native_inconclusive():
        raise AssertionError({'status':'inconclusive','error':'kernel failure'})
    assert assertion_check('native',TARGET,native_inconclusive,'fixture.py',SCOPE).run()[0].status==T.INCONCLUSIVE


@pytest.mark.parametrize('status,expected',[('passed',T.PASS),('failed',T.FAIL),('inconclusive',T.INCONCLUSIVE)])
def test_native_result_adapter(status,expected):
    assert engineering_evidence('native',TARGET,SimpleNamespace(status=status),'report.json',SCOPE).status==expected


def test_configuration_and_programming_errors_fail_clearly():
    def bug():
        raise KeyError('misspelled component')
    with pytest.raises(KeyError):
        Plan('x',(REQ,),SCOPE,(assertion_check('bug',TARGET,bug,'code.py',SCOPE),), questions=QUESTIONS).evaluate()
    with pytest.raises(ValueError):
        Plan('x',(REQ,),SCOPE,(Check('typo',(('bad','id'),),lambda:()),), questions=QUESTIONS).evaluate()
    with pytest.raises(ValueError):
        Plan('x',(REQ,),SCOPE, questions=QUESTIONS).evaluate(['typo'])
    with pytest.raises(ValueError):
        Plan('x',(REQ,),SCOPE,(Check('bad',TARGET,lambda:(ev(targets=(('bad','id'),)),)),), questions=QUESTIONS).evaluate()
    with pytest.raises(ValueError):
        Plan('x',(REQ,),SCOPE,retained=(replace(ev(),status='PASS'),), questions=QUESTIONS).evaluate()


def test_empty_result_and_partial_return_do_not_silently_pass():
    report=Plan('x',(REQ,),SCOPE,(Check('attempt',TARGET,lambda:()),), questions=QUESTIONS).evaluate()
    assert row(report)['status']=='UNKNOWN'
    assert row(report)['strategies']==['attempt']
    # A selected check still exposes every other applicable obligation.
    report=Plan('x',(REQ,),SCOPE,(Check('cad',TARGET,lambda:(ev(),)),), questions=QUESTIONS).evaluate([])
    assert report['focused'] and row(report)['status']=='UNKNOWN'


@pytest.mark.parametrize('change',[{'material':'TPU'},{'design':'hinged'},{'sources':'changed'}])
def test_historical_evidence_does_not_transfer_on_material_architecture_or_source_change(change):
    physical=ev('physical',targets=(('fixture.retain','feel'),))
    report=Plan('x',(REQ,),{**SCOPE,**change},retained=(physical,), questions=QUESTIONS).evaluate()
    assert row(report,qid='feel')['status']=='UNKNOWN'
    assert row(report,qid='feel')['out_of_scope']==['physical']
    assert report['evidence'][0]['status']==T.PASS  # history retained, not rewritten


def test_open_hypotheses_and_directives_are_not_scored():
    report=Plan('x',(REQ,),SCOPE,
        hypotheses=(Hypothesis('roughness','Layer lines may cause noise','README.md'),),
        directives=(Directive('stop','Discontinued',S('README.md','User ended work')),), questions=QUESTIONS).evaluate()
    assert 'status' not in report['hypotheses'][0]
    assert 'status' not in report['directives'][0]
    assert 'OPEN roughness' in human_report(report)


def test_inventory_guards_intent_and_invalidates_source_transfer(tmp_path):
    import hashlib
    from dataclasses import asdict
    (tmp_path/'notes').mkdir()
    source=tmp_path/'geometry.py';source.write_text('original')
    record={'source_sha256':{'geometry.py':hashlib.sha256(source.read_bytes()).hexdigest()},
            'user_requirements':[asdict(REQ)]}
    (tmp_path/'notes/verification_sources.json').write_text(json.dumps(record))
    protect_recorded_intent(tmp_path,(REQ,))
    with pytest.raises(ValueError):
        protect_recorded_intent(tmp_path,(DesignDecision(REQ.id,'Change to loose lid','agent'),))
    assert recorded_design_scope(tmp_path)=='migration-reviewed'
    source.write_text('changed')
    assert recorded_design_scope(tmp_path)=='modified-or-missing-source'
    source.unlink()
    assert recorded_design_scope(tmp_path)=='modified-or-missing-source'


def test_records_cannot_be_relabelled_by_putting_them_in_the_wrong_category():
    with pytest.raises(TypeError):
        Plan('x',(REQ,),SCOPE,decisions=(REQ,), questions=QUESTIONS).evaluate()
    with pytest.raises(ValueError):
        Plan('x',(REQ,),SCOPE,questions=(Q('',REQ.id,'',mode='CAD'),)).evaluate()
    with pytest.raises(ValueError):
        Plan('x',(REQ,),{}, questions=QUESTIONS).evaluate()


def test_missing_candidate_scope_key_cannot_match_an_unknown_evidence_key():
    report=Plan('x',(REQ,),{'design':'beads'},retained=(ev(scope={'material':None}),), questions=QUESTIONS).evaluate()
    assert row(report)['status']=='UNKNOWN'
    assert row(report)['out_of_scope']==['cad']


def test_callable_can_return_several_evidence_records_without_repeating_traversal():
    targets=TARGET+(('fixture.retain','feel'),)
    calls=[]
    def run():
        calls.append(1)
        yield ev('cad')
        yield ev('physical',T.UNKNOWN,(('fixture.retain','feel'),))
    report=Plan('x',(REQ,),SCOPE,(Check('traverse',targets,run),), questions=QUESTIONS).evaluate()
    assert calls==[1] and len(report['evidence'])==2
    assert row(report)['status']=='PASS' and row(report,qid='feel')['status']=='UNKNOWN'


def test_engineering_decomposition_replaced_without_new_user_provenance(tmp_path):
    from dataclasses import asdict
    (tmp_path/'notes').mkdir()
    (tmp_path/'notes/verification_sources.json').write_text(json.dumps(
        {'user_requirements':[asdict(REQ)]}))
    old=Plan('beads',(REQ,),SCOPE,questions=QUESTIONS)
    thread=Q('thread',REQ.id,'Thread engagement obstructs axial removal','CAD')
    target=((REQ.id,thread.id),)
    new=Plan('threads',(REQ,),{**SCOPE,'design':'threads'},questions=(thread,),
        checks=(Check('thread',target,lambda:(ev('thread',targets=target,
            scope={**SCOPE,'design':'threads'}),)),))
    protect_user_requirements(old.requirements,new.requirements)
    protect_recorded_intent(tmp_path,new.requirements)
    assert row(new.evaluate(),qid='thread')['status']=='PASS'
    # Engineering screens and sampling are challengeable too.
    replace(new,questions=(replace(thread,criterion='Use a revised axial witness'),)).validate()
    protect_recorded_intent(tmp_path,new.requirements)


def test_no_decomposition_cannot_hide_an_active_user_requirement():
    other=U('fixture.other','Other user intent',S('fixture','User asks another function'))
    q=Q('check',other.id,'Other function works','CAD')
    target=((other.id,q.id),)
    report=Plan('threads',(REQ,other),SCOPE,questions=(q,),
        checks=(Check('other',target,lambda:(ev(targets=target),)),)).evaluate()
    requirement=report['requirements'][0]
    assert requirement['id']==REQ.id and requirement['questions']==[]
    assert requirement['coverage']=='uncovered'
    assert row(report,rid=other.id,qid=q.id)['status']=='PASS'
    assert 'UNKNOWN fixture.retain [uncovered]' in human_report(report)


@pytest.mark.parametrize('change',[
    {'text':'Interior may have any size'},
    {'acceptance_criteria':('Interior must be 168 × 88 × 68 mm',)},
    {'acceptance_criteria':()},
    {'source':S('agent notes','Agent chose other dimensions')},
    {'id':'renamed'},
])
def test_explicit_user_interior_dimensions_are_protected(change):
    requirement=U('case.cavity','Requested interior',
        S('user confirmation','User explicitly requires 158 × 78 × 63 mm interior'),
        ('Interior must be 158 × 78 × 63 mm',))
    with pytest.raises(ValueError,match='user instruction'):
        protect_user_requirements((requirement,),(replace(requirement,**change),))
    later=S('later user instruction','User changes interior to 168 × 88 × 68 mm')
    protect_user_requirements((requirement,),(replace(requirement,**change),),
        changes={requirement.id:later})


def test_keeper_derivation_can_be_retired_without_retiring_cover_intent():
    keeper=D('fixture.keeper','Keeper remains captured',(REQ.id,),'Separate keeper architecture')
    capture=Q('capture',keeper.id,'Keeper pull is obstructed','CAD')
    old=Plan('keeper',(REQ,keeper),SCOPE,questions=QUESTIONS+(capture,))
    new=Plan('thread',(REQ,),SCOPE)
    protect_user_requirements(old.requirements,new.requirements)
    report=new.evaluate()
    assert [r['id'] for r in report['requirements']]==[REQ.id]
    assert report['requirements'][0]['coverage']=='uncovered'
    na=replace(old,non_applicable={keeper.id:'Threaded design has no keeper'}).evaluate()
    assert na['requirements'][1]['non_applicable']
    assert all(q['status']=='UNKNOWN' for q in na['requirements'][0]['questions'])


def test_question_parent_and_local_id_validation():
    with pytest.raises(ValueError,match='parent'):
        Plan('x',(REQ,),SCOPE,questions=(Q('x','absent','Works','CAD'),)).validate()
    with pytest.raises(ValueError,match='unique'):
        Plan('x',(REQ,),SCOPE,questions=QUESTIONS+QUESTIONS).validate()
