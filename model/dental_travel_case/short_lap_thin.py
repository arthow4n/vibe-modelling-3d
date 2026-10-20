"""Thin full-box comparison; nominal 1.2mm walls, locally backed snap recesses.

The 30mm overlap and wall-snap profile are retained. Both mating dimensions move;
this is a matching thin body/cap pair, not a cap for the reinforced baseline.
Two 0.65mm external pads retain 1.2mm of backing behind the pocket/runout instead
of leaving a fragile 0.55mm skin or opening the long runout into a slot.
"""
from dataclasses import replace
import cadquery as cq
import m1_design as base
import short_lap_design as comparison
from short_lap_refinement import bump

OVERLAP = 30.
WALL = 1.2
PAD_PROJECTION = .65
PAD_WIDTH = 14.


def build_three_line():
    d = replace(comparison.dimensions(OVERLAP),wall=WALL,sleeve_wall=WALL,
                floor=WALL,clearance=.10,detent=.6,axial_play=.10)
    outer = base.prism(d.width,d.depth,d.corner,0,d.seam)
    outer = base.rounded_print_end(outer,d,top=False).edges('>Z').fillet(.6)
    sleeve = base.prism(d.sleeve_width,d.sleeve_depth,d.sleeve_corner,d.seam-.5,d.lap+.5)
    sleeve = sleeve.edges('>Z').chamfer(.4)
    cavity = cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (d.floor,d.width-2*WALL,d.depth-2*WALL,d.corner-WALL),
            (d.seam-6,d.width-2*WALL,d.depth-2*WALL,d.corner-WALL),
            (d.seam,d.sleeve_width-2*WALL,d.sleeve_depth-2*WALL,d.sleeve_corner-WALL),
            (d.seam+d.lap+1,d.sleeve_width-2*WALL,d.sleeve_depth-2*WALL,d.sleeve_corner-WALL))],ruled=True))
    cavity = cavity.edges('<Z').fillet(d.end_radius-WALL)
    plain = outer.union(sleeve).cut(cavity).clean()
    cap_outer = base.prism(d.width,d.depth,d.corner,d.seam,d.length-d.seam)
    cap_outer = base.rounded_print_end(cap_outer,d,top=True).edges('<Z').fillet(.6)
    radius = d.width/2
    pad = cq.Workplane('XZ',origin=(0,PAD_WIDTH/2,0)).polyline([
        (radius-.12,d.seam),(radius+PAD_PROJECTION,d.seam),
        (radius+PAD_PROJECTION,d.seam+d.lap+2),(radius,d.seam+d.lap+6),
        (radius-.12,d.seam+d.lap+6)]).close().extrude(PAD_WIDTH)
    pad = pad.edges('|Z').fillet(.3)
    pads = pad.union(pad.mirror('YZ'))
    cap_cavity = base.prism(d.width-2*WALL,d.depth-2*WALL,d.corner-WALL,
                           d.seam-1,d.length-d.floor-d.seam+1)
    cap_cavity = cap_cavity.edges('>Z').fillet(d.end_radius-WALL)
    cap = cap_outer.union(pads).cut(cap_cavity)
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
    result = cq.Assembly(name='three_line_short_lap_case')
    result.add(body,name='thin_body')
    result.add(base.print_cap(cap,d.length),name='thin_cap')
    return dict(dimensions=d,body=body,cap=cap,plain_body=plain,bump=tooth,
                pocket=pocket,pads=pads,result=result,main_wall=WALL,
                pad_projection=PAD_PROJECTION,kind='shell_end')
