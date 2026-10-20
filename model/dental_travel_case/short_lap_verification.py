"""Current short-lap prototype: explicit scope, inherited intent and unknowns."""
from dataclasses import replace
import json
from pathlib import Path
from product_verification import (Plan, Question as Q, UserRequirement as U,
    UserSource as S, Directive, DesignDecision, Hypothesis, assertion_check,
    protect_user_requirements, CalculationInconclusive)
from closure_short_verification import make_short_plan
from closure_research_verification import require_sources
from closure_research_checks import hashes
import short_lap_design as design
import short_lap_reinforced as production

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'
RECORD = 'notes/short_lap.md'
SOURCE = S(RECORD+'#authorized-direction--2026-10-19',
    'User discards hinged box, reopens smaller-bite wall snaps, accepts potentially tolerable opening noise, and requests a grounded shorter overlap range with very good retention against sideways handling and an improved full model')
SIDE_HIT_SOURCE = S(RECORD+'#sideways-hit-clarification--2026-10-20',
    'User clarifies: hitting the box from sideways should not open the box, specifically knocks and bumps inside a travel bag; no numeric impact severity is specified')
PUBLICATION_INPUTS = ('m1_design.py','closure_research_design.py','short_lap_design.py',
    'short_lap_refinement.py','short_lap_reinforced.py','short_lap_case.py','short_lap_joint_test.py',
    '../../uv.lock','../../evaluate_model.py')


def cad():
    data = json.loads((OUT/'cad.json').read_text())
    require_sources(data['source_sha256'])
    assert data['selected_overlap_mm'] == production.SELECTED_OVERLAP
    assert min(r['obstruction_mm3'] for r in data['independent_capture']) > .05
    assert all(r['guide_intersection_mm3'] < 1e-5 for r in data['path'])
    assert all(r['snap_intersection_mm3'] < 1e-5 for r in data['path'] if r['travel_mm'] >= 6)
    assert min(data['individual_passage_gaps_mm'].values()) >= .8-1e-6
    assert data['sample']['complete_production_cap'] and data['hard_seat'] and data['grips_clear']


def comparison():
    data = json.loads((OUT/'comparison.json').read_text())
    require_sources(data['source_sha256'])
    assert set(data['cases']) == set(map(str,design.OVERLAPS))
    from short_lap_study import question
    for lap in design.OVERLAPS:
        row = data['cases'][str(lap)]
        for member,record in row['members'].items():
            answer = replace(question(lap,member),mesh_size_mm=1.75).read_evidence(
                OUT/'flex'/f'{lap:g}_{member}'/'mesh_sensitivity_1')
            assert answer.completed
            assert record['mesh_relative_change'] < .10 and record['balance'] < .01
        for path in row['paths'].values():
            assert path['peak_step_change'] < .10
            assert all(abs(p['CAD_retraction_mm']-p['profile_retraction_mm']) < .001 for p in path['CAD_witnesses'])
    refined = json.loads((OUT/'refinement.json').read_text())
    require_sources(refined['source_sha256'])
    from short_lap_refinement_study import question as refined_question
    for member,record in refined['members'].items():
        answer = replace(refined_question(member),mesh_size_mm=1.75).read_evidence(
            OUT/'flex'/('balanced_'+member)/'mesh_sensitivity_1')
        assert answer.completed and record['mesh_relative_change'] < .10
        assert record['balance'] < .01
    assert refined['overlap_mm'] == design.SELECTED_OVERLAP
    assert refined['missing_bite_zero_barrier']
    assert all(refined['provisional_screens'].values()), refined['provisional_screens']
    for path in refined['paths'].values():
        assert path['peak_step_change'] < .10 and path['energy_step_change'] < .10
        assert all(abs(w['CAD_retraction_mm']-w['profile_retraction_mm']) < .001 for w in path['CAD_witnesses'])
    final = json.loads((OUT/'reinforced.json').read_text())
    require_sources(final['source_sha256'])
    from short_lap_reinforced_study import question as final_question
    for member,record in final['members'].items():
        answer = replace(final_question(member),mesh_size_mm=1.75).read_evidence(
            OUT/'flex'/('reinforced_'+member)/'mesh_sensitivity_1')
        assert answer.completed and record['mesh_relative_change'] < .10 and record['balance'] < .01
    assert final['overlap_mm'] == production.SELECTED_OVERLAP
    assert final['missing_bite_zero_barrier'] and all(final['provisional_screens'].values())
    for path in final['paths'].values():
        assert path['peak_step_change'] < .10 and path['energy_step_change'] < .10
        assert all(abs(w['CAD_retraction_mm']-w['profile_retraction_mm']) < .001 for w in path['CAD_witnesses'])


