"""M1: two flush cups with a lap guide and opposed recessed squeeze catches.

Millimetres. Assembly Z runs from the brush butt to its head. Builders do not
publish files. The body prints as assembled; the cap prints closed-end down.
The two catch tongues are integral with the body, at opposite widthwise ends.
"""
from dataclasses import dataclass
import math
import cadquery as cq


@dataclass(frozen=True)
class Dimensions:
    length: float = 264.0
    seam: float = 174.0
    width: float = 74.2  # 25 mm narrower after the first joint print
    depth: float = 51.2
    corner: float = 6.0
    end_radius: float = 4.0  # large top/bottom round, tangent to a printable foot
    wall: float = 2.0
    receiver_wall: float = 2.7  # local internal band, no exterior collar
    floor: float = 2.0
    lap: float = 12.0
    lap_clearance: float = .25  # per side, distinct from axial catch play
    axial_play: float = .15
    lap_wall: float = 1.6
    brush_x: float = 0.0
    brush_y: float = -5.0
    catch_y: float = 0.0
    beam_width: float = 14.0
    beam_thickness: float = 1.6
    beam_length: float = 40.4
    catch_height: float = 4.0  # retaining shoulder above seam
    hook_projection: float = 2.0
    hook_width: float = 8.0
    release: float = 2.7  # tip travel; smaller travel at the body squeeze point
    slot: float = .8

    @property
    def sleeve_width(self):
        return self.width-2*(self.receiver_wall+self.lap_clearance)

    @property
    def sleeve_depth(self):
        return self.depth-2*(self.receiver_wall+self.lap_clearance)

    @property
    def sleeve_corner(self):
        return self.corner-self.receiver_wall-self.lap_clearance

    @property
    def beam_outer(self):
        # End catches act along world X. Local spring builders use Y normal,
        # then rotate together into the world frame with at_end().
        return self.sleeve_width/2

    @property
    def hook_bottom(self):
        return self.seam+self.catch_height

    @property
    def beam_tip(self):
        return self.hook_bottom+4.4

    @property
    def beam_root(self):
        return self.beam_tip-self.beam_length

    @property
    def press_z(self):
        return self.seam-8


D = Dimensions()


def rounded_wire(width, depth, radius, z):
    a, b, r = width/2, depth/2, radius
    return (cq.Workplane('XY', origin=(0, 0, z)).moveTo(-a+r, -b)
            .lineTo(a-r, -b).radiusArc((a, -b+r), -r)
            .lineTo(a, b-r).radiusArc((a-r, b), -r)
            .lineTo(-a+r, b).radiusArc((-a, b-r), -r)
            .lineTo(-a, -b+r).radiusArc((-a+r, -b), -r).close().val())


def prism(width, depth, radius, bottom, height):
    return cq.Workplane(obj=cq.Solid.extrudeLinear(
        rounded_wire(width, depth, radius, bottom), [], cq.Vector(0, 0, height)))


def box(x, y, z, width, depth, height):
    return cq.Workplane('XY').box(width, depth, height).translate((x, y, z))


def rounded_print_end(part, d, *, top):
    """R4 blend above a tangent 45-degree foot; avoid a full fillet overhang.

    The large radius joins the chamfer to the wall. A small final foot blend
    removes the touch edge; its rise is below one 0.2 mm layer. Bed face stays flat.
    """
    foot = d.end_radius*(2-math.sqrt(2))
    part = part.edges('>Z' if top else '<Z').chamfer(foot)
    level = d.length-foot if top else foot
    edges = [e for e in part.val().Edges() if abs(e.Center().z-level)<1e-6]
    if not edges:
        raise ValueError('M1 end-blend junction selection is empty')
    return (part.newObject(edges).fillet(d.end_radius)
            .edges('>Z' if top else '<Z').fillet(.35))


def mirrored(part, sign):
    return part if sign == 1 else part.mirror('YZ', union=False)


def at_end(part, sign):
    """One local frame for every spring, channel, pocket and control feature."""
    return mirrored(part.rotate((0, 0, 0), (0, 0, 1), 90), sign)


