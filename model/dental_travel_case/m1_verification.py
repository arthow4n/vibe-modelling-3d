"""M1 intent and explicit digital/physical coverage through the shared CLI."""
from functools import cache
import hashlib
import json
from pathlib import Path
from product_verification import (UserRequirement as U, UserSource as S,
    Question as Q, Plan, Directive, DesignDecision, Hypothesis, assertion_check,
    protect_recorded_intent, protect_user_requirements, CalculationInconclusive)

ROOT = Path(__file__).resolve().parent
RECORD = 'notes/m1.md'
SOURCE = S(RECORD+'#user-instruction-and-architecture',
           'User selected M1, accepted a separate cap, requested no exterior hinge, rounded overlap and resistance to popping open when hit in a backpack; authorized modelling')


def requirements(baseline):
    # Preserve earlier tube variation intent rather than silently dropping it
    # under the later minimal-size preference. Its physical coverage stays open.
    return tuple(baseline) + (
        U('form.minimal', 'Make M1 minimal in design and occupied size',
          S('notes/slim_exploration.md', 'User rejected earlier bulky designs and requested the most slim minimal suggestions; then selected M1')),
        U('closure.secure', 'Separate cap with no exterior hinge and a rounded joint that resists opening when struck in a backpack', SOURCE),
        U('travel.protection', 'Protect the attached toothbrush and full toothpaste tube from outside backpack contents and pressure',
          S('notes/slim_exploration.md', 'User said floss can travel elsewhere and the case mainly protects toothpaste and toothbrush from contact and crashes')),
        U('print.supportfree', 'Make the selected architecture support-free',
          S('notes/README.md#backpack-retention-and-cylinder-direction--2026-10-14',
            'User asked for a support-free rounded R2/C combination')),
    )


def make_m1_plan(variant, baseline):
    if variant != 'slim-m1':
        raise ValueError('Unknown M1 variant: '+variant)
    intent = requirements(baseline)
    protect_recorded_intent(ROOT, intent)
    recorded = json.loads((ROOT/'notes/verification_sources.json').read_text())['variants'][variant]
    previous = tuple(U(r['id'], r['text'], S(**r['source']), tuple(r['acceptance_criteria'])) for r in recorded)
    protect_user_requirements(previous, intent)
    from m1_design import build
    import m1_checks as checks
    @cache
    def candidate():
        return build()
    scope = dict(design=variant, material='intended PETG',
                 process='0.4 mm nozzle / 0.2 mm layers', revision='2026-10-14 unprinted M1')
    questions, groups = [], []
    def add(id, targets, criterion, run, reference, mode):
        questions.extend(Q(qid, rid, criterion, mode) for rid, qid in targets)
        groups.append(assertion_check(id, tuple(targets), run, reference, scope))
    for id, targets, fn, criterion, mode in (
        ('case.construction', [('print.material', 'construction'), ('test.fit', 'representative')],
         checks.construction, 'Two connected cups; full-rim test is cropped from production in matching print orientation', 'CAD'),
        ('contents.fit', [('brush.fit', 'envelope'), ('paste.fit', 'envelope')],
         checks.fit, 'Measured 255/30 mm brush and full 160 x 55 x 40 tube clear; continuous rigid axial extraction envelopes pass the complete mouth with >=0.8 mm clearance', 'CAD'),
        ('cap.retention', [('closure.secure', 'capture')], checks.closure,
         'Hard rim seats; both catches independently obstruct axial pull including +/-0.4 mm guide play; removing catches removes obstruction', 'CAD'),
        ('cap.release', [('closure.secure', 'release')], checks.release_path,
         'Five point-loaded fixed-root squeeze poses clear channels/contents; conservative continuous cap sweep and 16 actual cap poses clear; transverse guide-play release checked', 'CAD'),
        ('cap.admission', [('closure.secure', 'admission')], checks.assembly_path,
         'Ten sampled precompressed squeeze-and-push poses clear; lap independently limits translation and twist; passive snap-on force not established', 'CAD'),
        ('flexure.screen', [('print.material', 'compliance')], checks.compliance,
         'Point-loaded rectangular-beam analogy at body contact, shortened root and +0.3 mm tip-travel allowance stays below provisional uncalibrated 1% strain and 5 N per-leaf squeeze screens', 'analytical'),
    ):
        add(id, targets, criterion, lambda fn=fn: fn(candidate()), 'm1_checks.py#'+fn.__name__, mode)
    def size():
        d = candidate()['dimensions']
        assert d.width <= 100 and d.depth <= 52 and d.length == 264
        assert d.width < 132 and d.depth < 66
    add('form.size', [('form.minimal', 'envelope')],
        'Agent-selected <=100 x 52 x 264 mm construction envelope and two printed parts, smaller cross-section than old R2; not proof of absolute minimum',
        size, 'm1_design.py#Dimensions', 'CAD')
    def slices():
        for name in ('m1_case', 'm1_joint_test'):
            path = ROOT/'notes/slicer_review'/f'{name}.json'
            if not path.exists():
                raise CalculationInconclusive('Missing final slice receipt: '+name)
            receipt = json.loads(path.read_text())
            review = receipt.get('slice', {})
            assert receipt['ok'] and receipt['geometry']['valid'] and review.get('ok'), name+' evaluation/slice failed'
            assert review['input_sha256'] == hashlib.sha256((ROOT/f'{name}.stl').read_bytes()).hexdigest(), name+' stale STL receipt'
            if review['review_required']:
                raise CalculationInconclusive(name+' support/notice review required; see notes/m1.md')
            settings = review['effective_settings']
            assert settings['layer_height'] == '0.2' and settings['nozzle_diameter'] == ['0.4']
            assert settings['filament_type'] == ['PETG']
    add('print.slice', [('print.supportfree', 'slice')],
        'Delivered matching STLs accepted by Orca under named PETG diagnostic profiles, with support-probe review explicit; not physical print or GUI STEP qualification',
        slices, 'notes/slicer_review', 'slicer')
    for rid, qid, criterion, mode in (
        ('brush.fit', 'physical', 'Actual attached brush fits, is accessible and avoids button activation', 'physical'),
        ('paste.fit', 'variation', 'Actual current and desired alternative full tubes fit without unwanted squeeze', 'physical'),
        ('print.material', 'effort-life', 'Printed leaves operate, recover and withstand repeated use without cracks or creep', 'physical'),
        ('test.fit', 'trial', 'User reports useful fit/closure observations from the new joint pair', 'physical'),
        ('closure.secure', 'backpack', 'Actual loaded cap resists accidental bump, peel and pulling during backpack use while deliberate release remains comfortable', 'physical'),
        ('travel.protection', 'use', 'Actual loaded case protects items from external pressure and contact; no crush/drop rating assumed', 'physical'),
        ('form.minimal', 'judgment', 'User accepts complete size, proportions and handling as minimal', 'subjective'),
        ('print.supportfree', 'physical', 'Actual ledges, bridges and vertical PETG leaf roots print successfully without supports', 'physical'),
    ):
        questions.append(Q(qid, rid, criterion, mode))
    return Plan(variant, intent, scope, checks=tuple(groups), questions=tuple(questions),
        directives=(Directive('floss.optional', 'No required floss volume or dedicated pocket', SOURCE),),
        decisions=(DesignDecision('m1.two-cups', 'Plain shared cavity; 12 mm guided lap; two integral opposed recessed body catches', RECORD),),
        hypotheses=(Hypothesis('m1.physical', 'Vertical PETG leaves, shell flex and approximate item shape remain uncalibrated; small test cannot qualify full-shell impact protection', RECORD),))
