"""Scoped human-interaction receipt plus unresolved integrated operation.

The existing CAD/physical engineering records remain in README.md. This small
plan protects the recorded adjustment intent, not every historical stand study.
"""
import json
from pathlib import Path

import numpy as np
from product_verification import (UserRequirement, UserSource, Question, Check,
    Evidence, Status, Plan, DesignDecision, Hypothesis, cli, protect_recorded_intent)

ROOT=Path(__file__).resolve().parent
RECEIPT=ROOT/'notes/v3_human_interaction.json'
VARIANTS={'v3-60-nominal':1.,'v3-60-scale-0.9':.9,'v3-60-scale-1.1':1.1}
REQUIREMENTS=(UserRequirement('stand.adjustment',
    'Stand provides selectable angles through the selected press-and-tilt interaction',
    UserSource('README.md#agreement-and-architecture-decisions',
        'User authorized compact proposal A; angles are requested and press-and-tilt is the selected interaction')),)
QUESTIONS=(
    Question('endpoint','stand.adjustment','Finite declared human model finds rear-button contact satisfying target, joint and collision screens','kinematic'),
    Question('access','stand.adjustment','Finite model finds 40 mm approach, held 3 mm press and withdrawal with independently sampled transitions','kinematic'),
    Question('operation','stand.adjustment','Integrated stand adjusts satisfactorily with actual phone and supporting hand; effort, binding and return need a physical trial','physical'),)


def replay(run):
    """Revalidate stored configurations against current CAD; never rerun search.

    Stored optimizer flags/counts cannot promote a state or path to PASS. The
    current fixture and nonlinear FK own these judgments. Bad record structure
    is attempted evidence, not a physical failure.
    """
    import human_interaction as human
    setup=human.Setup(run['setup']['angle_deg'],run['setup']['scale'],tuple(run['setup']['shoulder_mm']))
    if setup != human.Setup(60.,scale=setup.scale):
        raise ValueError('Receipt setup differs from declared experiment')
    if len(run['candidates'])!=human.STARTS:
        raise ValueError('Incomplete finite search receipt')
    model=human.Interaction(setup)
    endpoints=complete=0
    for c in run['candidates']:
        q=np.asarray(c['q_rad'],dtype=float)
        if not model.diagnostics(q)['accepted']:
            continue
        endpoints+=1
        pre=np.asarray(c['approach_q_rad'],dtype=float)
        out=np.asarray(c['withdrawal_q_rad'],dtype=float)
        press=np.asarray(c['press']['q_rad'],dtype=float)
        if press.shape!=(7,len(model.free)) or not np.array_equal(press[0],q):
            raise ValueError('Incomplete/mismatched press configurations')
        approach=model.diagnostics(pre,offset_mm=40.)['accepted'] and model.segment(pre,q)['accepted']
        held=all(model.diagnostics(p,stroke_mm=float(t))['accepted'] for p,t in zip(press,np.linspace(0,human.cad.RELEASE,7)))
        strokes=np.linspace(0,human.cad.RELEASE,7)
        held &= all(model.segment(a,b,stroke_a=float(ta),stroke_b=float(tb),contact=True)['accepted']
                    for a,b,ta,tb in zip(press[:-1],press[1:],strokes[:-1],strokes[1:]))
        withdrawal=(model.diagnostics(out,offset_mm=40.,stroke_mm=human.cad.RELEASE)['accepted'] and
                    model.segment(press[-1],out,stroke_a=human.cad.RELEASE,stroke_b=human.cad.RELEASE)['accepted'])
        complete+=int(approach and held and withdrawal)
    return endpoints,complete


def read_receipt(scale,path=RECEIPT):
    import human_interaction as human
    if not path.is_file():
        return Status.UNKNOWN, 'No retained human-interaction receipt', None
    try:
        record=json.loads(path.read_text())
        if record['schema_version']!=1:
            raise ValueError('Unknown receipt version')
        if record['sources']!=human.sources():
            return Status.UNKNOWN,'Receipt inputs changed; run the explicit study again',None
        tools={'python':human.sys.version.split()[0],'mujoco':human.mujoco.__version__,'numpy':human.np.__version__,'scipy':human.scipy.__version__}
        if record['tools']!=tools:
            return Status.UNKNOWN,'Native tool identity differs from receipt',None
        runs=record['runs']
        if sorted(r['setup']['scale'] for r in runs)!=[.9,1.,1.1]:
            raise ValueError('Incomplete/malformed sensitivity cases')
        run=next(r for r in runs if r['setup']['scale']==scale)
        return Status.PASS,'Stored joint states independently replayed on current CAD envelopes',replay(run)
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        return Status.INCONCLUSIVE,f'Malformed/unreplayable attempted receipt: {exc}',None


def make_plan(variant):
    import human_interaction as human
    if variant not in VARIANTS:
        raise ValueError(variant)
    protect_recorded_intent(ROOT,REQUIREMENTS)
    scale=VARIANTS[variant]
    scope={'design':'v3','human_setup':variant,'geometry_source':human.sources()['model/analysis_phone_stand/v3_components.py']}
    def evidence():
        state,summary,counts=read_receipt(scale)
        records=[]
        for question,index in (('endpoint',0),('access',1)):
            status=state
            message=summary
            if counts is not None:
                status=Status.PASS if counts[index]>0 else Status.INCONCLUSIVE
                message=(f'{counts[index]}/{human.STARTS} candidates satisfy the declared {question} screen; '
                         'finite model/search only; no comfort/force/physical qualification')
            records.append(Evidence('human.'+question,(('stand.adjustment',question),),status,message,
                'notes/v3_human_interaction.json',scope))
        return tuple(records)
    return Plan(variant,REQUIREMENTS,scope,
        checks=(Check('human.release',(('stand.adjustment','endpoint'),('stand.adjustment','access')),evidence),),
        questions=QUESTIONS,
        decisions=(DesignDecision('stand.human-proxy','Conservative CAD boxes and assumed arm/palm/index screen access only; prior CAD/physical studies retain their own scope','README.md#articulated-release-access'),),
        hypotheses=(Hypothesis('stand.scale','Uniform scale and fixed shoulder are uncalibrated geometry/setup hypotheses, not user profiles','README.md#articulated-release-access'),))


if __name__=='__main__':
    raise SystemExit(cli(make_plan,tuple(VARIANTS)))
