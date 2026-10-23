"""Explicit V3 intent coverage; unresolved physical obligations stay visible."""
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
REQUIREMENTS += (
    UserRequirement('vent.material', 'Further reduce material while preserving diffuser/shield functionality.',
        UserSource('notes/brief.md#follow-up-directions',
            "Do you think it's possible to further reduce the material usage while keeping the functionality? If possible go do it")),
    UserRequirement('vent.clamp', 'Increase stationary-rim contact and provide compliant adjustable clamping tolerant of modest measurement error.',
        UserSource('notes/brief.md#follow-up-directions',
            "Btw I think you need a bit more contact area with the rim to ensure the mounting is stable, consider also making the mechanism a bit clamping so it's both compliant and clamping so I can mount easily without worrying about slightly wrong measuring")),
)
REQUIREMENTS += (
    UserRequirement('vent.access', 'Make nut loading and driver approaches usable; assemble hood and clamp on the bench before tightening the installed rim clamp.',
        UserSource('notes/brief.md#fastener-access-revision', 'Reverse the problematic head/nut directions and fix screwdriver and nut installation access for bench-first assembly.')),
    UserRequirement('vent.ribs', 'Keep the existing front stiffening ribs.',
        UserSource('notes/brief.md#fastener-access-revision', 'Otherwise, I agree with you we keep the stiffening ribs.')),
)
QUESTIONS = (
    Question('nominal', 'vent.envelope', 'Declared dimensions remain within requested limits.', 'CAD'),
    Question('mass', 'vent.envelope', 'Physical mass and existing attachment capacity are acceptable.', 'physical'),
    Question('conditional-path', 'vent.flow', 'For an approximate 20–35 mm emission band, nominal CAD clears valve and 12 mm annular band; projected exits and added full-flow section screen ≥80 cm².', 'CAD'),
    Question('actual-opening', 'vent.flow', 'Measured valve opening is unobstructed and installed flow remains acceptable.', 'physical'),
    Question('clamp-geometry', 'vent.clamp', '16 mm band and adjustable screw-driven closure; geometric 129–132 mm poses, slot alignment and removal path remain clear.', 'CAD'),
    Question('clamp-use', 'vent.clamp', 'Physical fit, clamping effort, retention and long-term creep on the actual fixed rim are acceptable.', 'physical'),
    Question('saving', 'vent.material', 'Combined hood and clamp CAD material falls below V1, retaining front thickness, ribs, outlet area and air keepout.', 'CAD'),
    Question('saving-use', 'vent.material', 'Physical operation confirms material reduction preserves stiffness, airflow and quietness.', 'physical'),
    Question('tools', 'vent.mount', 'Straight rear M3 bench approach and clear-side installed M4 L-key approach clear the assembly.', 'CAD'),
    Question('drivers', 'vent.access', 'Straight rear M3 bench access and installed clear-side M4 approach clear the complete assembly.', 'CAD'),
    Question('nuts', 'vent.access', 'M3 nuts enter side channels; M4 nut enters its room-facing loading slot.', 'CAD'),
    Question('sequence', 'vent.access', 'Bench-first assembly and final installed clamping work physically with usable tightening effort and no rattle.', 'physical'),
    Question('retained', 'vent.ribs', 'The eight existing 2 × 3 mm front ribs retain actual material witnesses.', 'CAD'),
    Question('retention', 'vent.mount', 'Measured stationary-rim fit, retention, attachment capacity and adjustment remain acceptable.', 'physical'),
    Question('geometry', 'vent.shield', 'Forward disc footprint has a solid shield; eight rounded peripheral windows, no internal baffle.', 'CAD'),
    Question('construction', 'vent.print', 'Nominal thicknesses and manufacturing geometry follow recorded FDM plan.', 'CAD'),
    Question('print-result', 'vent.print', 'Actual PETG part prints without unacceptable sag, warp or separation.', 'physical'),
    Question('noise', 'vent.use', 'Matched-condition physical test shows useful noise reduction without excessive ventilation loss.', 'subjective/physical'),
    Question('clean-stable', 'vent.use', 'Installed part remains secure, cleanable and free of rattle, panel resonance and condensation traps.', 'physical'),
)


def make_plan(variant):
    if variant != 'v3-access':
        raise ValueError(f'Unknown variant: {variant}')
    protect_recorded_intent(ROOT, REQUIREMENTS)
    import checks
    scope = {'variant': variant, 'interface': 'split-ring-geometric129-132mm-unmeasured-rim', 'emission-band': 'user-approximate-wall20-35mm'}
    checks_declared = (
        assertion_check('nut-loading', (('vent.access','nuts'),), checks.nut_access, 'checks.py; hardware.py', scope),
        assertion_check('ribs', (('vent.ribs','retained'),), checks.ribs, 'checks.py', scope),
        assertion_check('clamp-path', (('vent.clamp','clamp-geometry'),),
                        checks.mounting, 'checks.py; mounting_clamp.py', scope),
        assertion_check('tools', (('vent.mount','tools'),('vent.access','drivers')),
                        checks.tool_access, 'checks.py', scope),
        assertion_check('material', (('vent.material','saving'),),
                        checks.material, 'checks.py', scope),
        assertion_check('envelope', (('vent.envelope', 'nominal'), ('vent.print', 'construction')),
                        checks.envelope, 'checks.py; README.md', scope),
        assertion_check('shield-clearance', (('vent.shield', 'geometry'),),
                        checks.nominal_fit, 'checks.py', scope),
        assertion_check('conditional-flow', (('vent.flow', 'conditional-path'),),
                        lambda: (checks.nominal_fit(), checks.flow()), 'checks.py', scope),
    )
    return Plan(variant, REQUIREMENTS, scope, checks_declared, questions=QUESTIONS,
        decisions=(DesignDecision('vent.v3-architecture',
            'Two printed pieces: 1.4 mm hood shell with unchanged solid 2.4 mm shield and ribs, plus 16.7 mm split rim clamp with rear flange; M4 head on the clear +Y side; M3 heads on the open rear with sliding captive nuts in the hood. Bench-first fit and torque remain physical.',
            'README.md'),))


if __name__ == '__main__':
    raise SystemExit(cli(make_plan, ('v3-access',)))
