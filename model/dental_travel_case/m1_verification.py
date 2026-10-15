"""M1 intent and explicit digital/physical coverage through the shared CLI."""
from functools import cache
import hashlib
import json
from pathlib import Path
from product_verification import (UserRequirement as U, UserSource as S,
    Question as Q, Plan, Directive, DesignDecision, Hypothesis, assertion_check,
    protect_recorded_intent, protect_user_requirements, CalculationInconclusive,
    Evidence, Status)

ROOT = Path(__file__).resolve().parent
RECORD = 'notes/m1.md'
SOURCE = S(RECORD+'#user-instruction-and-architecture',
           'User selected M1, accepted a separate cap, requested no exterior hinge, rounded overlap and resistance to popping open when hit in a backpack; authorized modelling')
FEEDBACK = S(RECORD+'#printed-joint-feedback--2026-10-15',
             'User printed the test, requested 25 mm less width using diagonal toothpaste placement, deeper/longer teeth and tight retention at both widthwise ends; inserts deferred')
PACKING = S(RECORD+'#printed-joint-feedback--2026-10-15',
            'User confirms trying the real brush and toothpaste together: the diagonal arrangement works; no further orientation description is needed')
ENDS = S(RECORD+'#printed-joint-feedback--2026-10-15',
         'User additionally requests much larger fillets at both top and bottom ends of the case and asks that this be learned for future handled designs')
EXPORT_INPUTS = ('m1_design.py','m1_case.py','m1_joint_test.py',
                 '../../uv.lock','../../evaluate_model.py')
EXPORT_NAMES = ('m1_case','m1_joint_test')


