"""V3 vent hood; separate adjustable stationary-rim clamp. Millimetres; bed/front at Z=0; rear at Z=print_depth; wall at Z=depth.

Nominal mounting dimensions are placeholders, not a measured valve interface.
Importing this file constructs no CAD and writes nothing.
"""
import math
from vent_parameters import Parameters
from mounting_clamp import bolt_position
import cadquery as cq




def rounded_wire(points, radius, corners=None):
    wire = cq.Workplane('XZ').polyline(points).close().val()
    vertices = wire.Vertices()
    if corners is not None:
        vertices = [v for v in vertices if any(
            abs(v.X-x) < 1e-6 and abs(v.Z-z) < 1e-6 for x, z in corners)]
    return wire.fillet2D(radius, vertices)


def window_profile(p):
    half = p.outlet_width / 2
    bottom = p.outlet_bottom
    peak = bottom + p.outlet_height
    points = [(-half, bottom), (half, bottom), (half, peak-half*p.outlet_roof_slope),
              (0, peak), (-half, peak-half*p.outlet_roof_slope)]
    # Teardrop option points the lower end too; both retain the selected sloping upper roofs.
    if p.outlet_shape == 'teardrop':
        points = [(0, bottom), (half, bottom+half), (half, peak-half*p.outlet_roof_slope),
                  (0, peak), (-half, peak-half*p.outlet_roof_slope), (-half, bottom+half)]
        if p.outlet_height <= half*(1+p.outlet_roof_slope):
            raise ValueError('Teardrop needs positive straight sides between its end slopes')
    wire = rounded_wire(points, p.outlet_corner_radius, [point for point in points if point != (0, peak)])
    return wire.fillet2D(p.outlet_tip_radius, [v for v in wire.Vertices()
        if abs(v.X) < 1e-6 and abs(v.Z-peak) < 1e-6])


