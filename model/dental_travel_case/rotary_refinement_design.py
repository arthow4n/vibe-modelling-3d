"""Rough stock-material rotary closure with a blind nut and printed shoulder axle.

Storage-facing walls remain continuous. A separate spring detent resists opening;
the axle seats on a shoulder, so tightening it does not set rotor friction.
"""
from dataclasses import dataclass,replace
from math import sin,cos,radians
import cadquery as cq
import m1_design as base
from rotary_r1_design import axial_cylinder,sector,yz_prism


@dataclass(frozen=True)
class Dimensions:
    width: float=75.8
    depth: float=52.8
    seam: float=174.
    lap: float=30.
    length: float=264.
    reveal: float=3.
    pivot_drop: float=3.5
    pod_face: float=32.3
    wheel_back: float=32.6
    wheel_front: float=36.8
    nose_back: float=27.
    nose_inner: float=13.3
    nose_outer: float=15.7
    keeper_radius: float=12.5
    axle_under: float=34.3
    axle_front: float=36.5
    axle_tip: float=25.9
    detent_radius: float=10.5
    detent_pin_radius: float=1.2
    detent_radial_travel: float=.35

    @property
    def pivot(self):return self.seam-self.pivot_drop
    @property
    def rim(self):return self.seam+self.reveal


D=Dimensions()
SAMPLE=replace(D,seam=24.,length=70.)


def printed_axle():
    """Print external 8mm hex head down, M6x1 thread up; fit needs a real stock nut.

    Metal-nut ISO profile is approximated, with a deliberate 0.10mm radial
    reduction of the major diameter. No calibrated thread-fit claim is made.
    """
    d=D;head=d.axle_front-d.axle_under;shoulder=d.axle_under-d.pod_face
    start=head+shoulder;end=d.axle_front-d.axle_tip
    root,crest,pitch=2.325,2.9,1.
    helix_start=start-1.;height=end-start+2.
    path=cq.Wire.makeHelix(pitch,height,root,center=(0,0,helix_start))
    ridge=(cq.Workplane('XZ').polyline([(root-.10,helix_start-.394),
        (crest,helix_start-.063),(crest,helix_start+.063),
        (root-.10,helix_start+.394)]).close().sweep(path,isFrenet=True))
    thread=cq.Workplane('XY',origin=(0,0,start)).circle(root).extrude(end-start)
    thread=thread.union(ridge).intersect(base.box(0,0,(start+end)/2,10,10,end-start))
    lead=(cq.Workplane('XY',origin=(0,0,end-.7)).circle(crest)
          .workplane(offset=.7).circle(root).loft())
    thread=thread.intersect(base.box(0,0,(start+end-.7)/2,10,10,end-.7-start).union(lead))
    head_part=cq.Workplane('XY').polygon(6,8/cos(radians(30))).extrude(head)
    head_part=head_part.edges('|Z').fillet(.25)
    journal=cq.Workplane('XY',origin=(0,0,head-.05)).circle(4.).extrude(shoulder+.05)
    return head_part.union(journal).union(thread).clean()


