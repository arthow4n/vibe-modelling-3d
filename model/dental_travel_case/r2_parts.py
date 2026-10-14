"""PETG grips, captive clip gates, snap pins and closure; pure builders."""
import cadquery as cq
from components import sized_clip, socket
from mechanisms import block
from parameters import CLIP_POSITIONS,CLIP_WIDTH,CLIP_WALL,FOOT_HEIGHT,CRADLE_LIFT
from r2_geometry import (HEIGHT,HALF_HEIGHT,FLOOR,RIM,BRUSH_Y,BRUSH_Z,half_width)

GRIP_DIAMETER=27.0  # target inferred from user-requested 3 mm bore reduction
GRIP_THROAT=25.4
GRIP_CENTRE=FOOT_HEIGHT+(GRIP_DIAMETER/2+.15)+CLIP_WALL
FOOT_Z=BRUSH_Z-GRIP_CENTRE
GATE_OFFSET=-12.3
GATE_SEAT=FOOT_Z-.35
GATE_STEM=10.0
GUARD_BOTTOM=48.5
LATCH_START=12.0
LATCH_RELEASE=3.5


def revised_clip():
    return sized_clip(diameter=GRIP_DIAMETER,throat=GRIP_THROAT)


def raised_socket():
    # Tested retaining lips, channel and backstop, now on a tapered foundation.
    retainer=socket().intersect(block(0,0,CRADLE_LIFT+2,24,44,4))
    retainer=retainer.translate((0,0,FOOT_Z-CRADLE_LIFT))
    support=(cq.Workplane('YZ',origin=(-11,0,0)).polyline(
        [(-13.5,FLOOR),(13.5,FLOOR),(20.3,FOOT_Z),(-20.3,FOOT_Z)])
        .close().extrude(22))
    housing=(cq.Workplane('XY',origin=(GATE_OFFSET,0,FLOOR))
             .circle(3.6).extrude(GATE_SEAT-FLOOR))
    bore=(cq.Workplane('XY',origin=(GATE_OFFSET,0,GATE_SEAT-GATE_STEM-.3))
          .circle(1.95).extrude(GATE_STEM+.6))
    return support.union(retainer).union(housing).cut(bore)


def gate_pin():
    """Head-down print. Installed stem points down; brush prevents withdrawal."""
    head=cq.Workplane('XY').circle(2.7).extrude(2)
    shaft=cq.Workplane('XY',origin=(0,0,2)).circle(1.8).extrude(GATE_STEM)
    return head.union(shaft)


def installed_gate(x):
    return gate_pin().rotate((0,0,0),(1,0,0),180).translate(
        (x+GATE_OFFSET,BRUSH_Y,GATE_SEAT+2))


def keeper_cap():
    # Prints upward from the lid panel; broad flat contact limits handle lift.
    return block(0,BRUSH_Y,(FLOOR+HEIGHT-GUARD_BOTTOM)/2,
                 14,28,HEIGHT-GUARD_BOTTOM-FLOOR).edges('|Z').fillet(1)


def snap_pin(*, joint):
    if joint not in ('body','lid'):
        raise ValueError('Unknown pin joint: '+joint)
    head_height=2.0
    ramp_start=24.7 if joint=='body' else 18.2
    head=cq.Workplane('XY').circle(4.8).extrude(head_height)
    shaft=cq.Workplane('XY',origin=(0,0,head_height)).circle(3).extrude(ramp_start+.6-head_height)
    ramp=cq.Workplane(obj=cq.Solid.makeCone(3,3.6,.6,cq.Vector(0,0,ramp_start)))
    tip=cq.Workplane(obj=cq.Solid.makeCone(3.6,2.7,1.4,cq.Vector(0,0,ramp_start+.6)))
    # Barbs only on the two arm tips. A split full-circumference cone would
    # remain oversized across the unsplit direction even after squeezing.
    barbs=ramp.union(tip).intersect(block(0,0,ramp_start+1,10,2,2.2))
    core_tip=cq.Workplane(obj=cq.Solid.makeCone(3,2.7,1.4,cq.Vector(0,0,ramp_start+.6)))
    pin=head.union(shaft).union(core_tip).union(barbs)
    slot_bottom=ramp_start+.6-13.5
    slot=block(0,0,slot_bottom+15,1.6,12,30)
    return pin.cut(slot)


