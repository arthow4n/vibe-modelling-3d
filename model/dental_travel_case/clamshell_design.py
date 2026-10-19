"""C6 horizontal dental case: compact rear connections and explicit-release loop.

Dimensions in mm. Cavity follows the accepted slim M1 main interior, rotated
horizontal. No global wall-flex detents or long withdrawal sleeve. No side effects.
"""
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import math
import cadquery as cq
import m1_design as base

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sunglasses_e_components',ROOT.parent/'sunglasses_case/e_closure.py')
closure=importlib.util.module_from_spec(spec);spec.loader.exec_module(closure)
KINDS=('screw_pin','filament_pin','lift_off')


@dataclass(frozen=True)
class Dimensions:
    width:float=264.
    depth:float=74.2
    length:float=51.2
    wall:float=2.
    floor:float=2.
    corner:float=6.
    end_radius:float=4.
    @property
    def seam(self):return self.length/2


D=Dimensions()
SEATED_GAP=.35  # E's .20 plus .15 for the shortened loop's bending-tip motion


def short_loop():
    """Keep E's rail/contact position; move roots 7.5mm toward rail, thin leaves.

    Root-to-upper-rail span20 vs27.5; clear span to lower rail17 vs24.5.
    Thickness1.8 vs2.8. This is a NEW unprinted
    flexure, not physical transfer of E's release effort or durability.
    """
    inner=closure.LOOP_WALL_GAP;outer=inner+1.8
    front=2*closure.REFERENCE_HY+closure.REFERENCE_DEPTH/2
    def out(x,points,width):
        return closure.profile(x,[(front+r,z) for r,z in points],width)
    parts=[]
    for x in (-9.,6.):
        root=out(x,[(-.6,9),(outer,9+outer+.6),(outer,19),(-.6,19)],3)
        leaf=out(x,[(inner,17.5),(outer,17.5),(outer,39),(inner,39)],3)
        part=root.union(leaf).edges(cq.selectors.NearestToPointSelector((x+1.5,front+inner,19))).fillet(.8)
        parts.append(part)
    rail=out(-9,[(inner,36),(outer,36),(outer,39),(inner,39)],18)
    grip=out(-4,[(outer-.1,37),(outer+.8,37.9),(outer+.8,38.8),(outer-.1,38.8)],8)
    return parts[0].union(parts[1]).union(rail).union(grip).clean()


def front_parts(loop_kind):
    if loop_kind not in ('short','accepted_e'):raise ValueError(loop_kind)
    receiver=closure.receiver().translate((0,-D.depth/2+20,D.seam-30))
    keeper=closure.keeper().translate((0,-D.depth/2+20,D.seam-30))
    original=short_loop() if loop_kind=='short' else closure.loop()
    # Open E reference is turned over into the closed lid's front-wall frame.
    loop=original.rotate((0,closure.REFERENCE_HY,30),(1,closure.REFERENCE_HY,30),180)
    loop=loop.translate((0,-D.depth/2+20,D.seam-30))
    if loop_kind=='short':loop=loop.translate((0,0,-(SEATED_GAP-.2)))
    return receiver,keeper,loop


def half():
    outer=base.prism(D.width,D.depth,D.corner,0,D.seam)
    outer=base.rounded_print_end(outer,D,top=False)
    cavity=base.prism(D.width-4,D.depth-4,D.corner-2,2,D.seam)
    cavity=cavity.edges('<Z').fillet(2)
    return outer.cut(cavity).edges('>Z').fillet(.4)


def barrel(x0,x1,axis_y,radius,*,lid):
    r=radius;t=r/math.sqrt(2)
    profile=(cq.Workplane('YZ',origin=(x0,axis_y,D.seam)).moveTo(0,-r*math.sqrt(2))
        .lineTo(t,-t).threePointArc((r,0),(0,r)).threePointArc((-r,0),(-t,-t)).close().extrude(x1-x0))
    if lid: profile=profile.mirror('XY',basePointVector=(0,0,D.seam))
    low=D.seam-r*math.sqrt(2)-(axis_y-D.depth/2+.3)
    points=[(D.depth/2-.3,low),(axis_y,D.seam-r*math.sqrt(2)),(axis_y,D.seam),(D.depth/2-.3,D.seam)]
    web=cq.Workplane('YZ',origin=(x0,0,0)).polyline(points).close().extrude(x1-x0)
    if lid:web=web.mirror('XY',basePointVector=(0,0,D.seam))
    return profile.union(web)


def build(kind,*,loop_kind='short'):
    if kind not in KINDS:raise ValueError(kind)
    bottom=half();top=bottom.rotate((0,0,D.seam),(1,0,D.seam),180)
    receiver,keeper,loop=front_parts(loop_kind)
    body=bottom.union(receiver);lid=top.union(loop)
    radius=3.8 if kind=='screw_pin' else 2.6
    axis_y=D.depth/2+radius+.3
    if kind!='lift_off':
        bore=1.7 if kind=='screw_pin' else 1.05
        for center in (-84.,84.):
            # 7mm ear stack leaves nominal 5mm on an M3x12 for two jam nuts.
            # Nuts lock against one another rather than squeezing the moving ear.
            fixed=barrel(center-3.5,center-1.9,axis_y,radius,lid=False).union(
                barrel(center+1.9,center+3.5,axis_y,radius,lid=False))
            moving=barrel(center-1.6,center+1.6,axis_y,radius,lid=True)
            hole=cq.Workplane('YZ',origin=(center-6,axis_y,D.seam)).circle(bore).extrude(12)
            body=body.union(fixed.cut(hole));lid=lid.union(moving.cut(hole))
    else:
        # Rough lift-off alternative: two rear tongues entering outside pockets.
        # These are visualization geometry; a complete extraction path is not
        # qualified and this variant is not published as printable.
        for center in (-84.,84.):
            receiver=base.box(center,39.1,D.seam-2,12,4.6,4)
            pocket=base.box(center,39.1,D.seam-.8,8.6,2.6,3)
            body=body.union(receiver.cut(pocket))
            tongue=base.box(center,39.1,D.seam-.5,8,2,2.4)
            neck=base.box(center,37.8,D.seam+.5,8,2,1)
            lid=lid.union(neck).union(tongue)
    return dict(kind=kind,body=body.clean(),lid=lid.clean(),keeper=keeper,loop=loop,
        receiver=front_parts(loop_kind)[0],shell_lid=top,axis_y=axis_y,hinge_radius=radius,
        loop_kind=loop_kind)


def posed(parts,angle):
    if parts['kind']=='lift_off':
        return parts['lid'].translate((0,0,angle/15))
    return parts['lid'].rotate((0,parts['axis_y'],D.seam),(1,parts['axis_y'],D.seam),-angle)


def assembly(parts,angle=0):
    a=cq.Assembly(name='C6_'+parts['kind'])
    a.add(parts['body'],name='body');a.add(posed(parts,angle),name='lid');a.add(parts['keeper'],name='keeper')
    return a


def print_part(name):
    p=build('screw_pin')
    if name=='body':part=p['body']
    elif name=='lid':part=p['lid'].rotate((0,0,0),(1,0,0),180).translate((0,0,D.length))
    elif name=='keeper':return closure.keeper().rotate((0,0,0),(0,1,0),-90).translate((29.4,22.1,5.5))
    else:raise ValueError(name)
    return part.rotate((0,0,0),(0,0,1),45)