def leaf_offset(d, z, displacement):
    """Small-deflection point-load displacement normalized by terminal travel."""
    # Keep the blended one-millimetre attachment stub exactly stationary.
    root = d.beam_root+1
    if z <= root:
        return 0.0
    length = d.beam_tip-root
    contact = d.press_z-root
    s = z-root
    fraction = (s*s*(3*contact-s)/(contact**2*(3*length-contact))
                if s <= contact else (3*s-contact)/(3*length-contact))
    return displacement*fraction


def hook(d, displacement=0):
    # The lower face retains; the upper ramp bends the leaf only during closing.
    # Rounded outside corner/entry, deliberately flat positive retaining shoulder.
    y = d.beam_outer
    points = [(y-.3, d.hook_bottom),
              (y+d.hook_projection, d.hook_bottom),
              (y+d.hook_projection, d.hook_bottom+1.2),
              (y, d.beam_tip), (y-.3, d.beam_tip)]
    part = (cq.Workplane('YZ', origin=(d.catch_y-d.hook_width/2, 0, 0))
            .polyline([(y-leaf_offset(d, z, displacement), z) for y, z in points])
            .close().extrude(d.hook_width))
    return part.edges('|X and >Y').fillet(.25)


def tongue(d, displacement=0):
    """Fixed-root small-deflection envelope, not a constitutive/contact solve.

    At zero this is the production rectangular beam. Prescribed release uses
    a point load at the recessed body contact, with the root left fixed and the
    unloaded upper span continuing at the contact tangent. It predicts travel,
    not a calibrated deformation/contact result.
    """
    root = d.beam_root+1
    length = d.beam_tip-root
    wires = []
    for s in (0, .125, .25, .375, .5, .625, .75, .875, 1):
        delta = leaf_offset(d, root+s*length, displacement)
        wires.append(cq.Workplane('XY', origin=(d.catch_y,
            d.beam_outer-d.beam_thickness/2-delta,
            root+s*length)).rect(d.beam_width, d.beam_thickness).val())
    beam = cq.Workplane(obj=cq.Solid.makeLoft(wires))
    beam = beam.union(box(d.catch_y, d.beam_outer-d.beam_thickness/2,
                          d.beam_root+.5, d.beam_width, d.beam_thickness, 1))
    # A low, guarded contact pad reduces finger reach into the end-wall port.
    y, z = d.beam_outer, d.press_z
    pad_points = [(y-.2,z-2.4),(y,z-2.4),(y+1.2,z-1),
                  (y+1.2,z+1),(y,z+2.4),(y-.2,z+2.4)]
    pad = (cq.Workplane('YZ', origin=(d.catch_y-(d.beam_width-4)/2,0,0))
           .polyline([(v-leaf_offset(d,h,displacement),h) for v,h in pad_points])
           .close().extrude(d.beam_width-4).edges('|X and >Y').fillet(.6))
    return at_end(beam.union(hook(d, displacement)).union(pad), 1)


