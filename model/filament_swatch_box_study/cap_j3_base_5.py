"""J3: J2 card supports with two upward-facing base holding ledges.

PETG .4/.2, two walls/7% adaptive cubic. G/V1 hoods and I key unchanged.
"""
import cap_j2_base_5 as previous
import upward_grips as grips


def base(include_panels=True,include_detents=True):
    return grips.revise(previous.base(include_panels,include_detents))


if __name__ in ('__main__','__cqgi__'):
    result=base().translate(grips.g.PRINT_ANCHOR)
