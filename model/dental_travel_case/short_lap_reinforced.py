"""30mm production candidate with locally stronger bearing walls.

Keep the exterior and seam. A 2mm sleeve and 2.7mm receiving band address the
first 24mm candidate's flexible side-bearing response. Main cup walls stay 2mm;
the mouth is 64.6 x 41.6mm. No internal spring channels are introduced.
"""
from dataclasses import replace
import cadquery as cq
import short_lap_design as comparison
from short_lap_refinement import bump
import m1_design as base

SELECTED_OVERLAP = 30.
MAIN_WALL = 2.


def build(overlap):
    d = replace(comparison.dimensions(overlap),wall=2.7,sleeve_wall=2.,
                clearance=.10,detent=.6,axial_play=.10)
    outer = base.prism(d.width,d.depth,d.corner,0,d.seam)
    outer = base.rounded_print_end(outer,d,top=False).edges('>Z').fillet(.6)
    sleeve = base.prism(d.sleeve_width,d.sleeve_depth,d.sleeve_corner,d.seam-.5,d.lap+.5)
    sleeve = sleeve.edges('>Z').chamfer(.4)
    inner = cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (d.floor,d.width-2*MAIN_WALL,d.depth-2*MAIN_WALL,d.corner-MAIN_WALL),
            (d.seam-6,d.width-2*MAIN_WALL,d.depth-2*MAIN_WALL,d.corner-MAIN_WALL),
            (d.seam,d.sleeve_width-2*d.sleeve_wall,d.sleeve_depth-2*d.sleeve_wall,d.sleeve_corner-d.sleeve_wall),
            (d.seam+d.lap+1,d.sleeve_width-2*d.sleeve_wall,d.sleeve_depth-2*d.sleeve_wall,d.sleeve_corner-d.sleeve_wall))],ruled=True))
    inner = inner.edges('<Z').fillet(d.end_radius-MAIN_WALL)
    plain = outer.union(sleeve).cut(inner).clean()
    cap_outer = base.prism(d.width,d.depth,d.corner,d.seam,d.length-d.seam)
    cap_outer = base.rounded_print_end(cap_outer,d,top=True).edges('<Z').fillet(.6)
    cap_inner = cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(d.width-2*t,d.depth-2*t,d.corner-t,z)
        for z,t in ((d.seam-1,d.wall),(d.seam+d.lap+2,d.wall),
                    (d.seam+d.lap+6,MAIN_WALL),(d.length-d.floor,MAIN_WALL))],ruled=True))
    cap_inner = cap_inner.edges('>Z').fillet(d.end_radius-MAIN_WALL)
    cap = cap_outer.cut(cap_inner)
    tooth = bump(d.sleeve_width/2,d,pocket=False).rotate((0,0,0),(0,0,1),90)
    tooth = tooth.union(tooth.mirror('YZ'))
    pocket = bump(d.sleeve_width/2,d,pocket=True).rotate((0,0,0),(0,0,1),90)
    pocket = pocket.union(pocket.mirror('YZ'))
    top = d.latch_z-3.2
    track = base.box(d.sleeve_width/2+(d.detent+.15-.2)/2,0,(d.seam-1+top)/2,
                     d.detent+.15+.2,d.bump_width+.6,top-d.seam+1)
    track = track.union(track.mirror('YZ'))
    body = plain.union(tooth).clean()
    cap = cap.cut(pocket).cut(track).cut(comparison.grip_cut(d)).clean()
    result = cq.Assembly(name='reinforced_short_lap_case')
    result.add(body,name='body')
    result.add(base.print_cap(cap,d.length),name='cap')
    return dict(dimensions=d,body=body,cap=cap,plain_body=plain,bump=tooth,
                pocket=pocket,kind='shell_end',result=result)
