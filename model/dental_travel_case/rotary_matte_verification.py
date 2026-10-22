"""Minimal control repair, preserving the covered case's user intent."""
import json
from pathlib import Path
from product_verification import (Plan,Question as Q,Directive,UserSource as S,
    assertion_check,protect_user_requirements)
from closure_research_verification import require_sources

ROOT=Path(__file__).resolve().parent
VARIANT='rotary-matte-pla'
RECORD='notes/matte_rotary.md'


def cad():
    r=json.loads((ROOT/'notes/matte_rotary/cad.json').read_text())
    require_sources(r['source_sha256'])
    assert all(v<1e-5 for v in r['unchanged'].values())
    assert len(r['full']['locked_witnesses'])==21
    assert len(r['clearances'])==107 and len(r['spring'])==12
    assert len(r['key_obstructions'])==4 and min(r['key_obstructions'])>1e-5
    assert len(r['thread_motion'])==13 and max(r['thread_motion'])<1e-5
    assert r['solid_core']['missing_mm3']<1e-5


def publication():
    root=ROOT/'notes/matte_rotary'
    association=json.loads((root/'publication.json').read_text())
    require_sources(association['source_sha256']);require_sources(association['artifacts'])
    report=json.loads((root/'native.json').read_text())
    assert report['ok'] and report['geometry']['valid']
    assert all(x['ok'] for x in report['exports'])
    assert report['reuse']['identity']==association['native_input_identity']
    assert report['slice']['ok'] and report['slice']['input_sha256']==association['slice_input_sha256']
    r=json.loads((root/'step.json').read_text())
    require_sources(r['artifacts'])
    assert len(r['replacement'])==2
    assert all(x['solids']==1 and x['non_two_incident_edges']==0 for x in r['replacement'])
    assert r['exported_core_missing_mm3']<1e-5
    assert json.loads((root/'paths.json').read_text())['review_complete']


def make_plan(variant,baseline):
    if variant!=VARIANT:
        raise ValueError(variant)
    from rotary_covered_verification import make_plan as prior
    parent=prior('rotary-covered-pla',baseline)
    intent=parent.requirements
    protect_user_requirements(parent.requirements,intent)
    scope=dict(design=variant,material='PLA intended; matte PLA replacements untested',
        geometry='Printed body/lid and existing wheel/nut unchanged; 2mm face/rim, compatible solid screw',
        evidence='CAD and diagnostic PETG slicing; no actual matte-PLA thermal or force calibration')
    geometry=tuple((q.requirement_id,q.id) for q in parent.questions if q.mode=='CAD')
    manufacturing=tuple((q.requirement_id,q.id) for q in parent.questions if q.mode=='slicer')
    questions=tuple(Q(q.id,q.requirement_id,
        'Retained case checks and affected cover/thread paths, same printed shell interfaces' if q.mode=='CAD'
        else 'Actual repaired STEP solids, clean tessellation and diagnostic final slice' if q.mode=='slicer'
        else q.criterion,q.mode) for q in parent.questions)
    source=S(RECORD+'#user-feedback','User reports matte-PLA cap/screw print difficulty and STEP import warnings; requires minimal repair preserving already printed body/lid and roughly the same exterior')
    return Plan(variant,intent,scope,questions=questions,
        checks=(assertion_check('matte.CAD',geometry,cad,'notes/matte_rotary/cad.json',scope),
                assertion_check('matte.publication',manufacturing,publication,'notes/matte_rotary/publication.json',scope)),
        directives=(Directive('matte.repair','Improve cap/screw printability while retaining printed box',source),))
