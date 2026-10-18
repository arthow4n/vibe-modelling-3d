"""M2 research candidate: long guide, outward-seating retaining faces.

Preserves M1 as the failed printed baseline. Geometry is provisional until the
retention study resolves both shell contact and intentional operation.
"""
from dataclasses import dataclass
import math
import cadquery as cq
import m1_design as m1


@dataclass(frozen=True)
class Dimensions(m1.Dimensions):
    lap: float = 30.
    hook_width: float = 9.
    gusset_width: float = 1.2
    gusset_relief_inner: float = 4.15
    gusset_relief_outer: float = 6.05
    axial_play: float = .65
    retaining_angle_deg: float = 7.
    shelf_side_margin: float = 1.
    skin_reinforcement: float = .8
    pocket_outer_skin: float = .5


D = Dimensions()


def hook_core(d, displacement=0):
    y = d.beam_outer
    slope = math.tan(math.radians(d.retaining_angle_deg))
    points = [(y-.3,d.hook_bottom+.3*slope),
              (y+d.hook_projection,d.hook_bottom-d.hook_projection*slope),
              (y+d.hook_projection,d.hook_bottom+1.2),
              (y,d.beam_tip),(y-.3,d.beam_tip)]
    part = (cq.Workplane('YZ',origin=(d.catch_y-d.hook_width/2,0,0))
            .polyline([(r-m1.leaf_offset(d,z,displacement),z) for r,z in points])
            .close().extrude(d.hook_width))
    return part.edges('|X and >Y').fillet(.25)


def hook(d, displacement=0):
    """Retaining tooth with integral supported end gussets.

    The outward-descending retaining face alone starts as a floating print island.
    Side gussets grow outward at about 45 degrees, making its first central layer
    a bridge between attached ends. Receiver side channels clear these gussets.
    """
    part=hook_core(d,displacement)
    y=d.beam_outer
    outer_bottom=d.hook_bottom-d.hook_projection*math.tan(math.radians(d.retaining_angle_deg))
    points=[(y-.2,d.hook_bottom-2.6),(y+d.hook_projection,outer_bottom),
            (y+d.hook_projection,d.hook_bottom+1.2),(y-.2,d.hook_bottom+1.2)]
    for x in (-d.hook_width/2-d.gusset_width,d.hook_width/2):
        side=(cq.Workplane('YZ',origin=(d.catch_y+x,0,0))
              .polyline([(r-m1.leaf_offset(d,z,displacement),z) for r,z in points])
              .close().extrude(d.gusset_width))
        part=part.union(side)
    return part.clean()


def tongue(d, displacement=0):
    # Reuse the accepted beam/pad; replace only its original hook. The new hook
    # fills the same .3 mm attachment overlap so no detached tooth is introduced.
    original = m1.tongue(d,displacement)
    old_hook = m1.at_end(m1.hook(d,displacement),1)
    new_hook = m1.at_end(hook(d,displacement),1)
    return original.cut(old_hook).union(new_hook).clean()


def cap(d):
    outer = m1.prism(d.width,d.depth,d.corner,d.seam,d.length-d.seam)
    outer = m1.rounded_print_end(outer,d,top=True).edges('<Z').fillet(.6)
    cavity = cq.Workplane(obj=cq.Solid.makeLoft([
        m1.rounded_wire(d.width-2*t,d.depth-2*t,d.corner-t,z)
        for z,t in ((d.seam-1,d.receiver_wall),
                    (d.seam+d.lap+2,d.receiver_wall),
                    (d.seam+d.lap+6,d.wall),
                    (d.length-d.floor,d.wall))],ruled=True))
    cavity = cavity.edges('>Z').fillet(d.end_radius-d.wall)
    part = outer.cut(cavity)
    # External support keeps the existing cavity section; the cap prints inverted,
    # so the upper end of this reinforcement eases outward on a 45-degree slope.
    for sign in (-1,1):
        y = d.width/2
        rib = (cq.Workplane('YZ',origin=(-d.hook_width/2-4,0,0))
               .polyline([(y-.3,d.seam+.8),(y+d.skin_reinforcement,d.seam+.8),
                          (y+d.skin_reinforcement,d.seam+d.lap+1),
                          (y-.3,d.seam+d.lap+2.1)]).close()
               .extrude(d.hook_width+8))
        part = part.union(m1.at_end(rib,sign))
    # Loft the actual pocket floor, rather than claiming an undercut while
    # retaining the old flat receiver. The pocket side flanks remain gabled.
    # The deeper blind pocket leaves .45 mm nominal tooth-to-skin clearance,
    # exceeding .25 mm guide play; the external rib retains 1.3 mm total skin.
    a,b = d.hook_width/2+d.shelf_side_margin,d.hook_width/2+3
    slope = math.tan(math.radians(d.retaining_angle_deg))
    for sign in (-1,1):
        wires=[]
        for y in (d.width/2-d.receiver_wall-.3,d.width/2-d.pocket_outer_skin):
            bottom = d.hook_bottom-d.axial_play-(y-d.beam_outer)*slope
            outline = [(-a,bottom),(a,bottom),(b,bottom+b-a),(b,d.hook_bottom+7),
                       (3,d.hook_bottom+11),(-3,d.hook_bottom+11),
                       (-b,d.hook_bottom+7),(-b,bottom+b-a)]
            wires.append(cq.Workplane('XZ',origin=(d.catch_y,y,0)).polyline(outline).close().val())
        window=cq.Workplane(obj=cq.Solid.makeLoft(wires,ruled=True))
        part=part.cut(m1.at_end(window,sign))
        # Widthwise clearance includes .25 mm guide motion and .10 mm margin.
        # These channels leave the central 8.3 mm retaining shelf intact.
        for side in (-1,1):
            relief=m1.box(d.catch_y+side*(d.gusset_relief_inner+d.gusset_relief_outer)/2,
                (d.width/2-d.receiver_wall-.3+d.width/2-d.pocket_outer_skin)/2,
                d.hook_bottom+(-3+1.3)/2,
                d.gusset_relief_outer-d.gusset_relief_inner,
                d.receiver_wall+.3-d.pocket_outer_skin,4.3)
            part=part.cut(m1.at_end(relief,sign))
    return part.clean()


def build(d=D):
    if not d.length > d.seam+d.lap > d.beam_tip > d.seam > d.beam_root:
        raise ValueError('M2 longitudinal ordering invalid')
    fixed=m1.body_fixed(d)
    lower=fixed
    for sign in (-1,1):
        lower=lower.union(m1.mirrored(tongue(d),sign))
    upper=cap(d)
    assembly=cq.Assembly(name='m2_research_print')
    assembly.add(lower,name='body')
    assembly.add(m1.print_cap(upper,d.length),name='cap')
    return dict(dimensions=d,fixed=fixed,body=lower.clean(),cap=upper,
                references=m1.references(d),result=assembly)


def configuration(parts, *, cap_lift, releases):
    d=parts['dimensions']
    assembly=cq.Assembly(name='m2')
    assembly.add(parts['fixed'],name='body_fixed')
    for sign,delta in zip((-1,1),releases,strict=True):
        assembly.add(m1.mirrored(tongue(d,delta),sign),name='catch_'+str(sign))
    assembly.add(parts['cap'],name='cap',loc=cq.Location(cq.Vector(0,0,cap_lift)))
    return assembly
