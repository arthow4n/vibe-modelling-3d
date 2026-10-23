"""Actual Classic paths through the full-height cups; selected setup only."""
from collections import defaultdict
from pathlib import Path
import hashlib,json
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
import rotary_l20_uniform_design as d

ROOT=Path(__file__).resolve().parent


def main():
    report=json.loads((ROOT/'notes/uniform_l20/print_review.json').read_text())
    assert report['ok'] and report['slice']['ok']
    run=Path(report['slice']['kept_run_directory']);gcode=run/'plate_1.gcode'
    settings=json.loads((run/'effective-settings.json').read_text())
    assert settings['wall_generator']=='classic' and settings['detect_thin_wall']=='0'
    assert settings['sparse_infill_density']=='100%' and settings['wall_loops']=='2'
    assert settings['top_shell_layers']=='4' and settings['bottom_shell_layers']=='4'
    assert settings['ironing_type']=='top' and settings['ironing_flow']=='50%'
    assert settings['filament_max_volumetric_speed']==['9']
    layers=defaultdict(list)
    for q in orca_linear_paths(gcode):
        if not q[-1].startswith(('Support','Brim')):layers[round(q[4],5)].append(q)
    assert layers
    transposed={z:[(y,x,ny,nx,zz,w,role) for x,y,nx,ny,zz,w,role in rows]
                for z,rows in layers.items()}
    skin_count=0;surface_count=0;core_count=0;tie_count=0;min_core=d.CORE;max_missing=0.;coverage=[]
    def section(part,axis,along,z,span):
        cx,cy,_=d.PRINT_CENTRES[part]
        axis_centre=cy if axis=='y' else cx
        section_x=(cx if axis=='y' else cy)+along
        data=layers[z] if axis=='y' else transposed[z]
        return section_coverage(data,x_mm=section_x,z_mm=z,
            span_mm=(axis_centre+min(span),axis_centre+max(span)))
    for part in ('body','cap'):
        zs=[z for z in sorted(layers) if d.FLOOR_TOTAL+.2-1e-5<=z<=d.height(part)+.11]
        assert len(zs)>250,(part,len(zs))
        for z in zs:
            w,h,_=d.profile_at(part,min(d.height(part)-.001,z-.1))
            for axis,depth in (('x',w),('y',h)):
                # A tie centre crosses tiny internal corner pockets where the
                # hole perimeter turns. Inspect the full skin between ties;
                # independently retain both exposed faces at the tie column.
                along=0.
                for zone in d.wall_zones(part):
                    if zone[0]<=z-.1<=zone[1]:
                        p=d.wall_spec(part,zone,axis,1)
                        along=(p['along'][1]+p['along'][2])/2
                for sign in (-1,1):
                    for interval in ((0.,d.SKIN),(d.SKIN+d.CORE,d.WALL)):
                        span=[sign*(depth/2-i) for i in interval]
                        r=section(part,axis,along,z,span)
                        assert r['uncovered_width_mm']<.06,(part,axis,sign,z,interval,r)
                        max_missing=max(max_missing,r['uncovered_width_mm']);skin_count+=1
                    for interval in ((0.,.3),(d.WALL-.3,d.WALL)):
                        span=[sign*(depth/2-i) for i in interval]
                        r=section(part,axis,0.,z,span)
                        assert r['uncovered_width_mm']<.015,(part,axis,sign,z,'exposed skin face',r)
                        surface_count+=1
        for zone in d.wall_zones(part):
            for axis in ('x','y'):
                for sign in (-1,1):
                    p=d.wall_spec(part,zone,axis,sign)
                    between=(p['along'][1]+p['along'][2])/2
                    span=(p['radial']-d.CORE/2,p['radial']+d.CORE/2)
                    for z in zs:
                        if not zone[0]+.2-1e-5<=z<=zone[1]+1e-5:continue
                        r=section(part,axis,between,z,span)
                        assert r['uncovered_width_mm']>=.35,(part,axis,sign,z,r)
                        min_core=min(min_core,r['uncovered_width_mm']);core_count+=1
                    for zz in (p['vertical'][0],p['vertical'][len(p['vertical'])//2],p['vertical'][-1]):
                        z=min(zs,key=lambda z:abs(z-.1-zz))
                        r=section(part,axis,p['along'][1],z,span)
                        assert r['uncovered_width_mm']<.06,(part,axis,sign,z,'tie',r)
                        tie_count+=1
        # Floor skins and open core between posts, plus one complete post.
        p=d.floor_spec(part)
        x=(p['x'][1]+p['x'][2])/2;y=(p['y'][1]+p['y'][2])/2
        for z in (.2,.4,.6,.8,1.4,1.6,1.8,2.):
            r=section(part,'y',x,z,(y-.35,y+.35))
            assert r['uncovered_width_mm']<.06,(part,z,'floor skin',r)
            coverage.append(dict(part=part,z_mm=z,kind='floor skin',coverage=r))
        r=section(part,'y',x,1.,(y-.35,y+.35))
        assert r['filled_width_mm']<.01,(part,'floor air',r)
        coverage.append(dict(part=part,z_mm=1.,kind='floor air',coverage=r))
        r=section(part,'y',p['x'][1],1.,(p['y'][1]-.4,p['y'][1]+.4))
        assert r['uncovered_width_mm']<.06,(part,'floor post',r)
        coverage.append(dict(part=part,z_mm=1.,kind='floor post',coverage=r))
    support=[]
    if report['slice']['support_probe']['generated']:
        for q in orca_linear_paths(run/'support_probe/plate_1.gcode'):
            if not q[-1].startswith('Support'):continue
            # Expected forced support is enclosed in the horizontal floor
            # air core. A new signal elsewhere requires separate review.
            assert q[4]<=d.SKIN+d.CORE+1e-5,('Support outside reviewed floor core',q)
            support.append(q)
        assert support
    inputs=('rotary_l20_uniform_design.py','rotary_l20_uniform_print_checks.py','../tpu_damping_box/l20_standard.py','../../physical_analysis/manufacturing.py')
    out=dict(source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
        effective_settings={k:settings[k] for k in ('wall_generator','detect_thin_wall','layer_height',
            'initial_layer_print_height','top_shell_layers','bottom_shell_layers','wall_loops','sparse_infill_density','enable_support',
            'ironing_type','ironing_flow','ironing_speed','ironing_spacing','filament_max_volumetric_speed')},
        slice_input_sha256=report['slice']['input_sha256'],gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
        wall_skin_sections=skin_count,exposed_surface_sections=surface_count,wall_core_sections=core_count,tie_sections=tie_count,
        minimum_core_clear_width_mm=min_core,maximum_skin_uncovered_width_mm=max_missing,
        skin_uncovered_limit_mm=.06,exposed_face_band_mm=.3,exposed_face_uncovered_limit_mm=.015,
        core_clear_width_limit_mm=.35,floor_sections=coverage,
        tie_corner_review='At body layer 9.4mm, a tie-column section has a 0.08056mm internal corner pocket between perimeter paths; the outside face stays covered. Full-skin sections use positions between ties, with separate face-continuity and tie/core sections. This is an internal toolpath corner pocket, not a missing skin or a measured strength qualification.',
        forced_support_segments=len(support),forced_support_max_z_mm=max((q[4] for q in support),default=None),
        support_decision='Supports remain OFF. Forced-probe paths lie only in the enclosed 0.4mm floor air core. Its short roofs bridge between 0.8mm posts, in the revised uniform L20 construction; adding support would fill the damping void.',
        review_complete=True,limits='Width-envelope sections through actual paths, not measured printed gap openness, bonding, tall-wall stability, quietness or insertion force.')
    (ROOT/'notes/uniform_l20/paths.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('wall_skin_sections','wall_core_sections','tie_sections','minimum_core_clear_width_mm','forced_support_segments')}))


if __name__=='__main__':main()
