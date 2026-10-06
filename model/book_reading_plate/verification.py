"""Reuse plate seating checks and retained conditional analytical evidence."""
from functools import cache
import json
import math
from pathlib import Path
from product_verification import (Question as Q, UserRequirement as U, DerivedRequirement as D,
    UserSource as S, DesignDecision, Hypothesis, Evidence, Status, Plan, Check,
    assertion_check, cli, recorded_design_scope, protect_recorded_intent)

ROOT=Path(__file__).resolve().parent
RECORD='README.md'
REQUIREMENTS=(
    U('plate.use','Complete reading plate is satisfactory for its intended use',
      S(RECORD+'#physical-status','User reports complete revised plate printed with a really nice result'),
      (Q('assembly','Declared assembled components satisfy clearance and required seating/support roles'),
       Q('finish','Complete print result is satisfactory in reported use','subjective'),
       Q('load','Actual intended-load use is satisfactory; specific physical loads were not reported','physical'))),
    D('plate.joint','Joined halves carry the intended book/handling load',('plate.use',),
      'A multipart reading plate needs a working load path; assumed numerical load envelope is challengeable',
      (Q('screen','Retained analytical strength screens meet their provisional allowances under recorded assumptions','analytical'),
       Q('creep','Long-term creep/loosening remains acceptable; trial/criterion still unspecified','physical'))),
)


def make_plan(variant):
    protect_recorded_intent(ROOT,REQUIREMENTS)
    if variant not in ('accepted-plate','replacement-fixture'):
        raise ValueError(variant)
    scope={'design':variant,'sources':recorded_design_scope(ROOT),'material':'reported-print-process-unknown'}
    checks=[]
    if variant=='accepted-plate':
        import assembly_checks as a
        @cache
        def candidate():
            return a.configuration(a.build())
        checks.append(assertion_check('plate.seating',(('plate.use','assembly'),),
            lambda:a.verify(candidate()),'assembly_checks.py#verify',scope))
        def retained_screen():
            # Existing result source inventory, not another solve/cache identity.
            from execution.identity import digest
            path=ROOT/'notes/load_checks.json'
            if not path.is_file():
                return (Evidence('plate.analytical',(('plate.joint','screen'),),Status.UNKNOWN,
                    'Retained analytical record missing; no new solve launched','notes/load_checks.json',scope),)
            inventory=json.loads((ROOT/'notes/verification_sources.json').read_text())
            expected=inventory['analytical_coverage']
            if any(not isinstance(expected[key],list) or not expected[key] or
                   any(not isinstance(x,str) or not x for x in expected[key]) or
                   len(set(expected[key]))!=len(expected[key]) for key in ('inputs','checks')):
                raise ValueError('Invalid configured analytical coverage contract')
            try:
                record=json.loads(path.read_text())
                if not isinstance(record,dict):
                    raise ValueError('Analytical record must be a mapping')
                hashes=record['source_sha256']
                if (not isinstance(hashes,dict) or set(hashes)!=set(expected['inputs']) or
                        any(not isinstance(h,str) or len(h)!=64 or
                            any(c not in '0123456789abcdef' for c in h) for h in hashes.values())):
                    raise ValueError('Missing/invalid analytical input inventory')
                inputs={n:ROOT/('notes/sections.json' if n=='sections.json' else n) for n in hashes}
                reviewed=inventory.get('retained_analytical_source_associations',{})
                def applicable(name,recorded):
                    if not inputs[name].is_file():
                        return False
                    current=digest(inputs[name])
                    if current==recorded:
                        return True
                    association=reviewed.get(name,{})
                    return (association.get('recorded')==recorded and
                            association.get('reviewed_current')==current and bool(association.get('reason')))
                if not hashes or not all(applicable(n,h) for n,h in hashes.items()):
                    status=Status.UNKNOWN
                    message='Retained analytical inputs changed; rerun existing measurement/arithmetic route when useful'
                else:
                    screens=record['checks']
                    if not isinstance(screens,dict) or set(screens)!=set(expected['checks']):
                        raise ValueError('Incomplete analytical screen coverage')
                    for c in screens.values():
                        if (not isinstance(c,dict) or type(c['passes']) is not bool or
                                any(type(c[k]) not in (int,float) or not math.isfinite(c[k])
                                    for k in ('stress_MPa','allowable_MPa','margin')) or
                                c['stress_MPa']<=0 or c['allowable_MPa']<=0 or c['margin']<=0 or
                                c['passes'] != (c['stress_MPa']<=c['allowable_MPa']) or
                                not math.isclose(c['margin'],c['allowable_MPa']/c['stress_MPa'])):
                            raise ValueError('Invalid or inconsistent analytical quantities')
                    minimum=record['minimum_margin']
                    if (type(minimum) not in (int,float) or not math.isfinite(minimum) or
                            not math.isclose(minimum,min(c['margin'] for c in screens.values()))):
                        raise ValueError('Invalid or inconsistent minimum margin')
                    status=Status.PASS if all(c['passes'] for c in screens.values()) else Status.FAIL
                    message=f"Retained conditional screen; minimum margin {record['minimum_margin']:.3f}; no physical load qualification"
            except (KeyError, ValueError, TypeError) as exc:
                status=Status.INCONCLUSIVE
                message=f'Attempted retained-result interpretation failed: {exc}'
            return (Evidence('plate.analytical',(('plate.joint','screen'),),status,message,'notes/load_checks.json',scope),)
        checks.append(Check('plate.analytical',(('plate.joint','screen'),),retained_screen))
    retained=(Evidence('plate.print-report',(('plate.use','finish'),),Status.PASS,
        'Complete revised plate printed; user says really nice. Exact printed hash/material/settings and specific load observations unknown',
        RECORD+'#physical-status',{'design':'accepted-plate','sources':'migration-reviewed','material':'reported-print-process-unknown'}),)
    return Plan(variant,REQUIREMENTS,scope,tuple(checks),retained,
        decisions=(DesignDecision('plate.four-screws','Four printed screws, custom thread, conical seats and current dimensions are implementation choices, not immutable user requirements',RECORD+'#what-changed-after-the-successful-l-sample'),),
        hypotheses=(Hypothesis('plate.screen-assumptions','3 kg book, 2× handling, 800 MPa effective modulus, solid PETG and preload ≤40 N are provisional analytical assumptions, not user load rating or calibrated properties',RECORD+'#mechanical-review'),))


if __name__=='__main__':
    raise SystemExit(cli(make_plan,('accepted-plate','replacement-fixture')))
