"""C8: clear-interior clamshell with recessed, replaceable TPU spines.

PETG shells and TPU straps are separate single-material prints. Constant-curvature
poses exhibit one feasible folding path, not a solved flexible-joint equilibrium.
"""
from dataclasses import dataclass
import math
import cadquery as cq
from clamshell_design import base,front_parts,closure,D as C6


@dataclass(frozen=True)
class Size:
    width:float
    depth:float
    length:float=51.2
    wall:float=2.
    floor:float=2.
    corner:float=6.
    end_radius:float=4.
    @property
    def seam(self):return self.length/2


MINI=Size(64.,40.)
FULL=Size(264.,74.2)
WEB_LENGTH=16.
WEB_THICKNESS=.8
REAR_WALL=2.8


def half(d,*,rear_wall):
    outer=base.prism(d.width,d.depth,6,0,d.seam)
    outer=base.rounded_print_end(outer,d,top=False)
    extra=rear_wall-2
    cavity=base.prism(d.width-4,d.depth-4-extra,4,2,d.seam).translate((0,-extra/2,0))
    return outer.cut(cavity.edges('<Z').fillet(2)).edges('>Z').fillet(.4)


def pad(d,c,upper):
    # Shared mounting geometry; free strip occupies z=seam-8 .. seam+8.
    points=[(-4,8),(4,8),(7,10),(7,17),(-7,17),(-7,10)]
    if not upper:points=[(x,-z) for x,z in reversed(points)]
    points=[(c+x,d.seam+z) for x,z in points]
    part=cq.Workplane('XZ',origin=(0,d.depth/2,0)).polyline(points).close().extrude(.8)
    z=d.seam+(13 if upper else -13)
    for x in (c-3.2,c+3.2):
        neck=cq.Workplane('XZ',origin=(x,d.depth/2-.8,z)).circle(1.3).extrude(1.)
        head=cq.Workplane('XZ',origin=(x,d.depth/2-1.8,z)).circle(2.1).extrude(.8)
        crown=cq.Workplane(obj=cq.Solid.makeCone(2.1,1.9,.2,cq.Vector(x,d.depth/2-2.6,z),cq.Vector(0,-1,0)))
        part=part.union(neck).union(head).union(crown)
    return part.clean()


def web(d,c,angle):
    if not 0<=angle<=180:raise ValueError(angle)
    y=d.depth/2-.4;z=d.seam-8
    if angle==0:return base.box(c,y,d.seam,8,.8,16)
    theta=math.radians(angle);r=WEB_LENGTH/theta
    def point(rad,phi):return (y+r-rad*math.cos(phi),z+rad*math.sin(phi))
    return (cq.Workplane('YZ',origin=(c-4,0,0)).moveTo(*point(r+.4,0))
        .threePointArc(point(r+.4,theta/2),point(r+.4,theta))
        .lineTo(*point(r-.4,theta)).threePointArc(point(r-.4,theta/2),point(r-.4,0))
        .close().extrude(8))


def pose(d,shape,angle):
    if not 0<=angle<=180:raise ValueError(angle)
    if angle==0:return shape
    t=math.radians(angle);r=WEB_LENGTH/t
    return shape.rotate((0,d.depth/2-.4,d.seam+8),(1,d.depth/2-.4,d.seam+8),-angle).translate(
        (0,r*(1-math.cos(t)),r*math.sin(t)-WEB_LENGTH))


def strap(d,c,angle):
    return pad(d,c,False).union(web(d,c,angle)).union(pose(d,pad(d,c,True),angle)).clean()


def locator(d,x,clearance):
    # A short V seat within the existing end-wall thickness, not a cavity shelf.
    width=.8+clearance;height=.6+clearance
    return (cq.Workplane('XZ',origin=(0,4+clearance,0)).polyline(
        [(x-width,d.seam-.1),(x+width,d.seam-.1),(x,d.seam+height)])
        .close().extrude(8+2*clearance))


