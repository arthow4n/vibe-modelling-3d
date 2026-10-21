"""Smooth C case: retained intent, revised wall allowance and scoped evidence."""
import json
from product_verification import (Plan, Question as Q, UserRequirement as U,
    UserSource as S, Directive, DesignDecision, assertion_check, protect_user_requirements)
from closure_research_verification import require_sources
from smooth_case_checks import OUT

VARIANT = 'slim-short-lap-smooth-c'
RECORD = 'notes/smooth_exterior.md#authorized-c-implementation'
SOURCE = S(RECORD, 'User selects C and authorizes remodelling using engineering judgment; '
           'small size increases and more than three extrusion lines are acceptable')


def cad():
    r=json.loads((OUT/'cad.json').read_text());require_sources(r['source_sha256'])
    assert len(r['sleeve_sections'])==6 and all(abs(s['wall_mm']-2.0)<1e-5 for s in r['sleeve_sections'])
    assert r['seat_gap_mm']<1e-6
    assert r['overclose_obstruction_mm3']>.05 and r['collar_height_mm']==3
    assert len(r['sections'])==20 and r['large_end_rounds']
    assert all(p['guide_mm3']<1e-5 and (p['lift_mm']<6 or p['snap_mm3']<1e-5) for p in r['path'])
    assert len(r['catches'])==6 and min(c['obstruction_mm3'] for c in r['catches'])>.05
    assert all(min(p['body_gap_mm'],p['cap_gap_mm'])>=.8-1e-6 for p in r['passages'])


def publication():
    r=json.loads((OUT/'publication.json').read_text())
    require_sources(r['source_sha256']);require_sources(r['artifacts'])
    ev=json.loads((OUT/'print_review.json').read_text())
    assert ev['ok'] and ev['geometry']['valid']
    assert len(ev['exports'])==2 and all(e['ok'] for e in ev['exports'])
    assert ev['reuse']['identity']==r['native_input_identity']
    sl=ev['slice'];assert sl['ok'] and sl['input_sha256']==r['slice_input_sha256']
    assert sl['support_probe']['ok'] and not sl['support_probe']['generated']
    assert not sl['log_notices'] and sl['placement']=='center'
    assert sl['effective_settings']['wall_loops']=='3' and sl['effective_settings']['layer_height']=='0.2'


def retention():
    from smooth_retention_study import study_output
    RETENTION=study_output('retention-c2')
    r=json.loads((RETENTION/'pull.json').read_text());require_sources(r['source_sha256'])
    assert r['missing_bite_zero_barrier']
    assert all(m['mesh_relative_change']<.10 for m in r['members'].values())
    nominal=r['paths']['pair_0.0']
    assert nominal['peak_force_N']>0 and nominal['barrier_Nmm']>0
    assert 'nominal_ideal_threshold_at_least_3_5N' in r['provisional_comparison']
    assert all(p['peak_step_change']<.10 for p in r['paths'].values())


def side_screen():
    from smooth_retention_study import study_output
    RETENTION=study_output('retention-c2')
    r=json.loads((RETENTION/'side.json').read_text());require_sources(r['source_sha256'])
    assert set(r['comparison_to_c1'])=={'x','y'}
    assert all(v['improved_across_checked_meshes'] for v in r['comparison_to_c1'].values())


def make_plan(variant,baseline):
    if variant!=VARIANT:raise ValueError(variant)
    from short_lap_grip_verification import make_plan as prior_plan
    parent=prior_plan('slim-short-lap-three-line-grip',baseline)
    changes={rid:SOURCE for rid in ('closure.wall-comparison','form.cap-comfort')}
    intent=tuple(
        U(r.id,'Preserve previous comparison files and provide a complete matching smooth C pair; allow modest size and wall increases',
          SOURCE,acceptance_criteria=('More than three extrusion lines allowed where useful',))
        if r.id=='closure.wall-comparison' else
        U(r.id,'Provide smooth cap sides and comfortable rounded contact edges without local exterior backing bumps',SOURCE)
        if r.id=='form.cap-comfort' else r for r in parent.requirements)
    protect_user_requirements(parent.requirements,intent,changes=changes)
    intent += (U('form.smooth-exterior','Implement C: smooth aligned exterior, no separate wrap grip bands, and exposed overlap at the seam for grip',SOURCE),)
    scope=dict(design=variant,material='intended PETG; printed behavior uncalibrated',
               process='Q2C 0.4 mm nozzle / 0.2 mm layers / 3 configured wall loops; thicker end walls allowed',
               geometry='75.8 x 52.8 x 264 mm; 3 mm collar; 27 mm cap coverage; sleeve-tip stop; 2 mm main walls and sleeve / 0.75 mm bite')
    qs=[Q('physical',r.id,'Integrated printed C pair satisfies this intent in actual use','physical') for r in intent]
    geometry_targets=tuple((rid,'finished-CAD') for rid in ('form.smooth-exterior','form.grip-placement','form.cap-comfort',
        'closure.wall-comparison','brush.fit','paste.fit','closure.secure','closure.end-retention','form.end-rounds','closure.short-overlap'))
    qs.extend(Q(qid,rid,'Actual smooth wall sections, retained guide envelope / strengthened sleeve and bite, sleeve-tip seat, independent capture, sampled opening clearance and individual passage; no grip or force rating','CAD') for rid,qid in geometry_targets)
    sliced=tuple((rid,'publication') for rid in ('print.material','print.supportfree','closure.wall-comparison'))
    qs.extend(Q(qid,rid,'Current native guarded paired exports and selected-profile smoke slice, no generated support','slicer') for rid,qid in sliced)
    force_targets=(('research.force','conditional-pull'),)
    qs.append(Q('conditional-pull','research.force','Quantify actual-CAD paired/single force and energy scenarios with checked load coverage and mesh/travel precision; report the historical design-target comparisons separately, not as bag-retention acceptance','numerical'))
    side_targets=(('closure.short-overlap','side-bearing-screen'),)
    qs.append(Q('side-bearing-screen','closure.short-overlap','Both principal 2 N side-bearing responses are lower than C1 across the checked coarse/fine ranges; retain individual precision flags, with no sideways-release or impact claim','numerical'))
    # Parent directives remain historical; the latest instruction explicitly supersedes thin-only/form choices.
    directives=tuple(d for d in parent.directives if d.id not in ('grip.thin-only','thin.matching-pair'))
    return Plan(variant,intent,scope,questions=tuple(qs),
        checks=(assertion_check('smooth.CAD',geometry_targets,cad,'notes/smooth_case/cad.json',scope),
                assertion_check('smooth.publication',sliced,publication,'notes/smooth_case/publication.json',scope),
                assertion_check('smooth.retention',force_targets,retention,'notes/smooth_case/retention/final/pull.json',scope),
                assertion_check('smooth.side-screen',side_targets,side_screen,'notes/smooth_case/retention/final/side.json',scope)),
        directives=(*directives,Directive('smooth.selected','Implement C autonomously; modest dimension and wall increases are authorized',SOURCE)),
        decisions=(DesignDecision('smooth.envelope','Grow width and depth by 1.6 mm; preserve main cavity and guide envelope; 2 mm main walls and sleeve address weak pull and side-bearing routes',RECORD),
                   DesignDecision('smooth.seat','Expose 3 mm overlap and add a tapered internal sleeve-tip stop; physical grip and snap effort remain unqualified',RECORD)))
