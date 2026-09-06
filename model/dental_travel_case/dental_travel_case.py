"""Primary evaluation entry point: two captive shells in the actual print pose.

Print this main STEP/STL as one object; preserve the hinge gaps and shell positions.
Print accessories.stl separately, then slide the two clips into the body sockets
and drop the divider into a selected groove. See notes/README.md.
"""
from pathlib import Path
import sys
DIRECTORY=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/dental_travel_case/dental_travel_case.py')).resolve().parent
if str(DIRECTORY) in sys.path: sys.path.remove(str(DIRECTORY))
sys.path.insert(0,str(DIRECTORY))
import cadquery as cq
# MCP evaluations share an interpreter: refresh this object's dependencies.
previous_bytecode_setting=sys.dont_write_bytecode
sys.dont_write_bytecode=True
for module_name in ("parameters","mechanisms","components","reference_items"):
    if module_name in sys.modules:
        del sys.modules[module_name]
from parameters import *
from mechanisms import block, half, hinge, front_latch
from components import compound, clip, socket, divider, divider_flat, divider_guides, shoulder_stop
sys.dont_write_bytecode=previous_bytecode_setting

def build():
    body=half()
    open_lid=half().translate((0,2*HY,0))
    for c in BEARING_CENTERS:
        left,right,receiver=hinge(c)
        body=body.union(left).union(right)
        open_lid=open_lid.union(receiver)
    # Continuous partition reaches near the closed roof, protecting the head
    # even when the case is inverted. Rounded top for handling and cleaning.
    partition=block(0,PARTITION_Y,(FLOOR+HEIGHT-FLOOR-0.6)/2,
                    IW-1.2,WALL,IH-0.6).edges('|X').fillet(0.5)
    body=body.union(partition)
    body=body.union(shoulder_stop().translate((SHOULDER_X,BRUSH_Y,FLOOR)))
    for x in CLIP_POSITIONS:
        body=body.union(socket().translate((x,BRUSH_Y,FLOOR)))
    for x in DIVIDER_POSITIONS:
        body=body.union(cq.Workplane(obj=divider_guides(x)))
    front=-OD/2
    keeper=(cq.Workplane('YZ',origin=(-8,0,0))
            .polyline([(front+0.2,SEAM-5.6),(front-1.4,SEAM-4),
                       (front+0.2,SEAM-2.4)]).close().extrude(16))
    body=body.union(keeper)
    open_lid=open_lid.union(front_latch())
    # Side vents adjacent to head, vertical slots with arched ends. No floor holes.
    for x in (-IW/2+16,-IW/2+24,-IW/2+32):
        vent=(cq.Workplane('XZ',origin=(x,-OD/2+WALL+1,14))
              .slot2D(10,2.4,angle=90).extrude(WALL+2))
        body=body.cut(vent)
    lid=open_lid.rotate((0,HY,SEAM),(1,HY,SEAM),180)
    return body,open_lid,lid

body,open_lid,lid=build()
installed_clips=[clip().translate((x,BRUSH_Y,FLOOR+CRADLE_LIFT)) for x in CLIP_POSITIONS]
installed_divider=divider().translate((DIVIDER_X,STORAGE_Y,FLOOR))
result=compound(body,open_lid)
accessories=compound(clip(),clip().translate((32,0,0)),divider_flat().translate((85,0,0)))
closed=compound(body,lid,*installed_clips,installed_divider)
opened=compound(body,lid.rotate((0,HY,SEAM),(1,HY,SEAM),-110),*installed_clips,installed_divider)
assert len(body.solids().vals())==1 and body.val().isValid()
assert len(open_lid.solids().vals())==1 and open_lid.val().isValid()
assert clip().val().isValid() and len(clip().solids().vals())==1
assert body.intersect(lid).val().Volume()<0.001,'Closed shells interfere'
assert body.intersect(installed_divider).val().Volume()<0.001,'Divider interferes'
for angle in (15,30,60,90,120,150,180):
    moving=lid.rotate((0,HY,SEAM),(1,HY,SEAM),-angle)
    assert body.intersect(moving).val().Volume()<0.001,('Lid sweep collision',angle)
assert result.BoundingBox().xlen+6 <=260
assert result.BoundingBox().ylen+6 <=260
assert result.BoundingBox().zlen <=250
