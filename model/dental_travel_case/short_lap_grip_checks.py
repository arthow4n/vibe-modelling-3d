"""Actual band sections, unchanged joint geometry, passage and publication."""
from pathlib import Path
import json
import math
import cadquery as cq
import cairosvg
import m1_design as base
from short_lap_thin import build_three_line,WALL
from short_lap_grip import build,RAMP
from closure_research_drawings import canvas,label,section,BLUE,ORANGE
from closure_research_checks import hashes

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/grip_human'
STEM='short_lap_case_three_line_grip'
INPUTS=('short_lap_grip.py','short_lap_grip_checks.py',STEM+'.py','grip_placement.py',
    'short_lap_thin.py','short_lap_design.py','short_lap_refinement.py',
    'closure_research_design.py','m1_design.py','m1_checks.py',
    'closure_research_drawings.py','../../uv.lock')


def inspect(parts):
    d=parts['dimensions'];band=parts['band'];old=build_three_line();eps=1e-5
    # The replacement operation cuts a complete axial shell slice. Check the
    # intended reconnection explicitly; validity alone permits detached rings.
    for name in ('body','cap'):
        assert len(parts[name].val().Solids())==1,'Band must join both neighbouring shell regions'
    rows=[]
    for name,offset in (('body',band.body_center_mm),('cap',band.cap_center_mm)):
        center=d.seam+offset
        for dz in (-12.,-10.,-8.,-6.,-4.,0.,4.,6.,8.,10.,12.):
            z=center+dz
            for title,start,direction in (
                ('width',(0.,0.,z),(1.,0.,0.)),
                ('depth',(0.,0.,z),(0.,1.,0.)),
                ('corner',(d.width/2-d.corner,d.depth/2-d.corner,z),(2**-.5,2**-.5,0.))):
                a=cq.Vector(*start);v=cq.Vector(*direction)
                ray=cq.Edge.makeLine(a,a+v*80)
                edges=parts[name].val().intersect(ray).Edges()
                assert len(edges)==1,(name,dz,title,'unbroken shell section required')
                length=edges[0].Length()
                assert abs(length-WALL)<1e-5,(name,dz,title,length)
                rows.append(dict(part=name,offset_mm=dz,section=title,wall_mm=length))
        # Exact inward depth at the middle of each band, rather than a parameter-only assertion.
        edge=parts[name].val().intersect(cq.Edge.makeLine(cq.Vector(0,0,center),cq.Vector(80,0,center))).Edges()[0]
        assert abs(max(v.X for v in edge.Vertices())-(d.width/2-band.depth_mm))<1e-5
    joint=[]
    body_roi=base.box(0,0,d.seam+(d.lap-8)/2,d.width+4,d.depth+4,d.lap+8)
    cap_rois=[base.box(sign*d.width/2,0,d.seam+(d.lap+9)/2,10,d.depth+4,d.lap+9) for sign in (-1,1)]
    for name,roi in [('body',body_roi),*[('cap',r) for r in cap_rois]]:
        a=parts[name].intersect(roi);b=old[name].intersect(roi)
        difference=a.cut(b).val().Volume()+b.cut(a).val().Volume()
        assert difference<eps,(name,'joint altered',difference)
        joint.append(dict(part=name,symmetric_difference_mm3=difference))
    for sign in (-1,1):
        point=cq.Vector(0,sign*(d.depth/2-WALL/2),d.seam+1.5)
        assert parts['cap'].val().isInside(point,1e-6),'Old finger notch must be filled'
    assert parts['body'].intersect(parts['cap']).val().Volume()<eps
    path=[]
    for lift in (0.,.5,1.,2.,3.,6.,12.,30.,31.,90.):
        cap=parts['cap'].translate((0,0,lift))
        guide=parts['plain_body'].intersect(cap).val().Volume()
        snap=parts['body'].intersect(cap).val().Volume()
        assert guide<eps
        if lift>=6.:assert snap<eps
        path.append(dict(lift_mm=lift,guide_mm3=guide,snap_mm3=snap))
    assert parts['plain_body'].intersect(parts['cap'].translate((0,0,-.1))).val().Volume()>.05
    for sign in (-1,1):
        tooth=parts['bump'].intersect(base.box(sign*d.width/2,0,d.latch_z,d.width,20,8))
        for shift in (-d.clearance,0.,d.clearance):
            assert tooth.intersect(parts['cap'].translate((shift,0,1))).val().Volume()>.05
    passages=[]
    for name,gauge in (('brush',cq.Workplane('XY',origin=(0,-5,4.5)).circle(15).extrude(400)),
                       ('tube',base.box(0,0,200,55,40,394))):
        assert gauge.intersect(parts['body']).val().Volume()<eps
        gap=gauge.val().distance(parts['body'].val());assert gap>=.8-1e-6
        # Limit cap passage gauges to its grip region; a through-gauge should
        # not be tested against the intentionally closed roof.
        region=base.box(0,0,d.seam+band.cap_center_mm,d.width+4,d.depth+4,24)
        cap_gauge=gauge.intersect(region)
        assert cap_gauge.intersect(parts['cap']).val().Volume()<eps
        cap_gap=cap_gauge.val().distance(parts['cap'].val());assert cap_gap>=.8-1e-6
        passages.append(dict(gauge=name,body_gap_mm=gap,cap_band_gap_mm=cap_gap))
    from m1_checks import end_rounds
    end_rounds(parts)
    slope=band.depth_mm*1.875/RAMP
    return dict(sections=rows,joint=joint,path=path,passages=passages,
        old_notches_removed=True,max_radial_slope=slope,
        max_radial_step_per_02mm_layer=slope*.2,
        minimum_normal_wall_mm=WALL/math.sqrt(1+slope*slope),
        scope='Actual CAD and individual gauges; unchanged joint geometry, not a new force rating or simultaneous packing proof')


