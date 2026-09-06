"""PETG charger wrap with integrated MagSafe 3 parking rails. Dimensions in mm.

Reference attribution and physical-fit limitations: notes/README.md.
Standalone parametric source; no downloaded geometry is needed to build.
Print on the XY ring face at Z=0. Slide head toward ring, cable first.
"""
import cadquery as cq
from math import sqrt

opening_width = 79.6
opening_thickness = 28.0
corner_radius = 6.0
band_wall = 2.7
band_width = 6.0
groove_pitch = 5.4
tooth_count = 12
head_width = 18.81
head_length = 13.18
head_thickness = 4.48
side_clearance = 0.35  # per side, not measured on user's black cable
depth_clearance = 0.45  # total
cradle_center = 12.0  # first groove; skip covered 17.4 groove when winding
cradle_floor = 1.4
rail_wall = 1.6
lip_overlap = 1.2
cable_exit_width = 5.0
head_stop_z = 10.0
guard_extension = 1.8

def band():
    """Reconstruct the reference's analytic arcs and repeated scallops.

    The last tooth has a slightly asymmetric termination in the original;
    preserve that measured arc rather than changing its grip.
    """
    w, h, r, t = opening_width, opening_thickness, corner_radius, band_wall
    ro = r+t
    q = ro/sqrt(2)
    p = cq.Workplane('XY').moveTo(r,h+t)
    p=p.threePointArc((r-q,h-r+q),(-t,h-r)).lineTo(-t,r)
    p=p.threePointArc((r-q,r-q),(r,-t)).lineTo(6.6,-t)
    p=p.threePointArc((8.0696938343,-3.4607694993),(8.2970562748,-5.1))
    for i in range(tooth_count-1):
        x=9.3+i*groove_pitch
        p=p.threePointArc((x,-6.90845841623),(x+1.00294372515,-5.1))
        p=p.threePointArc((x+2.7,-t),(x+4.39705627485,-5.1))
    p=p.threePointArc((68.5446,-6.8982),(69.8314,-5.383))
    p=p.threePointArc((69.8461,-3.5915),(71.4,-t)).lineTo(w-r,-t)
    p=p.threePointArc((w-r+q,r-q),(w+t,r)).lineTo(w+t,h-r)
    p=p.threePointArc((w-r+q,h-r+q),(w-r,h+t)).lineTo(71.4,h+t)
    p=p.threePointArc((69.8461,h+3.5915),(69.8314,h+5.383))
    p=p.threePointArc((68.5446,h+6.8982),(67.69705627485,h+5.1))
    for i in reversed(range(tooth_count-1)):
        x=9.3+i*groove_pitch
        p=p.threePointArc((x+2.7,h+t),(x+1.00294372515,h+5.1))
        p=p.threePointArc((x,h+6.90845841623),(x-1.00294372515,h+5.1))
    p=p.threePointArc((8.0696938343,h+3.4607694993),(6.6,h+t)).close()
    outer=p.extrude(band_width)
    hole=(cq.Workplane('XY').center(w/2,h/2).rect(w,h)
          .extrude(band_width).edges('|Z').fillet(r))
    return outer.cut(hole)

def box(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))

def cradle():
    """Open slide rails. No snap force or contact-pin retention is required.

    Rails continue from the band face, avoiding unsupported horizontal roofs.
    Shoulders stop the housing, while the cable leaves through an open slot.
    The wrapped cable supplies axial retention; intentional removal is upward.
    """
    half=head_width/2+side_clearance
    left,right=cradle_center-half,cradle_center+half
    back=-cradle_floor
    front=back-head_thickness-depth_clearance
    top=head_stop_z+head_length+guard_extension
    floor=box(left-rail_wall,right+rail_wall,back,0,band_width-1,top)
    # Broad rear finger scallop; leaves the lower back and both side rails.
    relief=(cq.Workplane('XZ').center(cradle_center,top)
            .circle(6).extrude(3,both=True))
    floor=floor.cut(relief)
    for a,b in [(left-rail_wall,left),(right,right+rail_wall)]:
        floor=floor.union(box(a,b,front-rail_wall,0,0,top))
    # Retaining lips only overlap the two housing edges; centre stays open.
    for a,b in [(left,left+lip_overlap),(right-lip_overlap,right)]:
        floor=floor.union(box(a,b,front-rail_wall,front,0,top))
    for a,b in [(left,cradle_center-cable_exit_width/2),
                (cradle_center+cable_exit_width/2,right)]:
        floor=floor.union(box(a,b,front,back,0,head_stop_z))
    # Full-height exposed rail corners only: the stepped internal shoulders
    # meet the back scallop and cannot take a blanket edge fillet.
    floor=floor.edges('|Z').filter(lambda e: e.Length()>top-0.01).fillet(0.35)
    floor=floor.faces('>Z').edges().chamfer(0.2)
    return floor

result=band().union(cradle())
assert result.val().isValid()
assert len(result.solids().vals()) == 1
