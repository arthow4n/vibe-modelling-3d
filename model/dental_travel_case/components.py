"""Removable PETG cradles and divider, plus shared production sockets."""
import math
import cadquery as cq
from parameters import *
from mechanisms import block

def compound(*parts):
    return cq.Compound.makeCompound([p.val() if isinstance(p,cq.Workplane) else p for p in parts])

def clip():
    # Flat bed-facing dovetail foot. Slide into socket from negative X.
    foot=(cq.Workplane('YZ',origin=(-FOOT_LENGTH/2,0,0))
          .polyline([(-FOOT_WIDTH/2,0),(FOOT_WIDTH/2,0),
                     (FOOT_WIDTH/2-FOOT_HEIGHT,FOOT_HEIGHT),
                     (-FOOT_WIDTH/2+FOOT_HEIGHT,FOOT_HEIGHT)]).close().extrude(FOOT_LENGTH))
    ring=(cq.Workplane('YZ',origin=(-CLIP_WIDTH/2,0,CLIP_Z))
          .circle(CLIP_RADIUS+CLIP_WALL).circle(CLIP_RADIUS).extrude(CLIP_WIDTH))
    mouth_z=CLIP_Z+math.sqrt(CLIP_RADIUS**2-(CLIP_THROAT/2)**2)
    ring=ring.cut(block(0,0,mouth_z+20,CLIP_WIDTH+2,60,40))
    ring=ring.edges('|X').fillet(0.35)
    # Buttress the lower circular underside: otherwise its first widening
    # layers grow too quickly from the foot and trigger loose extrusions.
    top_z=CLIP_Z-(CLIP_RADIUS+CLIP_WALL)/math.sqrt(2)
    top_y=(CLIP_RADIUS+CLIP_WALL)/math.sqrt(2)
    pedestal=(cq.Workplane('YZ',origin=(-CLIP_WIDTH/2,0,0))
              .polyline([(-FOOT_WIDTH/2+FOOT_HEIGHT,FOOT_HEIGHT),
                         (FOOT_WIDTH/2-FOOT_HEIGHT,FOOT_HEIGHT),
                         (top_y,top_z),(-top_y,top_z)]).close().extrude(CLIP_WIDTH))
    bore=(cq.Workplane('YZ',origin=(-CLIP_WIDTH/2-1,0,CLIP_Z))
          .circle(CLIP_RADIUS).extrude(CLIP_WIDTH+2))
    part=foot.union(ring).union(pedestal.cut(bore))
    # Sloping ribs start on the bed: printable contact bumps, tuned by sample.
    for x in (-5,5):
        for side in (-1,1):
            rib=(cq.Workplane('YZ',origin=(x-1.5,0,0))
                 .polyline([(side*FOOT_WIDTH/2,0),
                            (side*(FOOT_WIDTH/2-1.5+GRIP_BUMP),1.5),
                            (side*(FOOT_WIDTH/2-3),3),
                            (side*(FOOT_WIDTH/2-3.5),3),
                            (side*(FOOT_WIDTH/2-0.5),0)]).close().extrude(3))
            part=part.union(rib)
    return part

def socket():
    # Sloping retaining lips: no horizontal roof. Back wall is a positive stop.
    length=FOOT_LENGTH+4
    slot_half=FOOT_WIDTH/2+SOCKET_CLEARANCE
    shell=block(0,0,2.0,length,BRUSH_LANE-0.4,4)
    channel=(cq.Workplane('YZ',origin=(-length/2-1,0,0))
             .polyline([(-slot_half-0.1,-0.1),(slot_half+0.1,-0.1),
                        (slot_half-FOOT_HEIGHT,FOOT_HEIGHT),
                        (slot_half-FOOT_HEIGHT,7),(-slot_half+FOOT_HEIGHT,7),
                        (-slot_half+FOOT_HEIGHT,FOOT_HEIGHT)]).close().extrude(length-1))
    upper=shell.cut(channel).edges('|Z').fillet(0.25).translate((0,0,CRADLE_LIFT))
    plinth=block(0,0,CRADLE_LIFT/2,length,BRUSH_LANE-0.4,CRADLE_LIFT).edges('|Z').fillet(0.5)
    return plinth.union(upper)

def divider():
    # Installed coordinates local X=0, Y=0, Z=0 on floor; exports rotate flat.
    width=STORAGE_LANE-0.6
    h=IH-0.5
    p=block(0,0,h/2,DIVIDER_THICKNESS,width,h).edges('|X').fillet(0.7)
    # Finger scoop too narrow for the nominal floss box to pass through.
    scoop=cq.Workplane('YZ',origin=(-3,0,h+3)).circle(12).extrude(6)
    return p.cut(scoop)

def divider_flat():
    return divider().rotate((0,0,0),(0,1,0),90).translate((0,0,DIVIDER_THICKNESS/2))

def divider_guides(x):
    out=[]
    for side in (-1,1):
        y=STORAGE_Y+side*(STORAGE_LANE/2-1.4)
        for sx in (-1,1):
            out.append(block(x+sx*(DIVIDER_THICKNESS/2+SLOT_CLEARANCE+0.7),y,
                             FLOOR+13,1.4,3.0,26).edges('|Z').fillet(0.3))
    return compound(*out)


def shoulder_stop():
    # Open notch admits neck but stops the wider handle sliding toward the head.
    center=CLIP_Z+CRADLE_LIFT
    fence=block(0,0,(center+2)/2,WALL,BRUSH_LANE-0.4,center+2)
    opening=block(0,0,center-7+25,WALL+2,14,50)
    return fence.cut(opening).edges('|X').fillet(0.5)
