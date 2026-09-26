"""Parametric PETG reading plate, mm. X width, Y book height, Z toward book.
Reusable builders only; evaluate book_reading_plate.py or export_plate.py with the shared command.
"""
from dataclasses import dataclass
import cadquery as cq

@dataclass(frozen=True)
class Parameters:
    width: float = 400
    inner_height: float = 250
    inner_lip: float = 40
    thickness: float = 10
    overlap_half: float = 35
    lap_gap: float = .12
    hole_x: float = 20
    lip_hole_z: float = 30
    back_top_margin: float = 40
    seating_radius: float = 12
    shoulder_diameter: float = 16
    shoulder_clearance: float = .10  # diametral; proven L-sample value
    head_diameter: float = 20
    head_rim: float = .6
    end_recess: float = .2  # head and tip, measured from assembled faces
    hex_af: float = 8.2  # standard 8 mm Allen key
    hex_depth: float = 2.6
    thread_pitch: float = 2.4
    thread_root: float = 14.4
    thread_major: float = 16
    thread_clearance: float = .24  # radial; retain successful L sample
    thread_start: float = 5.1
    lead_length: float = .8
    outer_bend_radius: float = 8
    edge_radius: float = 4
    end_chamfer: float = 2
    print_angle: float = 30

    @property
    def height(self): return self.inner_height + self.thickness
    @property
    def lip_height(self): return self.inner_lip + self.thickness
    @property
    def split(self): return self.thickness / 2
    @property
    def back_hole_y(self): return self.height - self.back_top_margin
    @property
    def screw_tip(self): return self.thickness - self.end_recess
    @property
    def cone_start(self): return self.end_recess + self.head_rim
    @property
    def cone_end(self): return self.cone_start + (self.head_diameter-self.shoulder_diameter)/2

P = Parameters()

def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))

def solid(s): return s.val() if isinstance(s,cq.Workplane) else s

def base(p=P):
    assert p.width/2 > p.overlap_half > p.hole_x + p.seating_radius
    assert p.hex_depth < p.thread_start-p.end_recess
    t=p.thickness
    profile=[(0,0),(p.height,0),(p.height,t),(t,t),(t,p.lip_height),(0,p.lip_height)]
    s=cq.Workplane('YZ',origin=(-p.width/2,0,0)).polyline(profile).close().extrude(p.width)
    edges=[e for e in s.edges('|X').vals() if e.Center().y<.01 and e.Center().z<.01]
    s=s.newObject(edges).fillet(p.outer_bend_radius)
    edges=[e for e in s.edges('|X').vals() if not(e.Center().y<p.outer_bend_radius+.01 and e.Center().z<p.outer_bend_radius+.01)]
    s=s.newObject(edges).fillet(p.edge_radius)
    return s.faces('|X').edges().chamfer(p.end_chamfer)

def posed(s,x,y,z,lip=False):
    if lip: s=s.rotate((0,0,0),(1,0,0),-90)
    return s.translate((x,y,z))

def stations(p=P):
    return [(x,0,p.lip_hole_z,True) for x in [-p.hole_x,p.hole_x]] + [(x,p.back_hole_y,0,False) for x in [-p.hole_x,p.hole_x]]

def cylinder(radius,z0,z1):
    return cq.Workplane('XY',origin=(0,0,z0)).circle(radius).extrude(z1-z0)

def head_seat(p=P):
    # Exact 45-degree bearing cone; radial clearance only above the seating cone.
    cone=(cq.Workplane('XY',origin=(0,0,p.cone_start)).circle(p.head_diameter/2)
          .workplane(offset=p.cone_end-p.cone_start).circle(p.shoulder_diameter/2).loft())
    return cylinder(p.head_diameter/2+.2,-1,p.cone_start).union(cone)

