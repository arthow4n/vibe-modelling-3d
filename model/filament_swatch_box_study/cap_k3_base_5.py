"""K3: K2 source-correct dome supports with upward-facing base ledges.

PETG .4/.2, two walls/7% adaptive cubic. G/V1 hoods and I key unchanged.
"""
import cap_k2_base_5 as previous
import upward_grips as grips


def base(include_panels=True,include_detents=True):
    return grips.revise(previous.base(include_panels,include_detents))


if __name__ in ('__main__','__cqgi__'):
    result=base().translate(grips.g.PRINT_ANCHOR)
