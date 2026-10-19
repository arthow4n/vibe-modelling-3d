"""C7 exploration: recessed pivots and a complete, short functional box.

All hinge material stays inside the closed rear silhouette. The segmented,
curved rear seam is essential: merely translating the C6 hinge inward jams it.
No publication side effects. Dimensions in mm; C6 loop/keeper remain unchanged.
"""
from dataclasses import dataclass
import cadquery as cq
from clamshell_design import base, front_parts, closure, D as C6


@dataclass(frozen=True)
class Size:
    width: float
    depth: float
    length: float = 51.2
    wall: float = 2.
    floor: float = 2.
    corner: float = 6.
    end_radius: float = 4.

    @property
    def seam(self): return self.length/2
    @property
    def axis_y(self): return self.depth/2-6.2


MINI = Size(64., 40.)
FULL = Size(264., 74.2)
KINDS = ('naive_internal', 'raised_seam', 'internal_screw', 'internal_cone')


def shell(d):
    outer=base.prism(d.width,d.depth,d.corner,0,d.seam)
    outer=base.rounded_print_end(outer,d,top=False)
    void=base.prism(d.width-4,d.depth-4,d.corner-2,2,d.seam)
    return outer.cut(void.edges('<Z').fillet(2)).edges('>Z').fillet(.4)


def cylinder(d, radius):
    return cq.Workplane('YZ',origin=(-d.width, d.axis_y,d.seam)).circle(radius).extrude(2*d.width)


def ear(d,x0,x1,lid):
    # Teardrop lower outline; mirrored for roof-down lid printing.
    r=3.6;t=r/2**.5
    part=(cq.Workplane('YZ',origin=(x0,d.axis_y,d.seam)).moveTo(0,-r*2**.5)
        .lineTo(t,-t).threePointArc((r,0),(0,r))
        .threePointArc((-r,0),(-t,-t)).close().extrude(x1-x0))
    web=closure.profile(x0,[(d.axis_y,d.seam-r*2**.5),
        (d.depth/2-.7,d.seam-r*2**.5-(6.2-.7)),
        (d.depth/2-.7,d.seam-8.6),(d.axis_y,d.seam-3.5)],x1-x0)
    part=part.union(web)
    return part.mirror('XY',basePointVector=(0,0,d.seam)) if lid else part


def cone(d,x,r,direction):
    return cq.Workplane(obj=cq.Solid.makeCone(r,.12,r-.12,
        cq.Vector(x,d.axis_y,d.seam),cq.Vector(direction,0,0)))


def build(kind, *, size):
    if kind not in KINDS: raise ValueError(kind)
    d=size;bottom=shell(d);top=bottom.rotate((0,0,d.seam),(1,0,d.seam),180)
    if kind=='naive_internal': body,lid=bottom,top
    elif kind=='raised_seam':
        body=bottom.union(top.intersect(cylinder(d,8.)))
        lid=top.cut(cylinder(d,8.4))
    else:
        # Curved lower seam: moving rear skirt travels in the relieved radius.
        # Fixed-ear stations reverse that seam so each web retains its own wall.
        body=bottom.cut(cylinder(d,10.4))
        lid=top.union(bottom.intersect(cylinder(d,10.)))
    receiver,keeper,loop=front_parts('short')
    shift=(0,(C6.depth-d.depth)/2,0)
    receiver=receiver.translate(shift);keeper=keeper.translate(shift);loop=loop.translate(shift)
    body=body.union(receiver)
    spacing=10. if d.width<100 else d.width*.3
    centers=(-spacing,spacing)
    for c in centers:
        if kind=='internal_cone':
            # Opposed cones: .6 radial (about .424 normal), .5 axial clearance.
            fixed=ear(d,c-6,c-3,False).union(ear(d,c+3,c+6,False))
            fixed=fixed.union(cone(d,c-3,2.2,1)).union(cone(d,c+3,2.2,-1))
            moving=ear(d,c-2.5,c+2.5,True)
            moving=moving.cut(cone(d,c-3,2.8,1)).cut(cone(d,c+3,2.8,-1))
        else:
            fixed=ear(d,c-3.5,c-1.9,False).union(ear(d,c+1.9,c+3.5,False))
            moving=ear(d,c-1.6,c+1.6,True)
            hole=cq.Workplane('YZ',origin=(c-6,d.axis_y,d.seam)).circle(1.7).extrude(12)
            fixed=fixed.cut(hole);moving=moving.cut(hole)
        if kind in ('internal_screw','internal_cone'):
            intervals=((c-6,c-3),(c+3,c+6)) if kind=='internal_cone' else ((c-3.5,c-1.9),(c+1.9,c+3.5))
            for lo,hi in intervals:
                # Extra .3 axial relief keeps the rotating rear-wall slot clear.
                strip=base.box((lo+hi)/2,d.axis_y,d.seam,hi-lo+.6,30,30)
                lid=lid.cut(strip.intersect(cylinder(d,10.4)))
                # Keep .3mm per side between fixed rear strips and moving skirt.
                # Equal-width cut/fill gives zero-volume contact and can fuse.
                fixed_strip=base.box((lo+hi)/2,d.axis_y,d.seam,hi-lo,30,30)
                fixed_wall=bottom.union(top).intersect(fixed_strip).intersect(cylinder(d,10.))
                body=body.union(fixed_wall)
        body=body.union(fixed);lid=lid.union(moving)
    structure=lid.clean()
    return dict(kind=kind,size=d,body=body.clean(),lid=structure.union(loop).clean(),structural_lid=structure,keeper=keeper,
        loop=loop,axis_y=d.axis_y,centers=centers)


def rotate(p,part,angle):
    d=p['size']
    return part.rotate((0,d.axis_y,d.seam),(1,d.axis_y,d.seam),-angle)


def assembly(p,angle):
    a=cq.Assembly(name='C7_'+p['kind'])
    a.add(p['body'],name='body');a.add(rotate(p,p['lid'],angle),name='lid')
    a.add(p['keeper'],name='keeper')
    return a


def print_layout(kind):
    if kind not in ('internal_screw','internal_cone'):raise ValueError(kind)
    p=build(kind,size=MINI);d=MINI
    a=cq.Assembly(name='C7_mini_'+kind)
    if kind=='internal_screw':
        a.add(p['body'],name='body')
        lid=p['lid'].rotate((0,0,0),(1,0,0),180).translate((78,0,d.length))
        a.add(lid,name='lid')
        offset=(155,22.1,5.5)
    else:
        # End-on, 90-degree-open trial: both short end walls start on the bed.
        # Full 264mm case cannot inherit this 64mm-tall print orientation.
        for name in ('body','lid'):
            part=p[name] if name=='body' else rotate(p,p[name],90)
            part=part.rotate((0,0,0),(0,1,0),-90).translate((0,0,d.width/2))
            a.add(part,name=name)
        offset=(50,70,5.5)
    keeper=closure.keeper().rotate((0,0,0),(0,1,0),-90).translate(offset)
    a.add(keeper,name='keeper')
    return a