def side_comparison():
    from short_lap_side_study import question
    records = {}
    for stage,prefix in (('first','side'),('reinforced','reinforced_side')):
        record = json.loads((OUT/(prefix+'.json')).read_text())
        require_sources(record['source_sha256'])
        for axis,row in record['cases'].items():
            for member,result in row['members'].items():
                answer = replace(question(member,axis,stage=stage),mesh_size_mm=1.75).read_evidence(
                    OUT/'flex'/f'{prefix}_{member}_{axis}'/'mesh_sensitivity_1')
                assert answer.completed
                assert result['balance'] < .01
            assert row['roof_mesh_relative_change'] < .10
        records[stage] = record
    for axis in ('x','y'):
        before = records['first']['cases'][axis]['estimated_extra_roof_motion_mm']
        after = records['reinforced']['cases'][axis]['estimated_extra_roof_motion_mm']
        assert after < before, 'Reinforcement must improve both declared side-bearing paths'


def lateral_release():
    """Preserve attempted coupled evidence without promoting partial snapshots."""
    for name in ('seated_x_0.2','seated_y_0.14'):
        data = json.loads((OUT/('lateral_capture_'+name+'.json')).read_text())
        require_sources({key:data['source_sha256'][key]
                         for key in ('short_lap_reinforced.py','short_lap_refinement.py')})
        assert not data['run_completed'], 'Historical interrupted snapshots must retain their scope'
    raise CalculationInconclusive(
        'A complete static snapshot shows almost all capture consumed at one widthwise bite while the other retains it. '
        'No qualified complete sequential-release path or mesh/increment/contact sensitivities; '
        '10 N is an agent comparison, not travel-bag impact acceptance. See notes/short_lap.md.')


def publication():
    record = json.loads((OUT/'publication.json').read_text())
    require_sources(record['inputs'])
    assert set(record['inputs']) == set(PUBLICATION_INPUTS)
    for stem in ('short_lap_case','short_lap_joint_test'):
        require_sources(record['artifacts'][stem])
        receipt = json.loads((OUT/(stem+'_slice.json')).read_text())
        assert receipt['geometry']['valid'] and receipt['slice']['ok']
        assert receipt['slice']['input_sha256'] == hashes((stem+'.stl',))[stem+'.stl']
        assert receipt['slice']['support_probe']['ok']
        assert not receipt['slice']['support_probe']['generated'], 'Support placement needs inspection'
    paths = json.loads((OUT/'paths.json').read_text())
    require_sources(paths['source_sha256'])
    sample = json.loads((OUT/'short_lap_joint_test_slice.json').read_text())
    assert paths['slice_input_sha256'] == sample['slice']['input_sha256']
    assert all(s['coverage']['uncovered_width_mm'] < .15 for s in paths['sections'].values())


def associate():
    cad()
    record = dict(inputs=hashes(PUBLICATION_INPUTS),artifacts={})
    for stem in ('short_lap_case','short_lap_joint_test'):
        receipt = 'notes/short_lap/'+stem+'_slice.json'
        r = json.loads((ROOT/receipt).read_text())
        assert r['ok'] and r['slice']['ok']
        assert r['slice']['input_sha256'] == hashes((stem+'.stl',))[stem+'.stl']
        record['artifacts'][stem] = hashes((stem+'.step',stem+'.stl',receipt))
    (OUT/'publication.json').write_text(json.dumps(record,indent=2)+'\n')


