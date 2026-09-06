"""Approximate envelopes for collision checks; not replicas or printable parts."""
import cadquery as cq
from parameters import *
from mechanisms import block

def reference_items():
    handle=(cq.Workplane('YZ',origin=(BRUSH_LENGTH/2-HANDLE_LENGTH,BRUSH_Y,FLOOR+CRADLE_LIFT+CLIP_Z))
            .circle(HANDLE_DIAMETER/2).extrude(HANDLE_LENGTH))
    neck=block(-70,BRUSH_Y,FLOOR+CRADLE_LIFT+CLIP_Z,40,10,10)
    head=block(-BRUSH_LENGTH/2+14,BRUSH_Y,FLOOR+CRADLE_LIFT+CLIP_Z+1,28,18,22)
    paste=block(IW/2-5-PASTE_LENGTH/2,STORAGE_Y,FLOOR+PASTE_THICKNESS/2,
                PASTE_LENGTH,PASTE_WIDTH,PASTE_THICKNESS)
    floss=block(-IW/2+4.5+FLOSS_THICKNESS/2,STORAGE_Y,FLOOR+FLOSS_HEIGHT/2,
                FLOSS_THICKNESS,FLOSS_WIDTH,FLOSS_HEIGHT)
    items={'handle':handle,'neck':neck,'head':head,'paste':paste,'floss':floss}
    return items
