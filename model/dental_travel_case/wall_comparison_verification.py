"""The thin comparison inherits intent, never the thick shell's force results."""
import json
from pathlib import Path
from product_verification import (Plan, Question as Q, UserRequirement as U,
    UserSource as S, Directive, DesignDecision, assertion_check)
from closure_research_verification import require_sources
from closure_research_checks import hashes

ROOT = Path(__file__).resolve().parent
RECORD = 'notes/wall_comparison.md'
SOURCE = S(RECORD+'#authorized-comparison',
    'User requests full 2 mm and three-line thin case variants for test printing, '
    'allows catch openings if needed and width variation, then selects the same general outside size with matching thin body and cap')
REQUIREMENT = U('closure.wall-comparison',
    'Preserve the current thick case and provide a complete thinner matching pair for practical print comparison',
    SOURCE,acceptance_criteria=('Three extrusion lines in ordinary thin walls',
                               'Full case for both variants; user can choose to print just the cap'))
COMFORT_REQUIREMENT = U('form.cap-comfort','Round the finger slots including interior corners and smooth the exterior joint backing',
    S(RECORD+'#comfort-revision','User visually rejects remaining square finger-slot corners and abrupt exterior joint transitions, and requests rounded, comfortable surfaces'))


def evidence():
    data = json.loads((ROOT/'notes/wall_comparison/checks.json').read_text())
    require_sources(data['source_sha256'])
    for name,artifacts in data['artifacts'].items():
        require_sources(artifacts)
        receipt = json.loads((ROOT/('notes/wall_comparison/'+name+'_slice.json')).read_text())
        assert receipt['geometry']['valid'] and receipt['slice']['ok']
        assert receipt['slice']['support_probe']['ok'] and not receipt['slice']['support_probe']['generated']
        stem = 'short_lap_case' if name == 'control' else 'short_lap_case_three_line'
        assert data['cases'][name]['slice_input_sha256'] == hashes((stem+'.stl',))[stem+'.stl']
        for row in data['cases'][name]['sections'].values():
            assert len(row['strokes']) == (3 if name == 'thin' else 5)
            assert row['coverage']['uncovered_width_mm'] < .05
            assert row['coverage']['internal_gap_mm'] < .01
    for fit in data['fits'].values():
        assert min(row['obstruction_mm3'] for row in fit['catches']) > .05
        assert all(row['guide_mm3'] < 1e-5 for row in fit['path'])
        assert all(row['snap_mm3'] < 1e-5 for row in fit['path'] if row['lift_mm'] >= 6)
        assert min(fit['individual_passage_gaps_mm'].values()) >= .8-1e-6
        assert fit['hard_seat'] and fit['grips_clear'] and fit['end_rounds']


def make_plan(variant,baseline):
    if variant not in ('slim-short-lap','slim-short-lap-three-line'):
        raise ValueError(variant)
    from short_lap_verification import make_plan as thick_plan
    parent = thick_plan('slim-short-lap',baseline)
    scope = dict(design=variant,material='uncalibrated PETG',
        process='0.4 mm nozzle / 0.2 mm layers; three thin or five control strokes across ordinary walls',
        phase='unprinted full matching body and cap; physical comparison',overlap_mm='30')
    questions = [Q('physical',r.id,'Finished full pair satisfies this intent in actual integrated printed use','physical')
                 for r in parent.requirements]
    targets = tuple((rid,'comparison-CAD-and-slice') for rid in
        ('closure.wall-comparison','form.cap-comfort','brush.fit','paste.fit','closure.secure',
         'closure.end-retention','research.grip','form.end-rounds','print.material','print.supportfree'))
    questions.extend(Q(qid,rid,'Finished matching-pair fit, reviewed cap rounding and native exports/slices; no force, comfort or impact rating','CAD/slicer')
                     for rid,qid in targets)
    return Plan(variant,parent.requirements,scope,questions=tuple(questions),
        checks=(assertion_check('wall-comparison.publication',targets,evidence,
                                'notes/wall_comparison/checks.json',scope),),
        directives=(*parent.directives,Directive('thin.matching-pair',
            'Keep general outside size and provide matching thin body/cap; overall width need not be exact',SOURCE)),
        decisions=(DesignDecision('thin.local-backing',
            '1.2 mm ordinary walls; 0.65 mm exterior pads preserve 1.2 mm backing behind recessed catches/runout',RECORD),))