def halves(p=P,threaded=True):
    whole=base(p); w=p.width/2; h=p.height; l=p.lip_height
    lo=p.split-p.lap_gap/2; hi=p.split+p.lap_gap/2
    rear_mask=box(-w-1,w+1,-1,lo,-1,l+1).union(box(-w-1,w+1,-1,h+1,-1,lo))
    front_mask=box(-w-1,w+1,hi,h+1,hi,l+1)
    rear=whole.intersect(rear_mask);front=whole.intersect(front_mask)
    a=whole.intersect(box(-w-1,-p.overlap_half,-1,h+1,-1,l+1)).union(rear.intersect(box(-p.overlap_half-.1,p.overlap_half,-1,h+1,-1,l+1)))
    b=whole.intersect(box(p.overlap_half,w+1,-1,h+1,-1,l+1)).union(front.intersect(box(-p.overlap_half,p.overlap_half+.1,-1,h+1,-1,l+1)))
    pilot=cylinder((p.shoulder_diameter+p.shoulder_clearance)/2,-1,hi+.3)
    seat=head_seat(p)
    pad=cylinder(p.seating_radius,lo-.05,hi)
    female=female_tool(p) if threaded else cylinder(p.thread_major/2+p.thread_clearance,hi-.1,p.thickness+1)
    for x,y,z,lip in stations(p):
        a=a.union(posed(pad,x,y,z,lip)).cut(posed(pilot,x,y,z,lip)).cut(posed(seat,x,y,z,lip))
        b=b.cut(posed(female,x,y,z,lip))
    return a,b

def thread_shape(p=P,clearance=0.,cutter=False):
    root=p.thread_root/2+clearance; crest=p.thread_major/2+clearance
    start=p.thread_start-p.thread_pitch
    height=p.screw_tip-p.thread_start+2*p.thread_pitch
    axial=.07 if cutter else 0
    path=cq.Wire.makeHelix(p.thread_pitch,height,root,center=(0,0,start))
    points=[(root-.12,start-1.05-axial),(crest,start-.2-axial),(crest,start+.2+axial),(root-.12,start+1.05+axial)]
    ridge=cq.Workplane('XZ').polyline(points).close().sweep(path,isFrenet=True)
    body=cylinder(root,start-2,start+height+2).union(ridge)
    return body.intersect(box(-12,12,-12,12,p.thread_start-.2 if cutter else p.thread_start,p.thickness+1 if cutter else p.screw_tip))

def screw(p=P):
    head=cylinder(p.head_diameter/2,p.end_recess,p.cone_start)
    head=head.faces('<Z').edges().chamfer(.15)
    cone=(cq.Workplane('XY',origin=(0,0,p.cone_start)).circle(p.head_diameter/2)
          .workplane(offset=p.cone_end-p.cone_start).circle(p.shoulder_diameter/2).loft())
    shank=cylinder(p.shoulder_diameter/2,p.cone_end-.05,p.thread_start).faces('>Z').edges().chamfer(.15)
    s=head.union(cone).union(shank).union(thread_shape(p))
    lead=(cq.Workplane('XY',origin=(0,0,p.screw_tip-p.lead_length)).circle(p.thread_major/2)
          .workplane(offset=p.lead_length).circle(p.thread_root/2).loft())
    s=s.intersect(box(-20,20,-20,20,-1,p.screw_tip-p.lead_length).union(lead))
    drive=(cq.Workplane('XY',origin=(0,0,p.end_recess-.1))
           .polygon(6,p.hex_af/(3**.5/2)).extrude(p.hex_depth+.1))
    return s.cut(drive)

def female_tool(p=P):
    return thread_shape(p,p.thread_clearance,True).union(cylinder((p.shoulder_diameter+p.shoulder_clearance)/2,p.split-.2,p.thread_start+.15))

def bed(s):
    bb=solid(s).BoundingBox()
    return s.translate((-bb.xmin,-bb.ymin,-bb.zmin))

def print_half(s,left,p=P):
    # Outside X end down; diagonal footprint accommodates 260 mm book height plus brim.
    s=s.rotate((0,0,0),(0,1,0),-90 if left else 90)
    return bed(s.rotate((0,0,0),(0,0,1),p.print_angle if left else -p.print_angle))

def print_screw(p=P):
    return bed(screw(p).rotate((0,0,0),(1,0,0),180))

def assembly(p=P):
    a,b=halves(p)
    bolt=screw(p)
    bolts=[posed(bolt,x,y,z,lip) for x,y,z,lip in stations(p)]
    return cq.Compound.makeCompound([solid(s) for s in [a,b]+bolts])
