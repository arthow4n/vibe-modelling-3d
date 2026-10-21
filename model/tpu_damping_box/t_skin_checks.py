"""Whole-pair intent checks for T skin variants; no physical promotion."""
import json
from pathlib import Path
from execution.identity import digest
from checks import contained, no_overlap
import t_skin_design as d

ROOT=Path(__file__).resolve().parent


def parts(name):
    return d.fixture.body(),d.cup(name),d.pad_print(name),d.pad_closed(name)


def fit(name,parts):
    v=d.variant_named(name)
    body,cup,_,pad=parts
    placed=cup.translate((0,0,d.fixture.FLOOR))
    for travel in (0,8,20,36):
        no_overlap(placed.translate((0,0,travel)),body)
        no_overlap(pad.translate((0,0,travel)),body)
        no_overlap(pad.translate((0,0,travel)),placed)
    no_overlap(pad,placed)
    for p in (placed,pad): no_overlap(p,d.fixture.lid_closed().translate((0,0,d.PRELOAD)))
    no_overlap(d.block(v.clear,v.clear,30.8,1.6),cup)
    assert abs((v.pocket-v.pad_size)/2-.2)<1e-8


def skins(name,parts):
    v=d.variant_named(name);_,cup,pad,_=parts
    contained(d.block(34,34,.2,.2),cup)
    contained(d.block(v.clear,v.clear,.4,1.2),cup)
    contained(d.block(v.pad_size,v.pad_size,.4,.2),pad)
    contained(d.block(v.pad_size,v.pad_size,.4,1.4),pad)
    # The intentional bed-side label recess is checked separately over its solid seat.
    backing=d.block(v.skin,34,34-d.LABEL_DEPTH,d.LABEL_DEPTH,-17+v.skin/2)
    inner=d.block(v.skin,v.clear,30.4,1.6,-17+v.wall-v.skin/2)
    for a in (0,90,180,270):
        contained(backing.rotate((0,0,0),(0,0,1),a),cup)
        contained(inner.rotate((0,0,0),(0,0,1),a),cup)


def cores(name,parts):
    v=d.variant_named(name);_,cup,pad,_=parts
    nx=-17+v.skin+.3
    air=d.block(.5,.3,20,6,nx,2.2)
    tie=d.block(.6,.8,.8,2.8,nx,0)
    off=d.block(.5,.3,.5,4.1,nx,0)
    land=d.block(.6,.3,20,6,nx,14)
    for a in (0,90,180,270):
        no_overlap(air.rotate((0,0,0),(0,0,1),a),cup)
        no_overlap(off.rotate((0,0,0),(0,0,1),a),cup)
        contained(tie.rotate((0,0,0),(0,0,1),a),cup)
        contained(land.rotate((0,0,0),(0,0,1),a),cup)
    for p,z,size in ((cup,.4,34),(pad,.6,v.pad_size)):
        for sx in (-1,1):
            for sy in (-1,1):
                contained(d.block(.3,.3,.76,z+.02,sx*(size/2-3),sy*(size/2-3)),p)
        no_overlap(d.block(.3,.3,.76,z+.02,2.2,2.2),p)
        contained(d.block(.8,.8,.8,z),p)


def labels(name,parts):
    v=d.variant_named(name);_,cup,pad,_=parts
    for size,p in ((34,cup),(v.pad_size,pad)):
        glyph=d.label_cut(name,size,.1)
        no_overlap(glyph,p)
        contained(glyph.translate((0,0,.2)),p)
        contained(d.label_backing(size,1.,.2),p)
        # Protect the reserved land's complete backing, not just glyph endpoints.
        assert abs(d.LABEL_DEPTH-.2)<1e-8 and d.LABEL_PATCH==(10.,6.5)


def publication(name):
    r=json.loads((ROOT/f'notes/t_skin/{name}_final.json').read_text())
    paths=json.loads((ROOT/'notes/t_skin/paths.json').read_text())
    assert r['geometry']['valid'] and all(x['ok'] for x in r['exports']) and r['slice']['ok']
    row=paths['variants'][name]
    assert row['artifact_identity']==r['reuse']['artifact_identity']
    assert row['input_sha256']==r['slice']['input_sha256']==digest(ROOT/f't_skin_{name}_m1.stl')
    assert all(digest(ROOT/f)==h for f,h in row['source_sha256'].items())
    assert all(digest(ROOT/f)==h for f,h in row['export_sha256'].items())
    assert paths['reviewer_sha256']==digest(ROOT/'review_t_skin.py')
    assert all(digest(ROOT/f)==h for f,h in row['profile_sha256'].items())
    assert row['checks_passed']
