"""Approximate envelopes for collision checks; not replicas or printable parts."""
import cadquery as cq
from parameters import *
from mechanisms import block

def reference_items():
    handle=(cq.Workplane('YZ',origin=(BRUSH_LENGTH/2-HANDLE_LENGTH,BRUSH_Y,FLOOR+CRADLE_LIFT+CLIP_Z))
            .circle(HANDLE_DIAMETER/2).extrude(HANDLE_LENGTH))
    # Only the combined 90 mm shoulder-to-tip length is measured. Reserve a
    # 28 mm head block provisionally; the neck fills the remaining span.
    neck_length=BRUSH_LENGTH-HANDLE_LENGTH-28
    neck=block(BRUSH_LENGTH/2-HANDLE_LENGTH-neck_length/2,BRUSH_Y,
               FLOOR+CRADLE_LIFT+CLIP_Z,neck_length,15,15)
    head=block(-BRUSH_LENGTH/2+14,BRUSH_Y,FLOOR+CRADLE_LIFT+CLIP_Z+1,28,15,25)
    paste=block(IW/2-5-PASTE_LENGTH/2,STORAGE_Y,FLOOR+PASTE_THICKNESS/2,
                PASTE_LENGTH,PASTE_WIDTH,PASTE_THICKNESS)
    return {'handle':handle,'neck':neck,'head':head,'paste':paste}
