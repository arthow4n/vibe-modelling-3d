"""Full rotary adoption: preserved user intent and explicit physical unknowns."""
import json
from pathlib import Path
from product_verification import (Plan,Question as Q,UserRequirement as U,UserSource as S,
    Directive,DesignDecision,Evidence,Status,assertion_check,protect_user_requirements)
from closure_research_verification import require_sources

ROOT=Path(__file__).resolve().parent
VARIANT='rotary-full-pla'
RECORD='notes/rotary_case.md'
SOURCE=S(RECORD+'#user-feedback-and-authorized-adoption',
    'User reports complete PLA trial works and stays together; requests slightly tighter tolerance, '
    'full wheel-width cap holding ledge and adaptation to the full box; earlier authorizes '
    'one-sided rotary closure, printed custom fasteners, concealed hardware and release resistance')


def cad():
    r=json.loads((ROOT/'notes/rotary_case/cad.json').read_text())
    require_sources(r['source_sha256']);f=r['full']
    assert len(f['corner_seats'])==4 and len(f['turn_with_play'])==80
    assert f['guide_clearance_per_side_mm']==.2 and f['keeper_span_mm']==34.
    assert abs(f['keeper_radial_gap_mm']-.5)<1e-6
    assert len(f['locked_witnesses'])==21 and len(f['turn'])==19


def publication():
    r=json.loads((ROOT/'notes/rotary_case/publication.json').read_text())
    require_sources(r['source_sha256']);require_sources(r['artifacts'])
    e=json.loads((ROOT/'notes/rotary_case/print_review.json').read_text())
    assert e['ok'] and e['geometry']['valid'] and all(x['ok'] for x in e['exports'])
    assert e['reuse']['identity']==r['native_input_identity']
    assert e['slice']['ok'] and e['slice']['input_sha256']==r['slice_input_sha256']
    s=json.loads((ROOT/'notes/rotary_case/support_review.json').read_text())
    assert s['all_support_outside_storage'] and s['reviewed_roles']==['Support','Support interface']


def make_plan(variant,baseline):
    if variant!=VARIANT:raise ValueError(variant)
    from smooth_case_verification import make_plan as previous
    parent=previous('slim-short-lap-smooth-c',baseline)
    # The later rotary instructions explicitly replace the paired snap strategy
    # and permit local external mechanism packaging. Historical sources stay in
    # the parent plan and human records. Support-free intent remains UNKNOWN.
    replacements={
      'closure.end-retention':'Retain the cap securely with the user-selected one-sided rotary lock',
      'form.cap-comfort':'Provide rounded hand-friendly cap contacts and a full wheel-width holding ledge',
      'form.smooth-exterior':'Keep aligned smooth case sides and exposed seam grip with a compact local rotary closure',
    }
    intent=tuple(U(r.id,replacements[r.id],SOURCE) if r.id in replacements else r
                 for r in parent.requirements)
    protect_user_requirements(parent.requirements,intent,changes={k:SOURCE for k in replacements})
    intent+=(U('rotary.fit','Make the successful PLA trial fit modestly tighter',SOURCE),
             U('rotary.printed','Use printable custom screw and nut with solid male thread core',SOURCE),
             U('rotary.index','Require resistance before rotary disengagement',SOURCE),
             U('rotary.storage','Keep hardware from snagging contents or protruding beyond the control face',SOURCE))
    scope=dict(design=variant,material='PLA intended; actual full case unprinted',
               geometry='75.8x52.8x264; guide .20 per side; keeper 34 wide / .50 radial gap',
               sample_basis='user accepted complete PLA quick trial; exact artifact and settings unknown')
    qs=[Q('full-use',r.id,'Full printed case satisfies this intent in actual travel use','physical') for r in intent]
    targets=tuple((rid,'geometry') for rid in ('brush.fit','paste.fit','closure.secure',
        'closure.end-retention','closure.short-overlap','form.cap-comfort','form.smooth-exterior',
        'rotary.fit','rotary.index','rotary.storage'))
    qs.extend(Q(q,r,'Sampled wheel turn/capture/withdrawal, detent barrier, guide play, seating and individual contents passage; no force or combined-packing claim','CAD') for r,q in targets)
    pub=(('print.material','publication'),('rotary.printed','publication'))
    qs.extend(Q(q,r,'Guarded matching exports and reviewed diagnostic slice; unchanged solid fastener pair retained','slicer') for r,q in pub)
    qs.append(Q('accepted-trial','test.fit','User reports complete PLA trial operates and stays together, with slight looseness','physical'))
    qs.append(Q('impact','closure.side-hit','Knocks and bumps inside a travel bag do not release the full printed case','physical'))
    qs.append(Q('force','research.force','Actual release effort and retention force quantified for this rotary case','physical'))
    return Plan(variant,intent,scope,questions=tuple(qs),
        checks=(assertion_check('rotary.CAD',targets,cad,'notes/rotary_case/cad.json',scope),
                assertion_check('rotary.publication',pub,publication,'notes/rotary_case/publication.json',scope)),
        retained=(Evidence('rotary.accepted-trial',(('test.fit','accepted-trial'),),Status.PASS,
             'Complete PLA quick trial works and stays together; slight looseness. This is sample evidence, not a full-case force/impact qualification.',
             RECORD+'#user-feedback-and-authorized-adoption',scope),),
        directives=(Directive('rotary.adopt','Proceed with the revised full box for printing',SOURCE),),
        decisions=(DesignDecision('rotary.clearances','Tighten guide .30 to .20 mm per side and keeper radial gap .80 to .50; preserve successful thread and spring',RECORD),))
