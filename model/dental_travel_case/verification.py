"""Measured two-lane case: declared user intent and scoped CAD/physical evidence."""
from functools import cache
from pathlib import Path
from product_verification import (UserRequirement as U, UserSource as S, Question as Q,
                                  Directive, DesignDecision, Hypothesis, Plan,
                                  assertion_check, cli, protect_recorded_intent)

RECORD = 'notes/README.md'
MEASUREMENTS = RECORD+'#measured-items-and-user-intent'
REQUIREMENTS = (
    U('brush.fit', 'Carry the measured electric toothbrush with its head attached',
      S(MEASUREMENTS, 'User measured 250–255 mm overall, nearly cylindrical 30 mm handle, 165 mm handle and 90 mm shoulder-to-tip')),
    U('paste.fit', 'Carry toothpaste on its own side with room for tube variation',
      S(MEASUREMENTS, 'User measured a new tube about 160 x 55 x 40 mm with 30 mm cap and requested margins for other versions')),
    U('print.material', 'Use a compliant printed design without a separate TPU print',
      S(MEASUREMENTS, 'User requested compliance and preferably no separately printed TPU part')),
    U('test.fit', 'Provide a small or simplified fit test that is easy and quick to print alongside the full model',
      S(RECORD+'#first-print-and-test-procedure', 'User authorized both the small fit test and complete model in one phase')),
)
QUESTIONS = (
    Q('envelopes', 'brush.fit', 'Approximate measured brush proxies clear shells and clips; button band stays free', 'CAD'),
    Q('path', 'brush.fit', 'Loaded shells/brush clips clear sampled opening angles 0..180 degrees in 10 degree steps', 'CAD'),
    Q('capture', 'brush.fit', 'Clip throat captures nominal handle; socket backstop/dovetail obstruct travel with small rib preload', 'CAD'),
    Q('closure', 'brush.fit', 'Latch obstructs initial lift and clears when pulled outward 3 mm; hinge coupon retains axial capture', 'CAD'),
    Q('use', 'brush.fit', 'Actual brush fits, releases comfortably and remains protected in integrated use', 'physical'),
    Q('envelopes', 'paste.fit', 'Agent-selected 200 x 60 x 44 mm tube proxy clears enclosure and sampled lid path', 'CAD'),
    Q('variation', 'paste.fit', 'Actual full tube and desired alternative tubes fit without unwanted squeeze', 'physical'),
    Q('construction', 'print.material', 'Valid connected PETG parts; planned panels-down envelope fits Q2C with 3 mm brim', 'CAD'),
    Q('compliance', 'print.material', 'Approximate straight-beam analogy stays below agent-selected 1% provisional strain screen', 'analytical'),
    Q('effort', 'print.material', 'Printed PETG clips/latch/hinge operate comfortably without cracking, whitening or unintended release', 'physical'),
    Q('life', 'print.material', 'Creep and repeated operation remain adequate in actual travel use', 'physical'),
    Q('representative', 'test.fit', 'Small test uses exact production clip/socket and orientation; mechanism tests preserve local interfaces', 'CAD'),
    Q('trial', 'test.fit', 'User reports useful physical fit and effort observations from the sample', 'physical'),
)


def make_plan(variant):
    if variant in ('rounded-c', 'plain-cylinder'):
        from current_verification import make_current_plan
        return make_current_plan(variant, REQUIREMENTS)
    if variant != 'measured-two-lane':
        raise ValueError('Unknown variant: '+variant)
    protect_recorded_intent(Path(__file__).resolve().parent, REQUIREMENTS)
    from design import build
    import checks
    from samples import samples
    scope = {'design': variant, 'material': 'intended-PETG', 'brush': '255x30-handle165',
             'process': '0.4mm-nozzle-0.2mm-layers', 'revision': '2026-10-13-unprinted'}
    @cache
    def candidate():
        return build()
    def representative():
        tests = samples(candidate())
        for name, part in tests.items():
            assert part.isValid(), name
        # Both sample and production use components.clip/socket unchanged,
        # preserving foot-down orientation and raised production plinth.
    groups = (
        ('brush.envelopes', (('brush.fit','envelopes'),), lambda: checks.brush_check(candidate()), 'checks.py#brush_check'),
        ('paste.envelopes', (('paste.fit','envelopes'),), lambda: checks.paste_check(candidate()), 'checks.py#paste_check'),
        ('fit.path', (('brush.fit','path'),), lambda: checks.shells_check(candidate()), 'checks.py#shells_check'),
        ('fit.capture', (('brush.fit','capture'),), lambda: checks.clips_check(candidate()), 'checks.py#clips_check'),
        ('case.closure', (('brush.fit','closure'),), lambda: checks.latch_check(candidate()), 'checks.py#latch_check'),
        ('case.construction', (('print.material','construction'),), lambda: checks.construction_check(candidate()), 'checks.py#construction_check'),
        ('clip.screen', (('print.material','compliance'),), checks.compliance_check, 'checks.py#compliance_check'),
        ('sample.interfaces', (('test.fit','representative'),), representative, 'samples.py'),
    )
    return Plan(variant, REQUIREMENTS, scope,
        checks=tuple(assertion_check(id, targets, run, ref, scope) for id,targets,run,ref in groups),
        questions=QUESTIONS,
        directives=(Directive('floss.optional', 'No dedicated floss bay; opportunistic fit and tissue packing are acceptable',
                             S(MEASUREMENTS, 'User said floss fit does not matter and requested removing its dedicated slot')) ,),
        decisions=(DesignDecision('two-lanes', 'Retain captive enclosure and removable PETG grips; remove shoulder stop whose neck fit is unmeasured', RECORD),),
        hypotheses=(Hypothesis('clip-feel', 'Thin curved arms may accommodate approximate diameter; effort, fatigue and useful fit range are unqualified', RECORD),))


if __name__ == '__main__':
    raise SystemExit(cli(make_plan, ('measured-two-lane', 'rounded-c', 'plain-cylinder')))
