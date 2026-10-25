"""Named actual-CAD C2 sections, retaining the existing explanatory drawings."""
from functools import cache
from assembly_geometry import Configuration
from cad_inspection import Camera, Frame, Region, Section, Label, Highlight, View, Inspection
from smooth_case_design import build, assembled


@cache
def parts():
    return build('retention-c2')


@cache
def scene():
    return Configuration.explicit(assembled(parts()), name='retention-c2-closed')


def section(feature):
    p = parts(); d = p['dimensions']
    center = (d.width/2, 0, d.seam+2 if feature == 'seam' else d.latch_z+1)
    region = Region.around(center, (9, 4, 14))
    frame = Frame() if feature == 'whole' else Frame(region, 1)
    annotations = (Highlight(region, 'Catch detail'),) if feature == 'whole' else (
        Label(center, 'Seam collar' if feature == 'seam' else 'Catch and sleeve', (25, -40)),)
    return Inspection(scene(), View(Camera.named('front'), frame=frame,
        section=Section((0, 0, 0), (0, 1, 0), 'planar'),
        colors=(('body', '#1769a6'), ('cap', '#ce741c')), annotations=annotations),
        'Inspect actual C2 body/cap profiles. Grip, opening effort and retention still require physical testing.',
        'C2 closed case — '+feature)


inspections = {name: (lambda name=name: section(name)) for name in ('whole', 'seam', 'catch')}

if __name__ in ('__main__', '__cqgi__'):
    result = scene().assembly()
