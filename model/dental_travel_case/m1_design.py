"""M1: two flush cups with a lap guide and opposed recessed squeeze catches.

Millimetres. Assembly Z runs from the brush butt to its head. Builders do not
publish files. The body prints as assembled; the cap prints closed-end down.
The two catch tongues are integral with the body, behind the brush-side walls.
"""
from dataclasses import dataclass
import cadquery as cq


@dataclass(frozen=True)
class Dimensions:
    length: float = 264.0
    seam: float = 174.0
    width: float = 99.2
    depth: float = 51.2
    corner: float = 6.0
    wall: float = 2.0
    floor: float = 2.0
    lap: float = 12.0
    lap_clearance: float = .4  # per side, distinct from axial catch play
    lap_wall: float = 1.6
    brush_x: float = -29.5
    paste_x: float = 17.0
    catch_x: float = -29.5
    beam_width: float = 10.0
    beam_thickness: float = 1.6
    beam_length: float = 33.4
    catch_height: float = 4.0  # retaining shoulder above seam
    hook_projection: float = 1.6
    release: float = 2.1  # tip travel; smaller travel at the body squeeze point
    slot: float = .8

    @property
    def sleeve_width(self):
        return self.width-2*(self.wall+self.lap_clearance)

    @property
    def sleeve_depth(self):
        return self.depth-2*(self.wall+self.lap_clearance)

    @property
    def sleeve_corner(self):
        return self.corner-self.wall-self.lap_clearance

    @property
    def beam_outer(self):
        return self.sleeve_depth/2

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
        return self.seam-6


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


def mirrored(part, sign):
    return part if sign == 1 else part.mirror('XZ', union=False)


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
              (y+d.hook_projection, d.hook_bottom+.8),
              (y, d.beam_tip), (y-.3, d.beam_tip)]
    part = (cq.Workplane('YZ', origin=(d.catch_x-3, 0, 0))
            .polyline([(y-leaf_offset(d, z, displacement), z) for y, z in points])
            .close().extrude(6))
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
        wires.append(cq.Workplane('XY', origin=(d.catch_x,
            d.beam_outer-d.beam_thickness/2-delta,
            root+s*length)).rect(d.beam_width, d.beam_thickness).val())
    beam = cq.Workplane(obj=cq.Solid.makeLoft(wires))
    beam = beam.union(box(d.catch_x, d.beam_outer-d.beam_thickness/2,
                          d.beam_root+.5, d.beam_width, d.beam_thickness, 1))
    return beam.union(hook(d, displacement))


