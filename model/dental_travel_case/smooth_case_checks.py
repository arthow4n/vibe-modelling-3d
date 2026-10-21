"""C-specific geometry checks and actual-CAD explanatory sections."""
from pathlib import Path
import json
import cadquery as cq
import cairosvg
import m1_design as base
from smooth_case_design import build, WALL, END_BACKING_EXTRA, COLLAR_HEIGHT
from closure_research_checks import hashes
from closure_research_drawings import canvas, label, section, BLUE, ORANGE

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/smooth_case'
INPUTS = ('smooth_case_design.py','smooth_case_checks.py','short_lap_case_smooth.py',
          'short_lap_case_smooth_assembled.py','short_lap_design.py','short_lap_refinement.py',
          'short_lap_thin.py','closure_research_design.py','m1_design.py','m1_checks.py',
          'closure_research_drawings.py','closure_research_checks.py','../../uv.lock')
EPS = 1e-5


def inspect(parts):
    d=parts['dimensions'];ex=parts['exterior']
    for name in ('body','cap'):
        assert parts[name].val().isValid()
        assert len(parts[name].val().Solids())==1, name+' must be connected'
    # The retention revision thickens inward, preserving the existing guide envelope.
    sleeve_sections=[]
    for z in (178.,185.,195.):
        for axis,end,expected in (('width',(80,0,z),d.sleeve_width/2),('depth',(0,80,z),d.sleeve_depth/2)):
            edges=parts['body'].val().intersect(cq.Edge.makeLine(cq.Vector(0,0,z),cq.Vector(*end))).Edges()
            assert len(edges)==1
            outside=max(v.X if axis=='width' else v.Y for v in edges[0].Vertices())
            assert abs(outside-expected)<1e-5
            assert abs(edges[0].Length()-d.sleeve_wall)<1e-5
            sleeve_sections.append(dict(z_mm=z,axis=axis,wall_mm=edges[0].Length(),outer_coordinate_mm=outside))
    assert abs(parts['rim_z']-d.seam-COLLAR_HEIGHT)<1e-6
    rows=[]
    for name,levels in (('body',(12.,60.,120.,168.)),('cap',(180.,190.,201.,220.,240.,255.))):
        for z in levels:
            for axis,end,expected in (('width',(80,0,z),ex.width/2),('depth',(0,80,z),ex.depth/2)):
                edges=parts[name].val().intersect(cq.Edge.makeLine(cq.Vector(0,0,z),cq.Vector(*end))).Edges()
                assert len(edges)==1,(name,z,axis,'unbroken wall')
                outside=max(v.X if axis=='width' else v.Y for v in edges[0].Vertices())
                assert abs(outside-expected)<1e-5,(name,z,axis,'exterior bump or groove')
                thick=edges[0].Length()
                expected_wall=(parts['broad_wall'] if axis=='depth' else WALL if name=='cap' and z in (180.,190.,201.) else WALL+END_BACKING_EXTRA)
                assert abs(thick-expected_wall)<1e-5,(name,z,axis,thick,expected_wall)
                rows.append(dict(part=name,z_mm=z,axis=axis,wall_mm=thick,outer_coordinate_mm=outside))
    assert parts['body'].intersect(parts['cap']).val().Volume()<EPS
    seat_gap=parts['plain_body'].val().distance(parts['cap'].val())
    assert seat_gap<1e-6,'Sleeve tip must contact the internal cap stop'
    seat_overlap=parts['plain_body'].intersect(parts['cap'].translate((0,0,-.1))).val().Volume()
    assert seat_overlap>.05,'Overclosing must hit a hard stop'
    path=[]
    for lift in (0.,.25,.5,1.,2.,3.,4.,6.,12.,27.,30.,31.,90.):
        cap=parts['cap'].translate((0,0,lift))
        guide=parts['plain_body'].intersect(cap).val().Volume()
        snap=parts['body'].intersect(cap).val().Volume()
        assert guide<EPS,(lift,'unintended guide obstruction',guide)
        if lift>=6:assert snap<EPS,(lift,'catch still dragging',snap)
        path.append(dict(lift_mm=lift,guide_mm3=guide,snap_mm3=snap))
    catches=[]
    for sign in (-1,1):
        tooth=parts['bump'].intersect(base.box(sign*d.width/2,0,d.latch_z,d.width,20,8))
        for shift in (-d.clearance,0.,d.clearance):
            volume=tooth.intersect(parts['cap'].translate((shift,0,1))).val().Volume()
            assert volume>.05,(sign,shift,'missing independent capture')
            catches.append(dict(end=sign,lateral_shift_mm=shift,obstruction_mm3=volume))
    # No-band/exposed-collar grip is dimensional only, not a finger-force proof.
    collar=base.box(0,0,d.seam+COLLAR_HEIGHT/2,ex.width+4,d.depth+4,COLLAR_HEIGHT-.02)
    assert parts['cap'].intersect(collar).val().Volume()<EPS
    passages=[]
    for name,gauge in (('brush',cq.Workplane('XY',origin=(0,-5,4.5)).circle(15).extrude(400)),
                       ('tube',base.box(0,0,200,55,40,394))):
        assert gauge.intersect(parts['body']).val().Volume()<EPS
        body_gap=gauge.val().distance(parts['body'].val())
        cap_gauge=gauge.intersect(base.box(0,0,(parts['rim_z']+260)/2,ex.width+4,d.depth+4,260-parts['rim_z']))
        assert cap_gauge.intersect(parts['cap']).val().Volume()<EPS
        cap_gap=cap_gauge.val().distance(parts['cap'].val())
        assert min(body_gap,cap_gap)>=.8-1e-6
        passages.append(dict(gauge=name,body_gap_mm=body_gap,cap_gap_mm=cap_gap))
    from m1_checks import end_rounds
    end_rounds(parts)
    return dict(variant=parts['variant'],sections=rows,sleeve_sections=sleeve_sections,seat_gap_mm=seat_gap,
                overclose_obstruction_mm3=seat_overlap,path=path,catches=catches,passages=passages,
                collar_height_mm=COLLAR_HEIGHT,large_end_rounds=True,
                scope='Rigid CAD; obstruction is not retention force. Individual gauges are not simultaneous loaded packing.')


