"""C: continuous outer walls, exposed seam collar and a sleeve-tip hard seat.

Assembly Z follows the brush; body floor is Z=0. No publication on import.
The original 1.2 mm sleeve, catch profile and mating cavity stay unchanged.
Only width grows: ordinary end walls are 1.85 mm, broad walls remain 1.2 mm.
"""
from dataclasses import replace
import cadquery as cq
import m1_design as base
from short_lap_design import dimensions
from short_lap_refinement import bump

WALL = 1.2
END_BACKING_EXTRA = .65
COLLAR_HEIGHT = 3.0
SEAT_OVERHANG = 1.0
SEAT_RAMP_HEIGHT = 1.5
RIM_RADIUS = .45


def build():
    d = replace(dimensions(30.), wall=WALL, sleeve_wall=WALL, floor=WALL,
                clearance=.10, detent=.6, axial_play=.10)
    exterior = replace(d, width=d.width+2*END_BACKING_EXTRA)
    rim_z = d.seam+COLLAR_HEIGHT
    seat_z = d.seam+d.lap
    inner_w = d.width-2*WALL
    inner_h = d.depth-2*WALL
    inner_r = d.corner-WALL
    if not (0 < COLLAR_HEIGHT < d.lap-d.tip_offset-4):
        raise ValueError('Collar must stay below catches and their retaining lips')
    if not (.4+d.clearance < SEAT_OVERHANG < WALL+d.clearance):
        raise ValueError('Seat must overlap the chamfered sleeve tip without blocking its bore')

    outer = base.prism(exterior.width,d.depth,d.corner,0,d.seam)
    outer = base.rounded_print_end(outer,exterior,top=False).edges('>Z').fillet(.6)
    sleeve = base.prism(d.sleeve_width,d.sleeve_depth,d.sleeve_corner,d.seam-.5,d.lap+.5)
    sleeve = sleeve.edges('>Z').chamfer(.4)
    cavity = cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (d.floor,inner_w,inner_h,inner_r),
            (d.seam-6,inner_w,inner_h,inner_r),
            (d.seam,d.sleeve_width-2*WALL,d.sleeve_depth-2*WALL,d.sleeve_corner-WALL),
            (seat_z+1,d.sleeve_width-2*WALL,d.sleeve_depth-2*WALL,d.sleeve_corner-WALL))],ruled=True))
    cavity = cavity.edges('<Z').fillet(d.end_radius-WALL)
    plain = outer.union(sleeve).cut(cavity).clean()

    cap_outer = base.prism(exterior.width,d.depth,d.corner,rim_z,d.length-rim_z)
    cap_outer = base.rounded_print_end(cap_outer,exterior,top=True)
    # A stepped cavity creates the downward-facing sleeve seat at Z=seat_z.
    # In the inverted print the seat grows inward along the 1.5 mm taper.
    lower = base.prism(inner_w,inner_h,inner_r,rim_z-1,seat_z-rim_z+1)
    upper = cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (seat_z,inner_w-2*SEAT_OVERHANG,inner_h-2*SEAT_OVERHANG,inner_r-SEAT_OVERHANG),
            (seat_z+SEAT_RAMP_HEIGHT,inner_w,inner_h,inner_r),
            (d.length-d.floor,inner_w,inner_h,inner_r))],ruled=True))
    upper = upper.edges('>Z').fillet(d.end_radius-WALL)
    cap = cap_outer.cut(lower.union(upper)).edges('<Z').fillet(RIM_RADIUS)

    tooth = bump(d.sleeve_width/2,d,pocket=False).rotate((0,0,0),(0,0,1),90)
    tooth = tooth.union(tooth.mirror('YZ'))
    pocket = bump(d.sleeve_width/2,d,pocket=True).rotate((0,0,0),(0,0,1),90)
    pocket = pocket.union(pocket.mirror('YZ'))
    track_top = d.latch_z-3.2
    track = base.box(d.sleeve_width/2+(d.detent+.15-.2)/2,0,(rim_z-1+track_top)/2,
                     d.detent+.15+.2,d.bump_width+.6,track_top-rim_z+1)
    track = track.union(track.mirror('YZ'))
    body = plain.union(tooth).clean()
    cap = cap.cut(pocket).cut(track).clean()
    result = cq.Assembly(name='smooth_seam_grip_case')
    result.add(body,name='body')
    result.add(base.print_cap(cap,d.length),name='cap')
    return dict(dimensions=d, exterior=exterior, body=body, cap=cap,
                plain_body=plain, bump=tooth, pocket=pocket, result=result,
                rim_z=rim_z, seat_z=seat_z)


def assembled(parts):
    result = cq.Assembly(name='smooth_case_closed')
    result.add(parts['body'],name='body',color=cq.Color(.50,.66,.72))
    result.add(parts['cap'],name='cap',color=cq.Color(.78,.72,.59))
    return result
