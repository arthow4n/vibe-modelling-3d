"""Fit, both skins and full channel witnesses for S16/S12."""
import design as b
import skin_design as s
from checks import contained,no_overlap


def candidate(name):
    return b.body(),s.cup(name),s.pad_closed(name)


def fit(name,parts):
    v=s.variant_named(name)
    body,cup,pad=parts
    placed=cup.translate((0,0,b.FLOOR))
    no_overlap(placed,body);no_overlap(placed,pad);no_overlap(pad,body)
    for dz in (0,8,20,36):
        no_overlap(placed.translate((0,0,dz)),body)
        no_overlap(pad.translate((0,0,dz)),body)
        no_overlap(pad.translate((0,0,dz)),placed)
    space=b.block(v.clear,v.clear,v.clear,b.FLOOR+v.thickness)
    no_overlap(space,placed);no_overlap(space,pad)
    for axis in range(3):
        for shift in (-(v.clear-12)/2,0,(v.clear-12)/2):
            xyz=[0,0,b.FLOOR+17];xyz[axis]+=shift
            probe=b.block(12,12,12,-6).translate(tuple(xyz))
            no_overlap(probe,placed);no_overlap(probe,pad)


def skins(name,parts):
    v=s.variant_named(name)
    _,cup,pad=parts
    contained(b.block(v.clear,v.clear,v.skin,v.thickness-v.skin),cup)
    wall=b.block(v.skin,v.clear,v.clear,v.thickness).translate((-(v.clear+v.skin)/2,0,0))
    outer=b.block(v.backing,34,34).translate((-(34-v.backing)/2,0,0))
    for angle in (0,90,180,270):
        contained(wall.rotate((0,0,0),(0,0,1),angle),cup)
        contained(outer.rotate((0,0,0),(0,0,1),angle),cup)
    # Recesses are 0.1 mm deep, leaving a continuous 0.3 mm floor backing.
    contained(b.block(34,34,v.backing-s.LABEL_DEPTH,s.LABEL_DEPTH),cup)
    contained(b.block(v.clear,v.clear,v.skin,b.FLOOR+34-v.thickness),pad)
    printed=s.pad_print(name)
    contained(b.block(v.pad_size,v.pad_size,v.backing+v.preload-s.LABEL_DEPTH,s.LABEL_DEPTH),printed)
    no_overlap(b.block(v.clear,v.clear,v.clear,v.thickness),cup)
    no_overlap(b.block(v.clear,v.clear,v.clear,b.FLOOR+v.thickness),pad)


def cores(name,parts):
    v=s.variant_named(name)
    _,cup,_=parts
    printed=s.pad_print(name)
    # Broad channel volume between ribs at X=0 and X=4.4, not just one air point.
    air=b.block(3.3,12,v.core-.04,v.backing+.02).translate((2.2,0,0))
    no_overlap(air,cup);no_overlap(air.translate((0,0,v.preload)),printed)
    web=b.block(.4,12,v.core,v.backing)
    contained(web,cup);contained(web.translate((0,0,v.preload)),printed)
    side_air=air.rotate((0,0,0),(1,1,1),120).translate((-17,0,18))
    side_web=web.rotate((0,0,0),(1,1,1),120).translate((-17,0,18))
    for angle in (0,90,180,270):
        no_overlap(side_air.rotate((0,0,0),(0,0,1),angle),cup)
        contained(side_web.rotate((0,0,0),(0,0,1),angle),cup)


def labels(name,parts):
    _,cup,_=parts
    glyph=s.label_cut(name,.04)
    bounds=glyph.val().BoundingBox()
    assert bounds.ylen>=8 and bounds.xlen<=28
    for part in (cup,s.pad_print(name)):
        no_overlap(glyph,part)
        contained(glyph.translate((0,0,.15)),part)


def selection():
    assert s.SELECTED_NAMES==('S16','S12')
    assert len(s.placements())==4
    assert {p[0] for p in s.placements()}=={f'{kind}_{n}' for n in s.SELECTED_NAMES for kind in ('cup','pad')}
    assert [s.variant_named(n).thickness for n in s.SELECTED_NAMES]==[1.6,1.2]
    for name in s.SELECTED_NAMES:
        v=s.variant_named(name)
        assert v.skin>=.4 and v.backing>=.4 and v.web>=.9 and v.core>=.4-1e-9
        assert s.PITCH-v.web>=3.5
