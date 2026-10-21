"""B1 coupon checks: retention, release path, rail capture and intentional detent.

Rigid motion is checked with the light spring detents removed from the cap;
their actual geometric interference is recorded separately, not a force result.
"""
from pathlib import Path
import hashlib
import json
import cadquery as cq
from assembly_geometry import Configuration, PairRequirement, check_pair
from slider_b_design import build, configuration
import m1_design as base

ROOT = Path(__file__).resolve().parent
INPUTS = ('slider_b_design.py','slider_b_checks.py','slider_b_test.py',
          'slider_b_test_assembled.py','slider_b_test_open.py','m1_design.py')


def hashes():
    return {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in INPUTS}


def clear(first, second, intent):
    r = check_pair(first, second, PairRequirement(intent,max_overlap_mm3=1e-5))
    r.require_passed()
    return r.to_dict()


def main():
    identity = hashes()
    p = build()
    d = p['dimensions']
    # Connectivity matters here: the U must survive the exit windows, tunnels and slots.
    for name in ('body','cap','yoke'):
        assert len(p[name].val().Solids()) == 1, name+' has a detached feature'
    configs = {}
    for state in ('locked','unlocked','open','print'):
        c = Configuration.explicit(configuration(p,state),name=state,
                                   kind='print' if state=='print' else 'operating')
        configs[state] = [c.check(a,b,PairRequirement('Distinct seated/print components',max_overlap_mm3=1e-5)).to_dict()
                          for a,b in (('body','cap'),('body','yoke'),('cap','yoke'))]
        assert all(r['status']=='passed' for r in configs[state]), configs[state]
    assert p['body'].val().distance(p['cap'].val()) < 1e-6
    stop = p['body'].intersect(p['cap'].translate((0,0,-.1))).val().Volume()
    assert stop > .05, 'Separate sleeve-tip seat must prevent overclosing'
    shifts = [(0.,0.),(.3,0.),(-.3,0.),(0.,.3),(0.,-.3),(.2,.2),(-.2,.2),(.2,-.2),(-.2,-.2)]
    captures = []
    for sx,sy in shifts:
        clear(p['body'],p['cap'].translate((sx,sy,0)),'Guide play must remain possible')
        for side in (-1,1):
            lug = p['lug'].intersect(base.box(0,side*29.,29.,12.,12.,10.))
            shifted = p['yoke'].translate((-d.travel+sx,sy,.7))
            v = lug.intersect(shifted).val().Volume()
            assert v > 1., (side,sx,sy,'missing independent locked ledge')
            captures.append(dict(side=side,guide_shift_mm=[sx,sy],obstruction_mm3=v))
    slider = []
    for shift in (-10.,-9.,-8.,-7.,-6.,-5.,-4.,-3.,-2.,-1.,0.):
        yoke = p['yoke'].translate((shift,0,0))
        clear(p['body'],yoke,'Slide yoke before lifting')
        clear(p['cap_guide'],yoke,'Cap rail/peg path excluding declared elastic detents')
        v = p['cap'].intersect(yoke).val().Volume()
        slider.append(dict(shift_mm=shift,detent_interference_mm3=v))
    assert slider[0]['detent_interference_mm3'] < 1e-5
    assert slider[-1]['detent_interference_mm3'] < 1e-5
    assert max(r['detent_interference_mm3'] for r in slider) > .001
    withdrawal = []
    # Include end-stop slack and lateral guide play; not only a favorable central path.
    for shift in (-.3,0.,.3):
        for sx,sy in shifts:
            for lift in (0.,.3,.7,1.,2.,4.,8.,16.,20.,23.,28.):
                clear(p['body'],p['cap'].translate((sx,sy,lift)),'Unlocked cap withdrawal')
                clear(p['body'],p['yoke'].translate((shift+sx,sy,lift)),'Unlocked lug exit through yoke')
        withdrawal.append(dict(slider_end_play_mm=shift,guide_positions=len(shifts),sampled_lifts_mm=[0,.3,.7,1,2,4,8,16,20,23,28]))
    # Slot end walls and the dovetail, not friction, keep the yoke on the cap.
    capture = []
    for shift in (-11.,1.):
        v = p['cap_guide'].intersect(p['yoke'].translate((shift,0,0))).val().Volume()
        assert v > .1, 'Slider overtravel must meet peg/end stop'
        capture.append(dict(x_shift_mm=shift,obstruction_mm3=v))
    for dz in (-.8,.8):
        v = p['cap_guide'].intersect(p['yoke'].translate((-5.,0,dz))).val().Volume()
        assert v > .1, 'Dovetail must resist lifting/pushing yoke off cap'
        capture.append(dict(z_shift_mm=dz,obstruction_mm3=v))
    assert identity == hashes()
    data = dict(source_sha256=identity,configurations=configs,
                stop_obstruction_mm3=stop,independent_capture=captures,
                slider_path=slider,withdrawal=withdrawal,yoke_capture=capture,
                scope='B1 rigid geometry and explicit small detent interference. No PLA force, snap-on assembly, durability or bag-impact validation.')
    dest = ROOT/'notes/slider_b/cad.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data))


if __name__=='__main__':
    main()
