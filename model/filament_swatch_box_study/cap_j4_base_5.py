"""J4: J2 upright card supports with recessed upward-facing base grips.

PETG .4/.2, two walls/7% adaptive cubic. Accepted G hood and I key unchanged.
"""
import cap_j2_base_5 as previous
import recessed_grips as grips


def base(include_panels=True,include_detents=True):
    return grips.revise(previous.base(include_panels,include_detents))


if __name__ in ('__main__','__cqgi__'):
    result=base().translate(grips.g.PRINT_ANCHOR)
