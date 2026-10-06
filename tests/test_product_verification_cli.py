"""CLI outcomes carry their meaning in JSON, never distinct shell error codes."""
import json
from types import SimpleNamespace
import pytest
from product_verification import (Question, UserRequirement, UserSource, Evidence,
    Check, Plan, Status, cli)

REQ=UserRequirement('fixture.use','Usable product',UserSource('README.md','User asks usable product'),
                    (Question('geometry','Geometry works'),))
SCOPE={'design':'candidate'}
TARGET=(('fixture.use','geometry'),)
ARGS=['--variant','candidate']


def plan(status=Status.PASS):
    evidence=Evidence('fixture.check',TARGET,status,'Checked criterion','fixture.py',SCOPE)
    return Plan('candidate',(REQ,),SCOPE,(Check('fixture.check',TARGET,lambda:(evidence,)),))


def read(capsys):
    captured=capsys.readouterr()
    payload=json.loads(captured.out)  # Rejects text prefixes or multiple documents.
    assert set(payload)=={'schema_version','variant','selected_checks','available_variants',
                          'available_checks','exit_reason','error','report','help'}
    assert payload['schema_version']==1 and payload['available_variants']==['candidate']
    return payload,captured.err


@pytest.mark.parametrize('status,reason,code',[
    (Status.PASS,'verification_complete',0),
    (Status.FAIL,'criterion_failed',1),
    (Status.UNKNOWN,'unresolved_evidence',1),
    (Status.INCONCLUSIVE,'unresolved_evidence',1)])
def test_normal_outcomes_share_json_shape_and_only_binary_exit_codes(status,reason,code,capsys):
    assert cli(lambda variant:plan(status),('candidate',),argv=ARGS)==code
    result,stderr=read(capsys)
    assert result['variant']=='candidate'
    assert result['exit_reason']==reason and result['error'] is None
    assert result['report']['requirements'][0]['questions'][0]['status']==status
    assert result['available_checks']==['fixture.check']
    assert not stderr


def test_progress_never_pollutes_json_stdout(capsys):
    def factory(variant):
        print('planning progress')
        candidate=plan()
        def run():
            print('check progress')
            return candidate.checks[0].run()
        return Plan('candidate',(REQ,),SCOPE,(Check('fixture.check',TARGET,run),))
    assert cli(factory,('candidate',),argv=ARGS)==0
    result,stderr=read(capsys)
    assert result['exit_reason']=='verification_complete'
    assert 'planning progress' in stderr and 'check progress' in stderr


def test_focused_selection_is_structured_and_uncovered_questions_stay_visible(capsys):
    assert cli(lambda variant:plan(),('candidate',),argv=ARGS+['--check','fixture.check'])==0
    result,_=read(capsys)
    assert result['selected_checks']==['fixture.check'] and result['report']['focused']


@pytest.mark.parametrize('argv',[[],['--bogus'],['--check'],['--variant','absent'],
    ARGS+['--json'],ARGS+['--human'],ARGS+['--output','summary.json']])
def test_argument_errors_are_json_with_choices_and_no_argparse_exit_two(argv,capsys):
    assert cli(lambda variant:pytest.fail('Must not run an invalid invocation'),('candidate',),argv=argv)==1
    result,_=read(capsys)
    assert result['exit_reason']=='argument_error'
    assert result['error']['stage']=='arguments' and result['report'] is None
    if 'absent' in argv:
        assert result['variant']=='absent'


def test_unknown_check_lists_valid_names_without_running_checks(capsys):
    assert cli(lambda variant:plan(),('candidate',),argv=ARGS+['--check','misspelled'])==1
    result,_=read(capsys)
    assert result['exit_reason']=='argument_error' and result['report'] is None
    assert result['error']['stage']=='selection'
    assert result['available_checks']==['fixture.check']


@pytest.mark.parametrize('stage',['planning','verification'])
@pytest.mark.parametrize('error',[KeyError('program bug'),SystemExit(7),KeyboardInterrupt()])
def test_runtime_errors_interrupts_and_unexpected_exits_emit_json(stage,error,capsys):
    def broken(*args):
        print('before error')
        raise error
    factory=broken if stage=='planning' else lambda variant:SimpleNamespace(checks=(),evaluate=broken)
    assert cli(factory,('candidate',),argv=ARGS)==1
    result,stderr=read(capsys)
    assert result['exit_reason']==('interrupted' if isinstance(error,KeyboardInterrupt) else 'execution_error')
    assert result['error']['stage']==stage and result['error']['type']==type(error).__name__
    assert result['report'] is None and 'before error' in stderr


