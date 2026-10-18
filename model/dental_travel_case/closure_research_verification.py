"""Research specimens compose CAD, elasticity evidence and physical unknowns."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from product_verification import (Plan,Question as Q,UserRequirement,UserSource,Directive,
    DesignDecision,Hypothesis,CalculationInconclusive,assertion_check,protect_recorded_intent)
from m1_verification import requirements
from closure_research_design import KINDS

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_research'
RECORD='notes/closure_research.md'


def require_sources(records):
    for name,digest in records.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise CalculationInconclusive('Research evidence predates '+name)


def current_publication(kind):
    if kind not in KINDS:raise ValueError(kind)
    record=json.loads((OUT/'publication.json').read_text())
    require_sources(record['inputs']);require_sources(record['artifacts'][kind])
    return record


def cad():
    data=json.loads((OUT/'cad.json').read_text())
    require_sources(data['source_sha256'])
    assert set(data['cases'])==set(KINDS)
    for kind,case in data['cases'].items():
        assert max(p['retaining_overlap_mm3'] for p in case['poses'])>0
        assert all(p['without_detent_mm3']<1e-5 for p in case['poses'])
        if kind!='slide_wall':
            assert case['complete_cap_preserved'] and case['no_runout_overlap_at_30mm_mm3']>0
            assert all(p['retaining_overlap_mm3']<1e-5 for p in case['poses'] if p['lift_mm']>=6)
    for name in ('concepts','tip_motion','slide_section','wall_flexure'):
        block=ET.parse(OUT/(name+'.svg')).find('{http://www.w3.org/2000/svg}metadata')
        require_sources(json.loads(block.text))


def flex():
    data=json.loads((OUT/'flex_summary.json').read_text())
    require_sources(data['source_sha256'])
    for kind,case in data['cases'].items():
        assert case['numerical_confidence']['mesh_sensitivity']=='stable'
        assert case['pad_response_relative_mesh_change']<.10
        assert case['max_force_balance_relative']<.01
        result=json.loads((OUT/'flex'/kind/'mesh_sensitivity_1/result.json').read_text())
        assert result['completed'] and result['metrics']['question']['numerical_evidence_adequate']
        assert result['provenance']['input_sha256']==case['solver_input_sha256']
    return data


def sliced(kind):
    current_publication(kind)
    receipt=json.loads((OUT/(kind+'_slice.json')).read_text())
    assert receipt['slice']['ok'] and receipt['slice']['support_probe']['ok']
    assert not receipt['slice']['support_probe']['generated'],'Inspect support locations before accepting this specimen receipt'
    if kind=='slide_wall':
        rails=json.loads((OUT/'rail_paths.json').read_text())
        require_sources({'closure_research_toolpaths.py':rails['producer_sha256']})
        assert rails['STL_sha256']==receipt['slice']['input_sha256']
        assert all(len(s['path_centres_crossing_mm'])>=2 for s in rails['sections'].values())


def pull_estimate():
    data=json.loads((OUT/'pull_estimate.json').read_text())
    require_sources(data['source_sha256'])
    for kind,row in data['cases'].items():
        assert row['cap_compliance_mesh_change']<.10
        assert row['cap_balance']<.01
        result=json.loads((OUT/'pull'/kind/'mesh_sensitivity_1/result.json').read_text())
        assert result['completed'] and result['metrics']['question']['numerical_evidence_adequate']
        assert result['provenance']['input_sha256']==row['cap_native_input_sha256']
        for path in row['paths'].values():
            assert path['peak_force_step_change']<.10
            assert path['release_energy_step_change']<.10
            assert all(abs(p['CAD_retraction_mm']-p['profile_retraction_mm'])<.001 for p in path['CAD_witnesses'])
    block=ET.parse(OUT/'pull_estimate.svg').find('{http://www.w3.org/2000/svg}metadata')
    require_sources(json.loads(block.text))
    return data


def make_research_plan(variant,baseline):
    if variant!='research-minimal-closures':raise ValueError(variant)
    old=requirements(baseline)
    protect_recorded_intent(ROOT,old)
    source=UserSource(RECORD,'User requests autonomous space-first alternatives, their free-rim idea, visual explanations and corresponding test pieces; full models only as useful; no sub-agents unless explicitly requested')
    intent=old+(UserRequirement('research.samples','Create corresponding test pieces for each explored closure, including the user idea',source),
                UserRequirement('research.interior','Maximize clear interior and explore flat internal walls with minimal retention features',source),
                UserRequirement('research.force','Investigate retention force and equivalent hanging weight before printing, using a reasonable simulation where possible',
                    UserSource(RECORD,'User asks how much force or weight each variant can hold when lifting the box by its cap, and requests recorded computational estimates where feasible')))
    questions=tuple(Q('full-product',r.id,'Full-case adoption/physical behavior is outside this specimen research phase','physical') for r in old)+(
        Q('CAD','research.samples','Four current representative samples, capture, release tracks and independent guide controls','CAD'),
        Q('space','research.interior','Uniform central storage gauges clear actual CAD; no internal guarded cantilever','CAD'),
        Q('flexibility','research.interior','Mesh-checked shell flexibility distinguishes orientation under stated radial fixture','numerical'),
        Q('physical','research.samples','Printed fit, opening effort, holding, recovery and wear measured for these specimens','physical'))+tuple(
        Q(kind,'research.force','Conditional force estimate in the actual opening/load direction; not a measured or safe payload rating','numerical') for kind in KINDS)+tuple(
        Q(kind,'research.samples','Current paired exports slice under diagnostic PETG settings with support locations reviewed','slicer') for kind in KINDS)
    scope=dict(design=variant,phase='Research specimens only; no new full case adopted',material='uncalibrated PETG',process='0.4mm nozzle /0.2mm diagnostic PETG')
    groups=[assertion_check('research.CAD',(('research.samples','CAD'),('research.interior','space')),cad,RECORD,scope),
            assertion_check('research.flex',(('research.interior','flexibility'),),flex,'notes/closure_research/flex_summary.json',scope),
            assertion_check('research.pull-proxy',(('research.force','shell_broad'),('research.force','shell_end')),pull_estimate,'notes/closure_research/pull_estimate.json',scope)]
    for kind in KINDS:
        groups.append(assertion_check('research.slice.'+kind,(('research.samples',kind),),lambda kind=kind:sliced(kind),
                                     'notes/closure_research/'+kind+'_slice.json',scope))
    return Plan(variant,intent,scope,questions=questions,checks=tuple(groups),
        directives=(Directive('research.no-agents','Do not use sub-agents unless the user explicitly requests them',source),),
        decisions=(DesignDecision('research.scope','Full reference shells establish sample fidelity and space only; publish specimens, retain M5 as historical prototype',RECORD),),
        hypotheses=(Hypothesis('research.limits','Radial elastic response is not assembled opening force; coupon fit/retention/fatigue are unmeasured',RECORD),))
