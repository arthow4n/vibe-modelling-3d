"""Historical Q1/Q1F verification; does not reopen discontinued damping work."""
from functools import cache
from pathlib import Path
from product_verification import (Question as Q, UserRequirement as U, DerivedRequirement as D,
    UserSource as S, DesignDecision, Hypothesis, Directive, Evidence, Status, Plan,
    assertion_check, Check, cli, recorded_design_scope, protect_recorded_intent)

ROOT=Path(__file__).resolve().parent
RECORD='README.md'
REQUIREMENTS=(
    U('swatch.storage','Store and access the accepted 15-card collection',
      S(RECORD+'#quiet-tpu-revision--q1f-with-the-accepted-exterior-2026-10-05',
        'Accepted archive A capacity/pocket retained for this storage trial'),
      acceptance_criteria=('Store the accepted 15-card collection.',)),
    U('swatch.open','Closed cover remains retained and can be deliberately opened',
      S(RECORD+'#quiet-tpu-revision--q1f-with-the-accepted-exterior-2026-10-05','Established archive closure/opening task')),
    U('swatch.join','Join modules and open each independently',
      S(RECORD+'#damped-prototype-print-feedback-and-svg-exploration-2026-10-06','User reports successful Q1F module connections; preserve working joining')),
    U('swatch.quiet','Closing/sliding sound is acceptable to the user',
      S(RECORD+'#tpu-damping-discontinued-2026-10-06','User says remaining sound exceeds acceptable level')),
    U('swatch.appearance','Contrasting coverage and whole-shell appearance are acceptable',
      S(RECORD+'#damped-prototype-print-feedback-and-svg-exploration-2026-10-06','User rejects exposed white base and disconnected-looking black bands')),
    U('swatch.upper-fit','Upper jacket feels positively located',
      S(RECORD+'#damped-prototype-print-feedback-and-svg-exploration-2026-10-06','User rejects loose/floating upper regions')),
    D('swatch.landing-access','Chosen soft-seat and grip architecture has its declared geometric contacts/access',
      ('swatch.quiet','swatch.open'),'Contact is necessary for the proposed TPU landing role, and the chosen grip needs geometric access; neither establishes quietness or comfort'),
    D('swatch.insert-anchored','Chosen separate insert stays captured',
      ('swatch.open','swatch.upper-fit'),'A removable hood must not carry away its separate jacket; rigid witnesses do not establish release forces'),
    D('swatch.insert-connected','Q1F port cuts leave one connected printable insert',
      ('swatch.upper-fit',),'Chosen one-piece insert architecture requires connected port bypasses; observed CAD defect'),
    D('swatch.durability','Closure and joining remain usable after dwell/wear',
      ('swatch.open','swatch.join'),'Continued use requires retained function; duration/loads are not yet specified'),
)
DIRECTIVES=(Directive('swatch.stop',
    'Damping work discontinued 2026-10-06. No development or print recommendation unless user reopens it; A/G baseline retained, J4/K4 repairs deferred. Follow-up SVG proposals are superseded untested history.',
    S(RECORD+'#tpu-damping-discontinued-2026-10-06','User ended damping work')),)


# Current engineering decomposition; replace as the architecture changes.
QUESTIONS=(
    Q('seating', 'swatch.storage', 'Required 15-card fixture clears enclosure and seats on actual floor; existing entry/extraction paths clear', mode='CAD'),
    Q('use', 'swatch.storage', 'Loaded collection stays stored during reported cover handling', 'physical'),
    Q('closed', 'swatch.open', 'Nominal assembly clears forbidden overlaps', mode='CAD'),
    Q('path-retention', 'swatch.open', 'Existing sampled opening paths clear rigid parts and meet declared retention material', mode='CAD'),
    Q('effort', 'swatch.open', 'Comfortable deliberate opening and no unintended removal in actual use', 'physical'),
    Q('geometry', 'swatch.join', 'Declared joining/capture and independent opening work at both ends against named neighbours', mode='CAD'),
    Q('use', 'swatch.join', 'Module connections work in reported use', 'physical'),
    Q('sound', 'swatch.quiet', 'User finds sound acceptable', 'subjective'),
    Q('appearance', 'swatch.appearance', 'User accepts contrasting coverage and shell appearance', 'subjective'),
    Q('feel', 'swatch.upper-fit', 'Upper jacket is satisfactory in actual use', 'physical'),
    Q('roles', 'swatch.landing-access', 'Existing downward TPU-seat witness and finger-envelope clearance criteria hold', mode='CAD'),
    Q('capture', 'swatch.insert-anchored', 'Existing rigid lift/twist capture and explicit expanded-envelope access screens hold', mode='CAD'),
    Q('topology', 'swatch.insert-connected', 'Insert has one solid; retained local rim crest screens are at least 0.8 mm', mode='CAD'),
    Q('dwell', 'swatch.durability', 'Representative dwell/wear acceptance and observation still needed', 'physical'),
)


