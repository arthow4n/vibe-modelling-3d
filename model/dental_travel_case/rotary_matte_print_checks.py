"""Inspect final cap/key/thread deposition under the recorded diagnostic setup."""
from collections import defaultdict
from pathlib import Path
import json
import hashlib
from physical_analysis.manufacturing import orca_linear_paths,section_coverage

ROOT=Path(__file__).resolve().parent


def main():
    directory=ROOT/'notes/matte_rotary'
    r=json.loads((directory/'native.json').read_text())
    assert r['ok'] and r['slice']['ok']
    run=Path(r['slice']['kept_run_directory']);gcode=run/'plate_1.gcode'
    paths=list(orca_linear_paths(gcode));layers=defaultdict(list)
    for q in paths:
        layers[round(q[4],5)].append(q)
    result=[]
    def covered(label,x,z,span):
        c=section_coverage(layers[round(z,5)],x_mm=x,z_mm=z,span_mm=span)
        assert c['uncovered_width_mm']<.1,(label,x,z,c)
        result.append(dict(feature=label,x_mm=x,z_mm=z,span_mm=span,coverage=c))
    for z in (7.,8.,10.,12.):
        covered('solid screw core',100,z,(57.8,62.2))
    for x in (53.,67.):
        for z in (2.6,3.2,4.):
            covered('drive key',x,z,(58.7,61.3))
    for z in (.4,1.,1.8):
        covered('cap face',60,z,(68.8,75.))
    # Circular top rim nominal r=17.6..19.6, safely away from scallops.
    for z in (2.6,4.,6.):
        covered('2mm rim',60,z,(77.7,79.5))
    probe=r['slice']['support_probe']
    support=[]
    if probe['generated']:
        support=[q for q in orca_linear_paths(run/'support_probe/plate_1.gcode')
                 if q[-1].startswith('Support')]
    out=dict(review_complete=not support,sections=result,
        uncovered_width_limit_mm=.1,support_segments=len(support),
        support_probe_generated=probe['generated'],
        gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
        input_sha256=r['slice']['input_sha256'],
        scope='Nominal local path coverage only; diagnostic PETG, not matte-PLA bonding or fit calibration')
    (directory/'paths.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(sections=len(result),support_segments=len(support))))


if __name__=='__main__':
    main()
