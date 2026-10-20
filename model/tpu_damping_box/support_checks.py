"""Intent-driven checks of support experiments, reusing established CAD witnesses."""
import json
from pathlib import Path
import cadquery as cq
from execution.identity import digest
from checks import contained, no_overlap
import design as f
import support_design as d

ROOT = Path(__file__).resolve().parent


def parts(name):
    return f.body(), d.cup(name), d.pad_print(name), d.pad_closed(name)


def fit(name, parts):
    v = d.variant_named(name)
    body, cup, _, pad = parts
    placed = cup.translate((0, 0, f.FLOOR))
    for travel in (0, 8, 20, 36):
        no_overlap(placed.translate((0, 0, travel)), body)
        no_overlap(pad.translate((0, 0, travel)), body)
        no_overlap(pad.translate((0, 0, travel)), placed)
    # Constant square fixture bore and constant cup envelope exclude an
    # intermediate rigid blocker, but do not predict insertion force/damage.
    for part in (placed, pad):
        no_overlap(part, f.lid_closed().translate((0,0,d.PRELOAD)))
    no_overlap(placed, pad)
    space = d.block(v.clear, v.clear, v.clear, v.thickness)
    no_overlap(space, cup)
    no_overlap(space.translate((0, 0, f.FLOOR)), pad)
    assert abs((f.CUP_SIZE + 2*f.INSERT_ALLOWANCE - f.CUP_SIZE)/2 - .2) < 1e-8
    assert abs((f.CUP_SIZE-2*v.wall_skin-v.pad_size)/2 - .2) < 1e-8


def skins(name, parts):
    v = d.variant_named(name)
    _, cup, pad, _ = parts
    contained(d.block(v.clear, v.clear, d.FLOOR_SKIN,
                      v.thickness-d.FLOOR_SKIN), cup)
    contained(d.block(34, 34, d.FLOOR_SKIN-d.LABEL_DEPTH, d.LABEL_DEPTH), cup)
    contained(d.block(v.pad_size, v.pad_size, d.FLOOR_SKIN,
                      v.thickness+d.PRELOAD-d.FLOOR_SKIN), pad)
    contained(d.block(v.pad_size, v.pad_size,
                      d.FLOOR_SKIN+d.PRELOAD-d.LABEL_DEPTH, d.LABEL_DEPTH), pad)
    wall = d.block(v.wall_skin, v.clear, v.wall_height-v.thickness,
                   v.thickness, -(v.clear+v.wall_skin)/2)
    backing = d.block(v.wall_skin, 34, 34, cx=-(34-v.wall_skin)/2)
    for angle in (0, 90, 180, 270):
        contained(wall.rotate((0,0,0),(0,0,1),angle), cup)
        contained(backing.rotate((0,0,0),(0,0,1),angle), cup)
    # Full cavity is empty: skins and labels cannot protrude into contact space.
    no_overlap(d.block(v.clear,v.clear,v.clear,v.thickness), cup)


def cores(name, parts):
    v = d.variant_named(name)
    _, cup, pad, _ = parts
    # Air away from every support, through both horizontal panels.
    air = d.block(.3,.3,v.core-.04,d.FLOOR_SKIN+.02,2.2,2.2)
    no_overlap(air,cup)
    no_overlap(air.translate((0,0,d.PRELOAD)),pad)
    core_x = -17 + v.wall_skin + v.wall_core/2
    wall_air = d.block(v.wall_core-.04,.3,20,5,core_x,2.2)
    corner_air = d.block(.08,.08,15,5,-17+v.wall_skin+.2,-17+v.wall_skin+.2)
    for angle in (0,90,180,270):
        no_overlap(wall_air.rotate((0,0,0),(0,0,1),angle),cup)
        no_overlap(corner_air.rotate((0,0,0),(0,0,1),angle),cup)
    if v.topology == 'ties':
        for z in d.tie_heights(v):
            tie = d.block(v.wall_core,v.tie_size,v.tie_size,z-v.tie_size/2,core_x)
            for angle in (0,90,180,270):
                contained(tie.rotate((0,0,0),(0,0,1),angle),cup)
        # Same tangent, between height rows: excludes full-height ribs.
        gap = d.block(v.wall_core-.04,v.tie_size-.04,.6,5.1,core_x)
        for angle in (0,90,180,270):
            no_overlap(gap.rotate((0,0,0),(0,0,1),angle),cup)
        post = d.block(v.tie_size,v.tie_size,v.core,d.FLOOR_SKIN)
        contained(post,cup)
        contained(post.translate((0,0,d.PRELOAD)),pad)
    else:
        # An open square INSIDE the loop, not just air between solid plugs.
        opening = v.frame_opening
        hole = d.block(opening-.04,opening-.04,20,5,core_x)
        rail = d.block(v.tie_size,v.frame_opening+2*d.FRAME_CROSS_WEB,20,5,-17+v.wall_skin+v.tie_size/2)
        cross = d.block(v.wall_core,d.FRAME_CROSS_WEB,20,5,core_x,
                        (v.frame_opening+d.FRAME_CROSS_WEB)/2)
        for angle in (0,90,180,270):
            no_overlap(hole.rotate((0,0,0),(0,0,1),angle),cup)
            contained(rail.rotate((0,0,0),(0,0,1),angle),cup)
            contained(cross.rotate((0,0,0),(0,0,1),angle),cup)
        floor_hole=d.block(opening-.04,5,opening-.04,
                         d.FLOOR_SKIN+(v.core-opening)/2+.02)
        no_overlap(floor_hole,cup)
        no_overlap(floor_hole.translate((0,0,d.PRELOAD)),pad)


def labels(name, parts):
    _,cup,pad,_=parts
    glyph=d.label_cut(name,.1)
    assert glyph.val().BoundingBox().ylen >= 8
    assert glyph.val().BoundingBox().xlen <= 28
    for part in (cup,pad):
        no_overlap(glyph,part)
        contained(glyph.translate((0,0,.2)),part)
    assert tuple(row[0] for row in d.placements(name)) == (f'cup_{name}',f'pad_{name}')


def publication(name):
    native=json.loads((ROOT/f'notes/support_{name}_final.json').read_text())
    paths=json.loads((ROOT/'notes/support_path_review.json').read_text())
    assert native['geometry']['valid'] and all(e['ok'] for e in native['exports'])
    assert native['slice']['ok']
    assert native['slice']['input_sha256'] == digest(ROOT/f'support_{name}.stl')
    row=paths['variants'][name]
    assert row['artifact_identity']==native['reuse']['artifact_identity']
    assert all(digest(ROOT/file)==sha for file,sha in row['source_sha256'].items())
    assert all(digest(ROOT/file)==sha for file,sha in row['export_sha256'].items())
    assert row['checks_passed'], row


def classic(name):
    paths=json.loads((ROOT/'notes/support_path_review.json').read_text())
    row=paths['variants'][name]
    assert row['effective_process']['wall_generator']=='classic'
    assert all(digest(ROOT/file)==sha for file,sha in row['source_sha256'].items())
