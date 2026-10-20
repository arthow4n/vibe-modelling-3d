"""Selected printable three-line wrap-grip case: scoped CAD and slicer evidence."""
import json
from product_verification import (Plan,Question as Q,UserRequirement as U,UserSource as S,
    Directive,DesignDecision,assertion_check,protect_user_requirements)
from closure_research_verification import require_sources
from short_lap_grip_checks import OUT

RECORD='notes/grip_human.md#implemented-three-line-case'
SOURCE=S(RECORD,'User requests implementing the selected wrap-grip design only in the three-line version; old seam notches were previously directed to be removed')


def cad():
    r=json.loads((OUT/'finished_checks.json').read_text());require_sources(r['source_sha256'])
    assert r['old_notches_removed'] and all(abs(s['wall_mm']-1.2)<1e-5 for s in r['sections'])
    assert all(s['symmetric_difference_mm3']<1e-5 for s in r['joint'])
    assert all(p['guide_mm3']<1e-5 and (p['lift_mm']<6 or p['snap_mm3']<1e-5) for p in r['path'])
    assert all(min(p['body_gap_mm'],p['cap_band_gap_mm'])>=.8-1e-6 for p in r['passages'])


def publication():
    r=json.loads((OUT/'finished_publication.json').read_text())
    require_sources(r['source_sha256']);require_sources(r['artifacts'])
    assert len(r['sections'])==6 and all(len(s['strokes'])==3 for s in r['sections'])
    for s in r['sections']:
        assert s['coverage']['uncovered_width_mm']<.05 and s['coverage']['internal_gap_mm']<.01


def make_plan(variant,baseline):
    if variant!='slim-short-lap-three-line-grip':raise ValueError(variant)
    from grip_human_verification import make_plan as parent_plan
    parent=parent_plan('grip-band-placement',baseline)
    intent=tuple(U(r.id,'Use smooth cap grip surfaces and blended exterior joint backing; omit the old seam finger notches',SOURCE)
        if r.id=='form.cap-comfort' else r for r in parent.requirements)
    protect_user_requirements(parent.requirements,intent,changes={'form.cap-comfort':SOURCE})
    scope=dict(design=variant,material='intended PETG, uncalibrated strength',
        process='Q2C 0.4 mm nozzle / 0.2 mm layers / three walls',
        geometry='1.2 mm horizontal wall sections; 0.7 mm bands at +55/−30 mm; unchanged 30 mm joint')
    qs=[Q('physical',r.id,'Integrated printed pair meets this intent in actual use','physical') for r in intent]
    targets=tuple((rid,'finished-CAD') for rid in ('form.grip-placement','form.cap-comfort','closure.wall-comparison',
        'brush.fit','paste.fit','closure.secure','closure.end-retention','form.end-rounds'))
    qs.extend(Q(qid,rid,'Actual band sections, individual passage, unchanged joint region, snap obstruction and sampled guide path; no force rating','CAD') for rid,qid in targets)
    sliced=tuple((rid,'publication') for rid in ('print.material','print.supportfree','closure.wall-comparison','form.grip-placement'))
    qs.extend(Q(qid,rid,'Current paired exports and selected-profile smoke slice; three native toolpaths across band landings and ramps, no generated support','slicer') for rid,qid in sliced)
    return Plan(variant,intent,scope,questions=tuple(qs),
        checks=(assertion_check('grip-case.CAD',targets,cad,'notes/grip_human/finished_checks.json',scope),
                assertion_check('grip-case.publication',sliced,publication,'notes/grip_human/finished_publication.json',scope)),
        directives=(*parent.directives,Directive('grip.thin-only','Implement the selected grip only for the matching three-line pair; retain the old 2 mm case',SOURCE)),
        decisions=(DesignDecision('grip.wrap-shell','Move both skins inward using exact quintic profiles; preserve nominal horizontal wall thickness and original joint geometry',RECORD),))
