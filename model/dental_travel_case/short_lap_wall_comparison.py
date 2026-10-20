"""Fit checks and actual sliced-wall evidence for the two full print trials.

Run after evaluating/slicing both wrappers. No structural solver or force claim.
Kept Orca runs are read from the native receipts, never exported by this script.
"""
import json
import re
from pathlib import Path
import cadquery as cq
import cairosvg
import m1_design as base
import short_lap_reinforced as control
from short_lap_thin import build_three_line
from closure_research_checks import hashes
from closure_research_drawings import canvas, label, section, BLUE, ORANGE
from physical_analysis.manufacturing import orca_linear_paths, section_coverage

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/wall_comparison'
GEOMETRY_INPUTS = ('m1_design.py','closure_research_design.py','short_lap_design.py',
    'short_lap_refinement.py','short_lap_reinforced.py','short_lap_thin.py',
    'short_lap_case.py','short_lap_case_three_line.py')
INPUTS = GEOMETRY_INPUTS+('short_lap_wall_comparison.py','closure_research_drawings.py',
    '../../physical_analysis/manufacturing.py','../../uv.lock')
STEMS = {'control':'short_lap_case','thin':'short_lap_case_three_line'}


def inspect_fit(p):
    d = p['dimensions']
    eps = 1e-5
    assert p['body'].intersect(p['cap']).val().Volume() < eps
    catches = []
    for sign in (-1,1):
        tooth = p['bump'].intersect(base.box(sign*d.width/2,0,d.latch_z,d.width,20,8))
        for shift in (-d.clearance,0.,d.clearance):
            overlap = tooth.intersect(p['cap'].translate((shift,0,1))).val().Volume()
            assert overlap > .05, (sign,shift,overlap)
            catches.append(dict(end=sign,shift_mm=shift,obstruction_mm3=overlap))
    path = []
    for lift in (0,.2,.5,1,2,3,4,6,12,30,31,90):
        posed = p['cap'].translate((0,0,lift))
        guide = p['plain_body'].intersect(posed).val().Volume()
        snap = p['body'].intersect(posed).val().Volume()
        assert guide < eps
        if lift >= 6:
            assert snap < eps
        path.append(dict(lift_mm=lift,guide_mm3=guide,snap_mm3=snap))
    assert p['plain_body'].intersect(p['cap'].translate((0,0,-.1))).val().Volume() > .05
    gaps = {}
    for name,gauge in (('brush',cq.Workplane('XY',origin=(0,-5,4.5)).circle(15).extrude(400)),
                       ('tube',base.box(0,0,200,55,40,394))):
        assert gauge.intersect(p['body']).val().Volume() < eps
        gap = gauge.val().distance(p['body'].val())
        assert gap >= .8-1e-6
        gaps[name] = gap
    from m1_checks import end_rounds
    end_rounds(p)
    grip = base.box(0,25,d.seam+1.5,10,1,2.8)
    assert all(grip.intersect(p[name]).val().Volume() < eps for name in ('body','cap'))
    return dict(catches=catches,path=path,individual_passage_gaps_mm=gaps,
                hard_seat=True,grips_clear=True,end_rounds=True)


def sliced_sections(name):
    receipt = json.loads((OUT/(name+'_slice.json')).read_text())
    stem = STEMS[name]
    assert receipt['slice']['input_sha256'] == hashes((stem+'.stl',))[stem+'.stl']
    gcode = Path(receipt['slice']['kept_run_directory'])/'plate_1.gcode'
    paths = list(orca_linear_paths(gcode))
    # Known evaluator print placements and Orca's reported center placement.
    cx = 79. if name == 'control' else 78.675
    thin = name == 'thin'
    cases = [('body',40,cx+(35.9 if thin else 35.1),cx+37.1,135),
        ('cap',20,cx+112+(35.9 if thin else 35.1),cx+149.1,135),
        ('sleeve',190,cx+(34.6 if thin else 32.3),cx+(35.8 if thin else 34.3),135),
        ('runout_backing',70,cx+112+(36.55 if thin else 35.05),cx+112+(37.75 if thin else 37.1),135),
        ('pocket_backing',63,cx+112+(36.55 if thin else 35.05),cx+112+(37.75 if thin else 37.1),135)]
    rows = {}
    for title,z,lo,hi,y_cut in cases:
        hits = set()
        for x,y,nx,ny,zz,w,role in paths:
            if abs(zz-z)>1e-5 or abs(ny-y)<1e-9 or role.startswith(('Support','Brim')):
                continue
            if min(y,ny)<=y_cut<=max(y,ny):
                at = x+(nx-x)*(y_cut-y)/(ny-y)
                if lo<=at<=hi:
                    hits.add((round(at-lo,4),w,role))
        swapped = ((y,x,ny,nx,zz,w,r) for x,y,nx,ny,zz,w,r in paths)
        coverage = section_coverage(swapped,x_mm=y_cut,z_mm=z,span_mm=(lo,hi))
        assert len(hits) == (3 if thin else 5), (name,title,hits)
        assert coverage['uncovered_width_mm'] < .05 and coverage['internal_gap_mm'] < .01
        rows[title] = dict(print_z_mm=z,span_mm=[lo,hi],y_mm=y_cut,
            thickness_mm=hi-lo,strokes=[dict(offset_mm=a,width_mm=w,role=r) for a,w,r in sorted(hits)],
            coverage=coverage)
    text = gcode.read_text()
    grams = float(re.search(r'^; total filament used \[g\] = ([\d.]+)',text,re.M)[1])
    duration = re.search(r'^; estimated printing time \(normal mode\) = (.+)',text,re.M)[1]
    return dict(sections=rows,estimated_mass_g=grams,estimated_time=duration,
                slice_input_sha256=receipt['slice']['input_sha256'])