def build(p: Parameters):
    p.validate()
    r, t, b = p.radius, p.shell, p.bore
    offset = t * math.sqrt(1 + p.slope**2)
    inner_start = p.taper_start + (t-offset)/p.slope
    inner_end = p.shoulder_z + (p.collar_wall-offset)/p.slope
    corners = [(r, p.taper_start), (b+p.collar_wall, p.shoulder_z),
               (b, inner_end), (r-t, inner_start)]
    points = [(0, 0), (r, 0), (r, p.taper_start),
              (b+p.collar_wall, p.shoulder_z), (b+p.collar_wall, p.print_depth), (b, p.print_depth),
              (b, inner_end), (r-t, inner_start), (r-t, p.front), (0, p.front)]
    wire = rounded_wire(points, p.transition_radius, corners)
    # Floor/wall junction and outside bed rim are deliberately rounded separately.
    wire = wire.fillet2D(2.0, [v for v in wire.Vertices()
        if abs(v.X-r) < 1e-6 and abs(v.Z) < 1e-6])
    wire = wire.fillet2D(3.0, [v for v in wire.Vertices()
        if abs(v.X-(r-t)) < 1e-6 and abs(v.Z-p.front) < 1e-6])
    hood = cq.Workplane('XZ').add(wire).toPending().revolve(360, (0, 0), (0, 1))
    # Radial cutter extends completely through the shell, not across the chamber.
    cutter = cq.Solid.extrudeLinear(window_profile(p), [], cq.Vector(0, p.radius-p.bore+10, 0))
    cutter = cutter.translate((0, -p.radius-5, 0))
    for index in range(p.outlet_count):
        hood = hood.cut(cutter.rotate((0, 0, 0), (0, 0, 1),
                                     p.outlet_phase + index*360/p.outlet_count))
    # All resulting window lips, plus the exposed collar rim; exclude smooth seams.
    lip_edges = [e for e in hood.val().Edges() if
        p.outlet_bottom-0.01 <= e.Center().z <= p.outlet_bottom+p.outlet_height+0.01
        or abs(e.Center().z-p.print_depth) < 1e-6]
    hood = hood.newObject(lip_edges).fillet(p.lip_radius)
    for index in range(p.rib_count):
        length = p.rib_end_radius-p.rib_start_radius
        rib = (cq.Workplane('XY', origin=((p.rib_start_radius+p.rib_end_radius)/2, 0, p.front-0.2))
               .box(length, p.rib_width, p.rib_height+0.2, centered=(True, True, False))
               .edges('|Z').fillet(min(0.8, p.rib_width/2-0.1))
               .edges('>Z').fillet(0.6))
        hood = hood.union(rib.rotate((0, 0, 0), (0, 0, 1), index*360/p.rib_count))
    # Three supported screw lands; their undersides grow inward below 45 degrees.
    pad_top = p.print_depth
    pad_bottom = pad_top-p.mount_pad_thickness
    base_z = p.outlet_bottom+p.outlet_height+0.5
    outer_base = p.radius-p.slope*(base_z-p.taper_start)
    inner_base = p.inner_radius(base_z)-0.15
    assert (inner_base-p.mount_pad_inner)/(pad_bottom-base_z) <= 1
    profile = [(inner_base, base_z), (outer_base+0.15, base_z),
               (p.mount_pad_outer, pad_bottom), (p.mount_pad_outer, pad_top),
               (p.mount_pad_inner, pad_top), (p.mount_pad_inner, pad_bottom)]
    wire = cq.Workplane('XZ').polyline(profile).close().val()
    pad = cq.Solid.extrudeLinear(wire, [], cq.Vector(0, p.mount_pad_width, 0)).translate((0,-p.mount_pad_width/2,0))
    pad = cq.Workplane().add(pad).edges().filter(lambda e: abs(e.Center().z-pad_top) < 1e-6).fillet(0.3).val()
    for angle in p.mount_angles:
        hood = hood.union(pad.rotate((0,0,0),(0,0,1),angle))
        # Clamping contracts and rotates each tab. Slots follow that movement;
        # screw preload, rather than slot clearance, removes installed play.
        start = bolt_position(p, angle, p.clamp_min_diameter)
        end = bolt_position(p, angle, p.clamp_max_diameter)
        dx,dy = end[0]-start[0],end[1]-start[1]
        length = math.hypot(dx,dy)+p.mount_slot_width
        through_start=p.depth-(p.hood_standoff-p.mount_tab_thickness+p.mount_screw_length+1)
        cutter = (cq.Workplane('XY', origin=((start[0]+end[0])/2,(start[1]+end[1])/2,through_start))
                  .slot2D(length,p.mount_slot_width,math.degrees(math.atan2(dy,dx)))
                  .extrude(p.print_depth-through_start+1))
        hood = hood.cut(cutter)
        # Side-loaded sliding M3 nut: free insertion travel, antirotation flats,
        # a room-side retaining lip, and a full wall-side bearing land.
        travel=math.hypot(dx,dy)
        ux,uy=dx/travel,dy/travel
        vx,vy=-uy,ux
        cx,cy=(start[0]+end[0])/2,(start[1]+end[1])/2
        half=p.mount_nut_flats/2
        rad=p.mount_nut_flats/math.sqrt(3)
        left=travel/2+20  # entry runs into the open chamber, not a blind cavity
        right=travel/2
        profile=[(-left-rad,0),(-left-rad/2,-half),
                 (right+rad/2,-half),(right+rad,0),
                 (right+rad/2,half),(-left-rad/2,half)]
        points=[(cx+x*ux+y*vx,cy+x*uy+y*vy) for x,y in profile]
        pocket=(cq.Workplane('XY',origin=(0,0,pad_bottom+p.mount_nut_lip))
                .polyline(points).close().extrude(p.mount_nut_height))
        hood=hood.cut(pocket)
    return hood


if __name__ in ('__main__', '__cqgi__'):
    result = build(Parameters())
