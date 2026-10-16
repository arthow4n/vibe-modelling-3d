"""Consequential thin-sandwich checks against the reused enclosure."""
import cadquery as cq
import design as b
import thin_design as t
from checks import contained, no_overlap


def candidate(name):
    return b.body(),t.cup(name),t.pad_closed(name)


def fit(name,parts):
    v=t.variant_named(name)
    body,cup,pad=parts
    placed=cup.translate((0,0,b.FLOOR))
    no_overlap(placed,body)
    no_overlap(placed,pad)
    no_overlap(pad,body)
    for travel in (0,8,20,36):
        no_overlap(placed.translate((0,0,travel)),body)
    for travel in (0,4,20,36):
        no_overlap(pad.translate((0,0,travel)),placed)
        no_overlap(pad.translate((0,0,travel)),body)
    space=b.block(v.clear,v.clear,v.clear,b.FLOOR+v.thickness)
    no_overlap(space,placed)
    no_overlap(space,pad)
    # 12 mm stock-nut proxy can traverse the expanded cavity on every axis.
    for axis in range(3):
        for shift in (-(v.clear-12)/2,0,(v.clear-12)/2):
            xyz=[0,0,b.FLOOR+17]
            xyz[axis]+=shift
            probe=b.block(12,12,12,-6).translate(tuple(xyz))
            no_overlap(probe,placed)
            no_overlap(probe,pad)


def skins(name,parts):
    v=t.variant_named(name)
    _,cup,pad=parts
    contained(b.block(v.clear,v.clear,v.skin,v.thickness-v.skin),cup)
    wall=b.block(v.skin,v.clear,v.clear,v.thickness).translate((-(v.clear+v.skin)/2,0,0))
    for angle in (0,90,180,270):
        contained(wall.rotate((0,0,0),(0,0,1),angle),cup)
    contained(b.block(v.clear,v.clear,v.skin,b.FLOOR+b.CUP_HEIGHT-v.thickness),pad)
    no_overlap(b.block(v.clear,v.clear,v.clear,v.thickness),cup)
    no_overlap(b.block(v.clear,v.clear,v.clear,b.FLOOR+v.thickness),pad)


def cores(name,parts):
    v=t.variant_named(name)
    _,cup,_=parts
    pad=t.pad_print(name)
    # Central air and a chevron mid-depth material sample on all six faces.
    air=b.block(.2,2,.1,v.backing+v.core/2-.05)
    material=b.block(.1,2,.1,v.backing+v.core/2-.05).translate((-1.8+v.amplitude,0,0))
    no_overlap(air,cup)
    contained(material,cup)
    no_overlap(air.translate((0,0,b.PAD_PRELOAD)),pad)
    contained(material.translate((0,0,b.PAD_PRELOAD)),pad)
    inner=b.CUP_SIZE/2-v.backing
    air=b.block(.1,.2,2,18).translate((-inner+v.core/2,0,0))
    material=b.block(.1,.1,2,18).translate((-inner+v.core/2,-1.8+v.amplitude,0))
    for angle in (0,90,180,270):
        no_overlap(air.rotate((0,0,0),(0,0,1),angle),cup)
        contained(material.rotate((0,0,0),(0,0,1),angle),cup)


def labels(name,parts):
    _,cup,_=parts
    pad=t.pad_print(name)
    glyph=b.label_cut(name,.1)
    for part in (cup,pad):
        no_overlap(glyph,part)
        contained(glyph.translate((0,0,.21)),part)


def selection():
    assert t.SELECTED_NAMES==('I30','I24','I20')
    expected={f'{kind}_{name}' for name in t.SELECTED_NAMES for kind in ('cup','pad')}
    assert {row[0] for row in t.placements()}==expected
    assert len(t.placements())==6
    assert [t.variant_named(n).thickness for n in t.SELECTED_NAMES]==[3.,2.4,2.]
    assert all(t.variant_named(n).clear>=26 for n in t.SELECTED_NAMES)
