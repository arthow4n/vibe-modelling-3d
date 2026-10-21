"""Scoped CAD checks for the actual cropped C2 trial; no force qualification."""
import json
from pathlib import Path
import m1_design as base
from smooth_joint_test import make_sample
from closure_research_checks import hashes

INPUTS = ('smooth_joint_test.py', 'smooth_joint_test_checks.py',
          'smooth_case_design.py', 'short_lap_design.py',
          'short_lap_refinement.py', 'closure_research_design.py', 'm1_design.py')


def main():
    identity = hashes(INPUTS)
    s = make_sample()
    p = s['production']
    d = p['dimensions']
    body, cap = s['body'], s['cap']
    assert body.intersect(cap).val().Volume() < 1e-5
    assert body.val().distance(cap.val()) < 1e-6
    stop = body.intersect(cap.translate((0, 0, -.1))).val().Volume()
    assert stop > .05, 'Crop must preserve the seating stop'
    catches = []
    for sign in (-1, 1):
        tooth = p['bump'].intersect(base.box(sign*d.width/2, 0, d.latch_z,
                                           d.width, 20, 8))
        for shift in (-d.clearance, 0., d.clearance):
            v = tooth.intersect(cap.translate((shift, 0, 1))).val().Volume()
            assert v > .05, 'Crop must preserve each independent catch'
            catches.append(dict(end=sign, shift_mm=shift, obstruction_mm3=v))
    plain = p['plain_body'].intersect(body)
    path = []
    for lift in (0., .25, .5, 1., 2., 3., 4., 6., 12., 27., 30., 31.):
        moved = cap.translate((0, 0, lift))
        guide = plain.intersect(moved).val().Volume()
        snap = body.intersect(moved).val().Volume()
        assert guide < 1e-5
        if lift >= 6:
            assert snap < 1e-5
        path.append(dict(lift_mm=lift, guide_mm3=guide, snap_mm3=snap))
    assert identity == hashes(INPUTS), 'Inputs changed during checking'
    record = dict(source_sha256=identity, seated_clear=True,
                  overclose_obstruction_mm3=stop, catches=catches, path=path,
                  print_heights_mm=dict(body=d.seam+d.lap-s['bottom'],
                                        cap=s['top']-p['rim_z']),
                  scope='Rigid cropped-joint CAD. PLA effort/recovery and full-case force remain physical unknowns.')
    out = Path(__file__).resolve().parent/'notes/smooth_case/pla_trial/cad.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