@pytest.mark.parametrize('value',[float('nan'),object()])
def test_invalid_json_evidence_cannot_emit_nonstandard_json_or_claim_a_result(value,capsys):
    report=plan().evaluate()
    report['bad_quantity']=value
    assert cli(lambda variant:SimpleNamespace(checks=(),evaluate=lambda selected:report),
               ('candidate',),argv=ARGS)==1
    result,_=read(capsys)
    assert result['exit_reason']=='report_error' and result['report'] is None
    assert result['error']['stage']=='serialization'


def test_excessively_nested_report_still_emits_a_json_error(capsys):
    nested={}
    for _ in range(1100):
        nested={'child':nested}
    report=plan().evaluate()
    report['invalid_detail']=nested
    assert cli(lambda variant:SimpleNamespace(checks=(),evaluate=lambda selected:report),
               ('candidate',),argv=ARGS)==1
    result,_=read(capsys)
    assert result['exit_reason']=='report_error' and result['report'] is None
    assert result['error']['type']=='RecursionError'


@pytest.mark.parametrize('extra',[[],['--help']])
def test_invalid_check_metadata_cannot_poison_the_error_envelope(extra,capsys):
    candidate=Plan('candidate',(REQ,),SCOPE,(Check(object(),TARGET,lambda:()),))
    assert cli(lambda variant:candidate,('candidate',),argv=ARGS+extra)==1
    result,_=read(capsys)
    assert result['exit_reason']=='execution_error' and result['report'] is None
    assert result['available_checks'] is None
    assert result['error']['message']=='Declared check IDs must be nonempty strings'


def test_invalid_variant_configuration_is_a_json_error_not_a_poisoned_envelope(capsys):
    assert cli(lambda variant:plan(),(object(),),argv=['--help'])==1
    captured=capsys.readouterr()
    result=json.loads(captured.out)
    assert result['exit_reason']=='execution_error' and result['report'] is None
    assert result['available_variants']==[]


def test_help_is_a_successful_json_response_without_running_verification(capsys):
    assert cli(lambda variant:pytest.fail('Generic help must not build a plan'),
               ('candidate',),argv=['--help'])==0
    result,_=read(capsys)
    assert result['exit_reason']=='help_requested' and '--variant' in result['help']
    assert result['variant'] is None and result['available_checks'] is None
    assert result['report'] is None and result['error'] is None


def test_variant_help_lists_actual_checks_without_computation(capsys):
    candidate=Plan('candidate',(REQ,),SCOPE,(Check('named.check',TARGET,
        lambda:pytest.fail('Help must not execute checks')),))
    assert cli(lambda variant:candidate,('candidate',),argv=ARGS+['--help'])==0
    result,_=read(capsys)
    assert result['variant']=='candidate' and result['available_checks']==['named.check']
    assert result['exit_reason']=='help_requested' and result['report'] is None


def test_variant_help_still_exposes_programming_configuration_errors(capsys):
    candidate=Plan('candidate',(REQ,),SCOPE,(Check('bad.check',(('absent','id'),),lambda:()),))
    assert cli(lambda variant:candidate,('candidate',),argv=ARGS+['--help'])==1
    result,_=read(capsys)
    assert result['exit_reason']=='execution_error' and result['error']['type']=='ValueError'
    assert result['report'] is None


def test_mixed_evidence_survives_the_command_reason(capsys):
    questions=(Question('geometry','Geometry works'),Question('use','User accepts use','physical'),
               Question('life','Durability is known','physical'))
    requirement=UserRequirement(REQ.id,REQ.text,REQ.source,questions)
    retained=(Evidence('physical',((REQ.id,'use'),),Status.FAIL,'User rejected use','README.md',SCOPE),)
    candidate=Plan('candidate',(requirement,),SCOPE,plan().checks,retained)
    assert cli(lambda variant:candidate,('candidate',),argv=ARGS)==1
    result,_=read(capsys)
    assert result['exit_reason']=='criterion_failed'
    assert [q['status'] for q in result['report']['requirements'][0]['questions']]==['PASS','FAIL','UNKNOWN']
