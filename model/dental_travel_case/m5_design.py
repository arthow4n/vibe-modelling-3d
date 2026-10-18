"""M5 space study: short catch guards, perimeter guidance, flat exterior.

The selected flat77 version keeps M4's 77mm maximum width, exact leaves and
retaining pocket. Broad sides grow from 75 to 77mm; their raised ribs disappear.
Candidate builders retain rejected alternatives without publishing them.
"""
from dataclasses import dataclass, replace
import cadquery as cq
import m1_design as m1
import m2b_design as m2
import m4_design as m4


@dataclass(frozen=True)
class Dimensions(m4.Dimensions):
    width: float = 77.
    receiver_wall: float = 3.7
    pocket_outer_skin: float = 1.5
    skin_reinforcement: float = 0.
    guard_lap: float = 16.
    guide_notch_half: float = 9.
    broad_wall: float = 2.7
    matched_corner_bearing: bool = True

    @property
    def sleeve_width(self): return self.width-2*(self.wall+self.lap_clearance)

    @property
    def sleeve_depth(self): return self.depth-2*(self.broad_wall+self.lap_clearance)

    @property
    def sleeve_corner(self):
        offset=self.broad_wall if self.matched_corner_bearing else self.wall
        return self.corner-offset-self.lap_clearance

    @property
    def beam_outer(self): return self.width/2-self.receiver_wall-self.lap_clearance


D=Dimensions()
hook=m1.hook
tongue=m1.tongue


def guide(d, bottom):
    """Continuous 1.6mm stepped hoop, with longitudinal receiver travel reliefs."""
    top=d.seam+d.lap
    outer=m1.prism(d.sleeve_width,d.sleeve_depth,d.sleeve_corner,bottom,top-bottom)
    inner=m1.prism(d.sleeve_width-2*d.lap_wall,d.sleeve_depth-2*d.lap_wall,
                   d.sleeve_corner-d.lap_wall,bottom-1,top-bottom+2)
    for sign in (-1,1):
        for shape_name in ('outer','inner'):
            inset=0 if shape_name=='outer' else d.lap_wall
            edge=d.beam_outer-inset
            cut=m1.box(sign*(edge+10),0,(bottom+top)/2,20,
                       2*(d.guide_notch_half+inset),top-bottom+4)
            if shape_name=='outer':outer=outer.cut(cut)
            else:inner=inner.cut(cut)
    return outer.cut(inner).edges('>Z').chamfer(.6)


def body_fixed(d):
    # Existing construction preserves the root blends, controls and closed guard.
    # Only the guard's otherwise empty continuation above the leaf is removed.
    end=d.seam+d.guard_lap
    fixed=m2.body_fixed(replace(d,lap=d.guard_lap))
    for sign in (-1,1):
        cut=m1.box(sign*(d.beam_outer+10),0,(d.seam+end+1)/2,
                   20,2*d.guide_notch_half,end+1-d.seam)
        fixed=fixed.cut(cut)
    return fixed.union(guide(d,end-.6)).clean()


