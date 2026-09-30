"""Covered lift-off storage box, mm. Body upright, lid roof-down for printing.

The enclosure wall is continuous. Exterior snap recesses never enter the cavity.
Vertical body tabs flex inward; corners protect them within the box outline.
"""
from pathlib import Path
import re
import cadquery as cq

SWATCH_SOURCE=Path(__file__).resolve().parents[1]/'filament_archive_swatch/filament_archive_swatch.scad'
def dimension(name):
    matches=re.findall(rf'^\s*{name}\s*=\s*([0-9.]+)\s*;',SWATCH_SOURCE.read_text(),re.M)
    if len(matches)!=1: raise ValueError(f'Expected one literal SCAD dimension: {name}')
    return float(matches[0])

CARD_X,CARD_Y,CARD_T=map(dimension,('card_width','card_height','base_thickness'))
COUNT=20
INNER_X,INNER_Y=CARD_X+20,CARD_Y+6
FLOOR,PLATFORM,WALL=2.4,6.,1.6
SNAP_LINER=1.2  # continuous shield behind the exterior relief, not a cavity hole
STACK_Z=FLOOR+PLATFORM
CAVITY_H=PLATFORM+COUNT*CARD_T+6.4
RIM_Z=FLOOR+CAVITY_H
OUT_X,OUT_Y=INNER_X+2*WALL,INNER_Y+2*9.4
LID_T,FIT=2.4,.35
LID_TOP=RIM_Z+LID_T
TIP_X=0.
ARM_L,ARM_T,ARM_W=24.,1.8,16.
ARM_Y,HEAD_Y,CAM_R=INNER_Y/2+5,INNER_Y/2+5.8,2.
HEAD_Z=RIM_Z-4
ROOT_Z=HEAD_Z-ARM_L
LID_CAM_Y,LID_CAM_Z=HEAD_Y+3.2,HEAD_Z-1.9
CAM_WIDTH=16.
BUTTON_W,BUTTON_H=10.,6.
BUTTON_FRONT=OUT_Y/2+1.4
OVERLAP=2*CAM_R-(LID_CAM_Y-HEAD_Y)
RELIEF_TRAVEL=2.2
WINDOW_RELEASE_BEVEL=.8

def block(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z))

def rounded_box(dx,dy,dz,z=0,r=3):
    return cq.Workplane('XY').box(dx,dy,dz,centered=(True,True,False)).translate((0,0,z)).edges('|Z').fillet(r)

def cylinder_x(x,y,z,r,length):
    return cq.Workplane('YZ',origin=(x,y,z)).circle(r).extrude(length)

def snap_arm():
    arm=block(-ARM_W/2,ARM_Y-ARM_T/2,ROOT_Z,ARM_W,ARM_T,ARM_L)
    root=block(-ARM_W/2-2,INNER_Y/2+WALL-.2,ROOT_Z-2,ARM_W+4,
               ARM_Y+ARM_T/2-(INNER_Y/2+WALL)+.2,2)
    head=cylinder_x(-CAM_WIDTH/2,HEAD_Y,HEAD_Z,CAM_R,CAM_WIDTH)
    head=head.intersect(block(-CAM_WIDTH,0,HEAD_Z-.6,2*CAM_WIDTH,50,10))
    # Upper round lead-in, lower flat retaining shoulder. Exterior supports
    # may be needed under this small shoulder; it is not a supported ramp.
    neck=block(-CAM_WIDTH/2,ARM_Y-ARM_T/2,HEAD_Z-2,CAM_WIDTH,
               HEAD_Y-(ARM_Y-ARM_T/2),2)
    button=block(-BUTTON_W/2,HEAD_Y,HEAD_Z-BUTTON_H/2,BUTTON_W,
                 BUTTON_FRONT-HEAD_Y,BUTTON_H).edges('|Y').fillet(.8)
    return arm.union(root).edges('|X').fillet(.5).union(head).union(neck).union(button)

def lid_cam():
    cam=cylinder_x(-CAM_WIDTH/2,LID_CAM_Y,LID_CAM_Z,CAM_R,CAM_WIDTH)
    cam=cam.intersect(block(-CAM_WIDTH,0,LID_CAM_Z-10,2*CAM_WIDTH,50,10.6))
    support=block(-CAM_WIDTH/2,LID_CAM_Y,LID_CAM_Z,CAM_WIDTH,2,2.4)
    catch=cam.union(support)
    # Two small side catches leave the flush central press pad's path clear.
    return catch.cut(block(-5.5,0,LID_CAM_Z-5,11,50,10))

