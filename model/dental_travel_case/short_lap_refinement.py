"""Balanced production snap: tighter guidance and gentle closing ramp.

The comparison geometry stays in short_lap_design. This refinement increases
the small bump from .65 to .8mm, still below M1's 2mm independent hook, and
lengthens its closing ramp. Actual force remains an uncalibrated prediction.
"""
from dataclasses import replace
import cadquery as cq
import short_lap_design as comparison
import closure_research_design as research
import m1_design as base


def bump(radius,d,*,pocket):
    projection = d.detent+(.15 if pocket else 0)
    play = d.axial_play if pocket else 0
    z = d.latch_z
    points = [(radius-.2,z-1.25-play),(radius+projection,z-.25-play),
              (radius+projection,z+.25+play),(radius-.2,z+1.9+play)]
    width = d.bump_width+(.6 if pocket else 0)
    return cq.Workplane('YZ',origin=(-width/2,0,0)).polyline(points).close().extrude(width)


def build(overlap):
    d = replace(comparison.dimensions(overlap),clearance=.10,detent=.8,axial_play=.10)
    plain,cap = research.plain_shells(d)
    tooth = bump(d.sleeve_width/2,d,pocket=False).rotate((0,0,0),(0,0,1),90)
    tooth = tooth.union(tooth.mirror('YZ'))
    pocket = bump(d.sleeve_width/2,d,pocket=True).rotate((0,0,0),(0,0,1),90)
    pocket = pocket.union(pocket.mirror('YZ'))
    # Preserve a short retaining lip, then full radial relief for the .8mm bump.
    top = d.latch_z-3.2
    radial = d.sleeve_width/2
    track = base.box(radial+(d.detent+.15-.2)/2,0,(d.seam-1+top)/2,
                     d.detent+.15+.2,d.bump_width+.6,top-d.seam+1)
    track = track.union(track.mirror('YZ'))
    body = plain.union(tooth).clean()
    cap = cap.cut(pocket).cut(track).cut(comparison.grip_cut(d)).clean()
    result = cq.Assembly(name='balanced_short_lap_case')
    result.add(body,name='body')
    result.add(base.print_cap(cap,d.length),name='cap')
    return dict(dimensions=d,body=body,cap=cap,plain_body=plain,bump=tooth,
                pocket=pocket,kind='shell_end',result=result)