def _placed_pin(part,x,*,joint):
    from r2_geometry import AXIS_Y,LID_AXIS_Y,AXIS_Z
    if joint not in ('body','lid'):
        raise ValueError('Unknown pin joint: '+joint)
    sign=1 if x>0 else -1
    if joint=='body': sign=-sign
    base=-16.6 if joint=='body' else -10.1
    return (part.rotate((0,0,0),(0,0,1),90)
            .rotate((0,0,0),(0,1,0),sign*90).translate(
        (x+sign*base,AXIS_Y if joint=='body' else LID_AXIS_Y,
         AXIS_Z if joint=='body' else HEIGHT-AXIS_Z)))


def pin_in_joint(x,*,joint):
    return _placed_pin(snap_pin(joint=joint),x,joint=joint)


def compressed_pin_proxy(x,*,joint):
    """Admission-only mask: free arms shifted 0.5 mm inward; no force claim.

    Actual root transition is elastic. Shaft cross-sections move inward from
    their original 3 mm radius, staying within the 3.2 mm bearing while the two
    localized barbs are squeezed. This proxy is never a printable part.
    """
    from components import compound
    pin=snap_pin(joint=joint)
    start=(24.7 if joint=='body' else 18.2)+.6-13.5
    mask=block(0,0,start+15,20,20,30)
    base=pin.cut(mask)
    tips=pin.intersect(mask)
    left=tips.intersect(block(-5,0,15,10,20,40)).translate((.5,0,0))
    right=tips.intersect(block(5,0,15,10,20,40)).translate((-.5,0,0))
    return _placed_pin(cq.Workplane(obj=compound(base,left,right)),x,joint=joint)


def spring_latch():
    inner,outer=-68.7,-69.9
    start,top=LATCH_START,HALF_HEIGHT+10
    levels=(start,16,20,24,28,HALF_HEIGHT,top)
    inside=[(-half_width(z)-2.7,z) for z in levels]
    outside=[(y-1.2,z) for y,z in inside]
    root_outer=outside[0][0]
    root=(cq.Workplane('YZ',origin=(-8,0,0)).polyline(
        [(-49.5,0),(-50,0),(root_outer,start),
         (-half_width(start)+.5,start)]).close().extrude(16))
    leaf=(cq.Workplane('YZ',origin=(-8,0,0)).polyline(inside+list(reversed(outside)))
          .close().extrude(16).edges('>Z').chamfer(.25))
    tooth=(cq.Workplane('YZ',origin=(-6,0,0)).polyline(
        [(inner-.2,HALF_HEIGHT+3),( -66.7,HALF_HEIGHT+5.2),
         (inner-.2,HALF_HEIGHT+7.4)]).close().extrude(12))
    grip=(cq.Workplane('YZ',origin=(-7,0,0)).polyline(
        [(outer+.2,top-3),(outer-.8,top-1.8),(outer-.8,top-.5),(outer+.2,top-.5)])
        .close().extrude(14).edges('|X').fillet(.25))
    return root.union(leaf).union(tooth).union(grip)


def keeper():
    return (cq.Workplane('YZ',origin=(-7,0,0)).polyline(
        [(-half_width(HALF_HEIGHT-9)+.3,HALF_HEIGHT-9),
         (-67.4,HALF_HEIGHT-4),(-half_width(HALF_HEIGHT-2.4)+.3,HALF_HEIGHT-2.4)])
        .close().extrude(14))
