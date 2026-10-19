"""Product-local fit, capture, path and rocking checks for the short-lap box."""
import json
from pathlib import Path
import cadquery as cq
import short_lap_design as design
import short_lap_reinforced as refinement
import m1_design as base
from closure_research_checks import hashes

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'
EPS = 1e-5
INPUTS = ('m1_design.py','m1_checks.py','closure_research_design.py','short_lap_design.py',
          'short_lap_refinement.py','short_lap_reinforced.py','short_lap_checks.py')


def preflight():
    rows = {}
    for lap in design.OVERLAPS:
        p = design.build(lap)
        d = p['dimensions']
        assert p['body'].intersect(p['cap']).val().Volume() < EPS
        for name in ('body','cap'):
            assert p[name].val().isValid()
            assert len(p[name].solids().vals()) == 1, 'Disconnected snap/shell'
        # Obstruction must come from the snap, not a binding guide.
        obstruction = p['body'].intersect(p['cap'].translate((0,0,1))).val().Volume()
        assert obstruction > .05
        for travel in (0,1,3,6,lap,lap+1):
            cap = p['cap'].translate((0,0,travel))
            assert p['plain_body'].intersect(cap).val().Volume() < EPS
            if travel >= 6:
                assert p['body'].intersect(cap).val().Volume() < EPS
        rows[str(lap)] = dict(overlap_mm=lap, capture_at_1mm_mm3=obstruction)
        print('preflight',lap,rows[str(lap)],flush=True)
    return rows


def inspect():
    p = refinement.build(refinement.SELECTED_OVERLAP)
    d = p['dimensions']
    rows = []
    # Both end bumps must obstruct independently, even with guide play.
    for sign in (-1,1):
        half = base.box(sign*d.width/2,0,d.latch_z,d.width,20,8)
        bump = p['bump'].intersect(half)
        for shift in (-d.clearance,0.,d.clearance):
            volume = bump.intersect(p['cap'].translate((shift,0,1))).val().Volume()
            assert volume > .05,(sign,shift,volume)
            rows.append(dict(catch=sign,x_shift_mm=shift,obstruction_mm3=volume))
    path = []
    for travel in (0,.2,.5,1,1.5,2,3,4,6,12,d.lap,d.lap+1,90):
        posed = p['cap'].translate((0,0,travel))
        guide = p['plain_body'].intersect(posed).val().Volume()
        snap = p['body'].intersect(posed).val().Volume()
        assert guide < EPS
        if travel >= 6:
            assert snap < EPS
        path.append(dict(travel_mm=travel,guide_intersection_mm3=guide,snap_intersection_mm3=snap))
    assert p['plain_body'].intersect(p['cap'].translate((0,0,-.1))).val().Volume() > .05
    # Individual extraction gauges; the unknown tube taper is not invented to
    # claim simultaneous packing. Preserve accepted M1 real-item packing evidence
    # as historical; this altered mouth requires a new physical loading check.
    brush = cq.Workplane('XY',origin=(0,-5,4.5)).circle(15).extrude(400)
    tube = base.box(0,0,200,55,40,394)
    gaps = {}
    for name,gauge in (('brush_extraction',brush),('tube_individual_passage',tube)):
        assert gauge.intersect(p['body']).val().Volume() < EPS
        gap = gauge.val().distance(p['body'].val())
        assert gap >= .8-1e-6,(name,gap)
        gaps[name] = gap
    from m1_checks import end_rounds
    end_rounds(p)
    brush_reference = base.references(base.D)['brush']
    for name in ('body','cap'):
        assert brush_reference.val().distance(p[name].val()) >= .8-1e-6
    # Normal opening exposes the entire mouth. No clip, guard or hinge occupies it.
    gauge = base.prism(d.sleeve_width-2*d.sleeve_wall,d.sleeve_depth-2*d.sleeve_wall,
                       d.sleeve_corner-d.sleeve_wall,d.seam,d.lap)
    assert gauge.intersect(p['body']).val().Volume() < EPS
    # Grips remain open with the cap seated; corner seats remain intact.
    grip = base.box(0,25,d.seam+1.5,10,1,2.8)
    for name in ('body','cap'):
        assert grip.intersect(p[name]).val().Volume() < EPS
    specimen = design.sample(p)
    assert specimen['cap'] is p['cap']
    assert specimen['body'].val().isValid()
    assert len(specimen['body'].solids().vals()) == 1
    assert d.width == 74.2 and d.depth == 51.2 and d.length == 264
    data = dict(scope=__doc__+' Finite rigid obstructions do not establish elastic snap passage or printed retention.',
        source_sha256=hashes(INPUTS),selected_overlap_mm=d.lap,
        dimensions_mm=dict(width=d.width,depth=d.depth,length=d.length,seam=d.seam,
                           overlap=d.lap,guide_clearance_per_side=d.clearance,
                           sleeve_wall=d.sleeve_wall,bump=d.detent),
        independent_capture=rows,path=path,individual_passage_gaps_mm=gaps,
        central_aperture_mm=[d.sleeve_width-2*d.sleeve_wall,d.sleeve_depth-2*d.sleeve_wall],
        sample=dict(complete_production_cap=True,body_crop_below_seam_mm=16,
                    body_height_mm=16+d.lap,cap_height_mm=d.length-d.seam),
        hard_seat=True,grips_clear=True,end_rounds_checked=True)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'cad.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data),flush=True)
    return data


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['preflight']:
        preflight()
    elif not sys.argv[1:]:
        inspect()
    else:
        raise SystemExit('Use no arguments or preflight')
