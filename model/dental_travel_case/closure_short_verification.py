"""Short samples have their own evidence scope; never inherit long-sample force."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from product_verification import Plan, Question as Q, UserRequirement as U, UserSource as S, DesignDecision, assertion_check
from closure_research_verification import require_sources, make_research_plan
from closure_short_design import KINDS

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_short'
RECORD='notes/closure_short.md'


def cad():
    data=json.loads((OUT/'cad.json').read_text())
    require_sources(data['source_sha256'])
    assert set(data['cases'])==set(KINDS)
    for kind,row in data['cases'].items():
        assert all(v<1e-5 for v in row['interface_difference_mm3'].values())
        assert row['grip_clear'] and not row['forces_inherited']
        assert all(p['no_detent_mm3']<1e-5 for p in row['poses'])
        assert max(p['blocked_mm3'] for p in row['poses'])>.05
        assert row['CAD_solid_material_reduction_fraction']>0
    block=ET.parse(ROOT/'notes/closure_research/short_samples.svg').find('{http://www.w3.org/2000/svg}metadata')
    require_sources(json.loads(block.text))
    return data


def sliced(kind):
    if kind not in KINDS: raise ValueError(kind)
    publication=json.loads((OUT/'publication.json').read_text())
    require_sources(publication['inputs'])
    require_sources(publication['artifacts'][kind])
    receipt=json.loads((OUT/(kind+'_slice.json')).read_text())
    assert receipt['slice']['ok'] and receipt['slice']['support_probe']['ok']
    assert not receipt['slice']['support_probe']['generated']


def make_short_plan(variant, baseline):
    if variant!='research-short-closures': raise ValueError(variant)
    parent=make_research_plan('research-minimal-closures',baseline)
    source=S(RECORD,'User requests much shorter overlap/base while preserving full XY shapes, a small separation grip gap, and later rechecking full-case overlap and recessed grips')
    intent=parent.requirements+(
        U('research.short','Provide substantially shorter, lower-material retention samples without scaling the full cross-section or catches',source),
        U('research.grip','Provide a small accessible separation gap, and record ergonomic gripping and shorter-overlap questions for later full-case adoption',source))
    scope=dict(design=variant,phase='Low-material short-wall mechanism trials; no inherited long-sample force or full-case qualification',material='uncalibrated PETG',process='0.4mm nozzle /0.2mm diagnostic PETG')
    questions=tuple(Q('retained-intent',r.id,'Product/force intent retained; this short coupon does not inherit longer-shell mechanical or physical acceptance','physical') for r in parent.requirements)+(
        Q('CAD','research.short','Full-perimeter interfaces match; samples shorten walls and preserve seated/released geometry','CAD'),
        Q('gap','research.grip','Recessed gap clears both parts while remaining rim preserves seated stop; ergonomics remain unmeasured','CAD'),
        Q('comfort','research.grip','Printed gripping and intended separation are comfortable without squeezing release walls','physical'))+tuple(
        Q(kind,'research.short','Current paired exports smoke-slice under documented diagnostic profile','slicer') for kind in KINDS)
    checks=[assertion_check('short.CAD',(('research.short','CAD'),('research.grip','gap')),cad,RECORD,scope)]
    checks.extend(assertion_check('short.slice.'+kind,(('research.short',kind),),lambda kind=kind:sliced(kind),
        'notes/closure_short/'+kind+'_slice.json',scope) for kind in KINDS)
    return Plan(variant,intent,scope,questions=questions,checks=tuple(checks),directives=parent.directives,
        decisions=(DesignDecision('short.scope','24mm overlap is an economical experiment dimension, not a qualified production minimum; shortened walls change compliance',RECORD),))
