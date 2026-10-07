"""Small adoption of existing helical/axial checks and scoped print feedback."""
from functools import cache
from pathlib import Path
from product_verification import (Question as Q, UserRequirement as U, DerivedRequirement as D,
    UserSource as S, DesignDecision, Evidence, Status, Plan, assertion_check, cli, recorded_design_scope, protect_recorded_intent)

ROOT=Path(__file__).resolve().parent
RECORD='README.md'
REQUIREMENTS=(
    U('jar.envelope','Container fits the requested 50 mm diameter × 25 mm assembled height',
      S(RECORD+'#decisions-and-evidence','Requested 25 mm is assembled height; 50 mm diameter envelope'),
      (Q('dimensions','Declared diameter/closed height remain 50/25 mm; scallops are cut inward', mode='CAD'),)),
    U('jar.use','Two-piece jar opens/closes and works in reported use',
      S(RECORD+'#physical-print-status','User printed delivered full pair and reports it was good'),
      (Q('path','Declared opening path clears forbidden solid obstruction (sampled CAD only)', mode='CAD'),
       Q('retention','Declared retention geometry obstructs unintended removal; holding force remains physical', mode='CAD'),
       Q('print-use','Delivered full pair has a satisfactory reported print result','physical'),
       Q('handling','Actual opening/closing effort and retention need specific use observations','physical'))),
    D('jar.wear','Closure remains usable after repeated operation',('jar.use',),
      'Wear can change fit; no life target or physical wear trial exists',
      (Q('life','Wear qualification remains physical and unspecified','physical'),)),
)


def make_plan(variant):
    protect_recorded_intent(ROOT,REQUIREMENTS)
    if variant not in ('accepted-thread','replacement-fixture'):
        raise ValueError(variant)
    scope={'design':variant,'sources':recorded_design_scope(ROOT),'material':'reported-print-process-unknown'}
    checks=[]
    if variant=='accepted-thread':
        import assembly_checks as a
        @cache
        def candidate():
            return a.load()
        def envelope():
            m=candidate()
            assert (m['OUTER_DIAMETER'],m['CLOSED_HEIGHT'])==(50,25), 'Requested envelope changed'
        for id,target,run in (
            ('jar.envelope',('jar.envelope','dimensions'),envelope),
            ('thread.withdrawal',('jar.use','path'),lambda:a.withdrawal_checks(candidate())),
            ('thread.retention',('jar.use','retention'),lambda:a.retention_checks(candidate()))):
            checks.append(assertion_check(id,(target,),run,'assembly_checks.py / vaseline_container.py',scope))
    retained=(Evidence('jar.print-report',(('jar.use','print-use'),),Status.PASS,
        'Delivered full pair printed and good; print date, actual material/printer/profile and hash unknown (recorded 2026-09-12)',
        RECORD+'#physical-print-status',{'design':'accepted-thread','sources':'migration-reviewed','material':'reported-print-process-unknown'}),)
    return Plan(variant,REQUIREMENTS,scope,tuple(checks),retained,
        decisions=(DesignDecision('jar.thread-choice','Coarse 3 mm pitch screw closure and scallops are current implementation; no leak-tight seal requirement/claim',RECORD+'#use-and-files'),))


if __name__=='__main__':
    raise SystemExit(cli(make_plan,('accepted-thread','replacement-fixture')))
