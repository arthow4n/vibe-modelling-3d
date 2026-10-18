"""Low-material full-perimeter closure trials, explicitly not force-equivalent.

Reuse the actual research interface builders. Shorten surrounding walls rather
than scaling XY or isolating a clip. Preserve the longer historical specimens.
"""
from dataclasses import replace
import cadquery as cq
import closure_research_design as research
import m1_design as base

KINDS = research.KINDS
D = replace(research.D, seam=14., lap=24., length=50.)
BOTTOM = 8.  # six millimetres of open-bottom base below the shoulder
SLIDE_BOTTOM = 37.


def grip_cut(kind):
    """Recess the cap rim on non-catch walls; retain seated corner stops."""
    research.validate(kind)
    if kind == 'slide_wall':
        return base.box(0, 0, 48.2, 20, 8, 4).edges('|Y').fillet(.8)
    if kind == 'shell_end':
        cut = base.box(0, D.depth/2, D.seam+1, 20, 10, 4).edges('|Y').fillet(.8)
        return cut.union(cut.mirror('XZ'))
    cut = base.box(D.width/2, 0, D.seam+1, 10, 20, 4).edges('|X').fillet(.8)
    return cut.union(cut.mirror('YZ'))


def build(kind):
    research.validate(kind)
    if kind == 'slide_wall':
        original = research.slide(70.)
        crop = base.box(0, 35, (SLIDE_BOTTOM+52)/2, 82, 74, 52-SLIDE_BOTTOM)
        body = original['body'].intersect(crop).cut(grip_cut(kind)).clean()
        cap = original['cap']
        no_detent = original['plain_cap']
        body_print = body.translate((0,0,-SLIDE_BOTTOM))
        cap_print = cap.rotate((0,35,51.2),(1,35,51.2),180).translate((110,0,-51.2))
        bottom = SLIDE_BOTTOM
    else:
        original = research.tip_shell(kind, D)
        crop = base.box(0, 0, (BOTTOM+D.seam+D.lap)/2, 82, 56, D.seam+D.lap-BOTTOM)
        body = original['body'].intersect(crop).clean()
        cap = original['cap'].cut(grip_cut(kind)).clean()
        no_detent = original['plain_body'].intersect(crop).clean()
        body_print = body.translate((0,0,-BOTTOM))
        cap_print = base.print_cap(cap, D.length)
        bottom = BOTTOM
    result = cq.Assembly(name=kind+'_short_retention_pair')
    result.add(body_print, name='base'); result.add(cap_print, name='cap')
    assembled = cq.Assembly(name=kind+'_short_seated')
    assembled.add(body.translate((0,0,-bottom)), name='base')
    assembled.add(cap.translate((0,0,-bottom)), name='cap')
    return dict(kind=kind, dimensions=D, body=body, cap=cap, no_detent=no_detent,
                body_bottom_mm=bottom, result=result, assembled=assembled)
