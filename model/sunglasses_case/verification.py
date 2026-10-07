"""Current accepted case or deliberately uncovered architecture-replacement fixture."""
from functools import cache
from pathlib import Path
from product_verification import (Question as Q, UserRequirement as U, DerivedRequirement as D,
    UserSource as S, DesignDecision, Hypothesis, Evidence, Status, Plan, assertion_check,
    cli, recorded_design_scope, protect_recorded_intent)

ROOT=Path(__file__).resolve().parent
RECORD='notes/printing_and_design.md'
REQUIREMENTS=(
    U('case.cavity','Provide the user-confirmed 158 × 78 × 63 mm rounded interior',
      S(RECORD+'#confirmed-dimensions-and-physical-feedback','User explicitly confirmed reduced interior, superseding earlier approximate measurements'),
      acceptance_criteria=('Nominal interior is 158 × 78 × 63 mm.',)),
    U('case.operation','Case closes, retains and deliberately opens satisfactorily',
      S(RECORD+'#physical-print-status','D/E samples satisfactory; user printed current reduced integrated case and reports it works really well')),
    D('case.geometry','Enclosure components are valid connected printable parts',('case.operation',),
      'Current separate physical components must be constructible before interpreting their interaction checks'),
    D('case.keeper','Separate keeper remains geometrically captured',('case.operation',),
      'Only applies to separate inserted-keeper architecture; replace when architecture changes'),
    D('case.durability','Operation remains satisfactory after fatigue/backpack use',('case.operation',),
      'Repeated use can change closure/hinge function; no quantified lifespan was specified'),
)


# Current engineering decomposition; replace as the architecture changes.
QUESTIONS=(
    Q('dimensions', 'case.cavity', 'Nominal interior is 158 × 78 × 63 mm; rounded corners are part of its definition', mode='CAD'),
    Q('empty', 'case.cavity', 'Enclosure and mechanism leave the requested rounded cavity empty', mode='CAD'),
    Q('closed', 'case.operation', 'Closed components satisfy their declared clearance/contact roles', mode='CAD'),
    Q('path', 'case.operation', 'Declared opening path clears the enclosure; proxy exclusions remain explicit', mode='CAD'),
    Q('retention', 'case.operation', 'Declared retention geometry obstructs unintended opening; holding force remains physical', mode='CAD'),
    Q('release', 'case.operation', 'Declared intentional release path clears; actuation force remains physical', mode='CAD'),
    Q('use', 'case.operation', 'Integrated case works satisfactorily in reported use', 'physical'),
    Q('validity', 'case.geometry', 'Existing production component validity/connectivity and local print-placement assertions hold', mode='CAD'),
    Q('capture', 'case.keeper', 'Original vertical/outward 0.4 mm keeper pulls meet body with >1 mm³ overlap', mode='CAD'),
    Q('life', 'case.durability', 'Long-term fatigue and backpack durability require a defined physical trial', 'physical'),
)


def make_plan(variant):
    protect_recorded_intent(ROOT,REQUIREMENTS)
    if variant not in ('accepted-e','replacement-fixture','tpu-fixture'):
        raise ValueError(variant)
    scope={'design':variant,'sources':recorded_design_scope(ROOT),
           'material':'TPU-candidate' if variant=='tpu-fixture' else 'reported-print-process-unknown'}
    retained=(Evidence('case.full-print',(('case.operation','use'),),Status.PASS,
        'User reports current reduced full case works really well; exact printed hash/material/profile not recorded',
        RECORD+'#physical-print-status',{'design':'accepted-e','sources':'migration-reviewed','material':'reported-print-process-unknown'}),)
    retained+=tuple(Evidence('case.sample-'+sample,(('case.operation','use'),),Status.PASS,
        'User found '+sample+' sample satisfactory; E slightly preferred; coupon is not the integrated case or durability trial',
        'notes/mechanism_history.md',{'design':'sample-'+sample,'material':'reported-print-process-unknown'})
        for sample in ('D','E'))
    checks=[]
    if variant in ('accepted-e','tpu-fixture'):
        import assembly_checks as a
        @cache
        def candidate():
            return a.load(verify=False)
        def dimensions():
            m=candidate()
            assert (m['INNER_LENGTH'],m['INNER_WIDTH'],m['INNER_HEIGHT'])==(158,78,63), 'User-confirmed dimensions changed'
        def construction():
            m=candidate()
            m['verify_parts']()
            m['verify_print_layout']()
        for id,targets,run,reference in (
            ('case.validity',(('case.geometry','validity'),),construction,'sunglasses_case.py#verify_parts'),
            ('case.dimensions',(('case.cavity','dimensions'),),dimensions,'sunglasses_case.py'),
            ('case.cavity',(('case.cavity','empty'),),lambda:candidate()['verify_cavity'](),'sunglasses_case.py#verify_cavity'),
            ('e.closed',(('case.operation','closed'),),lambda:a.closed_checks(candidate()),'assembly_checks.py#closed_checks'),
            ('e.hinge',(('case.operation','path'),),lambda:a.hinge_checks(candidate()),'assembly_checks.py#hinge_checks'),
            ('e.retention',(('case.operation','retention'),),lambda:a.retention_checks(candidate()),'assembly_checks.py#retention_checks'),
            ('e.release',(('case.operation','release'),),lambda:a.release_checks(candidate()),'assembly_checks.py#release_checks'),
            ('e.keeper',(('case.keeper','capture'),),lambda:candidate()['verify_keeper_capture'](),'sunglasses_case.py#verify_keeper_capture')):
            checks.append(assertion_check(id,targets,run,reference,scope))
    return Plan(variant,REQUIREMENTS,scope,tuple(checks),retained,
        {'case.keeper':'Replacement declares no separate keeper'} if variant=='replacement-fixture' else {},
        questions=QUESTIONS,
        decisions=(DesignDecision('case.e-choice','E mechanism is preferred tested implementation, not a permanent user requirement; alternatives leave behind its physical qualification',RECORD+'#e-mechanism-integration'),),
        hypotheses=(Hypothesis('case.process','PETG and saved profile are intended printing assumptions; actual full-print settings are not calibrated evidence',RECORD+'#printing-and-assembly'),))


if __name__=='__main__':
    raise SystemExit(cli(make_plan,('accepted-e','replacement-fixture','tpu-fixture')))
