"""L-section overlap with recessed printed shoulder screws; millimetres.
X across plate, Y up book, Z toward book. Structural lip is Y=0..10, Z=0..50.
"""
from dataclasses import dataclass,replace
import cadquery as cq
@dataclass(frozen=True)
class Parameters:
    thickness:float=10
    lip_height:float=50
    sample_height:float=55
    half_width:float=40
    overlap_half:float=35
    layer_split:float=5
    face_gap:float=.10
    hole_x:float=20
    hole_z:tuple=(30,)
    back_hole_y:float=40
    shoulder_diameter:float=16
    shoulder_clearance:float=.10
    head_diameter:float=20
    head_thickness:float=2.4
    head_recess:float=.4
    thread_pitch:float=2.4
    thread_root:float=14.4
    thread_major:float=16
    thread_clearance:float=.24
    thread_start:float=5.1
    screw_tip:float=9.7
P=Parameters()
def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
def base(p=P):
    profile=[(0,0),(p.sample_height,0),(p.sample_height,p.thickness),(p.thickness,p.thickness),(p.thickness,p.lip_height),(0,p.lip_height)]
    s=cq.Workplane('YZ',origin=(-p.half_width,0,0)).polyline(profile).close().extrude(2*p.half_width)
    e=[e for e in s.edges('|X').vals() if e.Center().y<.01 and e.Center().z<.01]
    s=s.newObject(e).fillet(6)
    e=[e for e in s.edges('|X').vals() if not(e.Center().y<6.01 and e.Center().z<6.01)]
    return s.newObject(e).fillet(2)
def cylinder_y(x,z,r,y0,y1):
    return cq.Workplane('XZ',origin=(x,y1,z)).circle(r).extrude(y1-y0)
def positions(p=P):return [(x,z) for x in [-p.hole_x,p.hole_x] for z in p.hole_z]
def halves(p=P,threaded=False):
    whole=base(p)
    tool=female_tool(p) if threaded else None
    rear_mask=box(-p.half_width-1,p.half_width+1,-1,p.layer_split,-1,p.lip_height+1).union(box(-p.half_width-1,p.half_width+1,-1,p.sample_height+1,-1,p.layer_split-p.face_gap/2))
    front_mask=box(-p.half_width-1,p.half_width+1,p.layer_split,p.sample_height+1,p.layer_split+p.face_gap/2,p.lip_height+1)
    rear=whole.intersect(rear_mask);front=whole.intersect(front_mask)
    a=whole.intersect(box(-p.half_width-1,-p.overlap_half,-1,p.sample_height+1,-1,p.lip_height+1)).union(rear.intersect(box(-p.overlap_half-.1,p.overlap_half,-1,p.sample_height+1,-1,p.lip_height+1)))
    b=whole.intersect(box(p.overlap_half,p.half_width+1,-1,p.sample_height+1,-1,p.lip_height+1)).union(front.intersect(box(-p.overlap_half,p.overlap_half+.1,-1,p.sample_height+1,-1,p.lip_height+1)))
    for x,z in positions(p):
        a=a.cut(cylinder_y(x,z,(p.shoulder_diameter+p.shoulder_clearance)/2,-1,p.layer_split+.3))
        a=a.cut(cylinder_y(x,z,(p.head_diameter+.4)/2,-1,p.head_recess+p.head_thickness))
        # Major-diameter removal is a conservative strength audit before thread generation.
        b=b.cut(posed(tool,x,0,z,lip=True) if threaded else cylinder_y(x,z,(p.thread_major+2*p.thread_clearance)/2,p.layer_split-.1,p.thickness+1))
    for x in [-p.hole_x,p.hole_x]:
        hole=cq.Workplane('XY',origin=(x,p.back_hole_y,-1)).circle((p.shoulder_diameter+p.shoulder_clearance)/2).extrude(p.layer_split+1.3)
        recess=cq.Workplane('XY',origin=(x,p.back_hole_y,-1)).circle((p.head_diameter+.4)/2).extrude(1+p.head_recess+p.head_thickness)
        a=a.cut(hole).cut(recess)
        hole=cq.Workplane('XY',origin=(x,p.back_hole_y,p.layer_split-.1)).circle((p.thread_major+2*p.thread_clearance)/2).extrude(p.thickness-p.layer_split+1.1)
        b=b.cut(posed(tool,x,p.back_hole_y,0) if threaded else hole)
    return a,b

