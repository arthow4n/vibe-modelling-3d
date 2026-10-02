"""A: full-height lift-off hood + softly rounded five-card base, print layout."""
from cap_common import *


def cap(count=DEFAULT_COUNT):
    return hood_shell(count).union(stop_pads(count)).union(side_grips(count))


def print_layout(count=DEFAULT_COUNT):
    base=rounded_base(count)
    shift=OUTER_WIDTH/2+CAP_OUTER_X/2+10
    return compound(base,hood_print(cap(count)).translate((shift,0,0)))


if __name__ in ('__main__','__cqgi__'):
    result=print_layout()
