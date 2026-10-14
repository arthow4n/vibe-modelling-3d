"""Removable compliant PETG cradles and shared production sockets."""
import math
import cadquery as cq
from parameters import *
from mechanisms import block

def compound(*parts):
    return cq.Compound.makeCompound([p.val() if isinstance(p,cq.Workplane) else p for p in parts])

def clip():
    return sized_clip(diameter=HANDLE_DIAMETER, throat=CLIP_THROAT)


def sized_clip(*, diameter, throat):
    """Same tested foot/socket interface, independently specified round grip."""
    radius=diameter/2+CLIP_CLEARANCE
    centre_z=FOOT_HEIGHT+radius+CLIP_WALL
    if not 0 < throat < diameter:
        raise ValueError('Throat must capture the selected nominal diameter')
    # Flat bed-facing dovetail foot. Slide into socket from negative X.
    foot=(cq.Workplane('YZ',origin=(-FOOT_LENGTH/2,0,0))
          .polyline([(-FOOT_WIDTH/2,0),(FOOT_WIDTH/2,0),
                     (FOOT_WIDTH/2-FOOT_HEIGHT,FOOT_HEIGHT),
                     (-FOOT_WIDTH/2+FOOT_HEIGHT,FOOT_HEIGHT)]).close().extrude(FOOT_LENGTH))
    ring=(cq.Workplane('YZ',origin=(-CLIP_WIDTH/2,0,centre_z))
          .circle(radius+CLIP_WALL).circle(radius).extrude(CLIP_WIDTH))
    mouth_z=centre_z+math.sqrt(radius**2-(throat/2)**2)
    ring=ring.cut(block(0,0,mouth_z+20,CLIP_WIDTH+2,60,40))
    ring=ring.edges('|X').fillet(0.35)
    # Buttress the lower circular underside: otherwise its first widening
    # layers grow too quickly from the foot and trigger loose extrusions.
    top_z=centre_z-(radius+CLIP_WALL)/math.sqrt(2)
    top_y=(radius+CLIP_WALL)/math.sqrt(2)
    pedestal=(cq.Workplane('YZ',origin=(-CLIP_WIDTH/2,0,0))
              .polyline([(-FOOT_WIDTH/2+FOOT_HEIGHT,FOOT_HEIGHT),
                         (FOOT_WIDTH/2-FOOT_HEIGHT,FOOT_HEIGHT),
                         (top_y,top_z),(-top_y,top_z)]).close().extrude(CLIP_WIDTH))
    bore=(cq.Workplane('YZ',origin=(-CLIP_WIDTH/2-1,0,centre_z))
          .circle(radius).extrude(CLIP_WIDTH+2))
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