def thread_shape(p=P,clearance=0.,cutter=False):
    """Custom 16 x 2.4 mm trapezoidal print thread, ~45-degree flanks.
    Extra axial flank relief only on female cutter; not an ISO hardware thread.
    """
    root=p.thread_root/2+clearance; crest=p.thread_major/2+clearance
    start=p.thread_start-p.thread_pitch
    height=p.screw_tip-p.thread_start+2*p.thread_pitch
    axial=.07 if cutter else 0
    path=cq.Wire.makeHelix(p.thread_pitch,height,root,center=(0,0,start))
    points=[(root-.12,start-1.05-axial),(crest,start-.2-axial),
            (crest,start+.2+axial),(root-.12,start+1.05+axial)]
    ridge=cq.Workplane('XZ').polyline(points).close().sweep(path,isFrenet=True)
    body=cq.Workplane('XY',origin=(0,0,start-2)).circle(root).extrude(height+4).union(ridge)
    z0=p.thread_start-.2 if cutter else p.thread_start
    z1=p.thickness+1 if cutter else p.screw_tip
    return body.intersect(box(-12,12,-12,12,z0,z1))

def screw(p=P):
    head_end=p.head_recess+p.head_thickness
    head=cq.Workplane('XY',origin=(0,0,p.head_recess)).circle(p.head_diameter/2).extrude(p.head_thickness).edges('%Circle').chamfer(.2)
    shank=cq.Workplane('XY',origin=(0,0,head_end-.05)).circle(p.shoulder_diameter/2).extrude(p.thread_start-head_end+.05)
    shank=shank.faces('>Z').edges().chamfer(.15)
    thread=thread_shape(p)
    s=head.union(shank).union(thread)
    # Printable tapered lead at tip, avoiding a sharp thread start.
    lead=(cq.Workplane('XY',origin=(0,0,p.screw_tip-.7)).circle(p.thread_major/2)
          .workplane(offset=.7).circle(p.thread_root/2).loft())
    # Clip just the last .7 mm using the cone; preserve head/shaft below it.
    keep=box(-20,20,-20,20,-1,p.screw_tip-.7).union(lead)
    s=s.intersect(keep)
    # 8.2 mm across-flats hex; optional printed 7.8 mm driver supplied.
    drive=cq.Workplane('XY',origin=(0,0,p.head_recess-.1)).polygon(6,8.2/(3**.5/2)).extrude(1.3)
    return s.cut(drive)

def female_tool(p=P):
    t=thread_shape(p,p.thread_clearance,True)
    pilot=cq.Workplane('XY',origin=(0,0,p.layer_split-.2)).circle((p.shoulder_diameter+p.shoulder_clearance)/2).extrude(p.thread_start-p.layer_split+.35)
    return t.union(pilot)

def posed(s,x,y,z,lip=False):
    if lip:s=s.rotate((0,0,0),(1,0,0),-90)
    return s.translate((x,y,z))

def finished_halves(p=P):
    # Same structural geometry, with actual helical female threads.
    return halves(p,threaded=True)

def driver():
    grip=cq.Workplane('XY').box(40,12,6,centered=(True,True,False)).edges('|Z').fillet(2).faces('<Z').edges().chamfer(.5)
    shaft=cq.Workplane('XY',origin=(0,0,5.5)).polygon(6,7.8/(3**.5/2)).extrude(16.5)
    return grip.union(shaft).faces('>Z').edges().chamfer(.3)