def draw(parts):
    d=parts['dimensions'];items=canvas('Smooth C case — actual finished CAD sections',910)
    label(items,25,76,'75.8 × 52.8 × 264 mm exterior • 3 mm exposed seam • no wrap bands or local exterior pads',18)
    xf=lambda v:(140+2*v.x,680-2*v.z)
    section(items,parts['body'].val(),'XZ',(0,0,0),xf,BLUE)
    section(items,parts['cap'].val(),'XZ',(0,0,0),xf,ORANGE)
    label(items,35,725,'Closed axial section, same scale',16)
    label(items,370,135,'Seam grip — enlarged, true aspect ratio',20)
    crop=base.box(d.width/2,0,d.seam+2,8,4,14).val()
    xf=lambda v:(520+15*(v.x-d.width/2),280-15*(v.z-d.seam))
    for name,color in (('body',BLUE),('cap',ORANGE)):
        section(items,parts[name].val().intersect(crop),'XZ',(0,0,0),xf,color)
    label(items,700,215,'Cap rim stops 3 mm above body.',17)
    label(items,700,248,'Continuous sleeve stays behind it.',17)
    label(items,700,281,'Rounded opposing rim contacts.',17)
    label(items,370,430,'Catch + sleeve-tip stop — enlarged',20)
    crop=base.box(d.width/2,0,d.latch_z+1,9,4,14).val()
    xf=lambda v:(520+15*(v.x-d.width/2),580-15*(v.z-d.latch_z))
    for name,color in (('body',BLUE),('cap',ORANGE)):
        section(items,parts[name].val().intersect(crop),'XZ',(0,0,0),xf,color)
    label(items,700,510,'Stop contacts the sleeve tip.',17)
    label(items,700,543,'1.5 mm taper supports inverted print.',17)
    label(items,700,576,'0.75 mm bite; thicker sleeve.',17)
    label(items,700,609,'Flat cap outside; 1.2 mm pocket backing.',17)
    label(items,30,785,'Blue = body, orange = cap; both PETG. Main walls and sleeve 2.0 mm; catch-pocket backing 1.2 mm.',17)
    label(items,30,825,'Print body upright (204 mm); cap roof-down (87 mm). Use the matching smooth pair.',17)
    label(items,30,865,'CAD geometry only: actual grip, snap effort, packing and bag retention need physical testing.',16)
    items.append('</svg>');dest=ROOT/'renders/assembled/smooth_case_sections.svg'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(dest),write_to=str(dest.with_suffix('.png')))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    identity=hashes(INPUTS);parts=build('retention-c2');data=inspect(parts);draw(parts)
    assert identity==hashes(INPUTS),'Sources changed during checking'
    (OUT/'cad.json').write_text(json.dumps(dict(source_sha256=identity,**data),indent=2)+'\n')
    print(json.dumps(data))


if __name__=='__main__':main()