def draw(parts,records):
    items = canvas('Dental box: 2 mm control vs three-line thin pair',1000)
    label(items,25,76,'Actual CAD catch sections, common scale (height compressed). Blue = body; orange = cap.',18)
    for i,name in enumerate(('control','thin')):
        x0 = 140+575*i
        p = parts[name]
        label(items,25+575*i,118,'2 mm control' if i==0 else '1.2 mm ordinary walls',23)
        # Crop the actual shell: the pad and pocket remain visibly distinct.
        clip = base.box(35,0,192,12,4,44).val()
        xf = lambda v,x0=x0:(x0+22*(v.x-32),160+7*(211-v.z))
        for member,color in (('body',BLUE),('cap',ORANGE)):
            section(items,p[member].val().intersect(clip),'XZ',(0,0,0),xf,color)
        label(items,25+575*i,488,'30 mm overlap · 0.6 mm bite · 0.1 mm guide gap',17)
        label(items,25+575*i,520,'2.05 mm behind recess' if i==0 else '1.2 mm behind recess; local outside pad +0.65 mm',16)
    label(items,25,572,'Actual slicer strokes across a straight main wall — enlarged, common scale',21)
    colors = {'Outer wall':BLUE,'Inner wall':ORANGE,'Gap infill':'#598044'}
    for i,name in enumerate(('control','thin')):
        row = records[name]['sections']['body']
        y = 622+i*85
        label(items,25,y+8,f'{row["thickness_mm"]:.1f} mm: {len(row["strokes"])} lines',19)
        for stroke in row['strokes']:
            x = 300+200*stroke['offset_mm']
            items.append(f'<ellipse cx="{x:.2f}" cy="{y}" rx="{100*stroke["width_mm"]:.2f}" ry="20" fill="{colors[stroke["role"]]}" fill-opacity=".72"/>')
        label(items,790,y+8,f'{records[name]["estimated_mass_g"]:.2f} g / {records[name]["estimated_time"]}',18)
    label(items,25,774,'Blue = outside contour; orange = inner wall; green = center gap-fill line. No sparse infill here.',17)
    label(items,25,813,'Thin floor / roof: 1.2 mm = six 0.2 mm layers. Pads are locally thicker between recesses.',18)
    label(items,25,850,'Matching pairs only: thin cap + thin body. General size retained; pads increase width to 75.5 mm.',17)
    label(items,25,889,'Both full pairs slice without supports. Mass / time are estimates for the same PETG setup.',18)
    label(items,25,931,'Next useful evidence: print and compare flex, fit and snap return. Holding force / bag knocks untested.',17)
    items.append('</svg>')
    path = OUT/'comparison.svg'
    path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


def main():
    parts = dict(control=control.build(control.SELECTED_OVERLAP),thin=build_three_line())
    fit = inspect_fit(parts['thin'])
    print('Thin paired fit, capture and release-path checks passed',flush=True)
    records = {name:sliced_sections(name) for name in STEMS}
    draw(parts,records)
    artifacts = {}
    for name,stem in STEMS.items():
        artifacts[name] = hashes((stem+'.step',stem+'.stl','notes/wall_comparison/'+name+'_slice.json'))
    data = dict(scope='Rigid CAD fit and local linear toolpaths; not force, impact or physical validation',
        source_sha256=hashes(INPUTS),artifacts=artifacts,thin_fit=fit,cases=records)
    (OUT/'checks.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({name:{k:v for k,v in row.items() if k!='sections'} for name,row in records.items()}),flush=True)


if __name__ == '__main__':
    main()
