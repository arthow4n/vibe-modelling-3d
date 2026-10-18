"""M3 practical prototype: M2B guidance with thicker load-bearing leaves.

The full product remains two integral parts. Liner accessories are out of scope.
No construction side effects; exports use m3_case.py and the shared evaluator.
"""
from dataclasses import dataclass
import m2b_design as previous


@dataclass(frozen=True)
class Dimensions(previous.Dimensions):
    # Thicker leaf + its unchanged release channel would otherwise consume the
    # established toothpaste aperture. Move each side out .4mm instead.
    width: float = 75.0
    beam_thickness: float = 2.0
    skin_reinforcement: float = 1.0


D = Dimensions()
hook = previous.hook
tongue = previous.tongue
body_fixed = previous.body_fixed
cap = previous.cap
configuration = previous.configuration


def build(d=D):
    return previous.build(d)