def cap(d):
    outer=m1.prism(d.width,d.depth,d.corner,d.seam,d.length-d.seam)
    outer=m1.rounded_print_end(outer,d,top=True).edges('<Z').fillet(.6)
    band=d.broad_wall if d.matched_corner_bearing else d.wall
    cavity=cq.Workplane(obj=cq.Solid.makeLoft([
        m1.rounded_wire(d.width-2*d.wall,d.depth-2*t,d.corner-t,z)
        for z,t in ((d.seam-1,band),(d.seam+d.lap+2,band),
                    (d.seam+d.lap+6,d.wall),(d.length-d.floor,d.wall))],ruled=True))
    cavity=cavity.edges('>Z').fillet(d.end_radius-d.wall)
    part=outer.cut(cavity)
    # Keep the old full-height reinforced receiver strip in its original world
    # position, while replacing the surrounding inward band by the 2mm shell.
    for sign in (-1,1):
        inner=d.width/2-d.receiver_wall
        wall_inner=d.width/2-d.wall
        strip=(cq.Workplane('XZ',origin=(0,8.5,0)).polyline([
            (inner,d.seam),(d.width/2,d.seam),(d.width/2,d.seam+d.lap+6),
            (wall_inner,d.seam+d.lap+6),(inner,d.seam+d.lap+2)])
            .close().extrude(17))
        if sign==-1:strip=strip.mirror('YZ')
        part=part.union(strip.intersect(outer))
    # Keep M4's broad-face thickness through the guide-bearing region. A 2mm
    # alternative gained room but reduced cap-section bending stiffness.
    for sign in (-1,1):
        inside=d.depth/2-d.broad_wall
        wall_inner=d.depth/2-d.wall
        panel=(cq.Workplane('YZ',origin=(-d.width/2,0,0)).polyline([
            (inside,d.seam),(d.depth/2,d.seam),(d.depth/2,d.seam+d.lap+6),
            (wall_inner,d.seam+d.lap+6),(inside,d.seam+d.lap+2)])
            .close().extrude(d.width))
        if sign==-1:panel=panel.mirror('XZ')
        part=part.union(panel.intersect(outer))
    a,b=d.hook_width/2+d.shelf_side_margin,d.hook_width/2+3
    bottom=d.hook_bottom-d.axial_play
    outline=[(-a,bottom),(a,bottom),(b,bottom+b-a),(b,d.hook_bottom+7),
             (3,d.hook_bottom+11),(-3,d.hook_bottom+11),(-b,d.hook_bottom+7),(-b,bottom+b-a)]
    for sign in (-1,1):
        pocket=(cq.Workplane('XZ',origin=(d.catch_y,d.width/2-d.pocket_outer_skin,0))
            .polyline(outline).close().extrude(d.receiver_wall+.3-d.pocket_outer_skin))
        part=part.cut(m1.at_end(pocket,sign))
    return part.clean()


def build(d=D):
    if not d.beam_tip<d.seam+d.guard_lap<d.seam+d.lap<d.length-d.floor-6:
        raise ValueError('Guard, guide and cap roof ordering invalid')
    fixed=body_fixed(d)
    body=fixed
    for sign in (-1,1):body=body.union(m1.mirrored(tongue(d),sign))
    upper=cap(d)
    result=cq.Assembly(name='m5_print')
    result.add(body.clean(),name='body')
    result.add(m1.print_cap(upper,d.length),name='cap')
    return dict(dimensions=d,fixed=fixed,body=body.clean(),cap=upper,
                references=m1.references(d),result=result)


def build_candidate(name):
    if name=='M4':return m4.build()
    if name in ('short_guard','thin_sleeve'):
        d=m4.D if name=='short_guard' else replace(m4.D,lap_wall=1.2)
        end=d.seam+16
        fixed=m2.body_fixed(replace(d,lap=16.))
        ring=m1.prism(d.sleeve_width,d.sleeve_depth,d.sleeve_corner,end-.6,d.lap-16+.6)
        ring=ring.cut(m1.prism(d.sleeve_width-2*d.lap_wall,d.sleeve_depth-2*d.lap_wall,
                     d.sleeve_corner-d.lap_wall,end-1,d.lap-16+2)).edges('>Z').chamfer(min(.6,d.lap_wall/3 if d.lap_wall<1.6 else .6))
        fixed=fixed.union(ring).clean()
        parts=m4.build(d)
        body=fixed
        for sign in (-1,1):body=body.union(m1.mirrored(tongue(d),sign))
        parts.update(fixed=fixed,body=body.clean())
        return parts
    if name=='flat75':return build(replace(D,width=75.))
    if name=='flat77_light_cap':return build(replace(D,broad_wall=2.))
    if name=='flat77_loose_corners':return build(replace(D,matched_corner_bearing=False))
    if name=='flat77':return build()
    raise ValueError('Unknown space candidate: '+str(name))