def body_fixed(d):
    outer = prism(d.width, d.depth, d.corner, 0, d.seam)
    # A small bed chamfer preserves a broad stable footprint; seam edges are soft.
    outer = outer.edges('<Z').chamfer(.5).edges('>Z').fillet(.6)
    sleeve = prism(d.sleeve_width, d.sleeve_depth, d.sleeve_corner,
                   d.seam-.5, d.lap+.5).edges('>Z').chamfer(.6)
    inner = cq.Solid.makeLoft([
        rounded_wire(d.width-2*d.wall, d.depth-2*d.wall,
                     d.corner-d.wall, z) for z in (d.floor, d.seam-6)] + [
        rounded_wire(d.sleeve_width-2*d.lap_wall,
                     d.sleeve_depth-2*d.lap_wall,
                     d.sleeve_corner-d.lap_wall, z)
        for z in (d.seam, d.seam+d.lap+1)], ruled=True)
    fixed = outer.union(sleeve).cut(cq.Workplane(obj=inner))
    liner_top = d.beam_outer-d.beam_thickness-2.6
    liner_bottom = d.beam_root-2
    half_liner = d.beam_width/2+2.8
    end = d.seam+d.lap
    for sign in (-1, 1):
        # Slot stays inside the outside guard below the seam. The liner behind
        # it closes the cavity without intruding into the toothpaste column.
        channel_top = d.beam_outer+.8
        channel = box(d.catch_x, (liner_top+channel_top)/2, (d.beam_root+end+1)/2,
                      d.beam_width+2*d.slot, channel_top-liner_top,
                      end+1-d.beam_root)
        fixed = fixed.cut(mirrored(channel, sign))
        liner = box(d.catch_x, liner_top-.6, (liner_bottom+end)/2,
                    2*half_liner, 1.2, end-liner_bottom)
        # Supported inward ramp and side walls attach the enclosed liner.
        ramp = (cq.Workplane('YZ', origin=(d.catch_x-half_liner, 0, 0))
                .polyline([(d.depth/2-d.wall, d.beam_root-8),
                           (d.depth/2, d.beam_root-8), (d.depth/2, d.beam_root),
                           (liner_top-1.2, d.beam_root),
                           (liner_top-1.2, liner_bottom)])
                .close().extrude(2*half_liner))
        local = liner.union(ramp)
        for x in (-half_liner+.6, half_liner-.6):
            local = local.union(box(d.catch_x+x, (liner_top+d.beam_outer)/2,
                                    (liner_bottom+end)/2, 1.2,
                                    d.beam_outer-liner_top, end-liner_bottom))
        # Tongue attachment and a generous concave root blend are fixed.
        root_inside = d.beam_outer-d.beam_thickness-1.8
        root = box(d.catch_x, (root_inside+d.depth/2)/2, d.beam_root-1,
                   d.beam_width, d.depth/2-root_inside, 2)
        root = root.union(box(d.catch_x, d.beam_outer-d.beam_thickness/2,
                              d.beam_root+.5, d.beam_width, d.beam_thickness, 1))
        selected = [e for e in root.val().Edges()
                    if abs(e.Center().z-d.beam_root)<1e-6
                    and abs(e.Center().y-(d.beam_outer-d.beam_thickness))<1e-6
                    and e.Length()>d.beam_width-.1]
        if len(selected) != 1:
            raise ValueError('M1 root blend selector must find its concave edge')
        root = root.newObject(selected).fillet(.8)
        fixed = fixed.union(mirrored(local.union(root), sign))
    # Body controls stay below the cap. One hand can hold these pressed while
    # the other withdraws the cap; the closed liner separates fingers from items.
    port = [(-3.4, -12), (3.4, -12), (7, -8.4), (7, -4.6),
            (3.4, -1), (-3.4, -1), (-7, -4.6), (-7, -8.4)]
    cutter = (cq.Workplane('XZ', origin=(d.catch_x, d.depth/2+2, 0))
              .polyline([(x, z+d.seam) for x, z in port]).close().extrude(4.2)
              .edges('|Y').fillet(.4))
    for sign in (-1, 1):
        fixed = fixed.cut(mirrored(cutter, sign))
    # Profile corner rounds do not soften the face/depth junction touched by
    # fingers. Blend the actual exterior port rims after the cuts.
    rims = [e for e in fixed.val().Edges()
            if abs(abs(e.Center().y)-d.depth/2)<1e-6
            and abs(e.Center().x-d.catch_x)<7.5
            and d.seam-12.5 < e.Center().z < d.seam-.5]
    if not rims:
        raise ValueError('M1 exterior control-rim selection is empty')
    fixed = fixed.newObject(rims).fillet(.25)
    return fixed.clean()


def cap(d):
    outer = prism(d.width, d.depth, d.corner, d.seam, d.length-d.seam)
    # This end sits on the print bed: a chamfer grows without a fillet overhang.
    outer = outer.edges('>Z').chamfer(.6).edges('<Z').fillet(.6)
    cavity = prism(d.width-2*d.wall, d.depth-2*d.wall,
                   d.corner-d.wall, d.seam-1, d.length-d.floor-d.seam+1)
    part = outer.cut(cavity)
    # Blind pockets hide the hook and retain an outer skin. The central ledge
    # stays flat; diagonal flanks reduce its short print bridge.
    outline = [(x, z+d.hook_bottom) for x, z in
               [(-3.4, -.4), (3.4, -.4), (7, 3.2), (7, 7),
                (3, 11), (-3, 11), (-7, 7), (-7, 3.2)]]
    for sign in (-1, 1):
        window = (cq.Workplane('XZ', origin=(d.catch_x, d.depth/2-.6, 0))
                  .polyline(outline).close().extrude(3))
        part = part.cut(mirrored(window, sign))
    return part.clean()


def references(d):
    # Approximate measurements; neck/head subdivision and offsets unmeasured.
    brush = cq.Workplane('XY', origin=(d.brush_x, 0, 4.5)).circle(15).extrude(165)
    brush = brush.union(cq.Workplane('XY', origin=(d.brush_x, 0, 169.5))
                        .circle(5).extrude(62))
    brush = brush.union(box(d.brush_x, 0, 245.5, 15, 25, 28))
    paste = box(d.paste_x, 0, 83, 55, 40, 160)
    return {'brush': brush, 'paste': paste}


def configuration(parts, *, cap_lift, contents, releases):
    """Named native assembly used by inspection and mechanical checks."""
    d = parts['dimensions']
    assembly = cq.Assembly(name='m1')
    assembly.add(parts['fixed'], name='body_fixed')
    for sign, delta in zip((-1, 1), releases, strict=True):
        assembly.add(mirrored(tongue(d, delta), sign),
                     name='catch_front' if sign == -1 else 'catch_back')
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
