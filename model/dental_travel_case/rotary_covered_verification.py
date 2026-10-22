"""Matching keyed facecap adoption with retained user intent and physical limits."""
import json
from pathlib import Path
from product_verification import (Plan,Question as Q,UserRequirement as U,UserSource as S,
    Directive,DesignDecision,assertion_check,protect_user_requirements)
from closure_research_verification import require_sources

ROOT=Path(__file__).resolve().parent
VARIANT='rotary-covered-pla'
RECORD='notes/covered_rotary.md'
SOURCE=S(RECORD+'#authorized-matching-facecap',
    'User requires facecap to match underlying spinning piece for grip, positive joining so both spin together, and explicitly authorizes direct modelling')
WRAP_SOURCE=S(RECORD+'#wraparound-cover-request',
    'User requires full side coverage to hide the gap between facecap and wheel, with internal spring clearance preserved')


def cad():
    r=json.loads((ROOT/'notes/covered_rotary/cad.json').read_text())
    require_sources(r['source_sha256'])
    assert r['outline_difference_mm3']<1e-5 and len(r['positive_key_witnesses'])==40
    assert min(x['obstruction_mm3'] for x in r['positive_key_witnesses'])>1e-5
    assert all(x['overlap_mm3']<1e-5 for x in r['key_removed_controls'])
    assert r['solid_thread_core']['missing_mm3']<1e-5 and r['thread_difference_mm3']<1e-5
    assert len(r['turn_angles'])==19 and len(r['full']['locked_witnesses'])==21
    assert len(r['wraparound']['spring_envelope_checks'])==12
    assert r['wraparound']['axial_overlap_mm']>=4.2-1e-6


def publication():
    r=json.loads((ROOT/'notes/covered_rotary/publication.json').read_text())
    require_sources(r['source_sha256']);require_sources(r['artifacts'])
    for stem,receipt in r['publications'].items():
        e=json.loads((ROOT/receipt['report']).read_text())
        assert e['ok'] and e['geometry']['valid'] and all(x['ok'] for x in e['exports'])
        assert e['reuse']['identity']==receipt['native_input_identity']
        assert e['slice']['ok'] and e['slice']['input_sha256']==receipt['slice_input_sha256']
    paths=json.loads((ROOT/'notes/covered_rotary/print_paths.json').read_text())
    assert paths['support_review_complete'] and paths['exported_thread_missing_mm3']<1e-5


def make_plan(variant,baseline):
    if variant!=VARIANT:raise ValueError(variant)
    from rotary_case_verification import make_plan as prior
    parent=prior('rotary-full-pla',baseline)
    intent=parent.requirements+(U('rotary.cover','Conceal the wheel mechanism with a facecap matching its scalloped grip shape',SOURCE),
        U('rotary.keyed','Positively join facecap and wheel so they turn together',SOURCE),
        U('rotary.wrap','Cover the wheel edge and hide the facecap/wheel side gap while leaving the spring free',WRAP_SOURCE))
    protect_user_requirements(parent.requirements,intent)
    scope=dict(design=variant,material='PLA intended; covered assembly unprinted',
               geometry='75.8x52.8x264; wraparound scalloped facecap with 1.8mm parallel outline offset; two hub keys; 1.6mm extra projection',
               thread='Existing coarse printed thread and nut; longer shoulder/head position')
    qs=[Q('physical',r.id,'Covered printed case satisfies this intent in actual use','physical') for r in intent]
    targets=tuple((rid,'geometry') for rid in ('rotary.cover','rotary.keyed','rotary.wrap','rotary.index',
         'rotary.storage','rotary.fit','closure.secure','closure.end-retention','closure.short-overlap',
         'form.cap-comfort','form.smooth-exterior','rotary.printed','brush.fit','paste.fit'))
    qs.extend(Q(q,r,'Parallel scalloped outline, continuous wraparound wall, translated spring clearance screens, positive key obstruction with play and key-removed negative control, free common rotation and retained lock/withdrawal paths','CAD') for r,q in targets)
    pub=(('rotary.printability','publication'),('rotary.printed','publication'),('print.material','publication'))
    qs.extend(Q(q,r,'Matching native guarded exports and reviewed diagnostic slices; solid exported thread core and sampled fill','slicer') for r,q in pub)
    return Plan(variant,intent,scope,questions=tuple(qs),
        checks=(assertion_check('covered.CAD',targets,cad,'notes/covered_rotary/cad.json',scope),
                assertion_check('covered.publication',pub,publication,'notes/covered_rotary/publication.json',scope)),
        directives=(Directive('covered.model','Model the matching keyed facecap directly',SOURCE),),
        decisions=(DesignDecision('covered.keys','Two rectangular hub keys carry torque; annular spacer and rearward wraparound rim leave internal spring clearance; longer fixed shoulder screw retains both moving parts',RECORD),))
