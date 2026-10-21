"""Geometry and publication checks for the thinner T08-gap experiment."""
import json
from pathlib import Path
from execution.identity import digest
from checks import contained,no_overlap
import thin_gap_design as d

ROOT=Path(__file__).resolve().parent
b=d.base


def parts(name):return b.fixture.body(),d.cup(name),d.pad_print(name),d.pad_closed(name)


def geometry(name,parts):
    v=d.variant_named(name);body,cup,pad,closed=parts;placed=cup.translate((0,0,b.fixture.FLOOR))
    for travel in (0,8,20,36):
        no_overlap(placed.translate((0,0,travel)),body)
        no_overlap(closed.translate((0,0,travel)),body)
        no_overlap(closed.translate((0,0,travel)),placed)
    for p in (placed,closed):no_overlap(p,b.fixture.lid_closed().translate((0,0,b.PRELOAD)))
    no_overlap(b.block(v.clear,v.clear,30.8,1.6),cup)
    no_overlap(placed,closed)
    for w in (b.block(34,34,.2,.2),b.block(v.clear,v.clear,.4,1.2)):contained(w,cup)
    for w in (b.block(32,32,.4,.2),b.block(32,32,.4,1.4)):contained(w,pad)
    nx=-17+v.skin+v.gap/2
    for a in (0,90,180,270):
        material=[b.block(v.skin,34,33.8,.2,-17+v.skin/2),
                  b.block(v.skin,v.clear,30.4,1.6,-17+v.wall-v.skin/2),
                  b.block(v.gap,.8,.8,2.8,nx,0),b.block(v.gap,.3,20,6,nx,14)]
        for w in material:contained(w.rotate((0,0,0),(0,0,1),a),cup)
        for w in (b.block(v.gap-.04,.3,20,6,nx,2.2),b.block(v.gap-.04,.3,.5,4.1,nx,0)):
            no_overlap(w.rotate((0,0,0),(0,0,1),a),cup)
    for p,size,z in ((cup,34,.4),(pad,32,.6)):
        no_overlap(b.block(.3,.3,.76,z+.02,2.2,2.2),p);contained(b.block(.8,.8,.8,z),p)
        for sx in (-1,1):
            for sy in (-1,1):contained(b.block(.3,.3,.76,z+.02,sx*(size/2-3),sy*(size/2-3)),p)
        glyph=d.label_cut(name,size,.1);no_overlap(glyph,p);contained(glyph.translate((0,0,.2)),p)
        contained(b.label_backing(size,1.,.2),p)


def publication(name):
    native=json.loads((ROOT/f'notes/thin_gap/{name}_final.json').read_text())
    paths=json.loads((ROOT/'notes/thin_gap/paths.json').read_text());r=paths['variants'][name]
    assert native['geometry']['valid'] and all(x['ok'] for x in native['exports']) and native['slice']['ok']
    assert r['artifact_identity']==native['reuse']['artifact_identity']
    assert r['input_sha256']==native['slice']['input_sha256']==digest(ROOT/f'thin_gap_{name}.stl')
    for key in ('source_sha256','export_sha256','profile_sha256'):
        assert all(digest(ROOT/p)==h for p,h in r[key].items())
    assert paths['reviewer_sha256']==digest(ROOT/'review_thin_gap.py') and r['checks_passed']
