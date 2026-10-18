"""Current M4 full case and matching sample checks; no holding-force promotion."""
from dataclasses import asdict,replace
import hashlib
import json
from pathlib import Path
import sys

import m1_design as m1
import m3_design as m3
import m4_design as design
from m1_checks import fit,tube_aperture,end_rounds
from m3_samples import joint_sample
from retention_geometry import seated_land
from retention_m2b_checks import layer_connectivity

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m4'
INPUTS=('m1_design.py','m2b_design.py','m3_design.py','m4_design.py','m3_samples.py','m4_case.py','m4_joint_test.py')


def hashes(files):return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}


def inspect():
    parts=design.build()
    d=parts['dimensions']
    assert asdict(d)==asdict(replace(m3.D,lap=78.,lap_clearance=.15,axial_play=.40))
    fit(parts);tube_aperture(parts);end_rounds(parts)
    # A changed overlap must not silently retune the already studied catch.
    new=design.tongue(d).val()
    old=m3.tongue(m3.D).val().translate((-(m3.D.lap_clearance-d.lap_clearance),0,0))
    catch_difference=new.cut(old).Volume()+old.cut(new).Volume()
    assert catch_difference<1e-6
    cap=parts['cap'].val()
    sample=joint_sample(parts)
    bottom,top=sample['body_bottom_mm'],sample['cap_top_mm']
    assert bottom<d.beam_root-10 and top>d.seam+d.lap+6
    assert d.seam+d.lap<=256
    records=[]
    def clear(label,a,b,**pose):
        overlap=a.intersect(b).Volume()
        records.append(dict(label=label,overlap_mm3=overlap,clear=overlap<1e-5,**pose))
    clear('complete seated',parts['body'].val(),cap)
    c=d.lap_clearance
    offsets=((0,0),(c,0),(-c,0),(0,c),(0,-c))
    for release in (0,1.35,d.release):
        for sign in (-1,1):
            leaf=m1.mirrored(design.tongue(d,release),sign).val()
            for dx,dy in offsets:
                for dz in (-.15,0,.15):
                    clear('catch press/return',leaf,cap.translate((dx,dy,dz)),
                          catch=sign,release_mm=release,dx=dx,dy=dy,dz=dz)
    released={s:m1.mirrored(design.tongue(d,d.release),s).val() for s in (-1,1)}
    for lift in (0,.25,1,4,12,30,60,d.lap,d.lap+12,106):
        for dx,dy in offsets:
            moved=cap.translate((dx,dy,lift))
            clear('full guide withdrawal',parts['fixed'].val(),moved,lift_mm=lift,dx=dx,dy=dy)
            for sign in (-1,1):clear('released catch withdrawal',released[sign],moved,catch=sign,lift_mm=lift,dx=dx,dy=dy)
    full_lands={str(s):seated_land(d,cap,s) for s in (-1,1)}
    sample_lands={str(s):seated_land(d,sample['cap'].val(),s) for s in (-1,1)}
    assert sample_lands==full_lands
    expected_area=d.hook_width*(d.hook_projection-.25-d.lap_clearance)
    for rows in full_lands.values():assert abs(sum(x['area_mm2'] for x in rows)-expected_area)<1e-6
    for lift in (10,30,60,d.lap,d.lap+12,106):
        for sign in (-1,1):
            clear('controls may return after mouth clears teeth',m1.mirrored(design.tongue(d),sign).val(),
                  cap.translate((0,0,lift)),catch=sign,lift_mm=lift)
    for lift in (0,.25,1,12,30,d.lap,d.lap+12,106):
        moved=sample['cap'].val().translate((0,0,lift))
        fixed=parts['fixed'].val().intersect(sample['body'].val())
        clear('sample guide withdrawal',fixed,moved,lift_mm=lift)
        for sign in (-1,1):clear('sample released withdrawal',released[sign],moved,catch=sign,lift_mm=lift)
    # Preserve the actual joint region, not merely nominal tooth dimensions.
    for name,lo,hi in (('body',d.beam_root-10,d.seam+d.lap),('cap',d.seam,d.seam+d.lap+6)):
        region=m1.box(0,0,(lo+hi)/2,d.width+4,d.depth+4,hi-lo).val()
        assert parts[name].val().intersect(region).cut(sample[name].val()).Volume()<1e-5
    layers=layer_connectivity(d,design.tongue(d).val(),cap)
    assert layers['status']=='PASS'
    blocked_offsets=[]
    for dx,dy in ((c+.05,0),(-c-.05,0),(0,c+.05),(0,-c-.05)):
        overlap=parts['fixed'].val().intersect(cap.translate((dx,dy,0))).Volume()
        assert overlap>1e-5,'Guide does not block translation outside its declared clearance'
        blocked_offsets.append(dict(dx_mm=dx,dy_mm=dy,guide_overlap_mm3=overlap))
    failures=[r for r in records if not r['clear']]
    assert not failures,failures
    answer=dict(status='PASS',scope='Actual full case and matching crop; finite clearance and preservation checks, not physical holding.',
        source_sha256=hashes(INPUTS),producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        pose_count=len(records),poses=records,lands=full_lands,first_feature_layers=layers,
        unchanged_m3_catch_symmetric_difference_mm3=catch_difference,
        admissible_transverse_offsets_mm=c,blocked_transverse_offset_controls=blocked_offsets,
        sample=dict(body_height_mm=d.seam+d.lap-bottom,cap_height_mm=top-d.seam,assembled_length_mm=top-bottom,
                    guide_overlap_mm=d.lap,root_support_and_receiver_preserved=True,
                    entire_production_cap_preserved=sample['cap'].val().cut(cap).Volume()+cap.cut(sample['cap'].val()).Volume()<1e-6),
        print_heights_mm=dict(body=d.seam+d.lap,cap=d.length-d.seam),contents_scope='Existing individual brush and tube proxies; no invented combined packing.')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'cad.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(dict(status=answer['status'],pose_count=len(records),sample=answer['sample']))


if __name__=='__main__':inspect()
