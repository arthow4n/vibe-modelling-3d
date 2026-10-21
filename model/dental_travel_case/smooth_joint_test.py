"""Short open-ring PLA trial of the production C2 joint, in print placement.

Preserves both catches, full XY perimeter, overlap, tracks and axial stop.
Open ends change shell restraint: this is a fit/action trial, not a production
pull-force or impact specimen. No production geometry or clearances are retuned.
"""
import cadquery as cq
import m1_design as base
from smooth_case_design import build

BELOW_SEAM_MM = 16.0
ABOVE_SEAT_MM = 10.0


def make_sample():
    production = build('retention-c2')
    d = production['dimensions']
    ex = production['exterior']
    bottom = d.seam - BELOW_SEAM_MM
    top = production['seat_z'] + ABOVE_SEAT_MM
    crop = base.box(0, 0, (bottom + top) / 2,
                    ex.width + 4, ex.depth + 4, top - bottom)
    body = production['body'].intersect(crop).clean()
    cap = production['cap'].intersect(crop).clean()
    assembly = cq.Assembly(name='smooth_C2_PLA_joint_trial')
    assembly.add(body.translate((0, 0, -bottom)), name='body_ring')
    assembly.add(base.print_cap(cap, top), name='cap_ring')
    return dict(production=production, body=body, cap=cap, bottom=bottom,
                top=top, result=assembly)


result = make_sample()['result']