def build(kind,*,size):
    if kind not in ('tpu_spine','edge_pin'):raise ValueError(kind)
    d=size;rear_wall=REAR_WALL if kind=='tpu_spine' else 2.
    body=half(d,rear_wall=rear_wall)
    lid=body.mirror('XY',basePointVector=(0,0,d.seam))
    receiver,keeper,loop=front_parts('short');shift=(0,(C6.depth-d.depth)/2,0)
    receiver=receiver.translate(shift);keeper=keeper.translate(shift);loop=loop.translate(shift)
    centers=(-d.width*.22,d.width*.22)
    if kind=='tpu_spine':
        # Clearance only at the rear edge prevents the recessed neutral line
        # from driving the outer rim down during the first degrees of folding.
        body=body.cut(base.box(0,d.depth/2-1.4,d.seam, d.width+2,3.,.4))
        for c in centers:
            for upper in (False,True):
                target=lid if upper else body
                z=d.seam+(13 if upper else -13)
                pocket=base.box(c,d.depth/2-.39,z,14.4,.82,8.4)
                channel=base.box(c,d.depth/2-.39,d.seam+(4 if upper else -4),8.4,.82,8.4)
                # Taper transition is covered by a wider local pad recess.
                transition=base.box(c,d.depth/2-.39,d.seam+(9 if upper else -9),14.4,.82,2.4)
                target=target.cut(pocket.union(channel).union(transition))
                for x in (c-3.2,c+3.2):
                    hole=cq.Workplane('XZ',origin=(x,d.depth/2+.1,z)).circle(1.5).extrude(3.)
                    counter=cq.Workplane('XZ',origin=(x,d.depth/2-1.8,z)).circle(2.3).extrude(1.1)
                    target=target.cut(hole.union(counter))
                if upper:lid=target
                else:body=target
        for x in (-d.width/2+1,d.width/2-1):
            body=body.union(locator(d,x,0))
            lid=lid.cut(locator(d,x,.2))
    else:
        # Small external alternative: filament-sized bore, 2.7mm rear bump.
        r=2.3;axis=d.depth/2+.3
        for c in centers:
            def ear(lo,hi,upper):
                part=cq.Workplane('YZ',origin=(lo,axis,d.seam)).circle(r).extrude(hi-lo)
                sign=1 if upper else -1
                webpart=closure.profile(lo,[(d.depth/2-.3,d.seam),
                    (axis,d.seam),(axis,d.seam+sign*r),(d.depth/2-.3,d.seam+sign*(r+.6))],hi-lo)
                hole=cq.Workplane('YZ',origin=(lo-.1,axis,d.seam)).circle(1.05).extrude(hi-lo+.2)
                return part.union(webpart).cut(hole)
            def relief(lo,hi):
                return cq.Workplane('YZ',origin=(lo,axis,d.seam)).circle(2.6).extrude(hi-lo)
            body=body.cut(relief(c-2,c+2))
            lid=lid.cut(relief(c-5.3,c-1.7)).cut(relief(c+1.7,c+5.3))
            body=body.union(ear(c-5,c-2,False)).union(ear(c+2,c+5,False))
            lid=lid.union(ear(c-1.7,c+1.7,True))
    return dict(kind=kind,size=d,body=body.union(receiver).clean(),structural_lid=lid.clean(),
        lid=lid.union(loop).clean(),keeper=keeper,loop=loop,centers=centers)


def moving(p,shape,angle):
    d=p['size']
    if p['kind']=='tpu_spine':return pose(d,shape,angle)
    return shape.rotate((0,d.depth/2+.3,d.seam),(1,d.depth/2+.3,d.seam),-angle)


def assembly(p,angle):
    a=cq.Assembly(name='C8_'+p['kind'])
    a.add(p['body'],name='body');a.add(moving(p,p['lid'],angle),name='lid');a.add(p['keeper'],name='keeper')
    if p['kind']=='tpu_spine':
        for i,c in enumerate(p['centers']):a.add(strap(p['size'],c,angle),name='TPU_spine_'+str(i))
    return a


def print_layout(material):
    if material not in ('PETG','TPU'):raise ValueError(material)
    p=build('tpu_spine',size=MINI);d=MINI;a=cq.Assembly(name='C8_mini_'+material)
    if material=='PETG':
        a.add(p['body'],name='body')
        a.add(p['lid'].rotate((0,0,0),(1,0,0),180).translate((78,0,d.length)),name='lid')
        a.add(closure.keeper().rotate((0,0,0),(0,1,0),-90).translate((155,22.1,5.5)),name='keeper')
    else:
        for i,c in enumerate(p['centers']):
            part=strap(d,c,0).rotate((0,0,0),(1,0,0),-90).translate((0,-d.seam+17,d.depth/2))
            a.add(part,name='spine_'+str(i))
    return a
