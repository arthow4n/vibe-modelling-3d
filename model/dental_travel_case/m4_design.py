"""M4: earlier bearing support during peel; unchanged M3 catches and contents.

The overlap/contact-sequence exploration, not angle alone, motivates the 78mm
sleeve. Assembled length and width stay unchanged. M3 is retained as history.
"""
from dataclasses import dataclass
import m3_design as previous


@dataclass(frozen=True)
class Dimensions(previous.Dimensions):
    lap: float = 78.
    lap_clearance: float = .15
    axial_play: float = .40


D=Dimensions()
hook=previous.hook
tongue=previous.tongue
body_fixed=previous.body_fixed
cap=previous.cap
configuration=previous.configuration


def build(d=D):
    if d.seam+d.lap+6 >= d.length-d.floor:
        raise ValueError('Guide and receiving-band transition must fit below cap floor')
    if d.seam+d.lap+12>d.length:
        raise ValueError('Current joint-sample construction cannot exceed the full cap end')
    parts=previous.build(d)
    parts['result'].name='m4_prototype'
    return parts
