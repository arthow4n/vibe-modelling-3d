"""M2B: flat retaining shoulders, long guide and shorter accessible leaves.

M1 remains the printed failed baseline; M2A undercut geometry is retained in
m2_design.py as a rejected manufacturing investigation. Builders publish nothing.
"""
from dataclasses import dataclass
import cadquery as cq
import m1_design as m1


@dataclass(frozen=True)
class Dimensions(m1.Dimensions):
    lap: float = 30.
    axial_play: float = .25
    beam_length: float = 32.
    hook_width: float = 9.
    shelf_side_margin: float = 1.
    skin_reinforcement: float = .8
    pocket_outer_skin: float = .5

    @property
    def press_z(self):
        return self.seam-4


D=Dimensions()


def hook(d,displacement=0):
    return m1.hook(d,displacement)


def tongue(d,displacement=0):
    return m1.tongue(d,displacement)


def body_fixed(d):
    part=m1.body_fixed(d)
    # Open the existing guarded control to the rim rather than placing the raised
    # pad behind its old gabled roof. The cap begins above the recessed control.
    inner=d.beam_outer+.8
    outer=d.width/2+1
    low,high=d.press_z-3,d.seam+.1
    port=m1.box(d.catch_y,(inner+outer)/2,(low+high)/2,
                d.beam_width+2*d.slot,outer-inner,high-low)
    for sign in (-1,1):
        part=part.cut(m1.at_end(port,sign))
    return part.clean()


def cap(d):
    outer=m1.prism(d.width,d.depth,d.corner,d.seam,d.length-d.seam)
    outer=m1.rounded_print_end(outer,d,top=True).edges('<Z').fillet(.6)
    cavity=cq.Workplane(obj=cq.Solid.makeLoft([
        m1.rounded_wire(d.width-2*t,d.depth-2*t,d.corner-t,z)
        for z,t in ((d.seam-1,d.receiver_wall),(d.seam+d.lap+2,d.receiver_wall),
                    (d.seam+d.lap+6,d.wall),(d.length-d.floor,d.wall))],ruled=True))
    cavity=cavity.edges('>Z').fillet(d.end_radius-d.wall)
    part=outer.cut(cavity)
    for sign in (-1,1):
        y=d.width/2
        rib=(cq.Workplane('YZ',origin=(-d.hook_width/2-4,0,0))
             .polyline([(y-.3,d.seam+.8),(y+d.skin_reinforcement,d.seam+.8),
                        (y+d.skin_reinforcement,d.seam+d.lap+1),
                        (y-.3,d.seam+d.lap+2.1)]).close().extrude(d.hook_width+8))
        part=part.union(m1.at_end(rib,sign))
    a,b=d.hook_width/2+d.shelf_side_margin,d.hook_width/2+3
    bottom=d.hook_bottom-d.axial_play
    outline=[(-a,bottom),(a,bottom),(b,bottom+b-a),(b,d.hook_bottom+7),
             (3,d.hook_bottom+11),(-3,d.hook_bottom+11),(-b,d.hook_bottom+7),
             (-b,bottom+b-a)]
    for sign in (-1,1):
        pocket=(cq.Workplane('XZ',origin=(d.catch_y,d.width/2-d.pocket_outer_skin,0))
                .polyline(outline).close().extrude(d.receiver_wall+.3-d.pocket_outer_skin))
        part=part.cut(m1.at_end(pocket,sign))
    return part.clean()


def build(d=D):
    if not d.length>d.seam+d.lap>d.beam_tip>d.seam>d.press_z>d.beam_root+1:
        raise ValueError('M2B longitudinal ordering invalid')
    fixed=body_fixed(d)
    lower=fixed
    for sign in (-1,1):
        lower=lower.union(m1.mirrored(tongue(d),sign))
    upper=cap(d)
    assembly=cq.Assembly(name='m2b_research_print')
    assembly.add(lower.clean(),name='body')
    assembly.add(m1.print_cap(upper,d.length),name='cap')
    return dict(dimensions=d,fixed=fixed,body=lower.clean(),cap=upper,
                references=m1.references(d),result=assembly)


def configuration(parts,*,cap_lift,releases):
    d=parts['dimensions']
    assembly=cq.Assembly(name='m2b')
    assembly.add(parts['fixed'],name='body_fixed')
    for sign,delta in zip((-1,1),releases,strict=True):
        assembly.add(m1.mirrored(tongue(d,delta),sign),name='catch_'+str(sign))
    assembly.add(parts['cap'],name='cap',loc=cq.Location(cq.Vector(0,0,cap_lift)))
    return assembly
