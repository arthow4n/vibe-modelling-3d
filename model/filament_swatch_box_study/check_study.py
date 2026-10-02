"""Reject slot interference and a flip-cover sweep through tall seated cards.

These are sampled rigid-clearance checks, not printed-fit or hinge qualification.
"""
import cadquery as cq
from study import FLIP_END_SPACE, FLIP_RIM, OPEN_ANGLE, closed, contents, cover, flip_cover, tray

cards = cq.Compound.makeCompound(contents())
body = tray()
assert body.val().intersect(cards).Volume() < 1e-6, 'Cards intersect the individual guides'
assert cover().val().intersect(cards).Volume() < 1e-6, 'Closed hood touches the cards'
flip_body = tray(FLIP_RIM, FLIP_END_SPACE)
for angle in range(0, int(OPEN_ANGLE) + 1, 5):
    hood = flip_cover(angle).val()
    assert hood.intersect(cards).Volume() < 1e-6, f'Cover crosses seated cards at {angle} degrees'
    assert hood.intersect(flip_body.val()).Volume() < 1e-6, f'Cover crosses the tray at {angle} degrees'

result = closed()
