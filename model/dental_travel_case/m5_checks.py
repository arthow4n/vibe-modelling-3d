"""M5 space revision: current production/sample geometry and preserved mechanism."""
import hashlib
import json
from pathlib import Path
import cadquery as cq
import m1_design as m1
import m4_design as m4
import m5_design as design
from m1_checks import fit,tube_aperture,end_rounds
from m3_samples import joint_sample
from retention_geometry import seated_land
from retention_m2b_checks import layer_connectivity

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m5'
INPUTS=('m1_design.py','m2b_design.py','m3_design.py','m4_design.py','m5_design.py',
        'm3_samples.py','m5_case.py','m5_joint_test.py')


def hashes(files):return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}


def inspect():
    parts=design.build()
    old=m4.build()
    d=parts['dimensions']
    fit(parts);tube_aperture(parts);end_rounds(parts)
    original_leaf=design.tongue(d)
    leaf=original_leaf.val()
    previous=m4.tongue(m4.D).val()
    difference=leaf.cut(previous).Volume()+previous.cut(leaf).Volume()
    assert difference<1e-6,'Changed leaf cannot inherit isolated release evidence'
    # The old raised reinforcing strip becomes the new flat wall: preserve its
    # entire load-bearing region, not just the nominal receiver-wall parameter.
    preserved=[]
    for sign in (-1,1):
        region=m1.box(sign*37,0,(d.seam+d.seam+d.lap)/2,5,17,d.lap).val()
        missing=old['cap'].val().intersect(region).cut(parts['cap'].val()).Volume()
        assert missing<1e-5
        preserved.append(dict(sign=sign,old_receiver_strip_missing_mm3=missing))
    sample=joint_sample(parts)
    cap=parts['cap'].val()
    records=[]
    def clear(label,a,b,**pose):
        overlap=a.intersect(b).Volume()
        records.append(dict(label=label,overlap_mm3=overlap,clear=overlap<1e-5,**pose))
    clear('complete seated',parts['body'].val(),cap)
    offsets=((0,0),(.15,0),(-.15,0),(0,.15),(0,-.15))
    for delta in (0,1.35,d.release):
        for sign in (-1,1):
            moved=m1.mirrored(design.tongue(d,delta),sign).val()
            free=moved.intersect(m1.box(0,0,(d.beam_root+2+d.beam_tip+1)/2,
                                      90,60,d.beam_tip+1-d.beam_root-2).val())
            clear('leaf/guard free span',free,parts['fixed'].val(),release_mm=delta,catch=sign)
            for dx,dy in offsets:
                clear('catch press/return',moved,cap.translate((dx,dy,0)),release_mm=delta,catch=sign,dx=dx,dy=dy)
    for lift in (0,.25,1,4,10,16,30,60,78,90,106):
        for dx,dy in offsets:
            moved=cap.translate((dx,dy,lift))
            clear('guide withdrawal',parts['fixed'].val(),moved,lift_mm=lift,dx=dx,dy=dy)
            for sign in (-1,1):
                clear('released withdrawal',m1.mirrored(design.tongue(d,d.release),sign).val(),moved,
                      lift_mm=lift,catch=sign,dx=dx,dy=dy)
                if lift>=10:
                    clear('control return after tooth clearance',m1.mirrored(original_leaf,sign).val(),moved,lift_mm=lift,catch=sign,dx=dx,dy=dy)
    lands={str(s):seated_land(d,cap,s) for s in (-1,1)}
    for rows in lands.values():assert abs(sum(r['area_mm2'] for r in rows)-14.4)<1e-5
    for s in (-1,1):
        hook=m1.at_end(design.hook(d),s).val()
        for dx,dy in offsets:
            assert hook.intersect(cap.translate((dx,dy,.9))).Volume()>.5
    clear('hooks removed negative control',parts['fixed'].val(),cap.translate((0,0,.9)))
    for name in ('body','cap'):
        # Specific risks of the stitched guard/stepped guide and new strips.
        assert len(parts[name].solids().vals())==1,'Detached structural feature in '+name
        assert parts[name].val().isValid()
        envelope=m1.prism(d.width,d.depth,d.corner,-1,d.length+2).val()
        assert parts[name].val().cut(envelope).Volume()<1e-5,'Exterior projection'
    assert sample['cap'].val().cut(cap).Volume()+cap.cut(sample['cap'].val()).Volume()<1e-6
    crop=m1.box(0,0,(sample['body_bottom_mm']+d.seam+d.lap)/2,
                90,60,d.seam+d.lap-sample['body_bottom_mm']).val()
    assert parts['body'].val().intersect(crop).cut(sample['body'].val()).Volume()<1e-5
    layers=layer_connectivity(d,leaf,cap)
    assert layers['status']=='PASS'
    assert all(r['clear'] for r in records),[r for r in records if not r['clear']]
    result=dict(status='PASS',scope=__doc__,source_sha256=hashes(INPUTS),
        producer_sha256=hashes(('m5_checks.py',))['m5_checks.py'],pose_count=len(records),poses=records,
        unchanged_m4_leaf_symmetric_difference_mm3=difference,preserved_receiver_strips=preserved,
        lands=lands,first_feature_layers=layers,
        sample=dict(body_height_mm=d.seam+d.lap-sample['body_bottom_mm'],cap_height_mm=d.length-d.seam,
                    production_body_crop_and_complete_cap=True),
        print_heights_mm=dict(body=d.seam+d.lap,cap=d.length-d.seam))
    OUT.mkdir(exist_ok=True,parents=True)
    (OUT/'cad.json').write_text(json.dumps(result,indent=2)+'\n')
    print(dict(status=result['status'],poses=len(records),receiver_strips=preserved),flush=True)


if __name__=='__main__':inspect()
