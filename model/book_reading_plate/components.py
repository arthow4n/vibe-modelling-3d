"""PETG reading plate; mm. Evaluate this file for the assembled inspection pose.
Print/export entry point: export_plate.py. X=book width, Y=height, Z=front.
"""
from dataclasses import dataclass
import cadquery as cq


@dataclass(frozen=True)
class Parameters:
    width: float = 400.0
    inner_height: float = 250.0
    inner_lip: float = 40.0
    wall: float = 10.0
    corner_radius: float = 4.0
    outer_bend_radius: float = 9.0
    bed_edge_chamfer: float = 2.0
    tenon_length: float = 36.0
    tenon_width: float = 46.0
    tenon_thickness: float = 6.0
    tenon_radius: float = 1.5
    socket_clearance: float = 0.20  # per side in Y and Z; tip clearance separately
    tip_clearance: float = 0.6
    joint_count: int = 4
    joint_end_margin: float = 35.0  # centres measured from inner lower/upper ends
    slot_width: float = 8.0         # in Y, with 45 degree roofs in X
    slot_length: float = 8.0        # rectangle portion in X
    draw_offset: float = 0.8        # male hole shifted toward seam; wedge draws it closed
    key_side_clearance: float = 0.15
    key_taper: float = 0.10         # X width gain per mm of insertion (5.71 degrees)
    key_seat_clearance: float = 0.04
    key_head_half_width: float = 8.0
    key_lock_advance: float = 0.8
    latch_axial_clearance: float = 0.15
    latch_side_gap: float = 0.5
    latch_overlap: float = 1.4
    latch_thickness: float = 1.8
    latch_depth: float = 6.0
    latch_length: float = 32.0
    latch_root_fillet: float = 0.7
    latch_recess_shift: float = 8.0
    key_head_thickness: float = 1.4
    head_pocket_depth: float = 5.4
    latch_pocket_depth: float = 6.4
    print_rotation: float = 30.0
    design_book_kg: float = 3.0

    @property
    def height(self): return self.inner_height + self.wall
    @property
    def depth(self): return self.inner_lip + self.wall
    @property
    def stations(self):
        a = self.wall + self.joint_end_margin
        b = self.height - self.joint_end_margin
        return tuple(a + i * (b-a)/(self.joint_count-1) for i in range(self.joint_count))
    @property
    def slot_x(self): return self.tenon_length * 0.56


P = Parameters()


def validate(p):
    assert p.joint_count >= 2 and p.width / 2 + p.tenon_length < 250
    assert p.wall - p.tenon_thickness - 2*p.socket_clearance >= 3.5
    assert p.tenon_radius < p.tenon_thickness/2
    assert min(b-a for a,b in zip(p.stations,p.stations[1:])) > p.tenon_width+6
    assert p.stations[0]-p.tenon_width/2 > p.wall+p.corner_radius


def base_half(side, p=P):
    """Side +/-1. Outside end is the bed face; central seam is X=0."""
    profile = [(0,0),(p.height,0),(p.height,p.wall),
               (p.wall,p.wall),(p.wall,p.depth),(0,p.depth)]
    start = -p.width/2 if side < 0 else 0
    body = cq.Workplane('YZ', origin=(start,0,0)).polyline(profile).close().extrude(p.width/2)
    # Large outside elbow, then softer free edges and inner book/lip junction.
    elbow = [e for e in body.edges('|X').vals()
             if abs(e.Center().y) < 1e-5 and abs(e.Center().z) < 1e-5]
    body = body.newObject(elbow).fillet(p.outer_bend_radius)
    remaining = [e for e in body.edges('|X').vals()
                 if not (e.Center().y < p.outer_bend_radius+0.01 and
                         e.Center().z < p.outer_bend_radius+0.01)]
    body = body.newObject(remaining).fillet(p.corner_radius)
    # A 45-degree bed-edge treatment preserves adhesion and avoids a bottom fillet overhang.
    return body.faces('<X' if side < 0 else '>X').edges().chamfer(p.bed_edge_chamfer)


def tenon(station, p=P, clearance=0.0):
    lo = -2.0
    length = p.tenon_length + (p.tip_clearance if clearance else 0) - lo
    return (cq.Workplane('XY').box(length,p.tenon_width+2*clearance,
                                   p.tenon_thickness+2*clearance)
            .translate((lo+length/2,station,p.wall/2))
            .edges('|X').fillet(p.tenon_radius+clearance))


