"""Short-overlap end-wall snap; retain historical research geometry untouched.

Z is brush length, X is width. Complete shell walls flex; no cut cantilevers.
Construction has no publication side effects. All dimensions are millimetres.
"""
from dataclasses import replace
import cadquery as cq
import closure_research_design as research
import m1_design as base

OVERLAPS = (18., 24., 30.)
SELECTED_OVERLAP = 24.
KIND = 'shell_end'


def dimensions(overlap):
    if overlap not in OVERLAPS:
        raise ValueError(f'Undeclared overlap: {overlap}')
    return replace(research.D, width=74.2, lap=float(overlap))


def grip_cut(d):
    cut = base.box(0, d.depth/2, d.seam+1, 20, 10, 4).edges('|Y').fillet(.8)
    return cut.union(cut.mirror('XZ'))


def build(overlap):
    d = dimensions(overlap)
    parts = research.tip_shell(KIND, d)
    parts['cap'] = parts['cap'].cut(grip_cut(d)).clean()
    result = cq.Assembly(name='short_lap_end_snap')
    result.add(parts['body'], name='body')
    result.add(base.print_cap(parts['cap'], d.length), name='cap')
    parts['result'] = result
    return parts


def sample(parts):
    """Full production cap plus body crop; cap can be reused in the full box.

    Retain 16mm below the seam and the complete perimeter. Missing lower body
    and floor change restraint; this sample does not qualify full-box leverage.
    """
    d = parts['dimensions']
    bottom = d.seam-16
    crop = base.box(0, 0, (bottom+d.seam+d.lap)/2, d.width+4, d.depth+4,
                    d.seam+d.lap-bottom)
    body = parts['body'].intersect(crop).clean()
    result = cq.Assembly(name='short_lap_production_joint')
    result.add(body.translate((0,0,-bottom)), name='body_joint')
    result.add(base.print_cap(parts['cap'], d.length), name='reusable_cap')
    return dict(body=body, cap=parts['cap'], result=result, bottom_mm=bottom)
