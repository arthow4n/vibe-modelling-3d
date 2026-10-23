"""Uniform L20 cup/pad for the existing 34mm test chamber; mm."""
import cadquery as cq
from thin_gap_design import label_cut
from t_skin_design import label_backing
from model.tpu_damping_box import design as fixture
from model.tpu_damping_box.l20_standard import SKIN,CORE,TOTAL,TIE,PITCH,LAND,RIM_CAP,centres,floor_void

SIZE=34.
CLEAR=SIZE-2*TOTAL
POCKET=SIZE-2*SKIN
PAD_SIZE=POCKET-2*fixture.PAD_ALLOWANCE


def block(w,h,depth,*,x=0.,y=0.,z=0.):
    return cq.Workplane('XY').box(w,h,depth,centered=(True,True,False)).translate((x,y,z))


def cup():
    p=block(SIZE,SIZE,SIZE).cut(block(CLEAR,CLEAR,SIZE,z=TOTAL))
    # Matching 2mm lid pad nests in this top seat; no extra preload skin.
    p=p.cut(block(POCKET,POCKET,TOTAL+1,z=SIZE-TOTAL))
    p=p.cut(floor_void(SIZE,SIZE))
    low=SKIN;high=SIZE-TOTAL-RIM_CAP
    normal=-SIZE/2+SKIN+CORE/2
    channel=block(CORE,SIZE-2*LAND,high-low,y=0,x=normal,z=low)
    vertical=tuple((low+high)/2+z for z in centres(high-low,end_margin=1.))
    ties=cq.Compound.makeCompound([
        block(CORE+.2,TIE,TIE,x=normal,y=a,z=z-TIE/2).val()
        for a in centres(SIZE,end_margin=LAND) for z in vertical])
    for angle in (0,90,180,270):
        p=p.cut(channel.cut(ties).rotate((0,0,0),(0,0,1),angle))
    # The ID is confined to a solid corner seat, outside the active air panel.
    return p.union(label_backing(SIZE,TOTAL)).cut(label_cut('L20',SIZE,.2)).clean()


def pad_print():
    p=block(PAD_SIZE,PAD_SIZE,TOTAL).cut(floor_void(PAD_SIZE,PAD_SIZE))
    return p.union(label_backing(PAD_SIZE,TOTAL)).cut(label_cut('L20',PAD_SIZE,.2)).clean()


def pad_closed():
    return pad_print().rotate((0,0,0),(1,0,0),180).translate((0,0,fixture.FLOOR+SIZE))


def layout():
    return (cq.Assembly(name='uniform_L20_cup_and_matching_pad')
        .add(cup(),name='uniform_L20_cup',loc=cq.Location((60,60,0)))
        .add(pad_print(),name='uniform_L20_pad',loc=cq.Location((102,60,0))))
