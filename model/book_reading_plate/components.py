"""Two-piece PETG reading plate. X=width, Y=book height, Z=book-facing side.
Authoritative geometry; evaluate book_reading_plate.py or export_plate.py via MCP.
"""
from dataclasses import dataclass
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib


@dataclass(frozen=True)
class Parameters:
    width: float = 400.0
    inner_height: float = 250.0
    inner_lip: float = 40.0
    wall: float = 10.0
    corner_radius: float = 4.0
    outer_bend_radius: float = 9.0
    bed_edge_chamfer: float = 2.0
    rail_depth: float = 16.0
    rail_neck: float = 5.0
    rail_head: float = 7.0
    shoulder_x: float = 6.0
    rail_end_margin: float = 6.0
    rail_clearance: float = 0.12  # normal gap at the straight dovetail faces
    latch_root_x: float = -18.0
    latch_width: float = 14.0
    latch_thickness: float = 2.0
    latch_y: float = 40.0
    latch_nose_y: float = 36.0
    latch_shoulder_y: float = 43.0
    latch_tip_z: float = 0.6       # recessed below the rear plane; press toward +Z
    catch_clearance: float = 0.15 # travel before square retention shoulder contact
    latch_release: float = 1.0
    print_rotation: float = 30.0
    design_book_kg: float = 3.0

    @property
    def height(self): return self.inner_height+self.wall
    @property
    def depth(self): return self.inner_lip+self.wall
    @property
    def rail_start(self): return self.wall+self.rail_end_margin
    @property
    def rail_end(self): return self.height-self.rail_end_margin


P = Parameters()


def validate(p):
    assert 0 < p.rail_neck < p.rail_head < p.wall
    assert p.width/2+p.rail_depth < 250
    assert p.rail_clearance < (p.rail_head-p.rail_neck)/2
    assert p.rail_start+10 < p.latch_y < p.rail_end-10


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


def rail_profile(p=P):
    lo=(p.wall-p.rail_neck)/2
    hi=(p.wall+p.rail_neck)/2
    rise=(p.rail_head-p.rail_neck)/2
    x=p.shoulder_x
    return [(-1,lo),(x,lo),(x+rise,lo-rise),(p.rail_depth,lo-rise),
            (p.rail_depth,hi+rise),(x+rise,hi+rise),(x,hi),(-1,hi)]


def rail(p=P):
    # Continuous stepped dovetail: 45-degree retaining shoulders are printable
    # in both standing orientations and constrain widthwise separation.
    part=(cq.Workplane('XZ',origin=(0,p.rail_end,0)).polyline(rail_profile(p)).close()
          .extrude(p.rail_end-p.rail_start).edges('|Y').fillet(0.35))
    return part


def channel(p=P):
    # Open at the upper edge; the lower Y=rail_start face is a positive end stop.
    return (cq.Workplane('XZ',origin=(0,p.height+1,0)).polyline(rail_profile(p)).close()
            .offset2D(p.rail_clearance).extrude(p.height+1-p.rail_start))


def latch(p=P, retracted=False):
    """One integral leaf. It flexes inward (+Z); square Y shoulder blocks withdrawal.
    retracted is a rigid displacement for clearance checks, not elastic simulation.
    """
    lo=(p.wall-p.latch_thickness)/2
    beam=(cq.Workplane('XY').box(p.rail_depth-p.latch_root_x+1,
                                p.latch_width,p.latch_thickness)
          .translate(((p.rail_depth+p.latch_root_x-1)/2,p.latch_y,p.wall/2))
          .edges('|X').fillet(0.35))
    hook_profile=[(p.latch_nose_y,lo),(p.latch_nose_y,1.5),
                  (p.latch_y,p.latch_tip_z),(p.latch_shoulder_y,p.latch_tip_z),
                  (p.latch_shoulder_y,lo+0.2)]
    hook=(cq.Workplane('YZ',origin=(8,0,0)).polyline(hook_profile).close()
          .extrude(p.rail_depth-8))
    # The hook's rear projection grows at 45 degrees in the male print direction.
    support_profile=[(8,lo),(8,lo+1),(p.rail_depth,lo+1),
                     (p.rail_depth,p.latch_tip_z),(8+lo-p.latch_tip_z,p.latch_tip_z)]
    ramp=(cq.Workplane('XZ',origin=(0,p.latch_y+8,0)).polyline(support_profile).close().extrude(16))
    part=beam.union(hook.intersect(ramp))
    return part.translate((0,0,p.latch_release if retracted else 0))


def halves(p=P, retracted=False):
    validate(p)
    left=base_half(-1,p).union(rail(p))
    # Internal relief leaves 1 mm front/rear skins in the main plate. In the rail
    # it frees a single leaf; the rest of the continuous rail is structural.
    relief=(cq.Workplane('XY').box(p.rail_depth+1-p.latch_root_x,
                                  p.latch_width+2,p.wall-2)
            .translate(((p.rail_depth+1+p.latch_root_x)/2,p.latch_y,p.wall/2)))
    left=left.cut(relief).union(latch(p,retracted))
    right=base_half(1,p).cut(channel(p))
    window=(cq.Workplane('XY').box(7.0,p.latch_shoulder_y+p.catch_clearance-(p.latch_nose_y-0.3),3.0)
            .translate((13.75,(p.latch_shoulder_y+p.catch_clearance+p.latch_nose_y-0.3)/2,0.5)))
    # Leave the catch's Y shoulder square; the mouth is recessed and lightly beveled.
    mouth=(cq.Workplane('XY').box(8.0,p.latch_shoulder_y+p.catch_clearance-(p.latch_nose_y-0.3)+1,1.5)
           .translate((13.75,(p.latch_shoulder_y+p.catch_clearance+p.latch_nose_y-0.3)/2,-0.25))
           .edges('|Z').fillet(1.0).faces('>Z').edges().chamfer(0.5))
    right=right.cut(window.union(mouth))
    return left,right


def exact_bounds(shape):
    s=shape.val() if isinstance(shape,cq.Workplane) else shape
    box=Bnd_Box()
    BRepBndLib.AddOptimal_s(s.wrapped,box,False,False)
    return box.Get()


def on_bed(shape):
    b=exact_bounds(shape)
    return shape.translate((-b[0],-b[1],-b[2]))


def print_half(shape, side, p=P):
    return on_bed(shape.rotate((0,0,0),(0,1,0),-90 if side<0 else 90)
                  .rotate((0,0,0),(0,0,1),p.print_rotation))


def coupon(p=P):
    """Short rail sample; full latch, stop, mating section and print axes retained."""
    left,right=halves(p)
    crop=(cq.Workplane('XY').box(70,78,p.wall+2)
          .translate((10,51,p.wall/2)))  # X -25..45; Y 12..90
    return left.intersect(crop),right.intersect(crop)


def assembled(p=P):
    left,right=halves(p)
    return cq.Compound.makeCompound([left.val(),right.val()])