def body():
    shell=rounded_box(OUT_X,OUT_Y,RIM_Z,r=5).cut(rounded_box(INNER_X,INNER_Y,CAVITY_H+3,FLOOR,r=1))
    platform=rounded_box(CARD_X-10,CARD_Y-2,PLATFORM,FLOOR,r=2)
    shell=shell.union(platform)
    # End corner stops center the stack while leaving the middle of both end
    # wells open. They join the end wall, not slender freestanding posts.
    for sx in (-1,1):
        for sy in (-1,1):
            stop=block(CARD_X/2+1.5,18,FLOOR,INNER_X/2-(CARD_X/2+1.5),INNER_Y/2-18,CAVITY_H-4)
            if sx<0: stop=stop.mirror('YZ')
            if sy<0: stop=stop.mirror('XZ')
            shell=shell.union(stop)
    for sign in (-1,1):
        pocket=block(-14,INNER_Y/2+SNAP_LINER,ROOT_Z,28,OUT_Y/2-1.2-(INNER_Y/2+SNAP_LINER),RIM_Z-ROOT_Z+1)
        window=block(-5.5,OUT_Y/2-1.7,HEAD_Z-4,11,4,8)
        # The cap covers the upper recess; the body guard covers the lower
        # beam. Give the cap catches their path outside the inner enclosure.
        upper=block(-14,OUT_Y/2-1.2,RIM_Z-10,28,3,RIM_Z)
        if sign<0: pocket=pocket.mirror('XZ');window=window.mirror('XZ');upper=upper.mirror('XZ')
        shell=shell.cut(pocket).cut(window).cut(upper)
        arm=snap_arm()
        if sign<0: arm=arm.mirror('XZ')
        shell=shell.union(arm)
    return shell

def lid():
    roof=rounded_box(OUT_X+2*(FIT+1.6),OUT_Y+2*(FIT+1.6),LID_T,RIM_Z,r=6).edges('>Z').chamfer(.3)
    outer=rounded_box(OUT_X+2*(FIT+1.6),OUT_Y+2*(FIT+1.6),10,RIM_Z-10,r=6)
    outer=outer.cut(rounded_box(OUT_X+2*FIT,OUT_Y+2*FIT,10.2,RIM_Z-10.1,r=5.35))
    # Bevel only the inner lower wire: it must cam a flush pad inward, not
    # press on its flat top with a horizontal leading edge.
    inner_edges=outer.faces('<Z').val().innerWires()[0].Edges()
    outer=outer.newObject(inner_edges).chamfer(1.2)
    lip=rounded_box(INNER_X-2*FIT,INNER_Y-2*FIT,4,RIM_Z-4,r=1.5)
    lip=lip.cut(rounded_box(INNER_X-2*FIT-3.2,INNER_Y-2*FIT-3.2,4.2,RIM_Z-4.1,r=1))
    cap=roof.union(outer).union(lip)
    for sign in (-1,1):
        notch=block(-5.5,OUT_Y/2+.2,HEAD_Z-4,11,5,8)
        if sign<0: notch=notch.mirror('XZ')
        cap=cap.cut(notch)
        cam=lid_cam().intersect(rounded_box(OUT_X+2*(FIT+1.6),OUT_Y+2*(FIT+1.6),10,RIM_Z-10,r=6))
        if sign<0: cam=cam.mirror('XZ')
        cap=cap.union(cam)
    # The lower window ledge also crosses the returning pad during release.
    # A real inward lead avoids dragging its underside upward on a flat edge.
    y,z=OUT_Y/2+FIT,HEAD_Z-4
    lead=cq.Workplane('YZ',origin=(-5.5,0,0)).polyline(
        [(y,z-WINDOW_RELEASE_BEVEL),(y+WINDOW_RELEASE_BEVEL,z),(y,z)]).close().extrude(11)
    for sign in (-1,1):
        cap=cap.cut(lead if sign>0 else lead.mirror('XZ'))
    return cap

def analysis_cap():
    """Actual local cap rim/window/catches; roof keeps the fixture connected."""
    return lid().intersect(block(-12,INNER_Y/2+WALL+.2,HEAD_Z-7,24,15,LID_TOP-(HEAD_Z-7)+.1))

def lid_print():
    return lid().rotate((0,0,0),(1,0,0),180).translate((0,0,LID_TOP))

def print_layout():
    return cq.Compound.makeCompound([body().val(),lid_print().translate((0,-OUT_Y-14,0)).val()])

def assembled():
    return cq.Compound.makeCompound([body().val(),lid().val()])
