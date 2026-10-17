"""Local material/air witnesses: manufacturing geometry, never damping proof."""
import surface_design as d
from checks import contained, no_overlap


def geometry(name, part):
    v = d.variant_named(name)
    # Complete test field: continuous skins, planar ceiling and filled edges.
    contained(d.block(d.FIELD_X, d.FIELD_Y, d.BACKING, cy=d.FIELD_CY), part)
    contained(d.block(d.FIELD_X, d.FIELD_Y, v.skin, d.BACKING+d.CORE,
                      cy=d.FIELD_CY), part)
    no_overlap(d.block(d.FIELD_X, d.FIELD_Y, .1, v.thickness, cy=d.FIELD_CY), part)
    for x in (-14.3, 14.3):
        contained(d.block(1, 27, v.thickness, cx=x), part)
    contained(d.block(27, 1, v.thickness, cy=14.3), part)
    # Recessed label can enter the top 0.2 mm of the solid label band.
    contained(d.block(27, 1, v.thickness-d.LABEL_DEPTH, cy=-14.3), part)
    # Label is outside test field; source floor and no protruding lettering.
    glyph = d.label_cut(name)
    no_overlap(glyph, part)
    contained(glyph.translate((0, 0, -d.LABEL_DEPTH)), part)
    for x in d.centres(d.FIELD_X, v.pitch):
        contained(d.block(.7, d.FIELD_Y-.1, d.CORE, d.BACKING, x, d.FIELD_CY), part)
    if v.pattern == 'solid':
        contained(d.block(d.FIELD_X, d.FIELD_Y, d.CORE, d.BACKING, cy=d.FIELD_CY), part)
    else:
        # Witness spans nearly the entire core depth; intentionally between
        # X and Y ribs even for the grid, away from solid edge/label bands.
        # Shoulder variant has the smallest upper gap: still 2.3 mm nominal.
        gap = v.pitch - d.WEB - (1.2 if v.pattern == 'shoulders' else 0)
        for x in (-(v.pitch/2), v.pitch/2):
            no_overlap(d.block(gap-.1, 1.2, d.CORE-.04, d.BACKING+.02,
                               x, d.FIELD_CY+v.pitch/2), part)
        if v.pattern == 'shoulders':
            # Growth really exists beneath roof, rather than a renamed rib.
            contained(d.block(.3, 5, .1, d.BACKING+d.CORE-.1,
                              d.WEB/2+.2, d.FIELD_CY), part)
    assert len(d.placements()) == 8
    assert tuple(n for n, _ in d.placements()) == tuple(f'F{i}' for i in range(8))
