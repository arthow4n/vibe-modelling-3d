"""Finish-only phase composes local checks; full-box coverage remains UNKNOWN."""
from functools import cache
from product_verification import (Question as Q,
    Plan, DesignDecision, Hypothesis, assertion_check, protect_recorded_intent)
import surface_design as d
import surface_checks as c


def make_surface_plan(name, original_requirements, root):
    v = d.variant_named(name)
    requirements = original_requirements
    protect_recorded_intent(root, requirements)
    scope = {'variant': name, 'phase': '30mm-finish-only', 'material': 'TPU-uncalibrated',
             'layer_mm': '0.2', 'ironing_flow': '50%'}
    @cache
    def part():
        return d.coupon(name)
    targets = (('surface.batch', 'geometry'), ('study.flat', 'coupon-face'),
               ('study.two_skins', 'coupon-skins'), ('study.variants', 'coupon-labels'))
    questions = (
        Q('geometry', 'surface.batch', 'Eight separate 30 mm plates have filled edges, planar fields, recessed IDs and the declared skin/core geometry.', 'CAD'),
        Q('coupon-face', 'study.flat', 'The coupon contact field is flat and free of lettering/protrusions.', 'CAD'),
        Q('coupon-skins', 'study.two_skins', 'The coupon retains both full continuous skins.', 'CAD'),
        Q('coupon-labels', 'study.variants', 'Eight named plate placements include permanent recessed IDs outside test fields.', 'CAD'),
        Q('printed-finish', 'surface.finish', 'User compares identical-process coupons to F0 and F7 for reduced rib print-through, flatness and visible lines.', 'physical'),
        Q('damping', 'surface.damping', 'A later controlled physical comparison tests damping; no geometric proxy qualifies quietness.', 'physical'),
    )
    check = assertion_check('surface-geometry', targets,
        lambda: c.geometry(name, part()), 'surface_checks.py / surface_design.py', scope)
    return Plan(name, requirements, scope, (check,), (), questions=questions,
        decisions=(DesignDecision('surface-layout',
            '30 mm plates, 1.2 mm frame, 10 mm solid label band, backing down; CAD cores remain empty with 100% material fill. Solid F7 is a deliberate control.',
            'README.md#surface-finish-coupons--2026-10-17'),),
        hypotheses=(Hypothesis('finish-compliance-tradeoff',
            f'{name}: {v.pattern}, {v.skin:g} mm skin, {v.pitch:g} mm pitch. Thicker skins and closer supports may flatten the surface while increasing stiffness. Retained air is not acoustic evidence.',
            'README.md#surface-finish-coupons--2026-10-17'),))
