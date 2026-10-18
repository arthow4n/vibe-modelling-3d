"""Check shortened trials preserve interfaces, gripping access and release paths."""
import json
from pathlib import Path
import cadquery as cq
import closure_short_design as design
import closure_research_design as research
import m1_design as base
from closure_research_checks import hashes

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'notes/closure_short'
INPUTS = ('m1_design.py','closure_research_design.py','closure_short_design.py','closure_short_checks.py')


def inspect():
    rows = {}
    for kind in design.KINDS:
        short = design.build(kind)
        old = research.sample(kind)
        body, cap = short['body'], short['cap']
        for part in (body, cap):
            assert part.val().isValid() and len(part.solids().vals()) == 1
        assert body.intersect(cap).val().Volume() < 1e-5
        old_volume = sum(old[n].val().Volume() for n in ('body','cap'))
        new_volume = sum(short[n].val().Volume() for n in ('body','cap'))
        assert new_volume < old_volume
        differences = {}
        if kind == 'slide_wall':
            # Actual rail/detent region unchanged; full XY perimeter retained.
            band = base.box(0,35,47.6,82,74,3.2)
            for name in ('body','cap'):
                # Exclude only the declared central end-wall grip cut.
                a = short[name].intersect(band)
                b = old[name].cut(design.grip_cut(kind)).intersect(band)
                differences[name] = a.cut(b).val().Volume()+b.cut(a).val().Volume()
            travel = (0,.5,1,2,3,4,6,15,73)
            poses = [dict(travel_mm=s, blocked_mm3=body.intersect(cap.translate((0,-s,0))).val().Volume(),
                no_detent_mm3=body.intersect(short['no_detent'].translate((0,-s,0))).val().Volume()) for s in travel]
            lift = body.intersect(short['no_detent'].translate((0,0,.6))).val().Volume()
            assert lift > .05
            gap = base.box(0,0,47.7,10,2,2.8)
            assert body.intersect(gap).val().Volume() < 1e-5
            assert cap.intersect(gap).val().Volume() < 1e-5
            sizes = dict(body_height_mm=12.2,cap_height_mm=5.2,assembled_height_mm=14.2,XY_mm=[77,70])
        else:
            d = design.D
            shift = d.latch_z-research.D.latch_z
            band = base.box(0,0,d.latch_z,82,56,6)
            full = research.build(kind)
            for name in ('body','cap'):
                a = short[name].intersect(band)
                b = full[name].translate((0,0,shift)).intersect(band)
                differences[name] = a.cut(b).val().Volume()+b.cut(a).val().Volume()
            travel = (0,.25,.5,1,1.5,2,3,4,6,12,24,30,40)
            poses = [dict(travel_mm=s,blocked_mm3=body.intersect(cap.translate((0,0,s))).val().Volume(),
                no_detent_mm3=short['no_detent'].intersect(cap.translate((0,0,s))).val().Volume()) for s in travel]
            # Grip removal must not remove the seating stops: cap cannot sink.
            assert short['no_detent'].intersect(cap.translate((0,0,-.1))).val().Volume() > .05
            gap = (base.box(0,25,d.seam+1.5,10,1,2.8) if kind=='shell_end'
                   else base.box(38,0,d.seam+1.5,1,10,2.8))
            assert body.intersect(gap).val().Volume() < 1e-5
            assert cap.intersect(gap).val().Volume() < 1e-5
            sizes = dict(body_height_mm=30,cap_height_mm=36,assembled_height_mm=42,base_below_seam_mm=6,
                         overlap_mm=24,grip_gap_mm=3,XY_mm=[77,51.2])
        assert all(v < 1e-5 for v in differences.values()), (kind,differences)
        assert all(p['no_detent_mm3'] < 1e-5 for p in poses)
        assert max(p['blocked_mm3'] for p in poses) > .05
        assert all(p['blocked_mm3'] < 1e-5 for p in poses if p['travel_mm']>=6)
        rows[kind] = dict(**sizes,interface_difference_mm3=differences,poses=poses,
            old_CAD_solid_volume_mm3=old_volume,short_CAD_solid_volume_mm3=new_volume,
            CAD_solid_material_reduction_fraction=1-new_volume/old_volume,
            grip_clear=True,forces_inherited=False)
    data = dict(scope='Short specimen CAD only; local interface equivalence, grip gap and sampled motion. No force equivalence.',
                source_sha256=hashes(INPUTS),cases=rows)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'cad.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data),flush=True)
    return data


if __name__=='__main__': inspect()