def body_fixed(d):
    outer = prism(d.width, d.depth, d.corner, 0, d.seam)
    outer = rounded_print_end(outer,d,top=False).edges('>Z').fillet(.6)
    sleeve = prism(d.sleeve_width, d.sleeve_depth, d.sleeve_corner,
                   d.seam-.5, d.lap+.5).edges('>Z').chamfer(.6)
    inner = cq.Solid.makeLoft([
        rounded_wire(d.width-2*d.wall, d.depth-2*d.wall,
                     d.corner-d.wall, z) for z in (d.floor, d.seam-6)] + [
        rounded_wire(d.sleeve_width-2*d.lap_wall,
                     d.sleeve_depth-2*d.lap_wall,
                     d.sleeve_corner-d.lap_wall, z)
        for z in (d.seam, d.seam+d.lap+1)], ruled=True)
    envelope = outer.union(sleeve)
    # Inner R2 preserves wall stock behind the large outer end blend.
    inner = cq.Workplane(obj=inner).edges('<Z').fillet(d.end_radius-d.wall)
    fixed = envelope.cut(inner)
    liner_top = d.beam_outer-d.beam_thickness-(d.release+.3)
    liner_bottom = d.beam_root-2
    half_liner = d.beam_width/2+2.8
    end = d.seam+d.lap
    for sign in (-1, 1):
        # Slot stays inside the outside guard below the seam. The liner behind
        # it closes the cavity without intruding into the toothpaste column.
        channel_top = d.beam_outer+.8
        channel = box(d.catch_y, (liner_top+channel_top)/2, (d.beam_root+end+1)/2,
                      d.beam_width+2*d.slot, channel_top-liner_top,
                      end+1-d.beam_root)
        fixed = fixed.cut(at_end(channel, sign))
        liner = box(d.catch_y, liner_top-.6, (liner_bottom+end)/2,
                    2*half_liner, 1.2, end-liner_bottom)
        # Supported inward ramp and side walls attach the enclosed liner.
        ramp = (cq.Workplane('YZ', origin=(d.catch_y-half_liner, 0, 0))
                .polyline([(d.width/2-d.wall, d.beam_root-10),
                           (d.width/2, d.beam_root-10), (d.width/2, d.beam_root),
                           (liner_top-1.2, d.beam_root),
                           (liner_top-1.2, liner_bottom)])
                .close().extrude(2*half_liner))
        local = liner.union(ramp)
        for x in (-half_liner+.6, half_liner-.6):
            local = local.union(box(d.catch_y+x, (liner_top+d.width/2)/2,
                                    (liner_bottom+end)/2, 1.2,
                                    d.width/2-liner_top, end-liner_bottom))
        # Tongue attachment and a generous concave root blend are fixed.
        root_inside = d.beam_outer-d.beam_thickness-1.8
        root = box(d.catch_y, (root_inside+d.width/2)/2, d.beam_root-1,
                   d.beam_width, d.width/2-root_inside, 2)
        root = root.union(box(d.catch_y, d.beam_outer-d.beam_thickness/2,
                              d.beam_root+.5, d.beam_width, d.beam_thickness, 1))
        selected = [e for e in root.val().Edges()
                    if abs(e.Center().z-d.beam_root)<1e-6
                    and abs(e.Center().y-(d.beam_outer-d.beam_thickness))<1e-6
                    and e.Length()>d.beam_width-.1]
        if len(selected) != 1:
            raise ValueError('M1 root blend selector must find its concave edge')
        root = root.newObject(selected).fillet(.8)
        fixed = fixed.union(at_end(local.union(root), sign).intersect(envelope))
    # Body controls stay below the cap. One hand can hold these pressed while
    # the other withdraws the cap; the closed liner separates fingers from items.
    # Gabled port roof closes gradually instead of bridging above the contact.
    a = d.beam_width/2+1
    top, upper = -1, -1-a
    lower, bottom = upper-4, upper-4-a
    port = [(0,bottom),(a,lower),(a,upper),(0,top),
            (-a,upper),(-a,lower)]
    cutter = (cq.Workplane('XZ', origin=(d.catch_y, d.width/2+2, 0))
              .polyline([(x, z+d.seam) for x, z in port]).close().extrude(4.2)
              .edges('|Y').fillet(.4))
    for sign in (-1, 1):
        fixed = fixed.cut(at_end(cutter, sign))
    # Profile corner rounds do not soften the face/depth junction touched by
    # fingers. Blend the actual exterior port rims after the cuts.
    rims = [e for e in fixed.val().Edges()
            if abs(abs(e.Center().x)-d.width/2)<1e-6
            and abs(e.Center().y-d.catch_y)<a+.5
            and d.seam+bottom-.5 < e.Center().z < d.seam-.5]
    if not rims:
        raise ValueError('M1 exterior control-rim selection is empty')
    fixed = fixed.newObject(rims).fillet(.25)
    return fixed.clean()


