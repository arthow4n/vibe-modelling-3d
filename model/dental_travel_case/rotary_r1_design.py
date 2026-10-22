"""R1a: visible swivel-tab coupon. Three printed parts, M3x12 and two M3 nuts.

Z opens the cap. The operating control is on -Y. Angles: 0 locked, 90 parked.
A concentric keeper/nose permits rotation without an axial draw-in ramp.
"""
from dataclasses import dataclass
from math import sin, cos, radians
import cadquery as cq
import m1_design as base


@dataclass(frozen=True)
class Dimensions:
    width: float = 75.8
    depth: float = 52.8
    seam: float = 14.
    lap: float = 30.
    reveal: float = 3.
    pivot_z: float = 8.
    keeper_radius: float = 12.5
    nose_inner: float = 13.3
    nose_outer: float = 15.7
    tab_inner_y: float = 27.
    tab_outer_y: float = 29.4
    nose_inner_y: float = 24.8
    guide_clearance: float = .3

    @property
    def sleeve_top(self):return self.seam+self.lap
    @property
    def cap_top(self):return self.sleeve_top+6.
    @property
    def rim(self):return self.seam+self.reveal


D = Dimensions()


def yz_prism(points,start,width):
    return cq.Workplane('YZ',origin=(start,0,0)).polyline(points).close().extrude(width)


def axial_cylinder(radius,y,z,length):
    return cq.Workplane('XZ',origin=(0,y,z)).circle(radius).extrude(length)


def sector(ri,ro,start,finish,y,depth,z):
    a,b,m=map(radians,(start,finish,(start+finish)/2))
    return (cq.Workplane('XZ',origin=(0,y,z)).moveTo(ro*sin(a),ro*cos(a))
            .threePointArc((ro*sin(m),ro*cos(m)),(ro*sin(b),ro*cos(b)))
            .lineTo(ri*sin(b),ri*cos(b))
            .threePointArc((ri*sin(m),ri*cos(m)),(ri*sin(a),ri*cos(a)))
            .close().extrude(depth))


