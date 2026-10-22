"""Production-orientation R1 study, not an adopted or print-ready case.

A stock M3 screw head replaces the inverted printed keeper. All cam material
stays outside the cap. The wheel conceals the nose; both shells retain end-down
print orientation. No detent/strength/whole-case security is qualified here.
"""
from dataclasses import dataclass
from math import cos, radians
import cadquery as cq
import m1_design as base
from rotary_r1_design import axial_cylinder, sector, yz_prism


@dataclass(frozen=True)
class Dimensions:
    width: float = 75.8
    depth: float = 52.8
    seam: float = 174.
    lap: float = 30.
    length: float = 264.
    reveal: float = 3.
    pivot_drop: float = 2.
    wheel_back: float = 29.
    wheel_front: float = 32.6
    nose_back: float = 27.
    nose_inner: float = 13.3
    nose_outer: float = 15.7
    keeper_radius: float = 2.75
    keeper_offset: float = 9.75

    @property
    def pivot(self):return self.seam-self.pivot_drop
    @property
    def rim(self):return self.seam+self.reveal


D=Dimensions()


def nut(x,y,z):
    return (cq.Workplane('XZ',origin=(x,y,z)).polygon(6,5.5/cos(radians(30)))
            .extrude(2.4).cut(cq.Workplane('XZ',origin=(x,y+.1,z)).circle(1.6).extrude(2.6)))


def screw(x,y,z,length):
    """y is under-head plane; nominal head diameter5.5, height2, no threads."""
    shaft=cq.Workplane('XZ',origin=(x,y,z)).circle(1.5).extrude(length)
    head=cq.Workplane('XZ',origin=(x,y+2,z)).circle(2.75).extrude(2.)
    return shaft.union(head)


