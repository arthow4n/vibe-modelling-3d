"""C6 composition preserves earlier intent and explicit architecture supersession."""
import json
from product_verification import Plan,Question as Q,UserRequirement as U,UserSource as S,DesignDecision,assertion_check,protect_recorded_intent,protect_user_requirements
from m1_verification import requirements
from closure_research_verification import require_sources
from clamshell_study import ROOT,OUT
from clamshell_delivery import MODELS

RECORD='notes/clamshell_exploration.md'


def cad():
    d=json.loads((OUT/'cad.json').read_text());require_sources(d['source_sha256'])
    a=d['hypotheses']['screw_pin']
    assert a['closed_intersection_mm3']<1e-4 and a['storage_intrusion_mm3']<1e-4
    assert all(p['shell_intersection_mm3']<1e-4 for p in a['shell_sweep'])
    assert a['retaining_faces']['projected_contact_area_mm2']>10
    assert a['retaining_faces']['axial_gap_mm']==.35
    motion=json.loads((OUT/'rail_motion.json').read_text());require_sources(motion['source_sha256'])
    assert motion['selected_maximum_intersection_mm3']<1e-5
    return d


def sliced(name):
    if name not in MODELS:raise ValueError(name)
    p=json.loads((OUT/'publication.json').read_text());require_sources(p['inputs']);require_sources(p['artifacts'][name])
    r=json.loads((OUT/(name+'_slice.json')).read_text())
    assert r['slice']['ok'] and r['slice']['support_probe']['ok']
    if r['slice']['review_required']:
        review=json.loads((OUT/'manufacturing_review.json').read_text())
        require_sources(review['source_sha256'])
        row=review['layouts'][name]
        assert row['STL_sha256']==r['slice']['input_sha256']
        assert row['disposition']=='reviewed_experimental_print'


def sample_geometry():
    from c6_latch_test import sample
    from clamshell_design import build
    p=build('screw_pin');c=sample()
    assert p['loop'].cut(c['lid']).val().Volume()<1e-5
    assert c['body'].cut(p['body']).val().Volume()<1e-5
    assert len(c['body'].solids().vals())==len(c['lid'].solids().vals())==1


def make_clamshell_plan(variant,baseline):
    if variant!='clamshell-c6':raise ValueError(variant)
    old=requirements(baseline)
    src=S(RECORD,'2026-10-19: user rejects forceful/noisy short wall snaps, authorizes horizontal sunglasses-style dental case, minimal hinge alternatives and shorter front loop with matching tests; accepted slim interior remains basis')
    superseded={
        'closure.secure':U('closure.secure','Use a deliberate-release horizontal closure that resists accidental opening in backpack handling',src),
        'closure.end-retention':U('closure.end-retention','Use a practical minimal rear lid connection and secure front closure instead of the discontinued dual-end cap catches',src)}
    intent=tuple(superseded.get(r.id,r) for r in old)+(U('clamshell.operation','Open horizontally with an attached or otherwise practical minimal lid connection and deliberate secure closure',src),
        U('clamshell.short-loop','Explore shortening the front loop and provide its corresponding test pieces before relying on it',src))
    protect_recorded_intent(ROOT,intent,changes={id:src for id in superseded})
    protect_user_requirements(old,intent,changes={id:src for id in superseded})
    scope=dict(design=variant,phase='Unprinted computational prototype; trial short loop before committing to full-box print',material='PETG hypothesis, uncalibrated',process='0.4mm /0.2mm diagnostic PETG')
    questions=tuple(Q('use',r.id,'Intent retained; new complete case has no physical validation','physical') for r in old)+(
        Q('geometry','clamshell.operation','Closed fit, explicit-release path, sample hinge sweep and preserved nominal interior; no holding-force prediction','CAD'),
        Q('use','clamshell.operation','Integrated operation, quietness, force, hinge life, hardware retention and backpack protection tested in a print','physical'),
        Q('source','clamshell.short-loop','Matching crop and full lid share current authoritative short-loop builder and print orientation','CAD'),
        Q('trial','clamshell.short-loop','Printed shortened loop operates/repeats satisfactorily; analytical release screen is not physical approval','physical'))+tuple(
        Q(name,'clamshell.operation','Paired exports sliced; object-local warnings/bridge review retained; physical print remains unknown','slicer') for name in MODELS)
    checks=[assertion_check('c6.CAD',(('clamshell.operation','geometry'),),cad,RECORD,scope),
        assertion_check('c6.sample',(('clamshell.short-loop','source'),),sample_geometry,'c6_latch_test.py',scope)]
    checks.extend(assertion_check('c6.slice.'+name,(('clamshell.operation',name),),lambda name=name:sliced(name),
        'notes/clamshell/'+name+'_slice.json',scope) for name in MODELS)
    return Plan(variant,intent,scope,questions=questions,checks=tuple(checks),
        decisions=(DesignDecision('c6.prototype','Compact M3 hinge selected over unretained filament pins and uncaptured lift-off locators; loop shortened/thinned with matching trial',RECORD),))
