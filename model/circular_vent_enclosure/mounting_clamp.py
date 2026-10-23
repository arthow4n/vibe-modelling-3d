"""Split PETG rim clamp; print rear flange face on bed. No exports during import.

Diameter argument is an explicit constant-curvature geometric pose, not a
prediction of the real deformation or contact pressure distribution.
"""
import math
import cadquery as cq
from vent_parameters import Parameters


def neutral_offset(p):
    band_area=p.clamp_wall*p.clamp_contact_height
    flange_area=p.rear_flange_width*p.rear_flange_thickness
    return (band_area*p.clamp_wall/2+flange_area*p.rear_flange_width/2)/(band_area+flange_area)


def gap_angle(p, diameter):
    free_neutral = p.clamp_free_diameter/2+neutral_offset(p)
    free_angle = 2*math.asin(p.clamp_split/(2*free_neutral))
    length = free_neutral*(2*math.pi-free_angle)
    return 2*math.pi-length/(diameter/2+neutral_offset(p))


def bolt_position(p, angle, diameter):
    """Hood-print XY of a tab following the constant-neutral-arc pose."""
    neutral_free = p.clamp_free_diameter/2+neutral_offset(p)
    neutral = diameter/2+neutral_offset(p)
    theta = math.radians(angle)
    theta = math.pi+(theta-math.pi)*neutral_free/neutral
    radius = p.mount_radius+(diameter-p.clamp_free_diameter)/2
    return radius*math.cos(theta), radius*math.sin(theta)


def build_clamp(p, diameter):
    p.validate()
    if not p.clamp_min_diameter <= diameter <= p.clamp_max_diameter:
        raise ValueError('Diameter outside declared geometric clamp range')
    r, t, h = diameter/2,p.clamp_wall,p.clamp_contact_height
    beta = gap_angle(p,diameter)/2
    if beta <= 0:
        raise ValueError('Split closes before requested diameter')
    band = cq.Workplane('XY').circle(r+t).circle(r).extrude(h)
    reach = r+30
    split = cq.Workplane('XY').polyline([(0,0),(reach,-reach*math.tan(beta)),
        (reach,reach*math.tan(beta))]).close().extrude(h+1)
    band = band.cut(split).edges('|Z').fillet(0.5)
    band = band.cut(cq.Solid.makeCone(r+0.5,r,0.5))
    flange=(cq.Workplane('XY',origin=(0,0,p.clamp_contact_height))
            .circle(r+p.rear_flange_width).circle(r).extrude(p.rear_flange_thickness))
    flange=flange.cut(cq.Workplane('XY').polyline([(0,0),(reach,-reach*math.tan(beta)),
            (reach,reach*math.tan(beta))]).close().extrude(p.hood_standoff+1))
    band=band.union(flange)
    half_gap = (r+t/2)*math.sin(beta)
    ear_x = r+p.clamp_bolt_offset
    for sign in (-1,1):
        ear = (cq.Workplane('XY', origin=(r+8.75, sign*(half_gap+p.clamp_ear_wall/2),0))
               .box(18.5,p.clamp_ear_wall,h,centered=(True,True,False))
               .edges('|Z').fillet(0.8).edges('>Z').fillet(0.6))
        band = band.union(ear)
    # Supported head-seat extension lets the stock 25 mm screw clear the nearby
    # mounting brace even at the smallest grip setting.
    outside=half_gap+p.clamp_ear_wall
    yz=[(outside,3.5),(outside+p.clamp_head_standoff,3.5),
        (outside+p.clamp_head_standoff,15),(outside,15+p.clamp_head_standoff)]
    boss=(cq.Workplane('YZ',origin=(ear_x-4.5,0,0)).polyline(yz).close().extrude(9))
    band=band.union(boss)
    # Horizontal M4 clearance with a pointed roof instead of a circular ceiling.
    hole_r = p.clamp_bolt_hole/2
    axis = cq.Workplane('XZ').center(ear_x,8).circle(hole_r).extrude(30,both=True)
    roof = (cq.Workplane('XZ').polyline([(ear_x-hole_r,8),
        (ear_x+hole_r,8),(ear_x,8-hole_r*math.sqrt(2))]).close().extrude(30,both=True))
    band = band.cut(axis.union(roof))
    # M4 nut on the negative-Y side; screw head/driver approach from +Y.
    # Raised pointed roof preserves antirotation flats and prints progressively.
    f=7.4; rr=f/math.sqrt(3)
    nut_points=[(x,-z) for x,z in [(-f/2,-rr/2),(0,-rr),(f/2,-rr/2),(f/2,rr/2),
                (0,rr/2+f/2),(-f/2,rr/2)]]
    nut = (cq.Workplane('XZ').polyline([(ear_x+x,8+z) for x,z in nut_points])
           .close().extrude(2.1).translate((0,half_gap+p.clamp_ear_wall+0.1,0)))
    nut=nut.mirror('XZ')
    band = band.cut(nut)
    # Room-facing loading slot: drop nut into the saddle before assembly.
    feed=(cq.Workplane('XY',origin=(ear_x,-half_gap-p.clamp_ear_wall+0.3,8))
          .box(f,3.4,p.hood_standoff-8+1,centered=(True,True,False)))
    band=band.cut(feed)
    # Three open-backed nut channels with broad axial bearing roofs.
    for angle in p.mount_angles:
        px, py = bolt_position(p,angle,diameter)
        theta = math.atan2(py,px)
        radius = math.hypot(px,py)
        top = p.hood_standoff
        bottom = top-p.mount_tab_thickness
        root_radius=r+t
        profile=[(root_radius-0.6,0),(root_radius+7,0),
                 (radius+5,bottom),(radius+5,top),
                 (radius-5,top),(radius-5,bottom)]
        wire=cq.Workplane('XZ').polyline(profile).close().val()
        tab=cq.Solid.extrudeLinear(wire,[],cq.Vector(0,12,0)).translate((0,-6,0))
        tab=tab.rotate((0,0,0),(0,0,1),-math.degrees(theta))
        tab=cq.Workplane().add(tab).edges().fillet(0.5).val()
        # Installed XY is the reflection of the hood's print XY.
        band=band.union(tab)
        hole=(cq.Workplane('XY',origin=(px,-py,bottom-1)).circle(p.mount_hole/2)
              .extrude(p.mount_tab_thickness+2))
        band=band.cut(hole)
        # Socket-cap head on the open wall side. Straight rear bench access.
        counterbore=(cq.Workplane('XY',origin=(px,-py,-1)).circle(3.2)
                     .extrude(bottom+1))
        band=band.cut(counterbore)
    return band


if __name__ in ('__main__','__cqgi__'):
    p=Parameters()
    result=build_clamp(p,p.clamp_free_diameter).rotate((0,0,0),(1,0,0),180).translate((0,0,p.hood_standoff))