def draw(parts):
    d=parts['dimensions'];band=parts['band']
    items=canvas('Three-line wrap-grip case — actual finished CAD',940)
    label(items,25,75,'Body and cap: 1.2 mm horizontal wall sections, 0.7 mm inward wrap bands. No seam finger notches.',17)
    xf=lambda v:(135+2*v.x,670-2*v.z)
    section(items,parts['body'].val(),'XZ',(0,0,0),xf,BLUE)
    section(items,parts['cap'].val(),'XZ',(0,0,0),xf,ORANGE)
    label(items,35,725,'Closed-case axial section',17)
    for i,(name,center,color) in enumerate((('body',d.seam+band.body_center_mm,BLUE),('cap',d.seam+band.cap_center_mm,ORANGE))):
        top=125+i*310
        label(items,365,top,f'{name.capitalize()} band — exact quintic ramps, enlarged depth',20)
        crop=base.box(d.width/2,0,center,8,3,26).val()
        xf=lambda v,top=top,center=center:(600+35*(v.x-d.width/2),top+160-9*(v.z-center))
        section(items,parts[name].val().intersect(crop),'XZ',(0,0,0),xf,color)
        label(items,700,top+65,'20 mm wide / 0.7 mm deep',17)
        label(items,700,top+100,'6 mm ramp / 8 mm landing / 6 mm ramp',17)
        label(items,700,top+135,'Both skins move inward together',17)
        label(items,700,top+170,'1.2 mm across each printed layer',17)
        label(items,700,top+205,'Smooth slope and curvature at joins',17)
    label(items,30,790,'Band centres: body −30 mm / cap +55 mm from seam. Joint, local backing and rounded ends retained.',18)
    label(items,30,830,'Maximum radial movement: 0.044 mm per 0.2 mm layer. Minimum normal thickness ≈1.172 mm on ramps.',17)
    label(items,30,870,'Left: same axial/radial scale. Detail: 35 px/mm radially, 9 px/mm axially. Geometry is from the final builder.',16)
    label(items,30,910,'Use matching body and cap. Individual brush/tube passage checked; actual grip feel and loaded use need a print.',16)
    items.append('</svg>');path=OUT/'finished_band_sections.svg'
    path.write_text('\n'.join(items)+'\n');cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    identity=hashes(INPUTS);parts=build();data=inspect(parts);draw(parts)
    assert identity==hashes(INPUTS),'Inputs changed during CAD checking'
    (OUT/'finished_checks.json').write_text(json.dumps(dict(source_sha256=identity,**data),indent=2)+'\n')
    print(json.dumps(dict(sections=len(data['sections']),joint=data['joint'],passages=data['passages'],notches_removed=True)))


if __name__=='__main__':main()