def hex_outline(left, right, half_y):
    # Each end is a 45-degree roof in the standing panel print orientation.
    return [(left-half_y,0),(left,-half_y),(right,-half_y),
            (right+half_y,0),(right,half_y),(left,half_y)]


def slot(station, p=P, male=False):
    centre = p.slot_x - (p.draw_offset if male else 0)
    points = hex_outline(centre-p.slot_length/2, centre+p.slot_length/2, p.slot_width/2)
    return (cq.Workplane('XY', origin=(0,station,-1)).polyline(points).close()
            .extrude(p.wall+2))


def retaining_clip(station, side, p=P, released=False):
    """Rear catch, integral with receiver. Deflection/release is outward in Y.
    Printing rises toward decreasing X; root and hook have 45-degree growth ramps.
    released=True rigidly shifts the free clip outward for clearance checks only;
    it is not a deformation simulation and is never part of an exported panel.
    """
    tip = p.slot_x-2.0
    root = tip+p.latch_length
    inner = p.key_head_half_width+p.latch_side_gap
    outer = inner+p.latch_thickness
    rear, front = -8.0, -8.0+p.latch_depth
    catch_z = -5.0+p.key_lock_advance-p.latch_axial_clearance
    hook_y = p.key_head_half_width-p.latch_overlap
    beam = (cq.Workplane('XY').box(p.latch_length,p.latch_thickness,p.latch_depth)
            .translate(((tip+root)/2,(inner+outer)/2,(rear+front)/2)).edges('|X').fillet(0.4))
    # Anchor starts at the back face and grows out by one mm per printed mm.
    anchor_profile = [(root,-8),(root+8,0),(root+8,2),(root-1,2),(root-1,-8)]
    anchor = (cq.Workplane('XZ',origin=(0,outer+2,0)).polyline(anchor_profile).close()
              .extrude(p.latch_thickness+4))
    triangle = [(inner,-7.0),(hook_y,catch_z),(inner,catch_z)]
    hook = cq.Workplane('YZ',origin=(tip,0,0)).polyline(triangle).close().extrude(8)
    roof = [(tip,hook_y),(tip+8-(inner-hook_y),hook_y),
            (tip+8,inner),(tip+8,outer),(tip,outer)]
    ramp = cq.Workplane('XY',origin=(0,0,-9)).polyline(roof).close().extrude(9)
    free = beam.union(hook.intersect(ramp))
    clip = free.union(anchor)
    # Round the two vertical, concave beam-root edges; preserve the square catch face.
    roots = [e for e in clip.edges('|Z').vals()
             if abs(e.Center().x-(root-1))<1e-5
             and (abs(e.Center().y-inner)<1e-5 or abs(e.Center().y-outer)<1e-5)]
    if roots:
        clip = clip.newObject(roots).fillet(p.latch_root_fillet)
    if released:
        clip = clip.translate((0,p.latch_overlap+0.25,0))
    if side < 0:
        clip = clip.mirror('XZ')
    return clip.translate((0,station,p.latch_recess_shift))


def receiver_clips(station, p=P, released=False):
    return [retaining_clip(station,sign,p,released) for sign in (-1,1)]


def latch_pockets(station, p=P):
    """Recesses keep all catches/head below the flat rear face, Z=0.
    The head recess is also the insertion-depth stop. Two wider side channels
    provide room to spread the catch tips without protruding from the plate.
    """
    head_x=p.slot_length+p.slot_width+3+0.5
    head_y=2*p.key_head_half_width+0.5
    pocket=(cq.Workplane('XY').box(head_x,head_y,p.head_pocket_depth+1)
            .translate((p.slot_x,station,(p.head_pocket_depth-1)/2))
            .edges('|Z').fillet(2.25))
    # Rounded, 0.6 mm bevel at the accessible pocket rim.
    lead=(cq.Workplane('XY').box(head_x+1.2,head_y+1.2,1.6)
          .translate((p.slot_x,station,-0.2)).edges('|Z').fillet(2.85)
          .faces('>Z').edges().chamfer(0.6))
    pocket=pocket.union(lead)
    for sign in (-1,1):
        x0=p.slot_x-4.0
        x1=p.slot_x-2.0+p.latch_length+0.5
        y0=p.key_head_half_width-p.latch_overlap-0.8
        y1=p.key_head_half_width+p.latch_side_gap+p.latch_thickness+p.latch_overlap+0.6
        channel=(cq.Workplane('XY').box(x1-x0,y1-y0,p.latch_pocket_depth+1)
                 .translate(((x0+x1)/2,station+sign*(y0+y1)/2,(p.latch_pocket_depth-1)/2))
                 .edges('|Z').fillet(1.0))
        mouth=(cq.Workplane('XY').box(x1-x0+1.2,y1-y0+1.2,1.6)
               .translate(((x0+x1)/2,station+sign*(y0+y1)/2,-0.2))
               .edges('|Z').fillet(1.6).faces('>Z').edges().chamfer(0.6))
        pocket=pocket.union(channel).union(mouth)
    return pocket


