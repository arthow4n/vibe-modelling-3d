"""Rigid rocking contact sequence; no elastic or impact qualification.

The guide-only limit is deliberately not called free assembled motion. Locate
earlier tooth contact on the same path, including adverse initial side play.
"""
import json
from pathlib import Path

from closure_research_checks import hashes
import m1_design as base
from overlap_exploration import onset, peel
import short_lap_reinforced as design

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/short_lap'
EPS = 1e-5


def first_pickup(tooth, cap, d, *, axis, shift, limit):
    initial = peel(cap,d,0.,axis=axis,transverse=shift)
    if tooth.intersect(initial).Volume() > EPS:
        return [0.,0.]
    previous = 0.
    count = max(1, int(limit/.025)+1)
    for i in range(1,count+1):
        angle = limit*i/count
        posed = peel(cap,d,angle,axis=axis,transverse=shift)
        if tooth.intersect(posed).Volume() > EPS:
            lo, hi = previous, angle
            while hi-lo > .0005:
                mid = (lo+hi)/2
                if tooth.intersect(peel(cap,d,mid,axis=axis,transverse=shift)).Volume() > EPS:
                    hi = mid
                else:
                    lo = mid
            return [lo,hi]
        previous = angle
    return None


def run():
    parts = design.build(design.SELECTED_OVERLAP)
    d = parts['dimensions']
    cap = parts['cap'].val()
    teeth = {str(sign):parts['bump'].intersect(base.box(
        sign*d.width/2,0,d.latch_z,d.width,20,8)).val() for sign in (-1,1)}
    rows = []
    for axis in ('x','y'):
        for shift in (-d.clearance,0.,d.clearance):
            guide = onset(parts['plain_body'].val(),cap,d,axis=axis,transverse=shift)
            limit = guide['bracket_deg'][1]
            pickup = {label:first_pickup(tooth,cap,d,axis=axis,shift=shift,limit=limit)
                      for label,tooth in teeth.items()}
            row = dict(rotation_axis=axis,initial_side_shift_mm=shift,
                       guide_contact=guide,catch_contact_brackets_deg=pickup,
                       initial_tooth_overlap_mm3={label:tooth.intersect(peel(
                           cap,d,0.,axis=axis,transverse=shift)).Volume()
                           for label,tooth in teeth.items()})
            rows.append(row)
            print(json.dumps(row),flush=True)
    result = dict(scope=__doc__,intersection_tolerance_mm3=EPS,
        scan_step_at_most_deg=.025,bracket_width_at_most_deg=.0005,
        source_sha256=hashes(('short_lap_rocking.py','short_lap_reinforced.py',
            'short_lap_refinement.py','short_lap_design.py','closure_research_design.py',
            'overlap_exploration.py','m1_design.py')),cases=rows)
    (OUT/'rocking.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    run()
