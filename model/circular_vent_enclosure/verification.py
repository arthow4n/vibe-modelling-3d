"""Explicit V1 intent coverage; unresolved physical obligations stay visible."""
from pathlib import Path
from product_verification import (UserRequirement, UserSource, Question, Plan,
    DesignDecision, assertion_check, cli, protect_recorded_intent)

ROOT = Path(__file__).resolve().parent
REQUIREMENTS = tuple(UserRequirement(id, text, UserSource('notes/brief.md', source), criteria)
    for id, text, source, criteria in (
    ('vent.envelope', 'Compact lightweight circular enclosure within the specified envelope.',
     'Existing valve approximately 130 mm diameter and 35 mm projection; maximum OD approximately 230 mm; preferred 210–215 mm OD and 80–90 mm projection.',
     ('Maximum 50 mm extra radius; approximately 230 mm maximum OD.', 'Preferred OD 210–215 mm; projection 80–90 mm.')),
    ('vent.flow', 'Preserve the original annular air opening and avoid narrow added passages.',
     'Original valve and airflow gap must remain unobstructed; check the entire path, initially aim for 80–100 cm² outlets; effective valve area unknown.',
     ('No obstruction of original valve or airflow gap.',)),
    ('vent.mount', 'Removable non-destructive attachment to a stationary rim, preserving valve adjustment.',
     'Never grip the disc; mounting surface and rim not measured; keep diameter, clearance and engagement parametric; do not overload attachment.', ()),
    ('vent.shield', 'Solid front shield and broad rounded peripheral windows without an extra baffle.',
     'Shield direct forward radiation; 6–8 broad rounded windows; smooth internal transitions; no additional internal baffle in V1.', ()),
    ('vent.print', 'PETG FDM manufacture, preferably one support-free part with front against the bed.',
     'Shell 2.0–2.4 mm, front 2.4–3.0 mm; avoid unsupported bridges and evaluate taper, window tops, weight and stiffness.', ()),
    ('vent.use', 'Reduce perceived noise while retaining useful airflow, cleanability and stable quiet structure.',
     'No guaranteed silencing; no assumption of broadband volume attenuation; avoid whistles, rattles, debris traps and a flexible vibrating front.', ()),
))
QUESTIONS = (
    Question('nominal', 'vent.envelope', 'Declared dimensions remain within requested limits.', 'CAD'),
    Question('mass', 'vent.envelope', 'Physical mass and existing attachment capacity are acceptable.', 'physical'),
    Question('conditional-path', 'vent.flow', 'For an approximate 20–35 mm emission band, nominal CAD clears valve and 12 mm annular band; projected exits and added full-flow section screen ≥80 cm².', 'CAD'),
    Question('actual-opening', 'vent.flow', 'Measured valve opening is unobstructed and installed flow remains acceptable.', 'physical'),
    Question('retention', 'vent.mount', 'Measured stationary-rim fit, retention, attachment capacity and adjustment remain acceptable.', 'physical'),
    Question('geometry', 'vent.shield', 'Forward disc footprint has a solid shield; eight rounded peripheral windows, no internal baffle.', 'CAD'),
    Question('construction', 'vent.print', 'Nominal thicknesses and manufacturing geometry follow recorded FDM plan.', 'CAD'),
    Question('print-result', 'vent.print', 'Actual PETG part prints without unacceptable sag, warp or separation.', 'physical'),
    Question('noise', 'vent.use', 'Matched-condition physical test shows useful noise reduction without excessive ventilation loss.', 'subjective/physical'),
    Question('clean-stable', 'vent.use', 'Installed part remains secure, cleanable and free of rattle, panel resonance and condensation traps.', 'physical'),
)


def make_plan(variant):
    if variant != 'v1':
        raise ValueError(f'Unknown variant: {variant}')
    protect_recorded_intent(ROOT, REQUIREMENTS)
    import checks
    scope = {'variant': variant, 'interface': 'nominal-unmeasured-130mm', 'emission-band': 'user-approximate-wall20-35mm'}
    checks_declared = (
        assertion_check('envelope', (('vent.envelope', 'nominal'), ('vent.print', 'construction')),
                        checks.envelope, 'checks.py; README.md', scope),
        assertion_check('shield-clearance', (('vent.shield', 'geometry'),),
                        checks.nominal_fit, 'checks.py', scope),
        assertion_check('conditional-flow', (('vent.flow', 'conditional-path'),),
                        lambda: (checks.nominal_fit(), checks.flow()), 'checks.py', scope),
    )
    return Plan(variant, REQUIREMENTS, scope, checks_declared, questions=QUESTIONS,
        decisions=(DesignDecision('vent.v1-architecture',
            'One-piece hood with a continuous tapered rear, provisional slip collar and shallow front ribs; no qualified friction retention.',
            'README.md'),))


if __name__ == '__main__':
    raise SystemExit(cli(make_plan, ('v1',)))
