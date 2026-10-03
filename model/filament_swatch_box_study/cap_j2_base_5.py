"""J2: keep J's printed strong spring; extend the opposing straight datums.

PETG .4/.2, two walls, 7% adaptive cubic. G hood and I key 3 unchanged.
"""
import cap_j_base_5 as j
from upright_datums import add_to


def base(include_panels=True,include_detents=True):
    return add_to(j.base(include_panels,include_detents))


if __name__ in ('__main__','__cqgi__'):
    result=base().translate(j.g.PRINT_ANCHOR)
