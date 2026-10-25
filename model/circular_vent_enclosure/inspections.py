"""Installed overview and M3 joint details; inspection references, never print."""
from functools import cache
import math
from cad_inspection import Camera, Anchor, Frame, Region, Section, Label, View, Inspection
from assembly import configuration
from vent_parameters import Parameters

p = Parameters()


@cache
def scene():
    return configuration(p, p.clamp_free_diameter, 0, include_hardware=True)


def joint(mode):
    angle = math.radians(-p.mount_angles[0])
    radial = (math.cos(angle), math.sin(angle), 0)
    normal = (-radial[1], radial[0], 0)
    center = (p.mount_radius*radial[0], p.mount_radius*radial[1], p.hood_standoff)
    anchor = Anchor('M3_head_1', center)  # hardware is authored at its installed coordinates
    camera = Camera(normal, (0, 0, 1)) if mode == 'planar' else Camera(
        (normal[0]+.35*radial[0], normal[1]+.35*radial[1], .3))
    return Inspection(scene(), View(camera,
        frame=Frame(Region.around(anchor, (35, 35, 28)), margin_mm=2),
        section=Section(center, normal, mode, keep='negative'),
        components=('hood', 'clamp', 'M3_head_1', 'M3_nut_1'),
        colors=(('hood', '#1769a6'), ('clamp', '#ce741c'),
                ('M3_head_1', '#555555'), ('M3_nut_1', '#555555')),
        annotations=(Label(anchor, 'M3 joint: nominal hardware', (-120, -85)),)),
        'Inspect head, clamp, hood and nut in their installed positions. Smooth hardware envelopes omit threads.',
        title='Vent mounting joint — '+mode)


inspections = {
    'overview': lambda: Inspection(scene(), View(Camera((1, -1, .8))),
        'Locate mounting joints in the complete installed assembly; hardware is reference geometry.', 'Installed vent'),
    'joint-cutaway': lambda: joint('cutaway'),
    'joint-section': lambda: joint('planar'),
}

if __name__ in ('__main__', '__cqgi__'):
    result = scene().assembly()
