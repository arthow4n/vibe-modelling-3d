"""Current experiment inherits intent, not physical approval of the old floor."""
from pathlib import Path
import hashlib,json
from product_verification import (Plan,Question as Q,UserRequirement as U,UserSource as S,
    assertion_check,protect_user_requirements)
ROOT=Path(__file__).resolve().parent
SOURCE=S('notes/l20_standard.md#user-direction',
    'User requires identical wall and bottom sandwich construction in both TPU experiment and dental liner, and an updated reusable standard')


def guarded(name):
    r=json.loads((ROOT/'notes/uniform_l20'/name).read_text())
    for rel,digest in r['source_sha256'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
    return r


def cad():
    r=guarded('cad.json')
    assert r['profile_mm']==[.8,.4,.8] and r['total_mm']==2.
    assert len(r['probes'])==32 and r['old_floor_negative_control']


def publication():
    r=guarded('publication.json')
    for rel,digest in r['artifacts'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
    e=json.loads((ROOT/'notes/uniform_l20/native.json').read_text())
    assert e['ok'] and e['geometry']['valid'] and all(x['ok'] for x in e['exports'])
    assert e['slice']['ok'] and e['reuse']['identity']==r['native_input_identity']
    assert e['slice']['input_sha256']==r['slice_input_sha256']
    assert guarded('paths.json')['review_complete']


def make_plan(variant,baseline):
    if variant!='uniform-l20':raise ValueError(variant)
    from thin_gap_verification import make_thin_gap_plan
    parent=make_thin_gap_plan('L20',baseline,ROOT)
    intent=parent.requirements+(U('liner.uniform','Use identical 0.8/0.4/0.8 sandwich on walls, floor and lid panel',SOURCE),)
    protect_user_requirements(parent.requirements,intent)
    scope=dict(design=variant,profile='0.8/0.4/0.8 all active flat panels',material='TPU95A; new floor unprinted')
    qs=tuple(Q(q.id,q.requirement_id,
        'Existing fixture clearance, actual uniform panel material/air and flat coverage' if q.mode=='CAD' else q.criterion,q.mode)
        for q in parent.questions)+(Q('section','liner.uniform','Actual walls/floor/pad share the normal section; old floor fails the thicker-backing witness','CAD'),)
    geometry=tuple((q.requirement_id,q.id) for q in qs if q.mode=='CAD')
    printed=tuple((q.requirement_id,q.id) for q in qs if q.mode=='slicer')
    return Plan(variant,intent,scope,questions=qs,
        checks=(assertion_check('uniform.CAD',geometry,cad,'notes/uniform_l20/cad.json',scope),
                assertion_check('uniform.publication',printed,publication,'notes/uniform_l20/publication.json',scope)))