def make_plan(variant, baseline):
    if variant != 'slim-short-lap':
        raise ValueError(variant)
    parent = make_short_plan('research-short-closures',baseline)
    # The smaller wall bite supersedes M1's requested deeper independent teeth.
    # Retain the stable ID and explicit later provenance; history stays in m1.md.
    intent = tuple(U(r.id,'Use small wall-snap bites and tight holding at both widthwise ends of the case',SOURCE)
        if r.id == 'closure.end-retention' else r for r in parent.requirements)
    protect_user_requirements(parent.requirements,intent,changes={'closure.end-retention':SOURCE})
    intent += (U('closure.short-overlap','Find a reasonable shorter overlap range while retaining very good closure and sideways resistance',SOURCE),)
    intent += (U('closure.side-hit','The box stays closed when hit from the side',SIDE_HIT_SOURCE,
                 acceptance_criteria=('Knocks and bumps inside a travel bag',)),)
    from wall_comparison_verification import REQUIREMENT
    intent += (REQUIREMENT,)
    scope = dict(design=variant,material='uncalibrated PETG comparison',
                 process='0.4 mm nozzle / 0.2 mm layers / three walls',phase='unprinted full prototype and matching joint',
                 overlap_mm=str(production.SELECTED_OVERLAP))
    # Physical questions remain visible for all inherited intent. CAD and reduced
    # mechanics only answer their own obligations; no blanket full-product PASS.
    questions = [Q('physical',r.id,'Current full prototype satisfies this intent in actual printed integrated use','physical') for r in intent]
    checks = []
    def add(id,targets,criterion,mode,fn,reference):
        questions.extend(Q(qid,rid,criterion,mode) for rid,qid in targets)
        checks.append(assertion_check(id,tuple(targets),fn,reference,scope))
    add('short-lap.CAD',[(r,'geometry') for r in ('brush.fit','paste.fit','test.fit','form.minimal',
        'form.width-revision','form.end-rounds','closure.secure','closure.end-retention','research.interior','research.grip')],
        'Current production geometry has individual passage, two independent snap obstructions, clear guide/runout, hard seat, recessed grips, R4 ends and matching production crop; not elastic or physical qualification',
        'CAD',cad,'notes/short_lap/cad.json')
    add('short-lap.comparison',[(r,'comparison') for r in ('research.force','closure.short-overlap')],
        'New mesh-checked body/cap radial compliances and actual CAD energy paths compare 18/24/30mm; rigid guide motion and ideal bearing-couple reactions are separately scoped, not loaded stiffness or safe payload',
        'numerical',comparison,'notes/short_lap/comparison.json')
    add('short-lap.side',[(r,'side-screen') for r in ('closure.short-overlap','travel.protection')],
        'Stronger 30mm bearing sections improve both mesh-checked principal 2N/180Nmm side-load fixtures versus the first 24mm candidate; independent band tractions and roof extrapolation are not contact equilibrium or impact qualification',
        'numerical',side_comparison,'notes/short_lap/reinforced_side.json')
    add('short-lap.lateral-release',[('closure.side-hit','coupled-release')],
        'Coupled deformable cap/body loading with free axial cap motion excludes sequential release through a provisional 10N principal-plane comparison, with adequate contact and sensitivity evidence; separate from impact validation',
        'numerical',lateral_release,RECORD+'#sideways-hit-clarification--2026-10-20')
    add('short-lap.publication',[(r,'slice') for r in ('print.material','print.supportfree','test.fit')],
        'Current paired print exports have native source associations and successful diagnostic slices, no generated support',
        'slicer',publication,'notes/short_lap/publication.json')
    return Plan(variant,intent,scope,questions=tuple(questions),checks=tuple(checks),
        directives=(Directive('hinge.abandoned','Discard hinged dental-box direction; continue short wall snaps autonomously',SOURCE),
                    *parent.directives),
        decisions=(DesignDecision('short-lap.selection','Select overlap from the recorded compliance/guide tradeoff; prototype only, physical retention remains unknown',RECORD),),
        hypotheses=(Hypothesis('short-lap.sound','Less overlap may reduce sliding/rubbing time; it does not establish quieter snap release or easier engagement',RECORD),))