def halves(p=P):
    validate(p)
    left, right = base_half(-1,p), base_half(1,p)
    for y in p.stations:
        left = left.union(tenon(y,p)).cut(slot(y,p,male=True))
        right = right.cut(tenon(y,p,p.socket_clearance)).cut(slot(y,p))
        recess=latch_pockets(y,p)
        left=left.cut(recess)
        # Keep the rear relief open through the tenon tip: closing it again at
        # the pocket end would grow a 3.4 mm unsupported ledge in the standing print.
        entry=(cq.Workplane('XY').box(p.tenon_length+1-p.slot_x,
                                     2*p.key_head_half_width+0.5,p.head_pocket_depth+1)
               .translate(((p.tenon_length+1+p.slot_x)/2,y,(p.head_pocket_depth-1)/2)))
        left=left.cut(entry)
        right=right.cut(recess)
        for clip in receiver_clips(y,p):
            right = right.union(clip)
    return left, right


def key(station=0.0, p=P):
    """Draw key, in assembly pose. Push from rear toward book face to tighten.
    Left flank reacts against receiver; right flank draws male tenon into receiver.
    A small nominal clearance is consumed by another ~0.4 mm of key insertion.
    """
    hy = p.slot_width/2-p.key_side_clearance
    left = p.slot_x-p.slot_length/2 - p.key_side_clearance
    contact_z = p.head_pocket_depth
    right_at_contact = (p.slot_x-p.draw_offset+p.slot_length/2
                        +p.key_side_clearance-p.key_seat_clearance)
    def section(z):
        right = right_at_contact - p.key_taper*(z-contact_z)
        return hex_outline(left,right,hy)
    head_rear = -5.0+p.latch_recess_shift
    z0, z1 = head_rear+p.key_head_thickness, p.wall-1.0
    shaft = (cq.Workplane('XY',origin=(0,station,z0)).polyline(section(z0)).close()
             .workplane(offset=z1-z0).polyline(section(z1)).close().loft(ruled=True))
    head = (cq.Workplane('XY').box(p.slot_length+p.slot_width+3,2*p.key_head_half_width,p.key_head_thickness)
            .translate((p.slot_x,station,head_rear+p.key_head_thickness/2)).edges('|Z').fillet(2)
            .faces('<Z').edges().chamfer(0.6))
    return shaft.union(head)


def on_bed(shape):
    b = shape.val().BoundingBox()
    return shape.translate((-b.xmin,-b.ymin,-b.zmin))


def print_half(shape, side, p=P):
    # Both outside ends on bed. Left tenons and right sockets face upward.
    angle = -90 if side < 0 else 90
    return on_bed(shape.rotate((0,0,0),(0,1,0),angle)
                  .rotate((0,0,0),(0,0,1),p.print_rotation))


def print_key(shape):
    # Enlarged head on bed; shaft narrows upward, with no floating starts.
    return on_bed(shape)


def coupon(p=P):
    """One full interface, cropped from production; preserves skins and print axes."""
    l,r = halves(p)
    y = p.stations[1]
    width = p.tenon_width+14
    crop = cq.Workplane('XY').box(108,width,p.wall+12).translate((8,y,(p.wall-8)/2))
    l, r = l.intersect(crop), r.intersect(crop)
    return l,r,key(y,p)


def assembled(p=P):
    l,r = halves(p)
    return cq.Compound.makeCompound([l.val(),r.val()]+[key(y,p).translate((0,0,p.key_lock_advance)).val() for y in p.stations])
