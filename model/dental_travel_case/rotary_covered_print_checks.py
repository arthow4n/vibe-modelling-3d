"""Delivered solid screw, printed drive keys and accessible full-layout supports."""
from pathlib import Path
from collections import defaultdict
import hashlib,json
import cadquery as cq
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from rotary_covered_design import screw_print_pose,KEY_X,KEY_WIDTH,KEY_HEIGHT,SKIRT_OFFSET

ROOT=Path(__file__).resolve().parent


def main():
    n=ROOT/'notes/covered_rotary'
    reports={k:json.loads((n/(v+'_review.json')).read_text()) for k,v in
             [('mechanism','mechanism'),('complete','complete_mechanism'),('screw','screw'),('full','print'),('fasteners','fasteners')]}
    paths={};gcodes={};probe_reviews={}
    for name,r in reports.items():
        assert r['ok'] and r['slice']['ok']
        g=Path(r['slice']['kept_run_directory'])/'plate_1.gcode'
        gcodes[name]=hashlib.sha256(g.read_bytes()).hexdigest()
        paths[name]=list(orca_linear_paths(g))
        if name!='full':
            assert r['slice']['effective_settings']['sparse_infill_density']=='100%'
            assert r['slice']['effective_settings']['wall_loops']=='4'
            if r['slice']['support_probe']['generated']:
                assert name in ('mechanism','complete'),name
                # The probe forces supports even for short bridges. Its only
                # plug must lie inside a 2.6x3mm key pocket, not over the spring.
                yy=(118. if name=='mechanism' else 108.25)+SKIRT_OFFSET/2
                support_paths=[q for q in orca_linear_paths(g.parent/'support_probe/plate_1.gcode')
                               if q[-1].startswith('Support')]
                assert support_paths
                for q in support_paths:
                    cx=(q[0]+q[2])/2
                    key_x=min((112.5-SKIRT_OFFSET/2-KEY_X,112.5-SKIRT_OFFSET/2+KEY_X),key=lambda v:abs(v-cx))
                    assert min(q[0],q[2])-q[5]/2>=key_x-(KEY_WIDTH+.2)/2-.01,q
                    assert max(q[0],q[2])+q[5]/2<=key_x+(KEY_WIDTH+.2)/2+.01,q
                    assert min(q[1],q[3])-q[5]/2>=yy-(KEY_HEIGHT+.2)/2-.01,q
                    assert max(q[1],q[3])+q[5]/2<=yy+(KEY_HEIGHT+.2)/2+.01,q
                    assert q[4]<=2.,q
                probe_reviews[name]=dict(segments=len(support_paths),
                   roles=sorted({q[-1] for q in support_paths}),
                   decision='Primary supports remain off. Tiny 2.6x3mm blind-pocket roof is a short doubly anchored bridge; support plug is confined to that pocket. Roof finish remains a physical check.')
            else:
                probe_reviews[name]=dict(segments=0,decision='No automatic supports generated')
    # Concrete historical hollow-thread defect: target actual exported material.
    step=cq.importers.importStep(str(ROOT/'rotary_covered_screw.step'))
    witness=screw_print_pose(cq.Workplane('XY',origin=(0,0,4.2)).circle(2.28).extrude(6.39))
    missing=witness.cut(step).val().Volume();assert missing<1e-5,missing
    old=cq.importers.importStep(str(ROOT/'rotary_refinement_axle.step'))
    old_witness=cq.Workplane('XY',origin=(0,0,5.)).circle(1.5).extrude(4.)
    old_missing=old_witness.cut(old).val().Volume();assert old_missing>28
    core=[]
    for z in (6.2,7.,9.,11.,12.4):
        c=section_coverage(paths['screw'],x_mm=135,z_mm=z,span_mm=(132.8,137.2))
        assert c['uncovered_width_mm']<.1,(z,c)
        core.append(dict(z_mm=z,coverage=c))
    keys=[]
    # The larger cover changes centering by half its 1.8mm radial growth.
    cover_x=157.5-SKIRT_OFFSET/2;wheel_x=112.5-SKIRT_OFFSET/2
    center_y=118.+SKIRT_OFFSET/2
    for x in (cover_x-KEY_X,cover_x+KEY_X):
        for z in (2.,2.8,3.2):
            c=section_coverage(paths['mechanism'],x_mm=x,z_mm=z,span_mm=(center_y-1.3,center_y+1.3))
            assert c['uncovered_width_mm']<.1,(x,z,c)
            keys.append(dict(x_mm=x,z_mm=z,coverage=c))
    # Both keys have small blind pockets: check their actual bridging roof.
    roofs=[]
    for x in (wheel_x-KEY_X,wheel_x+KEY_X):
        c=section_coverage(paths['mechanism'],x_mm=x,z_mm=2.2,span_mm=(center_y-1.4,center_y+1.4))
        assert c['uncovered_width_mm']<.1,(x,c)
        roofs.append(dict(x_mm=x,z_mm=2.2,coverage=c))
    groups=defaultdict(list)
    for q in paths['full']:
        if q[-1] not in ('Support','Support interface'):continue
        x=(q[0]+q[2])/2;y=(q[1]+q[3])/2
        region='cap' if x>160 else 'body'
        groups[region,q[-1]].append(q)
    support={}
    for (region,role),rows in groups.items():
        low=min(min(q[1],q[3])-q[5]/2 for q in rows)
        high=max(max(q[1],q[3])+q[5]/2 for q in rows)
        assert high<112.95 if region=='body' else low>161.65,(region,low,high)
        support[region+' / '+role]=dict(segments=len(rows),deposited_y_extent_mm=[low,high],
                    z_mm=[min(q[4] for q in rows),max(q[4] for q in rows)])
    inputs=('rotary_covered_print_checks.py','rotary_covered_design.py',
            '../../physical_analysis/manufacturing.py')
    out=dict(source_sha256={v:hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for v in inputs},
        exported_thread_missing_mm3=missing,old_hollow_negative_control_missing_mm3=old_missing,
        core_sections=core,key_sections=keys,pocket_roof_sections=roofs,
        uncovered_width_limit_mm=.1,support_review_complete=True,support_regions=support,control_probe_reviews=probe_reviews,
        gcode_sha256=gcodes,slice_inputs={k:r['slice']['input_sha256'] for k,r in reports.items()},
        scope='Local width-based path coverage, not measured strength or polymer bonding. Full-layout support remains at the accessible outside body bore and cap keeper, outside storage. Remove before assembly. Primary control supports are off; any forced probe plug is reviewed separately inside a short key pocket.')
    (n/'print_paths.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(core_missing=missing,key_sections=len(keys),roof_sections=len(roofs),support_regions=list(support))))


if __name__=='__main__':main()
