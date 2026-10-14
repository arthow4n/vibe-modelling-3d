"""Architecture-specific questions composed from the current CAD checks."""
from functools import cache
import json
from pathlib import Path
from product_verification import UserRequirement as U, UserSource as S, Question as Q, Plan, Directive, assertion_check, protect_recorded_intent, protect_user_requirements, CalculationInconclusive
ROOT = Path(__file__).resolve().parent
RECORD = 'notes/README.md'
LATEST = RECORD + '#backpack-retention-and-cylinder-direction--2026-10-14'
SOURCE = S(LATEST, 'User authorized rounded R2/C and a grippable threaded cylinder; cylinder explicitly needs no clips or separators')

def make_current_plan(variant, baseline):
    if variant not in ('plain-cylinder',):
        raise ValueError('Unknown current architecture: ' + variant)
    cylindrical = variant == 'plain-cylinder'
    requirements = list(baseline)
    changes = {}
    requirements[1] = U('paste.fit', 'Carry toothpaste with variation room in a plain shared cavity', SOURCE)
    changes['paste.fit'] = SOURCE
    requirements += [U('form.rounded', 'Make the enclosure rounded overall and the hinge recessed where used', SOURCE), U('travel.protection', 'Protect the contents during backpack use; retain the brush in the hinged case', SOURCE), U('print.supportfree', 'Make the selected architecture support-free', S(LATEST, 'User asked for a support-free rounded R2/C combination'))]
    requirements.append(U('cylinder.simple', 'Provide a middle threaded joint, grippable exterior and plain interior', SOURCE))
    protect_recorded_intent(ROOT, requirements, changes=changes)
    recorded = json.loads((ROOT / 'notes/verification_sources.json').read_text())['variants'][variant]
    previous = tuple((U(r['id'], r['text'], S(**r['source']), tuple(r['acceptance_criteria'])) for r in recorded))
    protect_user_requirements(previous, requirements)
    scope = dict(design=variant, material='intended PETG', process='0.4 mm nozzle / 0.2 mm layers', revision='2026-10-14 unprinted')
    questions = []
    groups = []

    def add(id, targets, criterion, fn, reference, mode='CAD'):
        for rid, qid in targets:
            questions.append(Q(qid, rid, criterion, mode))
        groups.append(assertion_check(id, tuple(targets), fn, reference, scope))
    import cylinder_checks as checks
    import cylinder_design as design

    @cache
    def candidate():
        return design.build()
    add('case.construction', [('print.material', 'construction'), ('test.fit', 'representative')], 'Two connected cups and short joint test preserve full mating geometry and print orientation', lambda: checks.construction(candidate()), 'cylinder_checks.py#construction')
    add('contents.fit', [('brush.fit', 'envelope'), ('paste.fit', 'envelope'), ('cylinder.simple', 'plain')], '255 mm brush with original 30 mm handle and 60 x 44 mm tube fit the plain cavity with separation', lambda: checks.packing(candidate()), 'cylinder_checks.py#packing')
    add('thread.path', [('cylinder.simple', 'joint'), ('travel.protection', 'capture')], '61 helical poses at 30 degree steps and subsequent loaded straight lift clear; unturned axial pull meets flanks', lambda: checks.thread_motion(candidate()), 'cylinder_checks.py#thread_motion')

    def slice_receipts():
        import hashlib
        names = ('cylinder_case', 'cylinder_thread_test')
        for name in names:
            receipt = ROOT / 'notes/slicer_review' / f'{name}.json'
            if not receipt.exists():
                raise CalculationInconclusive('Missing final slice receipt: ' + name)
            record = json.loads(receipt.read_text())
            review = record.get('slice', {})
            assert record['ok'] and record['geometry']['valid'], name + ' export/evaluation failed'
            assert review.get('ok'), name + ' slice did not complete'
            digest = hashlib.sha256((ROOT / f'{name}.stl').read_bytes()).hexdigest()
            assert review['input_sha256'] == digest, name + ' receipt does not match delivered STL'
            assert review['support_probe']['ok'] and (not review['support_probe']['generated']), name + ' automatic support probe needs review'
            assert not review['review_required'], name + ' unresolved slicer notice'
            settings = review['effective_settings']
            assert settings['layer_height'] == '0.2' and settings['nozzle_diameter'] == ['0.4'], name + ' unexpected layer/nozzle setup'
            assert settings['filament_type'] == ['PETG'], name + ' unexpected material'
    add('print.slice', [('print.supportfree', 'slice')], 'Matching delivered STL receipts accepted under named PETG profiles with no generated supports; physical print and GUI STEP import unqualified', slice_receipts, 'notes/slicer_review', 'slicer')
    for rid, criterion in (('brush.fit', 'Actual brush fits without unintended button pressure'), ('paste.fit', 'Actual desired tubes fit without unwanted squeeze'), ('print.material', 'Printed effort, recovery and life are satisfactory'), ('test.fit', 'New sample gives useful physical fit observations'), ('travel.protection', 'Actual backpack pressure and handling remain satisfactory'), ('form.rounded', 'User finds the complete enclosure suitably rounded'), ('print.supportfree', 'Actual bridges, overhangs and layer adhesion print successfully without supports')):
        questions.append(Q('physical', rid, criterion, 'physical'))
    questions.append(Q('wet-grip', 'cylinder.simple', 'Fluted exterior grips comfortably with wet hands', 'physical'))
    return Plan(variant, tuple(requirements), scope, checks=tuple(groups), questions=tuple(questions), directives=(Directive('floss.optional', 'No dedicated floss bay', SOURCE), Directive('interior.choice', 'Cylinder has no separators or clips; hinged case retains positive brush capture', SOURCE)))
