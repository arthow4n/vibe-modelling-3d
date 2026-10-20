"""Practical placement checks; earlier native grasp replay retained as history."""
import json
from dataclasses import asdict
import numpy as np
from product_verification import (UserRequirement as U,UserSource as S,Question as Q,
    Check,Evidence,Status,Plan,Directive,DesignDecision)

RECORD='notes/grip_human.md'


def read_record(path):
    import grip_human_record as study
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
    import grip_human_record as study
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
    from grip_placement import selected_layout
    scope=dict(design=variant,phase='selected concept layout; production printable files unchanged',
               method='nominal functional zones and prescribed opening motion; no grasp/force claim')
    target=('form.grip-placement','layout')
    def run():
        result=selected_layout()
        checks=result['checks']
        checks['opening_zones_separate']=all(p['axial_band_gap_mm']>=result['metrics']['axial_band_gap_mm'] for p in result['travel'])
        status=Status.PASS if all(checks.values()) else Status.FAIL
        m=result['metrics'];p=result['layout']
        summary=(f"Selected +{p['cap_center_mm']:g}/{p['body_center_mm']:g} mm layout: {m['cap_backing_gap_mm']:g} mm beyond backing, {m['cap_closed_end_gap_mm']:g} mm below cap end, {m['body_seam_gap_mm']:g} mm below body seam; band gap {m['axial_band_gap_mm']:g} mm, increasing with cap lift. Nominal layout only"
                 if status==Status.PASS else 'Nominal layout contradicts checks: '+str([k for k,v in checks.items() if not v]))
        return (Evidence('grip.layout',(target,),status,summary,'notes/grip_human/layout.json',scope),)
    return Plan(variant,(*parent.requirements,requirement),scope,
        questions=(*parent.questions,
            Q('layout',requirement.id,'Bands occupy separate exterior zones outside sleeve/backing and end rounds, and separate under prescribed cap lift','dimensional'),
            Q('use',requirement.id,'Printed bands provide useful traction and comfortable upright/diagonal opening with actual contents','physical')),
        checks=(Check('grip.layout',(target,),run),),
        directives=(*parent.directives,Directive('grip.upright','Support body below cap; preserve upright/diagonal use to help retain toothbrush',source)),
        decisions=(DesignDecision('grip.selected-position','Use +55/−30 mm centres with 20 mm bands and 0.7 mm depth; keep full wrap for freely chosen hand contacts. Detailed rigid-fingertip IK is retired as a placement criterion',RECORD),))