def require_current_export_sources(association):
    """Conservative source association, not a cache or a physical qualification.

    Record only after native guarded evaluation/export has completed with Python
    frozen. Matching an old STL to its own old slice is insufficient after CAD edits.
    """
    if not association or set(association.get('inputs',{})) != set(EXPORT_INPUTS):
        raise CalculationInconclusive('Missing/review-required M1 export source association')
    for name in EXPORT_INPUTS:
        actual = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if association['inputs'][name] != actual:
            raise CalculationInconclusive('M1 exports predate current source: '+name)
    for name in EXPORT_NAMES:
        for suffix in ('.step','.stl'):
            file = name+suffix
            if association.get('outputs',{}).get(file) != hashlib.sha256((ROOT/file).read_bytes()).hexdigest():
                raise CalculationInconclusive('M1 export association does not match '+file)


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
        U('form.width-revision', 'Reduce the previous M1 exterior width by 25 mm',
          FEEDBACK, ('25 mm reduction from the previous 99.2 mm exterior width',)),
        U('closure.end-retention', 'Use deeper/longer teeth and tight holding at both widthwise ends of the case', FEEDBACK),
        U('form.end-rounds', 'Use substantially larger fillets at both top and bottom ends of the case', ENDS),
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
                 process='0.4 mm nozzle / 0.2 mm layers', revision='2026-10-15 unprinted narrow M1 with end catches',
                 packing_basis='user-confirmed real items together diagonally')
    questions, groups = [], []
    def add(id, targets, criterion, run, reference, mode):
        questions.extend(Q(qid, rid, criterion, mode) for rid, qid in targets)
        groups.append(assertion_check(id, tuple(targets), run, reference, scope))
    for id, targets, fn, criterion, mode in (
        ('case.construction', [('print.material', 'construction'), ('test.fit', 'representative')],
         checks.construction, 'Two connected cups; full-rim test is cropped from production in matching print orientation', 'CAD'),
        ('brush.fit', [('brush.fit', 'envelope')],
         checks.fit, 'Measured 255/30 mm brush individually clears shell and complete extraction opening with >=0.8 mm clearance; simultaneous packing separate', 'CAD'),
        ('paste.aperture', [('paste.fit', 'aperture')], checks.tube_aperture,
         'Full 55 x 40 tube box individually passes the mouth with >=0.8 mm clearance after brush removal; no claim of simultaneous packing', 'CAD'),
        ('case.end-rounds', [('form.end-rounds','geometry')], checks.end_rounds,
         'Actual horizontal-axis R4 cylindrical end surfaces cover left/right/front/back sides of both closed ends, above printable tangent feet', 'CAD'),
        ('cap.retention', [('closure.secure', 'capture'), ('closure.end-retention','geometry')], checks.closure,
         'Hard rim seats; deeper/wider catches lie at opposite widthwise ends and independently obstruct pull including +/-0.25 mm guide play; capture by 0.25 mm axial lift; removing hooks removes obstruction', 'CAD'),
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
        assert abs(d.width-(99.2-25)) < 1e-8 and d.depth == 51.2 and d.length == 264
        assert d.width < 132 and d.depth < 66
    add('form.size', [('form.minimal', 'envelope'), ('form.width-revision','dimensions')],
        '74.2 x 51.2 x 264 mm exterior: exactly 25 mm narrower than the previous model, two parts, no increased thickness; not a global minimum proof',
        size, 'm1_design.py#Dimensions', 'CAD')
    def slices():
        inventory = json.loads((ROOT/'notes/verification_sources.json').read_text())
        association = inventory.get('artifact_sources',{}).get(variant)
        require_current_export_sources(association)
        for name in EXPORT_NAMES:
            path = ROOT/'notes/slicer_review'/f'{name}.json'
            if not path.exists():
                raise CalculationInconclusive('Missing final slice receipt: '+name)
            receipt = json.loads(path.read_text())
            review = receipt.get('slice', {})
            if receipt['reuse']['identity'] != association['publication_identity']:
                raise CalculationInconclusive(name+' native publication association is stale')
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
        ('paste.fit', 'diagonal-arrangement', 'User has tried the real brush and toothpaste together and confirms that diagonal placement works', 'physical'),
        ('brush.fit', 'physical', 'Actual attached brush fits, is accessible and avoids button activation', 'physical'),
        ('paste.fit', 'variation', 'Actual current and desired alternative full tubes fit without unwanted squeeze', 'physical'),
        ('print.material', 'effort-life', 'Printed leaves operate, recover and withstand repeated use without cracks or creep', 'physical'),
        ('test.fit', 'trial', 'User reports useful fit/closure observations from the new joint pair', 'physical'),
        ('closure.secure', 'backpack', 'Actual loaded cap resists accidental bump, peel and pulling during backpack use while deliberate release remains comfortable', 'physical'),
        ('closure.end-retention', 'physical', 'Revised end catches hold tightly, recover and release comfortably with actual shell flex and print tolerances', 'physical'),
        ('travel.protection', 'use', 'Actual loaded case protects items from external pressure and contact; no crush/drop rating assumed', 'physical'),
        ('form.minimal', 'judgment', 'User accepts complete size, proportions and handling as minimal', 'subjective'),
        ('form.end-rounds', 'comfort', 'User finds the newly rounded top/bottom ends comfortable on the full print', 'physical'),
        ('print.supportfree', 'physical', 'Actual ledges, bridges and vertical PETG leaf roots print successfully without supports', 'physical'),
    ):
        questions.append(Q(qid, rid, criterion, mode))
    history_scope = {'design':variant, 'revision':'presumed 733b92f original 99.2 mm M1 test'}
    history = (
        Evidence('items.diagonal-confirmed', (('paste.fit','diagonal-arrangement'),), Status.PASS,
                 'User confirms real items fit together diagonally. Accepted packing basis; this is not a report of printing the revised case',
                 PACKING.reference, {'design':variant,'packing_basis':scope['packing_basis']}),
        Evidence('original.print.retention', (('closure.secure','backpack'),), Status.FAIL,
                 'User reports intermittent tooth engagement and weak far-end holding on the original printed test; exact file/settings unknown',
                 FEEDBACK.reference, history_scope),
        Evidence('original.print.bulk', (('form.minimal','judgment'),), Status.FAIL,
                 'User says original printed 99.2 mm test is 25 mm too wide and authorizes narrowing',
                 FEEDBACK.reference, history_scope),
    )
    return Plan(variant, intent, scope, checks=tuple(groups), questions=tuple(questions), retained=history,
        directives=(Directive('floss.optional', 'No required floss volume or dedicated pocket', SOURCE),
                    Directive('inserts.deferred', 'Keep the cavity plain; defer any handle insert', FEEDBACK)),
        decisions=(DesignDecision('m1.two-cups', 'Plain shared cavity; 12 mm lap; two recessed widthwise end catches; tighter overlap and seat play', RECORD),),
        hypotheses=(Hypothesis('m1.physical', 'The user-confirmed diagonal arrangement is the packing basis; revised printed clearances, end comfort and holding remain untested', RECORD),))
