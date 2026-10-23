"""Uniform L20 application; the old failed M1/S16 variant stays historical."""
from pathlib import Path
import hashlib,json
from product_verification import Plan,UserRequirement as U,UserSource as S,Question as Q,DesignDecision,assertion_check

ROOT=Path(__file__).resolve().parent
SOURCE=S('notes/rotary_l20.md#user-direction',
    'User confirms L20 recap and explicitly requests a new liner for the latest rotary dental box')
REQUIREMENTS=(U('rotary-liner.fit','Fit the latest rotary box while preserving closure and usable storage',SOURCE),
    U('liner.l20','Use accepted L20 skins, separated ties and post-supported end panels',SOURCE),
    U('liner.coverage','Line both body and lid with preformed cups',SOURCE),
    U('liner.quiet','Reduce contents impact noise',SOURCE))


def read(name):
    r=json.loads((ROOT/'notes/uniform_l20'/name).read_text())
    for rel,digest in r['source_sha256'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
    return r


def cad():
    r=read('cad.json')
    assert len(r['fit'])==19 and len(r['profile_probes'])==72
    assert r['floor_mouth_missing_mm3']<1e-5
    assert r['dimensions']['clear_length_mm']>=255.
    assert len(r['individual_storage_gauges'])==4
    assert r['cap_retention']['contact_mm3']>.01 and len(r['cap_retention']['pads'])==4
    assert r['cap_retention']['overlap_beyond_0p101_mm_mm3']<1e-5


def publication():
    r=read('publication.json')
    for name,digest in r['artifacts'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    e=json.loads((ROOT/'notes/uniform_l20/print_review.json').read_text())
    assert e['ok'] and e['geometry']['valid'] and all(x['ok'] for x in e['exports'])
    assert e['slice']['ok'] and e['reuse']['identity']==r['native_input_identity']
    assert e['slice']['input_sha256']==r['slice_input_sha256']
    paths=read('paths.json')
    assert paths['review_complete'] and paths['wall_skin_sections']>4000
    assert paths['minimum_core_clear_width_mm']>=.35


def make_plan(variant):
    if variant!='rotary-l20-uniform':raise ValueError(variant)
    scope=dict(design=variant,rigid_case='latest wraparound-wheel rotary box',material='TPU95A',
               setup='0.4mm/0.2mm; Classic; two walls; 100% CAD material fill; supports off; 9mm3/s')
    targets=(('liner.uniform','section'),('rotary-liner.fit','envelope'),('liner.l20','geometry'),('liner.coverage','geometry'))
    printed=(('liner.l20','paths'),('liner.coverage','publication'))
    qs=tuple(Q(q,r,'Current box clearance, free cap withdrawal and actual L20 skin/void/tie material witnesses','CAD') for r,q in targets)
    qs+=tuple(Q(q,r,'Matched raw exports, selected TPU slice, upright skin continuity and open core sections','slicer') for r,q in printed)
    qs+=(Q('installation','rotary-liner.fit','Wider walls compress gently through sleeve and both cups remain seated','physical'),
         Q('packing','rotary-liner.fit','Actual brush and toothpaste fit together and pass the lined mouth','physical'),
         Q('integrity','liner.l20','Tall printed skins and ties stay intact during printing and installation','physical'),
         Q('noise','liner.quiet','User accepts contents damping in the full box','subjective'))
    from product_verification import protect_user_requirements
    intent=REQUIREMENTS+(U('liner.uniform','Use the identical sandwich in floors and walls',
        S('notes/uniform_l20.md#user-direction','User requires identical 0.8/0.4/0.8 wall and bottom construction in both standard and dental liner')), )
    protect_user_requirements(REQUIREMENTS,intent)
    return Plan(variant,intent,scope,questions=qs,
        checks=(assertion_check('rotary.CAD',targets,cad,'notes/uniform_l20/cad.json',scope),
                assertion_check('rotary.publication',printed,publication,'notes/uniform_l20/publication.json',scope)),
        decisions=(DesignDecision('preformed','Two conformal cups; narrow leading floor and 0.3mm installation allowance; wider body walls require elastic compression. Four small ramped TPU pads give the lid cup local 0.1mm intended interference. Short shoulder transitions and corners stay solid.',
                                  'notes/rotary_l20.md'),))
