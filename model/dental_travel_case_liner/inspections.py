"""Reusable installed L20 liner views; no printable output or physical claims."""
from functools import cache
import cadquery as cq
from assembly_geometry import Configuration
from cad_inspection import Camera, Frame, Region, Section, Label, View, Inspection
from rotary_l20_uniform_design import rigid, installed, BODY_TOP, CAP_BOTTOM


@cache
def scene():
    a = cq.Assembly(name='lined_rotary_case')
    parts = rigid()
    for name in ('body', 'cap'):
        a.add(parts[name], name='rigid_'+name)
        a.add(installed(name), name='liner_'+name)
    return Configuration.explicit(a, name='installed-uniform-L20')


COLORS = (('rigid_body', '#555555'), ('rigid_cap', '#555555'),
          ('liner_body', '#1769a6'), ('liner_cap', '#ce741c'))


def cutaway(detail):
    z = (BODY_TOP+CAP_BOTTOM)/2
    frame = Frame(Region.around((0, 0, z), (85, 55, 25)), 2) if detail else Frame()
    return Inspection(scene(), View(Camera((1, 1, .7)), frame=frame,
        section=Section((0, 0, 0), (0, 1, 0), 'cutaway', keep='negative'), colors=COLORS,
        annotations=(Label((0, 0, z), 'Liner rim transition', (35, -30)),) if detail else ()),
        'Inspect installed rigid walls and TPU liners; the section is display-only and does not establish compressibility or fit.',
        'L20 liner — '+('rim detail' if detail else 'installed section'))


inspections = {'installed': lambda: cutaway(False), 'rim-detail': lambda: cutaway(True)}

if __name__ in ('__main__', '__cqgi__'):
    result = scene().assembly()
