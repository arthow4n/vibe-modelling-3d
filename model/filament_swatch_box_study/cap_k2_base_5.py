"""K2: put the shoulder catch on the REAL card's front at X=-16 mm.

Preserve K's spring dimensions, G hood and I key. Add plain-back upright rails.
PETG .4/.2, two walls, 7% adaptive cubic; five-card complete trial.
"""
import dome_latch_study as k
from upright_datums import add_to


def panel(y=0):
    return k.card_panel(y).mirror('YZ')


def crown(y=0):
    return k.shoulder_crown(y).mirror('YZ')


def base(include_panels=True,include_detents=True):
    corrected=k.rough_base(include_panels,include_detents).mirror('YZ')
    return add_to(corrected,side=-1)


if __name__ in ('__main__','__cqgi__'):
    result=base().translate(k.j.g.PRINT_ANCHOR)
