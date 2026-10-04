"""R2 corner: 15-card archive base; exact G hood / I key 3.

Shared dimensions and builders: archive_corner_proposals.py.
Print PETG, floor down, .4 nozzle/.2 layers, two walls/7% adaptive cubic.
"""
from archive_corner_proposals import base, r1

if __name__ in ('__main__', '__cqgi__'):
    result = base('corner').translate(r1.g.PRINT_ANCHOR)