def build():
    d=D
    sleeve_w,sleeve_h=71.2,48.2
    iw,ih=sleeve_w+2*d.guide_clearance,sleeve_h+2*d.guide_clearance
    outer=base.prism(d.width,d.depth,6.,0,d.seam).edges('<Z').chamfer(.25)
    outer=outer.union(base.prism(sleeve_w,sleeve_h,4.,d.seam-.5,d.lap+.5))
    pad=yz_prism([(23.8,2.),(26.8,2.),(26.8,11.2),(24.,14.),(23.8,14.)],-6.,12.)
    outer=outer.union(pad)
    cavity=cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (-1.,71.8,48.8,4.),(d.seam-6.,71.8,48.8,4.),
            (d.seam,67.2,44.2,2.),(d.sleeve_top+1.,67.2,44.2,2.))],ruled=True))
    body=outer.cut(cavity)
    body=body.cut(axial_cylinder(1.8,35.,d.pivot_z,22.))
    # Nut/pliers access from the interior; the gabled ceiling prints upright.
    access=(cq.Workplane('XZ',origin=(0,24.4,d.pivot_z)).polyline([
        (-4.8,-4.),(4.8,-4.),(4.8,1.2),(0.,6.),(-4.8,1.2)])
        .close().extrude(12.))
    body=body.cut(access)
    # Small angular stops with 45-degree lower growth in the upright print.
    locked_stop=yz_prism([(23.8,11.4),(26.4,11.4),(27.5,12.5),(24.,16.),(23.8,16.)],-5.2,1.4)
    parked_stop=yz_prism([(26.2,1.8),(27.8,3.4),(26.2,5.)],6.,4.)
    body_core=body.union(locked_stop).union(parked_stop).clean()
    # Four corner seats hold the 3 mm reveal without an internal cap overhang.
    seat_ring=base.prism(d.width,d.depth,6.,d.seam,d.reveal).cut(
        base.prism(iw,ih,4.3,d.seam-1,d.reveal+2))
    for sx in (-1,1):
        for sy in (-1,1):
            pad=seat_ring.intersect(base.box(sx*(d.width/2-6),sy*(d.depth/2-6),
                                             d.seam+d.reveal/2,8.,8.,d.reveal+2))
            body_core=body_core.union(pad)
    body_core=body_core.clean()
    # Recess only the inward nose sweep. Backing stays outside the existing
    # minimum sleeve passage; its inward buildup grows over a 45-degree ramp.
    backing=yz_prism([(24.3,0),(26.4,0),(26.4,14.),(22.1,14.),(22.1,2.3)],7.,12.)
    parking=sector(13.,16.,-18.,108.,30.,5.6,d.pivot_z)
    body_core=body_core.union(backing).cut(parking).clean()
    bump=cq.Workplane('XY').sphere(.6).translate((2.8,26.6,d.pivot_z+2.8))
    body=body_core.union(bump).clean()

    cap=base.prism(d.width,d.depth,6.,d.rim,d.cap_top-d.rim)
    cap=cap.cut(base.prism(iw,ih,4.3,d.rim-1,d.cap_top-d.rim+2))
    window=(cq.Workplane('XZ',origin=(0,33.,0)).polyline([
        (-5.4,d.rim-1),(18.,d.rim-1),(18.,24.6),(6.3,36.3),(-5.4,24.6)])
        .close().extrude(12.))
    keeper_disk=axial_cylinder(d.keeper_radius,33.,d.pivot_z,14.)
    # Leave a concentric crown on the lower rim, instead of a square shelf corner.
    cap=cap.cut(window.cut(keeper_disk)).clean()
    keeper=cap.intersect(window).clean()

    tab=axial_cylinder(5.5,d.tab_outer_y,d.pivot_z,d.tab_outer_y-d.tab_inner_y)
    stem=base.box(0,(d.tab_inner_y+d.tab_outer_y)/2,d.pivot_z+(d.nose_outer+.2)/2,
                  7.,d.tab_outer_y-d.tab_inner_y,d.nose_outer+.2)
    tab=tab.union(stem)
    a=radians(16.)
    ri,ro=d.nose_inner,d.nose_outer
    nose=(cq.Workplane('XZ',origin=(0,d.tab_outer_y,d.pivot_z))
          .moveTo(-ro*sin(a),ro*cos(a)).threePointArc((0,ro),(ro*sin(a),ro*cos(a)))
          .lineTo(ri*sin(a),ri*cos(a)).threePointArc((0,ri),(-ri*sin(a),ri*cos(a)))
          .close().extrude(d.tab_outer_y-d.nose_inner_y))
    tab=tab.union(nose).cut(axial_cylinder(1.8,35.,d.pivot_z,15.))
    for x in (-2.8,2.8):
        pocket=cq.Workplane('XY').sphere(.85).translate((x,26.6,d.pivot_z+2.8))
        tab=tab.cut(pocket)
    tab=tab.clean()
    # Mirror to show the control in the evaluator's normal front/isometric views.
    return dict(dimensions=d,**{n:p.mirror('XZ') for n,p in
                dict(body=body,body_core=body_core,cap=cap,tab=tab,
                     keeper=keeper,nose=nose,bump=bump).items()})


def tab_pose(parts,angle):
    d=parts['dimensions']
    return parts['tab'].rotate((0,0,d.pivot_z),(0,1,d.pivot_z),angle)


def hardware(parts):
    """Display-only nominal M3 geometry; threads deliberately not modelled."""
    d=parts['dimensions']
    shaft=axial_cylinder(1.5,29.7,d.pivot_z,12.)
    head=axial_cylinder(2.75,31.7,d.pivot_z,2.)
    bolt=shaft.union(head)
    nuts=[]
    for front in (24.2,21.8):
        n=(cq.Workplane('XZ',origin=(0,front,d.pivot_z)).polygon(6,5.5/cos(radians(30)))
           .extrude(2.4).cut(axial_cylinder(1.6,front+.1,d.pivot_z,2.6)))
        nuts.append(n.mirror('XZ'))
    return dict(bolt=bolt.mirror('XZ'),nut_inner=nuts[0],nut_jam=nuts[1])


def configuration(parts,state):
    if state not in ('print','locked','unlocked','open'):
        raise ValueError('Unknown R1a state: '+str(state))
    d=parts['dimensions'];out=cq.Assembly(name='R1a_'+state)
    if state=='print':
        out.add(parts['body'],name='body')
        out.add(parts['cap'].translate((100,0,-d.rim)),name='cap')
        out.add(parts['tab'].rotate((0,0,0),(1,0,0),90).translate((50,80+d.pivot_z,d.tab_outer_y)),name='tab')
    else:
        angle=0. if state=='locked' else 90.
        lift=36. if state=='open' else 0.
        out.add(parts['body'],name='body',color=cq.Color(.4,.65,.8))
        out.add(parts['cap'].translate((0,0,lift)),name='cap',color=cq.Color(.9,.7,.4))
        out.add(tab_pose(parts,angle),name='tab',color=cq.Color(.35,.7,.5))
        for name,part in hardware(parts).items():out.add(part,name=name,color=cq.Color(.6,.65,.7))
    return out
