"""Current native replay for the grip-placement concept, through the shared CLI."""
import json
from dataclasses import asdict
import numpy as np
from product_verification import (UserRequirement as U,UserSource as S,Question as Q,
    Check,Evidence,Status,Plan,Directive,DesignDecision)
import grip_human_record as study

RECORD='notes/grip_human.md'
TARGET=('form.grip-placement','endpoint')


def read_record(path):
    if not path.is_file():return Status.UNKNOWN,'No retained study',None
    try:
        r=json.loads(path.read_text())
        if r['schema_version']!=1:return Status.UNKNOWN,'Different study schema',None
        if r['sources']!=study.record_sources() or r['anatomy']!=study.anatomy_identity() or r['tools']!=study.tools():
            return Status.UNKNOWN,'Source, anatomy or native tools changed',None
        if r['screens']!=study.screens():raise ValueError('Screen metadata changed')
        if r['search']!=dict(starts=study.STARTS,seed=study.SEED,max_nfev=study.MAX_NFEV):raise ValueError('Search metadata changed')
        if r['setup']!=asdict(study.Setup('balanced',-25.,350.,1150.)):raise ValueError('Different discovery setup')
        attempts=r['attempts']
        if not attempts or len(attempts)>study.STARTS or [a['start'] for a in attempts]!=list(range(len(attempts))):
            raise ValueError('Incomplete starts')
        for a in attempts:
            q=np.asarray(a['result']['diagnostics']['q_rad'],dtype=float)
            if q.shape!=(52,) or not np.isfinite(q).all():raise ValueError('Invalid saved coordinates')
            cost=a['result']['cost']
            if not isinstance(cost,(int,float)) or not np.isfinite(cost):raise ValueError('Invalid optimizer cost')
    except (KeyError,TypeError,ValueError) as exc:
        return Status.INCONCLUSIVE,f'Malformed attempted receipt: {exc}',None
    return None,None,r


def evaluate(path):
    status,summary,record=read_record(path)
    if record is None:return status,summary
    # Construction/program errors remain errors. Only validated saved states are
    # passed to the native scene, and its current criteria determine acceptance.
    try:
        base,best,replayed,runs=study.replay_candidates(record)
    except study.ReceiptError as exc:
        return Status.INCONCLUSIVE,f'Incomplete attempted receipt: {exc}'
    passed=sum(r['diagnostics']['accepted'] for r in runs)
    if not passed:return Status.INCONCLUSIVE,'No accepted grasp in finite baseline search or translated placement replays; no physical impossibility established'
    return Status.PASS,f'{passed}/6 finite placement/orientation endpoint replays accepted; no comfort/force qualification'


def make_plan(variant,baseline):
    if variant!='grip-band-placement':raise ValueError(variant)
    from wall_comparison_verification import make_plan as parent_plan
    parent=parent_plan('slim-short-lap-three-line',baseline)
    source=S(RECORD+'#user-direction','User selected shallow smooth full-wrap exploration, requested anatomical placement and recorded visualizations; opening upright/diagonal to keep toothbrush from falling')
    requirement=U('form.grip-placement','Provide useful exterior grips for separating cap/body while holding the case upright or diagonal',source)
    scope=dict(design=variant,phase='concept investigation; production printable files unchanged',
               anatomy='MyoSim myohands; rigid hand placement, no arm reach or dynamics')
    def run():
        status,summary=evaluate(study.OUT/'study.json')
        return (Evidence('grip.native-replay',(TARGET,),status,summary,'notes/grip_human/study.json',scope),)
    return Plan(variant,(*parent.requirements,requirement),scope,
        questions=(*parent.questions,
            Q('endpoint',requirement.id,'Find at least one declared finite placement/orientation with native skin contacts and selected collision/joint screens','kinematic'),
            Q('opening',requirement.id,'Held grasp clears the first 6 mm lift; requires an accepted endpoint','kinematic'),
            Q('use',requirement.id,'Printed bands provide useful traction and comfortable upright/diagonal opening with actual contents','physical')),
        checks=(Check('grip.native-replay',(TARGET,),run),),
        directives=(*parent.directives,Directive('grip.upright','Support body below cap; preserve upright/diagonal use to help retain toothbrush',source)),
        decisions=(DesignDecision('grip.provisional-position','Compare +40/−15, +50/−30 and +65/−50 mm centres; balanced is a dimensional starting proposal, not a validated grasp',RECORD),))