def build(variant,*,dimensions):
    if variant not in ('paddle','wheel'):raise ValueError('Unknown form: '+str(variant))
    d=dimensions;z=d.pivot
    body=base.prism(d.width,d.depth,6.,0,d.seam).edges('<Z').fillet(3.)
    body=body.union(base.prism(71.2,48.2,4.,d.seam-.5,d.lap+.5))
    cavity=cq.Workplane(obj=cq.Solid.makeLoft([base.rounded_wire(w,h,r,hz)
        for hz,w,h,r in ((2.,71.8,48.8,4.),(d.seam-6.,71.8,48.8,4.),
            (d.seam,67.2,44.2,2.),(d.seam+d.lap+1.,67.2,44.2,2.))],ruled=True))
    body=body.cut(cavity)
    pad=yz_prism([(25.8,z-17.),(26.4,z-17.),(d.pod_face,z-11.1),
        (d.pod_face,d.rim-.5),(24.4,d.rim-.5),(24.4,d.seam),(25.8,d.seam)],-13.,26.)
    pad=pad.faces('>Y').edges('|Z').fillet(2.)
    # Remove only the outside nose sweep; storage/guide walls stay whole.
    body=body.union(pad.cut(sector(12.8,30.,0.,115.,40.,13.2,z)))
    # Stock M6 nut, flat sides captive in a top-loaded blind slot.
    nut_slot=base.box(0,(25.6+31.2)/2,(z-6.+d.rim-.4)/2,
                      10.4,31.2-25.6,d.rim-.4-(z-6.))
    body=body.cut(nut_slot).cut(axial_cylinder(3.2,40.,z,14.4))
    detent_pin=(cq.Workplane('XZ',origin=(-d.detent_radius,d.wheel_back+1.1,z))
                .circle(d.detent_pin_radius).extrude(1.5))
    body_core=body.clean()
    stop_pin=(cq.Workplane('XZ',origin=(-7.,d.wheel_back+.7,z)).circle(.7).extrude(1.1))
    body=body.union(detent_pin).union(stop_pin)
    seat=base.prism(d.width,d.depth,6.,d.seam,d.reveal).cut(
        base.prism(71.8,48.8,4.3,d.seam-1.,d.reveal+2.))
    for sx in (-1,1):
        for sy in (-1,1):
            corner=seat.intersect(base.box(sx*(d.width/2-6),sy*(d.depth/2-6),
                                    d.seam+d.reveal/2,8,8,d.reveal+2))
            body=body.union(corner);body_core=body_core.union(corner)
    body=body.clean();body_core=body_core.clean()
    cap=base.prism(d.width,d.depth,6.,d.rim,d.length-d.rim).edges('>Z').fillet(3.)
    cap_void=base.prism(71.8,48.8,4.3,d.rim-1.,d.length-d.rim-1.)
    cap=cap.cut(cap_void)
    # Integral outside keeper: accept accessible cap-exterior supports rather
    # than run stock screw tips/nuts into the passage or add another housing.
    crown=axial_cylinder(d.keeper_radius,29.,z,3.4).intersect(
        base.box(0,27.5,(d.rim+z+d.keeper_radius)/2,30,8,z+d.keeper_radius-d.rim))
    crown=crown.faces('>Y').edges().fillet(.35)
    left_root=base.box(-7.,27.2,(d.rim+z+14.)/2,3.,3.2,z+14.-d.rim)
    cap=cap.union(crown).union(left_root).clean()

    plate=axial_cylinder(17.,d.wheel_front,z,d.wheel_front-d.wheel_back)
    if variant=='wheel':
        for x in (-20.5,20.5):
            plate=plate.cut(cq.Workplane('XZ',origin=(x,40.,z)).circle(6.5).extrude(12.))
    else:
        hub=axial_cylinder(6.,d.wheel_front,z,d.wheel_front-d.wheel_back)
        stem=base.box(0,(d.wheel_front+d.wheel_back)/2,z+7.5,9.,d.wheel_front-d.wheel_back,15.)
        plate=plate.intersect(hub.union(stem))
    plate=plate.edges('|Y').fillet(.6).faces('>Y').edges().fillet(.5)
    nose=sector(d.nose_inner,d.nose_outer,-16.,16.,d.wheel_front,d.wheel_front-d.nose_back,z)
    rotor=plate.union(nose).cut(axial_cylinder(4.2,40,z,12.))
    rotor=rotor.cut(axial_cylinder(6.6,40,z,5.9))
    rotor_rigid=rotor
    if variant=='wheel':
        # A curved in-plane spring, printed flat. End pockets unload it at
        # LOCK/OPEN; the solid track ends are the angular travel stops.
        outer=d.detent_radius+d.detent_pin_radius-d.detent_radial_travel
        channel=sector(9.1,outer,-216.,-35.,40.,12.,z)
        for angle in (-90.,-180.):
            x=d.detent_radius*sin(radians(angle));zz=z+d.detent_radius*cos(radians(angle))
            channel=channel.union(cq.Workplane('XZ',origin=(x,40.,zz)).circle(1.6).extrude(12.))
        relief=sector(14.,15.3,-215.,-35.,40.,12.,z)
        # Free the distal end; the other end roots into the wheel at -35deg.
        end_cut=sector(9.,15.3,-216.,-208.,40.,12.,z)
        rotor=rotor.cut(channel).cut(relief).cut(end_cut)
        rotor=rotor.cut(sector(5.9,8.1,-189.,-81.,d.wheel_back+1.,1.2,z)).clean()
        spring_region=sector(outer-.1,14.1,-208.,-35.,40.,12.,z)
        rotor_rigid=rotor.cut(spring_region).clean()
    axle=printed_axle().rotate((0,0,0),(1,0,0),90).translate((0,d.axle_front,z))
    # Max stock M6 nut envelope; internal threads omitted, fit remains physical.
    nut=(cq.Workplane('XZ',origin=(0,31.,z)).polygon(6,10/cos(radians(30))).extrude(5.2)
         .cut(axial_cylinder(3.1,31.1,z,5.4))).rotate((0,0,z),(0,1,z),30.)
    parts=dict(body=body,body_core=body_core,cap=cap,rotor=rotor.clean(),
        rotor_rigid=rotor_rigid,nose=nose,detent_pin=detent_pin,pivot_axle=axle,pivot_nut=nut,
        body_void=cavity,cap_void=cap_void,stop_pin=stop_pin)
    return dict(dimensions=d,variant=variant,**{n:p.mirror('XZ') for n,p in parts.items()})


def rotor_pose(p,angle,*,rigid=False):
    z=p['dimensions'].pivot
    return p['rotor_rigid' if rigid else 'rotor'].rotate((0,0,z),(0,1,z),angle)


def configuration(p,state):
    if state not in ('locked','open','print-study'):raise ValueError(state)
    d=p['dimensions'];a=cq.Assembly(name='rotary_'+p['variant']+'_'+state)
    if state=='print-study':
        a.add(p['body'],name='body')
        a.add(p['cap'].rotate((0,0,0),(1,0,0),180).translate((100,0,d.length)),name='cap')
        a.add(p['rotor'].rotate((0,0,0),(1,0,0),90).translate((50,80+d.pivot,d.wheel_front)),name='rotor')
        a.add(printed_axle().translate((75,80,0)),name='printed_axle')
        return a
    lift=95. if state=='open' else 0.;angle=90. if state=='open' else 0.
    for name,color in (('body',(.35,.55,.65)),('cap',(.73,.79,.8)),('rotor',(.24,.36,.4))):
        part=rotor_pose(p,angle) if name=='rotor' else p[name]
        if name=='cap':part=part.translate((0,0,lift))
        a.add(part,name=name,color=cq.Color(*color))
    a.add(p['pivot_axle'],name='printed_axle',color=cq.Color(.24,.36,.4))
    a.add(p['pivot_nut'],name='stock_M6_nut',color=cq.Color(.65,.65,.65))
    return a
