"""Twenty swatches standing on their long edge, protected by a deep cap.

The front press-release interface is an unchanged translated lift-box interface.
Its source is explicitly reused; that model's numerical limitations still apply.
"""
from pathlib import Path
import importlib.util
import cadquery as cq

_path=Path(__file__).resolve().parents[1]/'filament_swatch_lift_box/components.py'
_spec=importlib.util.spec_from_file_location('lift_box_closure',_path)
closure=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(closure)
CARD_X,CARD_Y,CARD_T=closure.CARD_X,closure.CARD_Y,closure.CARD_T
SWATCH_SOURCE=closure.SWATCH_SOURCE
COUNT=20
INNER_X,INNER_Y=CARD_X+6,COUNT*CARD_T+16
FLOOR,WALL,FIT=2.4,1.6,.35
RIM_Z=32.
LID_T=2.4
ROOF_Z=FLOOR+CARD_Y+2.4
LID_TOP=ROOF_Z+LID_T
SHIFT_Y=1.8
SHIFT_Z=RIM_Z-closure.RIM_Z
ROOT_Z,HEAD_Z=closure.ROOT_Z+SHIFT_Z,closure.HEAD_Z+SHIFT_Z
ARM_Y,HEAD_Y=closure.ARM_Y+SHIFT_Y,closure.HEAD_Y+SHIFT_Y
ARM_L,ARM_W,ARM_T=closure.ARM_L,closure.ARM_W,closure.ARM_T
BUTTON_FRONT=closure.BUTTON_FRONT+SHIFT_Y
FRONT_Y=closure.OUT_Y/2+SHIFT_Y
BACK_Y=-INNER_Y/2-WALL
OUT_X=INNER_X+2*WALL
OUT_Y=FRONT_Y-BACK_Y
CENTER_Y=(FRONT_Y+BACK_Y)/2
BODY_R=2.6
CAP_R=BODY_R+FIT+WALL
CAP_BOTTOM=RIM_Z-10
# Upper cavity boundary and outboard telescoping shield. The shield overlaps
# the body without intruding into the card envelope or opening the cavity.
SEAL_X=OUT_X
SEAL_Y=INNER_Y+WALL+closure.SNAP_LINER
SEAL_CENTER_Y=(closure.SNAP_LINER-WALL)/2
SHIELD_BOTTOM=RIM_Z-4
LAYOUT_OFFSET=OUT_Y+14

block=closure.block
def rounded(dx,dy,dz,z=0,r=BODY_R,cy=CENTER_Y):
    return closure.rounded_box(dx,dy,dz,z,r).translate((0,cy,0))

def snap_arm():
    return closure.snap_arm().translate((0,SHIFT_Y,SHIFT_Z))

def body():
    shell=rounded(OUT_X,OUT_Y,RIM_Z).cut(rounded(INNER_X,INNER_Y,RIM_Z+2,FLOOR,r=1,cy=0))
    pocket=block(-14,INNER_Y/2+closure.SNAP_LINER,ROOT_Z,28,
        FRONT_Y-1.2-(INNER_Y/2+closure.SNAP_LINER),RIM_Z-ROOT_Z+1)
    window=block(-5.5,FRONT_Y-1.7,HEAD_Z-4,11,4,8)
    upper=block(-14,FRONT_Y-1.2,RIM_Z-10,28,3,RIM_Z)
    shell=shell.cut(pocket).cut(window).cut(upper)
    groove=rounded(SEAL_X+2*(FIT+WALL+FIT),SEAL_Y+2*(FIT+WALL+FIT),4.2,
        SHIELD_BOTTOM,r=BODY_R+FIT+WALL+FIT,cy=SEAL_CENTER_Y)
    groove=groove.cut(rounded(SEAL_X,SEAL_Y,4.4,SHIELD_BOTTOM-.1,r=BODY_R,cy=SEAL_CENTER_Y))
    return shell.cut(groove).union(snap_arm())

def lid():
    roof=rounded(OUT_X+2*(FIT+WALL),OUT_Y+2*(FIT+WALL),LID_T,ROOF_Z,r=CAP_R).edges('>Z').chamfer(.3)
    outer=rounded(OUT_X+2*(FIT+WALL),OUT_Y+2*(FIT+WALL),ROOF_Z-CAP_BOTTOM,CAP_BOTTOM,r=CAP_R)
    outer=outer.cut(rounded(OUT_X+2*FIT,OUT_Y+2*FIT,ROOF_Z-CAP_BOTTOM+.2,CAP_BOTTOM-.1,r=BODY_R+FIT))
    edges=outer.faces('<Z').val().innerWires()[0].Edges()
    outer=outer.newObject(edges).chamfer(1.2)
    shield=rounded(SEAL_X+2*(FIT+WALL),SEAL_Y+2*(FIT+WALL),ROOF_Z-SHIELD_BOTTOM,
        SHIELD_BOTTOM,r=CAP_R,cy=SEAL_CENTER_Y)
    shield=shield.cut(rounded(SEAL_X+2*FIT,SEAL_Y+2*FIT,ROOF_Z-SHIELD_BOTTOM+.2,
        SHIELD_BOTTOM-.1,r=BODY_R+FIT,cy=SEAL_CENTER_Y))
    cap=roof.union(outer).union(shield)
    cap=cap.cut(block(-5.5,FRONT_Y+.2,HEAD_Z-4,11,5,8))
    cap=cap.union(closure.lid_cam().translate((0,SHIFT_Y,SHIFT_Z)).intersect(
        rounded(OUT_X+2*(FIT+WALL),OUT_Y+2*(FIT+WALL),10,CAP_BOTTOM,r=CAP_R)))
    y,z=FRONT_Y+FIT,HEAD_Z-4
    bevel=closure.WINDOW_RELEASE_BEVEL
    lead=cq.Workplane('YZ',origin=(-5.5,0,0)).polyline([(y,z-bevel),(y+bevel,z),(y,z)]).close().extrude(11)
    return cap.cut(lead)

def card(i,thickness=CARD_T):
    return block(-CARD_X/2,-COUNT*CARD_T/2+i*CARD_T,FLOOR,CARD_X,thickness,CARD_Y)

def lid_print():
    return lid().rotate((0,0,0),(1,0,0),180).translate((0,0,LID_TOP))

def print_layout():
    return cq.Compound.makeCompound([body().val(),lid_print().translate((0,-LAYOUT_OFFSET,0)).val()])

def assembled():
    return cq.Compound.makeCompound([body().val(),lid().val()])
