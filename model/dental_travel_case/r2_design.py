"""Complete rounded case and small representative cross-section trial."""
import cadquery as cq
from components import compound
from mechanisms import block
from parameters import CLIP_POSITIONS,BRUSH_LENGTH,HANDLE_LENGTH
from r2_geometry import *
from r2_parts import (revised_clip,raised_socket,installed_gate,gate_pin,
                      keeper_cap,snap_pin,pin_in_joint,spring_latch,keeper,FOOT_Z,LATCH_START)


def flip_lid(part):
    return part.rotate((0,0,HEIGHT/2),(1,0,HEIGHT/2),180).mirror('XZ')


def references(*, diameter):
    handle=(cq.Workplane('YZ',origin=(BRUSH_LENGTH/2-HANDLE_LENGTH,BRUSH_Y,BRUSH_Z))
            .circle(diameter/2).extrude(HANDLE_LENGTH))
    neck=block(-68.5,BRUSH_Y,BRUSH_Z,62,15,15)
    head=block(-113.5,BRUSH_Y,BRUSH_Z+1,28,15,25)
    tube=block(0,TUBE_Y,FLOOR+22,TUBE_LENGTH,60,44)
    return dict(handle=handle,neck=neck,head=head,tube=tube)


def _build_without_bed_foundations():
    body=rear_half(lid_side=False)
    lid_print=rear_half(lid_side=True)
    # Low separator clears the moving guards. Tall head section shields bristles.
    partition=block(0,-14.2,(FLOOR+RIM)/2,251,2.4,RIM-FLOOR)
    partition=partition.edges('|Y and >Z').fillet(8).edges('|X').fillet(.5)
    head_partition=block(-82,-14.2,(FLOOR+HEIGHT-FLOOR-.6)/2,87,2.4,HEIGHT-2*FLOOR-.6)
    head_partition=head_partition.edges('|Y and >Z').fillet(8).edges('|X').fillet(.5)
    body=body.union(partition).union(head_partition).union(keeper())
    mount=raised_socket()
    for x in CLIP_POSITIONS:
        body=body.union(mount.translate((x,BRUSH_Y,0)))
        lid_print=lid_print.union(keeper_cap().translate((x,0,0)))
    latch=spring_latch()
    leaf=latch.intersect(block(0,-60,(LATCH_START+HALF_HEIGHT+11)/2,
                              30,40,HALF_HEIGHT+11-LATCH_START))
    lid_print=lid_print.union(latch)
    # Seating pads carry closure height; latch supplies retention, not a seat.
    for x,y in ((-70,-64.3),(70,-64.3),(0,64.3)):
        body=body.union(block(x,y,RIM+.3,10,2.4,.6))
    for x in (-115,-106,-97):
        vent=(cq.Workplane('XZ',origin=(x,-40,13)).slot2D(8,2,angle=90).extrude(35))
        body=body.cut(vent)
    lid=flip_lid(lid_print)
    clips=[revised_clip().translate((x,BRUSH_Y,FOOT_Z)) for x in CLIP_POSITIONS]
    gates=[installed_gate(x) for x in CLIP_POSITIONS]
    links=[link().translate((x,0,0)) for x in STATIONS]
    body_pins=[pin_in_joint(x,joint='body') for x in STATIONS]
    lid_pins=[pin_in_joint(x,joint='lid') for x in STATIONS]
    return dict(body=body,lid=lid,lid_print=lid_print,clips=clips,gates=gates,
                links=links,body_pins=body_pins,lid_pins=lid_pins,
                latch=flip_lid(latch),latch_leaf=flip_lid(leaf))



def bed_foundations():
    # Bearing bases used to start at the cup floor above the bed. Their rear
    # edges extend beyond that floor: carry these four local feet down to Z=0.
    feet=[]
    for x in STATIONS:
        for offset in (-6,6):
            feet.append(block(x+offset,49.5,FLOOR/2,3.8,15,FLOOR))
    return cq.Workplane(obj=compound(*feet))


def build():
    case=_build_without_bed_foundations()
    case['motion_body']=case['body']
    case['foundations']=bed_foundations()
    case['body']=case['body'].union(case['foundations'])
    return case


def assembly(case,*,phi,theta,loaded):
    a=cq.Assembly(name='rounded_dental_case')
    a.add(case['body'],name='body')
    a.add(lid_pose(case['lid'],phi,theta),name='lid')
    for key in ('clips','gates','body_pins'):
        for i,p in enumerate(case[key]):
            a.add(p,name=f'{key}_{i+1}')
    for i,p in enumerate(case['links']):
        a.add(link_pose(p,theta),name=f'folding_link_{i+1}')
    for i,p in enumerate(case['lid_pins']):
        a.add(lid_pose(p,phi,theta),name=f'lid_pin_{i+1}')
    if loaded:
        for name,p in references(diameter=27).items():
            a.add(p,name=name)
    return a


def flat_link():
    return link().rotate((0,0,0),(0,1,0),90).translate((-HEIGHT/2,-(AXIS_Y+LID_AXIS_Y)/2,LINK_THICKNESS/2))


def hardware():
    return compound(revised_clip().translate((-25,-25,0)),revised_clip().translate((5,-25,0)),
                    flat_link().translate((-10,25,0)),flat_link().translate((-10,52,0)),
                    snap_pin(joint='body').translate((35,-25,0)),snap_pin(joint='body').translate((53,-25,0)),
                    snap_pin(joint='lid').translate((35,-7,0)),snap_pin(joint='lid').translate((53,-7,0)),
                    gate_pin().translate((35,15,0)),gate_pin().translate((53,15,0)))


def section_test(case):
    centre=107.5
    crop=block(centre,0,HEIGHT/2,44,160,HEIGHT+2)
    lower=case['body'].intersect(crop).union(keeper().translate((centre,0,0)))
    upper=case['lid_print'].intersect(crop).union(spring_latch().translate((centre,0,0)))
    return compound(lower.translate((-centre,0,0)),upper.translate((60-centre,0,0)),
                    revised_clip().translate((120,-40,0)),flat_link().translate((130,20,0)),
                    snap_pin(joint='body').translate((140,-30,0)),
                    snap_pin(joint='lid').translate((160,-30,0)),gate_pin().translate((120,0,0)))