def make_plan(variant):
    protect_recorded_intent(ROOT,REQUIREMENTS)
    if variant not in ('q1f','q1','q1f-tpu-hood','replacement-fixture'):
        raise ValueError(variant)
    scope={'design':variant, 'sources':recorded_design_scope(ROOT),
           'hood-material':'TPU-reported' if variant=='q1f-tpu-hood' else 'PETG-planned/reported',
           'insert-material':'TPU95A-reported-stock'}
    # Physical associations are to the user's identified design, not exact print
    # files/settings (unknown). Changed source/material/architecture stays unknown.
    physical_scope={'design':'q1f','sources':'migration-reviewed',
                    'hood-material':'PETG-planned/reported','insert-material':'TPU95A-reported-stock'}
    retained=tuple(Evidence(id,((rid,qid),),status,text,RECORD+anchor,physical_scope)
        for id,rid,qid,status,text,anchor in (
        ('q1f.join-report','swatch.join','use',Status.PASS,'User reports joining works; neighbour identities/ends, loads and printed hashes/settings unknown','#damped-prototype-print-feedback-and-svg-exploration-2026-10-06'),
        ('q1f.noise-report','swatch.quiet','sound',Status.FAIL,'Substantial sliding sound remains unacceptable; no acoustic measurement','#damped-prototype-print-feedback-and-svg-exploration-2026-10-06'),
        ('q1f.coverage-report','swatch.appearance','appearance',Status.FAIL,'User rejects white/black coverage and visible connecting bands','#damped-prototype-print-feedback-and-svg-exploration-2026-10-06'),
        ('q1f.fit-report','swatch.upper-fit','feel',Status.FAIL,'Upper jacket feels loose/floating; no measured gap/cause','#damped-prototype-print-feedback-and-svg-exploration-2026-10-06')))
    tpu_scope={**physical_scope,'design':'q1f-tpu-hood','hood-material':'TPU-reported'}
    retained+=(Evidence('tpu-hood.sound',(('swatch.quiet','sound'),),Status.FAIL,
        'Unchanged G hood in TPU somewhat quieter but still unacceptable; actual grade/process unknown',
        RECORD+'#tpu-damping-discontinued-2026-10-06',tpu_scope),
        Evidence('tpu-hood.shape',(('swatch.appearance','appearance'),),Status.UNKNOWN,
        'Upper shell distorted/movable yet usable; not a failure to perform its task; timing/cause unknown',
        RECORD+'#tpu-damping-discontinued-2026-10-06',tpu_scope))
    retained+=(Evidence('archive.accepted-loaded',(('swatch.storage','use'),),Status.PASS,
        'Accepted archive A/G/I3 baseline; full 15-card load retained during reported hood lift. Exact files/settings unknown; not Q1/Q1F physical qualification',
        RECORD+'#physical-history-and-print-status',{'design':'archive-a-g-i3','material':'reported-print-process-unknown'}),)
    checks=[]
    if variant in ('q1f','q1'):
        import quiet_q1, quiet_q1_flush
        from quiet_assembly import QuietAssembly
        from check_quiet_q1 import closed_checks, card_checks, hood_checks, insert_checks, landing_checks, joining_checks
        from check_quiet_q1_flush import local_checks
        @cache
        def candidate():
            return QuietAssembly(quiet_q1_flush if variant=='q1f' else quiet_q1)
        for id,targets,fn,ref in (
            ('quiet.closed',(('swatch.open','closed'),),closed_checks,'check_quiet_q1.py'),
            ('quiet.cards',(('swatch.storage','seating'),),card_checks,'check_quiet_q1.py'),
            ('quiet.join',(('swatch.join','geometry'),),joining_checks,'check_quiet_q1.py')):
            checks.append(assertion_check(id,targets,lambda fn=fn:fn(candidate(),[]),ref,scope))
        # One composed check returns independent answers for different
        # obligations, sharing the actual candidate construction. A bad hood
        # path cannot falsely report failed insert capture (or suppress it).
        hood=assertion_check('quiet.hood.path',(('swatch.open','path-retention'),),
            lambda:hood_checks(candidate(),[]),'check_quiet_q1.py#hood_checks',scope)
        insert=assertion_check('quiet.hood.insert',(('swatch.insert-anchored','capture'),),
            lambda:insert_checks(candidate(),[]),'check_quiet_q1.py#insert_checks',scope)
        landing=assertion_check('quiet.hood.landing',(('swatch.landing-access','roles'),),
            lambda:landing_checks(candidate(),[]),'check_quiet_q1.py#landing_checks',scope)
        checks.append(Check('quiet.hood',hood.targets+insert.targets+landing.targets,
                            lambda:hood.run()+insert.run()+landing.run()))
        if variant=='q1f':
            checks.append(assertion_check('q1f.insert',(('swatch.insert-connected','topology'),),
                lambda:local_checks(candidate()),'check_quiet_q1_flush.py',scope))
    # The all-TPU physical trial has no material-qualified engineering strategy.
    # Reusing PETG nominal CAD is not whole-shell TPU qualification.
    na={} if variant in ('q1f','q1f-tpu-hood') else {
        'swatch.insert-connected':'Q1F port-bypass insert architecture absent; Q1 uses its original sleeve' if variant=='q1'
        else 'Replacement fixture declares no insert architecture'}
    if variant=='replacement-fixture':
        na['swatch.insert-anchored']='Replacement declares no separate jacket'
        na['swatch.landing-access']='Replacement declares no prototype TPU-seat/recessed-grip architecture'
    return Plan(variant,REQUIREMENTS,scope,tuple(checks),retained,na,
        questions=QUESTIONS,
        decisions=(DesignDecision('swatch.mechanism','Separate TPU jacket, four beads and (Q1F) reused G hood are historical implementation choices; replacement may discard them',RECORD),),
        hypotheses=(Hypothesis('swatch.layers','User suspects printed lines/roughness cause rubbing sound; unconfirmed',RECORD+'#tpu-damping-discontinued-2026-10-06'),),
        directives=DIRECTIVES)


if __name__=='__main__':
    raise SystemExit(cli(make_plan,('q1f','q1','q1f-tpu-hood','replacement-fixture')))
