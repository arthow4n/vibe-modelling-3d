"""Solid-control coverage using the existing fixture and geometric witnesses."""
import json
from functools import cache
from pathlib import Path
from execution.identity import digest
from product_verification import (Plan, Question as Q, DesignDecision,
    assertion_check, protect_recorded_intent)
from checks import contained, no_overlap
import design as f
import support_design as support
import solid_design as d

ROOT = Path(__file__).resolve().parent
SOURCE = 'README.md#solid-c12c16-controls--2026-10-20'


def fit(name, parts):
    v = d.variant_named(name)
    body, cup, _, pad = parts
    placed = cup.translate((0,0,f.FLOOR))
    for travel in (0,8,20,36):
        no_overlap(placed.translate((0,0,travel)),body)
        no_overlap(pad.translate((0,0,travel)),body)
        no_overlap(pad.translate((0,0,travel)),placed)
    for part in (placed,pad):
        no_overlap(part,f.lid_closed().translate((0,0,support.PRELOAD)))
    no_overlap(placed,pad)
    cavity = f.block(v.clear,v.clear,v.clear,v.thickness)
    no_overlap(cavity,cup)
    no_overlap(cavity.translate((0,0,f.FLOOR)),pad)
    assert abs((v.pocket-v.pad_size)/2-.2)<1e-8


def solid(name, parts):
    v = d.variant_named(name)
    _, cup, pad, _ = parts
    # Complete horizontal interiors above the deliberate exterior engraving.
    # These witnesses reject any hidden channels, posts or hollow infill CAD.
    contained(f.block(34,34,v.thickness-support.LABEL_DEPTH,support.LABEL_DEPTH),cup)
    contained(f.block(v.pad_size,v.pad_size,
        v.thickness+support.PRELOAD-support.LABEL_DEPTH,support.LABEL_DEPTH),pad)
    full_wall = support.block(v.thickness,34,v.wall_height-v.thickness,
        v.thickness,-17+v.thickness/2)
    rim = support.block((34-v.pocket)/2,34,34,cx=-(34+v.pocket)/4)
    for angle in (0,90,180,270):
        contained(full_wall.rotate((0,0,0),(0,0,1),angle),cup)
        contained(rim.rotate((0,0,0),(0,0,1),angle),cup)


def labels(name, parts):
    _,cup,pad,_ = parts
    glyph = d.label_cut(name,.1)
    assert glyph.val().BoundingBox().xlen<=28
    assert glyph.val().BoundingBox().ylen>=8
    for part in (cup,pad):
        no_overlap(glyph,part)
        contained(glyph.translate((0,0,support.LABEL_DEPTH)),part)


def publication(name):
    native = json.loads((ROOT/f'notes/solid_{name}_final.json').read_text())
    row = json.loads((ROOT/'notes/solid_path_review.json').read_text())['variants'][name]
    assert native['geometry']['valid'] and all(e['ok'] for e in native['exports'])
    assert native['slice']['ok'] and row['checks_passed']
    assert native['slice']['input_sha256']==digest(ROOT/f'solid_{name}.stl')
    assert native['reuse']['artifact_identity']==row['artifact_identity']
    assert all(digest(ROOT/file)==sha for file,sha in row['source_sha256'].items())
    assert all(digest(ROOT/file)==sha for file,sha in row['export_sha256'].items())


def make_solid_plan(name, requirements, root):
    v = d.variant_named(name)
    protect_recorded_intent(root,requirements)
    scope = {'variant':name,'phase':'solid-controls','material':'TPU-uncalibrated',
             'lining_mm':v.thickness,'layer_mm':.2,'wall_generator':'classic'}
    @cache
    def parts():
        return f.body(),d.cup(name),d.pad_print(name),d.pad_closed(name)
    questions = (
        Q('fit','study.enclosure','Cup/pad fit the existing fixture and straight swap path; .2 mm axial pad squeeze is intentional.','CAD'),
        Q('solid','solid.two','Walls, floor and lid pad contain solid material without hidden structures; nominal lining is 1.2 or 1.6 mm.','CAD'),
        Q('coverage','study.coverage','Solid TPU covers all six cavity faces.','CAD'),
        Q('flat','study.flat','All contact faces are flat; IDs are confined to exterior recesses.','CAD'),
        Q('labels','solid.two','Both parts carry the matching large C12/C16 ID and SOLID subtitle.','CAD'),
        Q('publication','solid.two','Matching current exports slice with ordinary Classic, thin-wall detection off and 100% material fill; all upright layers retain continuous walls.','slicer'),
        Q('integrity','support.integrity','Printed solid controls survive installation/removal without tears or splitting.','physical'),
        Q('quietness','study.quiet_priority','Compare C12/C16 with the printed R2 pairs and S16 using the same shell/nut.','physical'),
    )
    groups = (
        ('solid-fit',(('study.enclosure','fit'),),lambda:fit(name,parts())),
        ('solid-material',(('solid.two','solid'),('study.coverage','coverage'),('study.flat','flat')),lambda:solid(name,parts())),
        ('solid-labels',(('solid.two','labels'),),lambda:labels(name,parts())),
        ('solid-publication',(('solid.two','publication'),),lambda:publication(name)),
    )
    checks = tuple(assertion_check(id,targets,run,'solid_verification.py / solid_design.py',scope)
                   for id,targets,run in groups)
    return Plan(name,requirements,scope,checks,(),questions=questions,
        decisions=(DesignDecision('solid-interface',
            'Same 34 mm envelope, .5 mm upper pocket rim and 32.6 mm pad as R2. '
            'Lining is 1.2/1.6 mm; pads add .2 mm squeeze. Labels recess .2 mm. '
            'No CAD core; common 100% fill Classic TPU process.',SOURCE),))
