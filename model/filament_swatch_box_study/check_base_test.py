"""Check seated cards and hand-guided correction from all four directions.

Credible failure: a wider entrance accepts the tip but an inner step or side
rim blocks correction before the throat. Sample rigid paths with yaw and tilt,
including neighbours. These are possible motions, not passive-centering proof.
"""
import itertools
import math
import cadquery as cq
from card_base_test import FLOOR, FUNNEL_DEPTH, TOP_Z, build_base, slot_y
from study import UPRIGHT_HEIGHT, UPRIGHT_WIDTH, CARD_THICKNESS


def envelope(index, count, width, thickness, bottom=FLOOR,
             x_offset=0, y_offset=0, yaw=0, lean_x=0, lean_y=0):
    # Start a tilted card by its lowest corner, as it would meet the entrance.
    # Using its bottom-edge midpoint instead would pre-insert the low corner.
    low_corner_drop = (width / 2 * abs(math.sin(math.radians(lean_y)))
                       + thickness / 2 * abs(math.sin(math.radians(lean_x))
                                             * math.cos(math.radians(lean_y))))
    card = (cq.Workplane('XY').box(width, thickness, UPRIGHT_HEIGHT,
                                    centered=(True, True, False))
            .rotate((0, 0, 0), (1, 0, 0), lean_x)
            .rotate((0, 0, 0), (0, 1, 0), lean_y)
            .rotate((0, 0, 0), (0, 0, 1), yaw)
            .translate((x_offset, slot_y(index, count) + y_offset, bottom + low_corner_drop)))
    return card.val()


for count in (5, 15):
    base = build_base(count).val()
    for index in range(count):
        card = envelope(index, count, UPRIGHT_WIDTH, CARD_THICKNESS)
        assert base.intersect(card).Volume() < 1e-6, f'Seated slot {index}/{count} obstructed'

    # A full-width box is stricter than the chamfered card tip. Screen 51 x 2.2 mm.
    for index in (0, count // 2, count - 1):
        card = envelope(index, count, UPRIGHT_WIDTH + 1, CARD_THICKNESS + 0.2)
        assert base.intersect(card).Volume() < 1e-6, f'Variation card binds in slot {index}/{count}'
        neighbours = [envelope(j, count, UPRIGHT_WIDTH + 1, CARD_THICKNESS + 0.2)
                      for j in (index - 1, index + 1) if 0 <= j < count]
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), *itertools.product((-1, 1), repeat=2)]
        for sx, sy in directions:
            for step in range(21):
                fraction = step / 20
                correction = 1 - fraction
                bottom = TOP_Z - 0.2 - (FUNNEL_DEPTH - 0.2) * fraction
                card = envelope(index, count, UPRIGHT_WIDTH + 1, CARD_THICKNESS + 0.2,
                                bottom=bottom, x_offset=sx * 1.5 * correction,
                                y_offset=sy * 1.0 * correction,
                                yaw=sx * 1.0 * correction,
                                lean_x=sy * 2.0 * correction,
                                lean_y=sx * 2.0 * correction)
                assert base.intersect(card).Volume() < 1e-6, f'Correction blocked: {count} cards, slot {index}, direction {(sx, sy)}, step {step}'
                assert all(card.intersect(other).Volume() < 1e-6 for other in neighbours), 'Return hits neighbouring card'

result = build_base(5)