def cap(d):
    outer = prism(d.width, d.depth, d.corner, d.seam, d.length-d.seam)
    outer = rounded_print_end(outer,d,top=True).edges('<Z').fillet(.6)
    cavity = cq.Workplane(obj=cq.Solid.makeLoft([
        rounded_wire(d.width-2*t,d.depth-2*t,d.corner-t,z)
        for z,t in ((d.seam-1,d.receiver_wall),
                    (d.seam+20,d.receiver_wall), (d.seam+24,d.wall),
                    (d.length-d.floor,d.wall))], ruled=True))
    cavity = cavity.edges('>Z').fillet(d.end_radius-d.wall)
    part = outer.cut(cavity)
    # Blind pockets hide the hook and retain an outer skin. The central ledge
    # stays flat; diagonal flanks reduce its short print bridge.
    a, b = d.hook_width/2+.2, d.hook_width/2+3
    bottom = -d.axial_play
    outline = [(x, z+d.hook_bottom) for x,z in
               [(-a,bottom),(a,bottom),(b,bottom+b-a),(b,7),
                (3,11),(-3,11),(-b,7),(-b,bottom+b-a)]]
    for sign in (-1, 1):
        window = (cq.Workplane('XZ', origin=(d.catch_y, d.width/2-.8, 0))
                  .polyline(outline).close().extrude(3))
        part = part.cut(at_end(window, sign))
    return part.clean()


def references(d):
    # Approximate measurements; neck/head subdivision and offsets unmeasured.
    brush = cq.Workplane('XY', origin=(d.brush_x, d.brush_y, 4.5)).circle(15).extrude(165)
    brush = brush.union(cq.Workplane('XY', origin=(d.brush_x, d.brush_y, 169.5))
                        .circle(5).extrude(62))
    brush = brush.union(box(d.brush_x, d.brush_y, 245.5, 15, 25, 28))
    # No invented diagonal tube placement: the real tube profile is unmeasured.
    # Its 55x40 box is checked separately for individual passage, not packing.
    return {'brush': brush}


def configuration(parts, *, cap_lift, contents, releases):
    """Named native assembly used by inspection and mechanical checks."""
    d = parts['dimensions']
    assembly = cq.Assembly(name='m1')
    assembly.add(parts['fixed'], name='body_fixed')
    for sign, delta in zip((-1, 1), releases, strict=True):
        assembly.add(mirrored(tongue(d, delta), sign),
                     name='catch_right' if sign == -1 else 'catch_left')
    assembly.add(parts['cap'], name='cap', loc=cq.Location(cq.Vector(0, 0, cap_lift)))
    if contents:
        for name, shape in parts['references'].items():
            assembly.add(shape, name=name)
    return assembly


def print_cap(part, top):
    return part.rotate((0, 0, 0), (1, 0, 0), 180).translate((112, 0, top))


def build(d=D):
    if not (d.length > d.seam+d.lap > d.beam_tip > d.seam > d.beam_root):
        raise ValueError('M1 longitudinal ordering is invalid')
    if d.sleeve_corner <= d.lap_wall or d.wall <= 0:
        raise ValueError('M1 wall/profile dimensions are invalid')
    fixed = body_fixed(d)
    lower = fixed
    for sign in (-1, 1):
        lower = lower.union(mirrored(tongue(d), sign))
    upper = cap(d)
    result = cq.Assembly(name='m1_print')
    result.add(lower, name='body')
    result.add(print_cap(upper, d.length), name='cap')
    return dict(dimensions=d, fixed=fixed, body=lower.clean(), cap=upper,
                references=references(d), result=result)


def joint_test(parts):
    """Cropped production joint: preserve the complete rim and both controls."""
    d = parts['dimensions']
    lower_bottom, upper_top = d.beam_root-12, d.seam+30
    crop = lambda lo, hi: box(0, 0, (lo+hi)/2, d.width+2, d.depth+2, hi-lo)
    lower = parts['body'].intersect(crop(lower_bottom, d.seam+d.lap)).translate((0, 0, -lower_bottom))
    upper = parts['cap'].intersect(crop(d.seam, upper_top))
    assembly = cq.Assembly(name='m1_test_print')
    assembly.add(lower, name='body_joint')
    assembly.add(print_cap(upper, upper_top), name='cap_joint')
    return assembly
