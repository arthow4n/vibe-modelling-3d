"""Actual geometry and useful negative controls for four research specimens."""
import hashlib
import json
from pathlib import Path
import cadquery as cq
import m1_design as base
import closure_research_design as design
from m5_space_study import area,capacity

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_research'
INPUTS=('m1_design.py','closure_research_design.py','closure_research_checks.py','m5_space_study.py')


def hashes(files):return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files}


def in_longitudinal_frame(parts):
    return dict(dimensions=design.D,
        **{name:parts[name].rotate((0,0,0),(1,0,0),90).translate((0,25.6,0)) for name in ('body','cap')})


def inspect():
    OUT.mkdir(parents=True,exist_ok=True)
    records={};space_parts={}
    for kind in ('slide_wall','shell_broad','shell_end','perimeter_bead'):
        full=design.build(kind)
        sample=design.sample(kind)
        d=design.D
        seated=full['body'].intersect(full['cap']).val().Volume()
        if seated>1e-5:
            for solid in full['body'].intersect(full['cap']).solids().vals():
                b=solid.BoundingBox()
                print('SEATED BLOCK',kind,solid.Volume(),[b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax],flush=True)
        assert seated<1e-5,(kind,'seated interference',seated)
        for name in ('body','cap'):
            # Specific connectivity risks: lofted bead, suspended rail, tooth root.
            assert len(sample[name].solids().vals())==1,(kind,'disconnected '+name)
            assert sample[name].val().isValid()
        poses=[]
        if kind!='slide_wall':
            gauge=base.prism(d.sleeve_width-3.2,d.sleeve_depth-3.2,d.sleeve_corner-1.6,
                             d.floor+2,d.seam+d.lap-d.floor-3)
            assert full['body'].intersect(gauge).val().Volume()<1e-5
            cap_difference=full['cap'].val().cut(sample['cap'].val()).Volume()+sample['cap'].val().cut(full['cap'].val()).Volume()
            assert cap_difference<1e-5
            for lift in (0,.25,.5,1,1.5,2,3,4,6,12,30,60,78,90):
                posed=full['cap'].translate((0,0,lift))
                bite=full['body'].intersect(posed).val().Volume()
                no_hook=full['plain_body'].intersect(posed).val().Volume()
                assert no_hook<1e-5,(kind,lift,'guide interference')
                if lift>=6:assert bite<1e-5,(kind,lift,'runout still rubs')
                poses.append(dict(lift_mm=lift,retaining_overlap_mm3=bite,without_detent_mm3=no_hook))
            assert max(p['retaining_overlap_mm3'] for p in poses)>.05
            raw=design.tip_shell(kind,d,runout=False)
            raw_drag=raw['body'].intersect(raw['cap'].translate((0,0,30))).val().Volume()
            assert raw_drag>.05,'Negative control lost the long rubbing path'
            # Full 78mm guide, same root boundary and complete cap are retained.
            crop=base.box(0,0,(158+252)/2,82,56,94)
            assert full['body'].intersect(crop).val().cut(sample['body'].val()).Volume()<1e-5
            record=dict(poses=poses,guide_mm=d.lap,body_crop_start_mm=158,
                sample_body_height_mm=94,sample_cap_height_mm=90,complete_cap_preserved=True,
                central_width_mm=d.sleeve_width-3.2,central_depth_mm=d.sleeve_depth-3.2,
                area_at_joint_mm2=area(full,180),no_runout_overlap_at_30mm_mm3=raw_drag)
            if kind=='shell_broad':space_parts[kind]=full
        else:
            for length in (70.,264.):
                parts=sample if length==70 else full
                for travel in (0,.25,.5,1,1.5,2,3,4,6,15,40,length+3):
                    lid=parts['cap'].translate((0,-travel,0))
                    bite=parts['body'].intersect(lid).val().Volume()
                    plain=parts['body'].intersect(parts['plain_cap'].translate((0,-travel,0))).val().Volume()
                    assert plain<1e-5,('rail binding',length,travel,plain)
                    if travel>=6:assert bite<1e-5,('slide detent dragging',length,travel,bite)
                    poses.append(dict(reference_length_mm=length,travel_mm=travel,retaining_overlap_mm3=bite,without_detent_mm3=plain))
            assert max(p['retaining_overlap_mm3'] for p in poses)>.005
            gauge=base.prism(70.4,259.6,1.2,2.1,41.8).translate((0,132,0))
            assert full['body'].intersect(gauge).val().Volume()<1e-5
            lifting=sample['body'].intersect(sample['plain_cap'].translate((0,0,.6))).val().Volume()
            assert lifting>.1,'Rail does not positively obstruct lifting'
            transformed=in_longitudinal_frame(full)
            record=dict(poses=poses,sample_length_mm=70,full_reference_length_mm=264,
                main_interior_width_mm=70.6,opening_length_mm=260,
                lift_obstruction_without_detent_mm3=lifting)
            space_parts[kind]=transformed
        records[kind]=record
        print(kind,'CAD complete',record.get('central_volume_ml_2mm'),flush=True)
    for kind,parts in space_parts.items():
        records[kind].update(central_volume_ml_4mm=capacity(parts,4),central_volume_ml_2mm=capacity(parts,2))
        print(kind,'capacity complete',records[kind]['central_volume_ml_2mm'],flush=True)
    output=dict(scope=__doc__+' Finite rigid path obstructions, not physical holding or spring return.',
                source_sha256=hashes(INPUTS),cases=records)
    (OUT/'cad.json').write_text(json.dumps(output,indent=2)+'\n')


if __name__=='__main__':inspect()
