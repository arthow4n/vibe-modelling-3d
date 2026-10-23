"""Exploratory gap variants, with the dental and selected L20 recipe unchanged."""
from pathlib import Path
import json,hashlib
from product_verification import Plan,Question as Q,UserRequirement as U,UserSource as S,assertion_check
from gap_comparison_design import variant_named
ROOT=Path(__file__).resolve().parent
SOURCE=S('notes/gap_comparison.md#user-direction',
    'User requests only experiment cups with 0.8 and 1.6mm air gaps, skips 1.2, and explicitly keeps the dental liner as is')


def read(name,file):
    r=json.loads((ROOT/'notes/gap_comparison'/name/file).read_text())
    for p,h in r['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    return r


def cad(name):
    v=variant_named(name);r=read(name,'cad.json')
    assert r['skin_mm']==.8 and r['gap_mm']==v.gap and r['total_mm']==v.total
    assert len(r['probes'])==34 and r['pad_seat_gap_mm']<1e-6 and r['pad_lid_gap_mm']<1e-6
    assert r['pad_stop_obstruction_mm3']>.01


def publication(name):
    r=read(name,'publication.json')
    for p,h in r['artifacts'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    e=json.loads((ROOT/'notes/gap_comparison'/name/'native.json').read_text())
    assert e['ok'] and e['geometry']['valid'] and all(x['ok'] for x in e['exports']) and e['slice']['ok']
    assert e['reuse']['identity']==r['native_input_identity']
    assert e['slice']['input_sha256']==r['slice_input_sha256']
    assert read(name,'paths.json')['review_complete']


def make_plan(variant,baseline):
    v=variant_named(variant)
    intent=baseline+(U('comparison.gap','Print 0.8 and 1.6mm gap experiment cups with unchanged dental liner',SOURCE),
                     U('comparison.uniform','Use the chosen gap consistently in cup walls, floor and matching lid panel, keeping 0.8mm skins',SOURCE))
    scope=dict(design=variant,skin_mm=str(.8),gap_mm=str(v.gap),material='TPU95A; physical trial pending')
    targets=(('study.enclosure','fit'),('study.coverage','panels'),('study.flat','flat'),
             ('comparison.gap','geometry'),('comparison.uniform','section'))
    pub=(('comparison.gap','publication'),)
    qs=tuple(Q(q,r,'Existing fixture/seat path and actual fixed-skin/selected-gap material witnesses','CAD') for r,q in targets)
    qs+=tuple(Q(q,r,'Guarded native exports, same supplied TPU setup and reviewed skin/core paths','slicer') for r,q in pub)
    qs+=(Q('feel','comparison.gap','User compares damping, squeeze feel and finish under the same printing/use setup','physical'),)
    return Plan(variant,intent,scope,questions=qs,
        checks=(assertion_check('gap.CAD',targets,lambda:cad(variant),'notes/gap_comparison/'+variant+'/cad.json',scope),
                assertion_check('gap.publication',pub,lambda:publication(variant),'notes/gap_comparison/'+variant+'/publication.json',scope)))
