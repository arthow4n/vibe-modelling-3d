"""Inspection-only concepts for notch-up, independently supported swatches.

X: 50 mm card edge. Y: twenty separate positions. Z: 80 mm card edge.
Pivot cylinders are envelopes only, not a printable hinge. No exports.
"""
from pathlib import Path
import re
import cadquery as cq

SWATCH_SOURCE = Path(__file__).resolve().parents[1] / 'filament_archive_swatch' / 'filament_archive_swatch.scad'
_source = SWATCH_SOURCE.read_text()


def swatch_dimension(name):
    return float(re.search(rf'^{name}\s*=\s*([\d.]+)\s*;', _source, re.M).group(1))


CARD_WIDTH = swatch_dimension('card_width')
CARD_HEIGHT = swatch_dimension('card_height')
CARD_THICKNESS = swatch_dimension('base_thickness')
CARD_COUNT = 20
UPRIGHT_WIDTH = CARD_HEIGHT
UPRIGHT_HEIGHT = CARD_WIDTH
SLOT_WIDTH = 2.8
SLOT_PITCH = 4.8
GUIDE_HEIGHT = 14.0
SIDE_ALLOWANCE = 2.0
FLOOR = 2.4
WALL = 1.8
OVERLAP = 6.0
COVER_CLEARANCE = 0.4  # Per side; provisional, not printed-fit evidence.
HEADROOM = 2.0
ROOF_THICKNESS = 2.4
INNER_WIDTH = UPRIGHT_WIDTH + 2 * SIDE_ALLOWANCE
TRAY_WIDTH = INNER_WIDTH + 2 * WALL
COVER_WIDTH = TRAY_WIDTH + 2 * (COVER_CLEARANCE + WALL)
ROOF_UNDERSIDE = FLOOR + UPRIGHT_HEIGHT + HEADROOM
CLOSED_HEIGHT = ROOF_UNDERSIDE + ROOF_THICKNESS
# A exposes 64 mm of each card; B needs a higher pivot to clear tall contents.
LOW_RIM = 18.4
FLIP_RIM = 44.4
LOW_END_SPACE = 2.0
FLIP_END_SPACE = 8.0
OPEN_ANGLE = 100.0


def slot_y(index):
    return (index - (CARD_COUNT - 1) / 2) * SLOT_PITCH


def inner_depth(end_space):
    return (CARD_COUNT - 1) * SLOT_PITCH + SLOT_WIDTH + 2 * end_space


def tray_depth(end_space):
    return inner_depth(end_space) + 2 * WALL


def cover_depth(end_space):
    return tray_depth(end_space) + 2 * (COVER_CLEARANCE + WALL)


def block(width, depth, height, z=0):
    return cq.Workplane('XY').box(width, depth, height, centered=(True, True, False)).translate((0, 0, z))


def rounded_block(width, depth, height, z=0, radius=4):
    return block(width, depth, height, z).edges('|Z').fillet(radius)


def tray(rim=LOW_RIM, end_space=LOW_END_SPACE):
    shell = rounded_block(TRAY_WIDTH, tray_depth(end_space), rim)
    cavity = rounded_block(INNER_WIDTH, inner_depth(end_space), rim, FLOOR, 1.5)
    shell = shell.cut(cavity)
    # One lower comb supports each card separately, even with only six loaded.
    guides = block(INNER_WIDTH, inner_depth(end_space), GUIDE_HEIGHT, FLOOR)
    for index in range(CARD_COUNT):
        slot = block(INNER_WIDTH + 1, SLOT_WIDTH, GUIDE_HEIGHT + 0.2, FLOOR).translate((0, slot_y(index), 0))
        guides = guides.cut(slot)
    return shell.union(guides)


def cover(rim=LOW_RIM, end_space=LOW_END_SPACE):
    bottom = rim - OVERLAP
    outer = rounded_block(COVER_WIDTH, cover_depth(end_space), CLOSED_HEIGHT - bottom, bottom, 6.2)
    cavity = rounded_block(TRAY_WIDTH + 2 * COVER_CLEARANCE, tray_depth(end_space) + 2 * COVER_CLEARANCE,
                           ROOF_UNDERSIDE - bottom + 0.1, bottom - 0.1, 4.4)
    hood = outer.cut(cavity)
    # Seat lands stay outside card width during both cover motions.
    for sx in (-1, 1):
        for sy in (-1, 1):
            land = block(3, 8, 2, rim).translate(
                (sx * (TRAY_WIDTH / 2 - 0.4), sy * (tray_depth(end_space) / 2 - 10), 0))
            hood = hood.union(land.intersect(outer))
    return hood


def card_reference():
    """SCAD outline and notch rotated notch-up; surface details omitted."""
    w, h = CARD_WIDTH, CARD_HEIGHT
    outline = (cq.Workplane('XZ')
               .moveTo(-w / 2 + 4, FLOOR).lineTo(w / 2 - 3, FLOOR)
               .radiusArc((w / 2, FLOOR + 3), -3)
               .lineTo(w / 2, FLOOR + h - 3).radiusArc((w / 2 - 3, FLOOR + h), -3)
               .lineTo(-w / 2 + 4, FLOOR + h).lineTo(-w / 2, FLOOR + h - 4)
               .lineTo(-w / 2, FLOOR + 4).close().extrude(CARD_THICKNESS / 2, both=True))
    notch = cq.Workplane('XZ').center(w / 2, FLOOR + h / 2).circle(8).extrude(CARD_THICKNESS + 1, both=True)
    return outline.cut(notch).rotate((0, 0, 0), (0, 1, 0), -90).translate(
        (FLOOR + h / 2, 0, FLOOR + w / 2))


def contents(sparse=False, selected=False):
    reference = card_reference()
    indices = (0, 3, 7, 11, 15, 19) if sparse else range(CARD_COUNT)
    return [reference.translate((0, slot_y(i), 10 if selected and i == 10 else 0)).val() for i in indices]


def pivot():
    return cover_depth(FLIP_END_SPACE) / 2 + 3, FLIP_RIM - OVERLAP


def pivot_envelopes():
    y, z = pivot()
    return [cq.Workplane('YZ', origin=(x - 3, y, z)).circle(3.5).extrude(6).val()
            for x in (-21.0, 21.0)]


def flip_cover(angle):
    y, z = pivot()
    return cover(FLIP_RIM, FLIP_END_SPACE).rotate((0, y, z), (1, y, z), -angle)


def closed():
    return cq.Compound.makeCompound([tray().val(), cover().val()])


def open_lift_off(sparse=True):
    hood = cover().rotate((0, 0, 0), (1, 0, 0), 180).translate((COVER_WIDTH + 12, 0, CLOSED_HEIGHT))
    return cq.Compound.makeCompound([tray().val(), hood.val(), *contents(sparse=sparse, selected=not sparse)])


def open_flip():
    return cq.Compound.makeCompound([tray(FLIP_RIM, FLIP_END_SPACE).val(), flip_cover(OPEN_ANGLE).val(),
                                     *pivot_envelopes(), *contents(sparse=True)])


if __name__ in ('__main__', '__cqgi__'):
    result = closed()