def build(variant):
    if variant not in ('paddle','wheel'):raise ValueError('Unknown form: '+str(variant))
    d=D;z=d.pivot
    outer=base.prism(d.width,d.depth,6.,0,d.seam).edges('<Z').fillet(3.)
    outer=outer.union(base.prism(71.2,48.2,4.,d.seam-.5,d.lap+.5))
    cavity=cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,hz) for hz,w,h,r in (
            (2.,71.8,48.8,4.),(d.seam-6.,71.8,48.8,4.),
            (d.seam,67.2,44.2,2.),(d.seam+d.lap+1.,67.2,44.2,2.))],ruled=True))
    body=outer.cut(cavity)
    # Local external journal; its upper back face clears the moving cap.
    pad=yz_prism([(25.8,z-9.2),(26.4,z-9.2),(28.7,z-6.9),
                  (28.7,z+5.5),(26.9,z+5.5),(26.9,d.seam),
                  (25.8,d.seam)],-13.,26.)
    pad=pad.intersect(axial_cylinder(12.7,35.,z,12.))
    body=body.union(pad)
    # Open-ended guide track clears the cap keeper nut and protruding screw.
    # This deliberately sacrifices 10.4mm of the broad sleeve guide, not bore.
    track=base.box(0,25,d.seam+d.lap/2,10.4,20,d.lap+2)
    body=body.cut(track)
    access=(cq.Workplane('XZ',origin=(0,26.2,z)).polyline([
        (-4.8,-4.),(4.8,-4.),(4.8,1.2),(0.,6.),(-4.8,1.2)])
        .close().extrude(13.))
    body=body.cut(access).cut(axial_cylinder(1.8,35.,z,25.))
    # Nominal stop peg and shallow rear wheel slot. Not a position detent.
    peg=cq.Workplane('XZ',origin=(-8,29.7,z)).circle(1.).extrude(1.1)
    body=body.union(peg)
    seat_ring=base.prism(d.width,d.depth,6.,d.seam,d.reveal).cut(
        base.prism(71.8,48.8,4.3,d.seam-1.,d.reveal+2))
    for sx in (-1,1):
        for sy in (-1,1):
            body=body.union(seat_ring.intersect(base.box(sx*(d.width/2-6),
                sy*(d.depth/2-6),d.seam+d.reveal/2,8,8,d.reveal+2)))
    body=body.clean()
    cap=base.prism(d.width,d.depth,6.,d.rim,d.length-d.rim).edges('>Z').fillet(3.)
    cap=cap.cut(base.prism(71.8,48.8,4.3,d.rim-1,d.length-d.rim-1))
    # Only an ordinary screw bore, no large external window or keeper island.
    cap=cap.cut(cq.Workplane('XZ',origin=(0,35,z+d.keeper_offset)).circle(1.8).extrude(15)).clean()

    plate=axial_cylinder(17.,d.wheel_front,z,d.wheel_front-d.wheel_back)
    if variant=='wheel':
        for x in (-20.5,20.5):
            grip=cq.Workplane('XZ',origin=(x,35.,z)).circle(6.5).extrude(10.)
            plate=plate.cut(grip)
    if variant=='paddle':
        hub=axial_cylinder(6.,d.wheel_front,z,d.wheel_front-d.wheel_back)
        stem=base.box(0,(d.wheel_front+d.wheel_back)/2,z+7.5,
                      9.,d.wheel_front-d.wheel_back,15.)
        plate=plate.intersect(hub.union(stem))
    # Outer face is flat for printing. Small perimeter rounds do not create
    # a raised hub that would leave the whole wheel hanging over the bed.
    plate=plate.edges('|Y').fillet(.6)
    plate=plate.faces('>Y').edges().fillet(.5)
    nose=sector(d.nose_inner,d.nose_outer,-16.,16.,d.wheel_front,
                d.wheel_front-d.nose_back,z)
    rotor=plate.union(nose)
    rotor=rotor.cut(axial_cylinder(1.8,36,z,12))
    rotor=rotor.cut(axial_cylinder(3.0,35,z,4.4))
    if variant=='wheel':
        rotor=rotor.cut(sector(6.6,9.4,-189.,-81.,30.1,1.3,z))
    # The paddle needs no hidden wheel-stop track; form-only comparison.
    rotor=rotor.clean()
    pivot=screw(0,30.7,z,12.)
    keeper=screw(0,26.6,z+d.keeper_offset,10.)
    hw=dict(pivot_screw=pivot,pivot_nut=nut(0,26.,z),
            pivot_jam=nut(0,23.6,z),keeper_screw=keeper,
            keeper_nut=nut(0,24.3,z+d.keeper_offset))
    # Use the established front-facing presentation, authored positive-Y above.
    parts={n:p.mirror('XZ') for n,p in dict(body=body,cap=cap,rotor=rotor,nose=nose,**hw).items()}
    return dict(dimensions=d,variant=variant,**parts)


def rotor_pose(p,angle):
    z=p['dimensions'].pivot
    return p['rotor'].rotate((0,0,z),(0,1,z),angle)


def configuration(p,state):
    if state not in ('locked','open','print-study','exploded'):raise ValueError(state)
    d=p['dimensions'];a=cq.Assembly(name='rotary_'+p['variant']+'_'+state)
    colors={'body':(.35,.55,.65),'cap':(.73,.79,.8),'rotor':(.24,.36,.4)}
    if state=='print-study':
        a.add(p['body'],name='body')
        a.add(p['cap'].rotate((0,0,0),(1,0,0),180).translate((100,0,d.length)),name='cap')
        a.add(p['rotor'].rotate((0,0,0),(1,0,0),90).translate((50,80+d.pivot,d.wheel_front)),name='rotor')
        return a
    lift=95. if state=='open' else 0.
    angle=90. if state=='open' else 0.
    for name in ('body','cap','rotor'):
        part=p[name]
        if name=='cap':part=part.translate((0,0,lift))
        if name=='rotor':part=rotor_pose(p,angle)
        if state=='exploded' and name=='rotor':part=part.translate((0,-25,0))
        a.add(part,name=name,color=cq.Color(*colors[name]))
    for name in ('pivot_screw','pivot_nut','pivot_jam','keeper_screw','keeper_nut'):
        part=p[name]
        if name.startswith('keeper'):part=part.translate((0,0,lift))
        if state=='exploded' and name=='pivot_screw':part=part.translate((0,-25,0))
        a.add(part,name=name,color=cq.Color(.65,.65,.65))
    return a
