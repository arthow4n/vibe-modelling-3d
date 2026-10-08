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
RECEIPT=ROOT/'notes/v3_myoarm_interaction.json'
VARIANTS={'v3-60-nominal':'nominal','v3-60-shoulder-near':'near','v3-60-shoulder-far':'far'}
REQUIREMENTS=(UserRequirement('stand.adjustment',
    'Stand provides selectable angles through the selected press-and-tilt interaction',
    UserSource('README.md#agreement-and-architecture-decisions',
        'User authorized compact proposal A; angles are requested and press-and-tilt is the selected interaction')),)
QUESTIONS=(
    Question('endpoint','stand.adjustment','Finite declared human model finds rear-button contact satisfying target, joint and collision screens','kinematic'),
    Question('access','stand.adjustment','Finite model finds 40 mm approach, held 3 mm press and withdrawal with independently sampled transitions','kinematic'),
    Question('operation','stand.adjustment','Integrated stand adjusts satisfactorily with actual phone and supporting hand; effort, binding and return need a physical trial','physical'),)


class ReceiptError(ValueError):
    """Malformed retained data; never a native/checker programming exception."""


def coordinates(candidate,key,shape):
    try:
        values=np.asarray(candidate[key],dtype=float)
    except (KeyError,TypeError,ValueError) as exc:
        raise ReceiptError(f'Invalid {key}: {exc}') from exc
    if values.shape!=shape or not np.isfinite(values).all():
        raise ReceiptError(f'Wrong/nonfinite {key} coordinates')
    return values


def replay(run,model):
    """Replay current FK/screens; stored optimizer flags cannot supply PASS."""
    import human_interaction as human
    try:
        setup=human.Setup(run['setup']['angle_deg'],tuple(run['setup']['shoulder_mm']))
        candidates=run['candidates']
        starts=sorted(c['start'] for c in candidates)
    except (KeyError,TypeError,ValueError) as exc:
        raise ReceiptError(f'Invalid retained setup/starts: {exc}') from exc
    if setup!=model.setup or setup.angle_deg!=60. or setup.shoulder_mm not in human.SETUPS.values():
        raise ReceiptError('Receipt setup differs from declared replay experiment')
    if len(candidates)!=human.STARTS or starts!=list(range(human.STARTS)):
        raise ReceiptError('Incomplete finite search receipt')
    endpoints=complete=0
    shape=(len(model.free),)
    for c in candidates:
        q=coordinates(c,'q_rad',shape)
        if not model.diagnostics(q)['accepted']:
            continue
        endpoints+=1
        pre=coordinates(c,'approach_q_rad',shape)
        out=coordinates(c,'withdrawal_q_rad',shape)
        try:
            press_record=c['press']
        except (KeyError,TypeError) as exc:
            raise ReceiptError(f'Invalid press record: {exc}') from exc
        press=coordinates(press_record,'q_rad',(7,len(model.free)))
        if not np.array_equal(press[0],q):
            raise ReceiptError('Mismatched press configurations')
        approach=model.diagnostics(pre,offset_mm=40.)['accepted'] and model.segment(pre,q)['accepted']
        strokes=np.linspace(0,human.cad.RELEASE,7)
        held=all(model.diagnostics(p,stroke_mm=float(t))['accepted'] for p,t in zip(press,strokes))
        held &= all(model.segment(a,b,stroke_a=float(ta),stroke_b=float(tb),contact=True)['accepted']
                    for a,b,ta,tb in zip(press[:-1],press[1:],strokes[:-1],strokes[1:]))
        withdrawal=(model.diagnostics(out,offset_mm=40.,stroke_mm=human.cad.RELEASE)['accepted'] and
                    model.segment(press[-1],out,stroke_a=human.cad.RELEASE,stroke_b=human.cad.RELEASE)['accepted'])
        complete+=int(approach and held and withdrawal)
    return endpoints,complete


def read_receipt(setup_name,path=RECEIPT):
    import human_interaction as human
    if not path.is_file():
        return Status.UNKNOWN, 'No retained human-interaction receipt', None
    try:
        record=json.loads(path.read_text())
        if record['schema_version']!=2:
            return Status.UNKNOWN,'Receipt uses another anatomical foundation/version; historical evidence is not transferable',None
        if record['anatomy']!=human.anatomy_identity():
            return Status.UNKNOWN,'Imported anatomy/assets differ from receipt',None
        if record['sources']!=human.sources():
            return Status.UNKNOWN,'Receipt inputs changed; run the explicit study again',None
        tools=human.tools()
        if record['tools']!=tools:
            return Status.UNKNOWN,'Native tool identity differs from receipt',None
        if record['search']!=dict(starts=human.STARTS,seed=human.SEED,max_nfev=human.MAX_NFEV):
            raise ValueError('Numerical search settings differ from declared study')
        if record['screens']!=human.screen_settings():
            raise ValueError('Declared screen metadata differs from replay criteria')
        runs=record['runs']
        if sorted(tuple(r['setup']['shoulder_mm']) for r in runs)!=sorted(human.SETUPS.values()):
            raise ValueError('Incomplete/malformed sensitivity cases')
        run=next(r for r in runs if tuple(r['setup']['shoulder_mm'])==human.SETUPS[setup_name])
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        return Status.INCONCLUSIVE,f'Malformed/unreplayable attempted receipt: {exc}',None
    # Scene/model construction is command work, not malformed stored evidence.
    # Native import/compile/configuration failures must reach the shared CLI.
    model=human.Interaction(human.Setup(60.,human.SETUPS[setup_name]))
    try:
        return Status.PASS,'Stored joint states independently replayed on current CAD envelopes',replay(run,model)
    except ReceiptError as exc:
        return Status.INCONCLUSIVE,f'Malformed/unreplayable attempted receipt: {exc}',None


def make_plan(variant):
    import human_interaction as human
    if variant not in VARIANTS:
        raise ValueError(variant)
    protect_recorded_intent(ROOT,REQUIREMENTS)
    setup_name=VARIANTS[variant]
    scope={'design':'v3','human_setup':variant,'anatomy':human.anatomy_identity(),
           'geometry_source':human.sources()['model/analysis_phone_stand/v3_components.py']}
    def evidence():
        state,summary,counts=read_receipt(setup_name)
        records=[]
        for question,index in (('endpoint',0),('access',1)):
            status=state
            message=summary
            if counts is not None:
                status=Status.PASS if counts[index]>0 else Status.INCONCLUSIVE
                message=(f'{counts[index]}/{human.STARTS} candidates satisfy the declared {question} screen; '
                         'finite model/search only; no comfort/force/physical qualification')
            records.append(Evidence('human.'+question,(('stand.adjustment',question),),status,message,
                'notes/v3_myoarm_interaction.json',scope))
        return tuple(records)
    return Plan(variant,REQUIREMENTS,scope,
        checks=(Check('human.release',(('stand.adjustment','endpoint'),('stand.adjustment','access')),evidence),),
        questions=QUESTIONS,
        decisions=(DesignDecision('stand.human-proxy','Conservative CAD boxes and unchanged MyoSim MyoArm collision anatomy screen kinematic access only; prior studies retain their own scope','README.md#articulated-release-access'),),
        hypotheses=(Hypothesis('stand.setup','Imported anatomy is not a user profile; fixed torso and shoulder placement are unmeasured setup hypotheses','README.md#articulated-release-access'),))


if __name__=='__main__':
    raise SystemExit(cli(make_plan,tuple(VARIANTS)))
