"""Targeted production-interface checks and publication association for M3 sample."""
import hashlib
import json
from pathlib import Path
import sys

import m1_design as m1
import m3_design as design
from m3_samples import joint_sample
from retention_geometry import seated_land

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m3'
INPUTS=('m1_design.py','m2b_design.py','m3_design.py','m3_samples.py','m3_joint_test.py')


def hashes(files):
    return {file:hashlib.sha256((ROOT/file).read_bytes()).hexdigest() for file in files}


def inspect():
    parts=design.build()
    sample=joint_sample(parts)
    d=sample['dimensions']
    body,cap=sample['body'].val(),sample['cap'].val()
    lands={str(side):seated_land(d,cap,side) for side in (-1,1)}
    assert all(abs(sum(f['area_mm2'] for f in rows)-13.5)<1e-6 for rows in lands.values())
    assert body.intersect(cap).Volume()<1e-5,'Seated sample parts collide'
    assert sample['body_bottom_mm']<d.beam_root-10,'Root support ramp was truncated'
    assert sample['cap_top_mm']>d.seam+d.lap+6,'Cap crop truncates guide or band transition'
    # These exact production subregions must survive cropping. This check protects
    # against future over-shortened samples that still have valid solids.
    region=m1.box(0,0,(d.beam_root-10+d.seam+d.lap)/2,d.width+4,
                  d.depth+4,d.seam+d.lap-(d.beam_root-10)).val()
    assert parts['body'].val().intersect(region).cut(body).Volume()<1e-5
    region=m1.box(0,0,d.seam+(d.lap+6)/2,d.width+4,d.depth+4,d.lap+6).val()
    assert parts['cap'].val().intersect(region).cut(cap).Volume()<1e-5
    poses=[]
    for lift in (0,.25,1,4,12,30,42,50):
        moved=cap.translate((0,0,lift))
        fixed=parts['fixed'].val().intersect(body)
        assert fixed.intersect(moved).Volume()<1e-5
        for side in (-1,1):
            released=m1.mirrored(design.tongue(d,d.release),side).val()
            overlap=released.intersect(moved).Volume()
            assert overlap<1e-5,'Released tooth collides during withdrawal'
            poses.append(dict(lift_mm=lift,catch=side,overlap_mm3=overlap))
    # Actual teeth obstruct a short pull, while released teeth above do not.
    engaged=body.intersect(cap.translate((0,0,1))).Volume()
    assert engaged>1e-5
    answer=dict(status='PASS',scope='Exact production joint crop and finite release poses; not full-size retention or printed performance.',
        source_sha256=hashes(INPUTS),producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        body_height_mm=d.seam+d.lap-sample['body_bottom_mm'],
        cap_height_mm=sample['cap_top_mm']-d.seam,
        assembled_length_mm=sample['cap_top_mm']-sample['body_bottom_mm'],
        overlap_mm=d.lap,lands=lands,released_poses=poses,
        engaged_pull_obstruction_mm3=engaged,
        unchanged_root_support_and_cap_band=True)
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'joint_sample_cad.json').write_text(json.dumps(answer,indent=2)+'\n')
    return answer


def associate():
    record=json.loads((OUT/'joint_sample_cad.json').read_text())
    assert record['source_sha256']==hashes(INPUTS),'Sources changed since pre-publication checks'
    assert record['producer_sha256']==hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report=json.loads((OUT/'joint_sample_export_slice.json').read_text())
    assert report['ok'] and report['geometry']['valid'] and report['slice']['ok']
    outputs=('m3_joint_test.step','m3_joint_test.stl','notes/m3/joint_sample_export_slice.json')
    assert report['slice']['input_sha256']==hashes(('m3_joint_test.stl',))['m3_joint_test.stl']
    answer=dict(scope='Sources unchanged since preflight; paired publication and slice association, not physical acceptance.',
                inputs=hashes(INPUTS),outputs=hashes(outputs))
    (OUT/'joint_sample_association.json').write_text(json.dumps(answer,indent=2)+'\n')
    return answer


if __name__=='__main__':
    if not sys.argv[1:]:answer=inspect()
    elif sys.argv[1:]==['--associate']:answer=associate()
    else:raise SystemExit('Usage: m3_joint_checks.py [--associate]')
    print(json.dumps(answer))
