"""20-card slide-lid archive box. mm; assembled coordinates, lid travel +X.

Read the three envelope parameters from the authoritative SCAD, fail loudly if
its format changes. No recreation of swatch details is necessary for clearance.
"""
from pathlib import Path
import re
import cadquery as cq

SWATCH_SOURCE = Path(__file__).resolve().parents[1]/'filament_archive_swatch/filament_archive_swatch.scad'
def swatch_dimension(name):
    matches = re.findall(rf'^\s*{name}\s*=\s*([0-9.]+)\s*;', SWATCH_SOURCE.read_text(), re.M)
    if len(matches) != 1:
        raise ValueError(f'Expected one literal SCAD dimension: {name}')
    return float(matches[0])

CARD_X, CARD_Y, CARD_T = (swatch_dimension(n) for n in ('card_width','card_height','base_thickness'))
COUNT = 20
XY_ALLOWANCE = 2.0  # total per axis
STACK_ALLOWANCE = 4.0
INNER_X, INNER_Y = CARD_X+XY_ALLOWANCE, CARD_Y+XY_ALLOWANCE
FLOOR = 2.4
WALL = 5.3  # includes guide-bearing rim
CAVITY_H = COUNT*CARD_T+STACK_ALLOWANCE
RIM_Z = FLOOR+CAVITY_H
OUT_X, OUT_Y = INNER_X+2*WALL, INNER_Y+2*WALL
LID_T = 3.2
RUNNING_GAP = .3
LID_Z = RIM_Z+RUNNING_GAP
LID_HALF_Y = INNER_Y/2+3.7
LID_HALF_X = INNER_X/2+WALL-.4
RAIL_TOP = LID_Z+LID_T+.6
# One horizontal, in-layer flexure. Rounded contact cams, no sharp tooth edge.
ARM_ROOT_X = -16.0
ARM_TIP_X = -34.0
ARM_Y = LID_HALF_Y-1.9
ARM_T = 2.4
CAM_R = 2.4
CAM_OVERLAP = .8
BASE_CAM_X = ARM_TIP_X-4.0
BASE_CAM_Y = ARM_Y+2*CAM_R-CAM_OVERLAP
RELIEF_INWARD_SCREEN = CAM_OVERLAP + .3
ARM_GAP = CAM_R-ARM_T/2+CAM_OVERLAP+.4  # .4 mm head clearance at nominal bend

assert INNER_X/2 > abs(ARM_TIP_X)+CAM_R+2
assert CAVITY_H >= 16, "Keep a protected floor below the finger scoops"
assert ARM_GAP > CAM_R-ARM_T/2+RELIEF_INWARD_SCREEN

def block(x0,y0,z0,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x0,y0,z0))

def prism_yz(points,x0,length):
    return cq.Workplane('YZ',origin=(x0,0,0)).polyline(points).close().extrude(length)

def snap_arm():
    """Actual lid arm, including a root pad; local z=0 for analysis/printing."""
    arm=block(ARM_TIP_X,ARM_Y-ARM_T/2,0,ARM_ROOT_X-ARM_TIP_X,ARM_T,LID_T)
    cam=cq.Workplane('XY').center(ARM_TIP_X,ARM_Y).circle(CAM_R).extrude(LID_T)
    root=block(ARM_ROOT_X,ARM_Y-ARM_T/2-2,0,3,ARM_T+2,LID_T)
    return arm.union(cam).union(root).edges('|Z').fillet(.5)

def base_cam():
    return cq.Workplane('XY').center(BASE_CAM_X,BASE_CAM_Y).circle(CAM_R).extrude(LID_T+RUNNING_GAP+.6).translate((0,0,-RUNNING_GAP))

def body():
    outer=block(-OUT_X/2,-OUT_Y/2,0,OUT_X,OUT_Y,RIM_Z).edges('|Z').fillet(2)
    # Square envelope with small internal corner rounding: 1 mm card side clearance
    # is larger than the .8 mm internal radius intruding at a hypothetical sharp card.
    inner=block(-INNER_X/2,-INNER_Y/2,FLOOR,INNER_X,INNER_Y,CAVITY_H+10).edges('|Z').fillet(.8)
    shell=outer.cut(inner)
    # Two open-ended dovetail guide rails. 45-degree underside grows from side walls.
    for sign in (-1,1):
        pts=[(sign*y,z) for y,z in [(OUT_Y/2,RIM_Z-.1),(OUT_Y/2,RAIL_TOP),
              (LID_HALF_Y-1.7,RAIL_TOP),(LID_HALF_Y+.4,LID_Z+LID_T-1.5),(LID_HALF_Y+.4,RIM_Z-.1)]]
        rail=prism_yz(pts,-OUT_X/2,OUT_X)
        if sign==1:
            rail=rail.cut(block(-OUT_X/2-1,INNER_Y/2,RIM_Z,OUT_X/2+ARM_ROOT_X+5,10,10))
        shell=shell.union(rail)
    # Back stop fixes closed registration; the front remains open for sliding.
    shell=shell.union(block(OUT_X/2-.4,-OUT_Y/2,RIM_Z,.4,OUT_Y,RAIL_TOP-RIM_Z))
    # Tooth grows from solid outer rim; its vertical contact face matches analysis.
    pedestal=(cq.Workplane('XY',origin=(BASE_CAM_X,BASE_CAM_Y-2,RIM_Z-4))
              .circle(.5).workplane(offset=4).center(0,2).circle(CAM_R).loft())
    shell=shell.union(pedestal).union(base_cam().translate((0,0,LID_Z)))
    # Opposed 26 mm finger scoops expose the upper stack edges; tip the open
    # tray into a hand to remove the complete stack or the last few cards.
    for sign in (-1,1):
        scoop=cq.Workplane('XZ',origin=(0,sign*(INNER_Y/2+WALL+1),RIM_Z)).circle(13).extrude(sign*(WALL+2))
        scoop=scoop.union(block(-13,-OUT_Y/2-1,RIM_Z,26,OUT_Y+2,10))
        shell=shell.cut(scoop)
    return shell

def lid():
    # Bottom is broad/flat; upper bevels fit the self-supporting guides.
    plate=prism_yz([(-LID_HALF_Y,0),(LID_HALF_Y,0),(LID_HALF_Y,LID_T-1.5),
                   (LID_HALF_Y-1.5,LID_T),(-LID_HALF_Y+1.5,LID_T),(-LID_HALF_Y,LID_T-1.5)],
                   -LID_HALF_X,2*LID_HALF_X)
    plate=plate.cut(block(-LID_HALF_X-1,INNER_Y/2+2.5,-.1,2*LID_HALF_X+2,10,LID_T+.2))
    # Open-sided relief: arm bends toward the cavity; outer root joins lid plate.
    plate=plate.cut(block(-LID_HALF_X-1,ARM_Y-ARM_T/2-ARM_GAP, -.1,
                         LID_HALF_X+ARM_ROOT_X+1,12,LID_T+.2))
    plate=plate.union(snap_arm())
    # Thumb purchase: rounded recessed groove, leaving 2 mm floor.
    grip=cq.Workplane('XY').center(-LID_HALF_X+10,0).slot2D(25,6,90).extrude(1.2).translate((0,0,LID_T-1.2))
    return plate.cut(grip)

def print_layout():
    return cq.Compound.makeCompound([body().val(),lid().translate((0,-OUT_Y-12,0)).val()])
