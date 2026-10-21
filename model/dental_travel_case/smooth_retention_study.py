"""Conditional C pull/side screens using actual CAD and established question APIs.

No friction credit, impact rating or calibrated printed-force prediction.
Both paired and single-end radial loading are solved to expose shell coupling.
"""
from dataclasses import replace
from pathlib import Path
import json
import sys
import numpy as np
from physical_analysis import StructuralQuestion, Region, Support, SurfaceForce, QuestionStudy
from physical_analysis.evidence import retain_run
from execution.batch import ScriptTask, run as batch
from closure_research_flex import MATERIAL
from closure_research_checks import hashes
from closure_research_pull import required_retraction, profile_retraction, spring_path
from short_lap_report import segments
from short_lap_refinement import bump
import m1_design as base
from smooth_case_design import build

ROOT = Path(__file__).resolve().parent
OUTPUTS={
    'retention-c1':ROOT/'notes/smooth_case/retention/strengthened',
    'retention-c2':ROOT/'notes/smooth_case/retention/final',
}

def study_output(variant):
    if variant not in OUTPUTS:raise ValueError(variant)
    return OUTPUTS[variant]
INPUTS = ('smooth_case_design.py','smooth_retention_study.py','short_lap_refinement.py',
          '../../physical_analysis/questions.py','../../physical_analysis/backends/mesh.py',
          'short_lap_design.py','closure_research_design.py','m1_design.py',
          'closure_research_flex.py','closure_research_pull.py','short_lap_report.py','../../uv.lock')
PULL_KEYS = tuple(f'pull_{mode}_{member}' for mode in ('pair','single') for member in ('body','cap'))
SIDE_KEYS = tuple(f'side_{axis}_{member}' for axis in ('x','y') for member in ('body','cap'))


def mesh_levels(key,variant):
    fine=1.5 if key.endswith('_cap') and variant=='retention-c2' else 1.75
    return (('baseline',2.5),('mesh_sensitivity_1',fine))


def cap_reference(variant,label):
    OUT=study_output(variant)
    folder='cap_half_validation_v2' if variant=='retention-c2' and label!='baseline' else 'cap_half_validation'
    return OUT/'native'/folder/label


def question(key, *, cap_symmetry, variant):
    if key not in (*PULL_KEYS,*SIDE_KEYS):raise ValueError(key)
    family,mode,member=key.split('_')
    p=build(variant);d=p['dimensions'];forces=[]
    if member=='body':
        floor=d.seam-16
        part=p['body'].intersect(base.box(0,0,(floor+d.seam+d.lap)/2,d.width+8,d.depth+8,d.seam+d.lap-floor)).clean()
        clamp=floor
    else:part=p['cap'];clamp=d.length
    supports=[Support(Region.plane('z',clamp))]
    if cap_symmetry:
        if member!='cap':raise ValueError('Symmetry reduction is cap-only')
        axis='x' if family=='side' and mode=='y' else 'y'
        cutter=cq_box_half(axis)
        part=part.intersect(cutter).clean()
        supports.append(Support(Region.plane(axis,0),displacement_mm=(0,None,None) if axis=='x' else (None,0,None),name='symmetry'))
    if family=='pull':
        radius=d.sleeve_width/2+d.detent if member=='body' else d.width/2-d.wall
        lo,hi=(d.latch_z-.25,d.latch_z+.25) if member=='body' else (d.latch_z-3.2,d.latch_z-1)
        half=d.bump_width/2+(0 if member=='body' else .3)
        observations={}
        for sign in ((1,-1) if mode=='pair' else (1,)):
            pad=Region((sign*radius,-half,lo),(sign*radius,half,hi))
            force=sign*(-1 if member=='body' else 1)
            forces.append(SurfaceForce(pad,(force,0,0)))
            observations['positive' if sign==1 else 'negative']=pad
    else:
        index=0 if mode=='x' else 1
        radius=(d.sleeve_width if index==0 else d.sleeve_depth)/2
        if member=='cap':radius+=d.clearance
        # Both bands are inside the ACTUAL 27mm cap coverage, clear of its rim rounding.
        lower,upper=p['rim_z']+3,d.seam+d.lap-3
        high=(2*(d.length-d.seam)-2*(lower-d.seam))/(upper-lower)
        low=2-high
        across=18 if index==0 else 28
        def region(sign,z):
            return (Region((sign*radius,-across,z-2),(sign*radius,across,z+2)) if index==0 else
                    Region((-across,sign*radius,z-2),(across,sign*radius,z+2)))
        observations={'top':region(-1,upper),'bottom':region(1,lower)}
        for name,total in (('top',high),('bottom',low)):
            load=[0.,0.,0.];load[index]=total*(1 if member=='body' else -1)
            forces.append(SurfaceForce(observations[name],tuple(load)))
    if cap_symmetry:forces=[SurfaceForce(f.region,tuple(v/2 for v in f.force_N)) for f in forces]
    return StructuralQuestion(name='smooth_'+key,part=part,material=MATERIAL,
        supports=tuple(supports),forces=tuple(forces),
        observations=observations,mesh_size_mm=2.5,nonlinear=False,max_increment=1.,
        mesh_min_size_mm=.5 if member=='cap' else None,
        mesh_curvature_points=16 if member=='cap' else None)


def solve(key,variant):
    OUT=study_output(variant)
    q=question(key,cap_symmetry=key.endswith('_cap') and (key!='pull_pair_cap' or variant=='retention-c2'),variant=variant)
    suffix='_curvature05' if key=='pull_pair_cap' else '_symmetry' if key.endswith('_cap') else ''
    native=OUT/'native'/(key+suffix);compact=OUT/'flex'/key
    if native.exists() or compact.exists():raise ValueError('Existing study; do not overwrite '+key)
    # Max displacement is the established scalar study metric; the report also
    # checks the actual radial pad compliance / derived side motion used below.
    compact.parent.mkdir(parents=True,exist_ok=True)
    evidence={}
    if key in ('pull_single_cap','side_x_cap'):
        for label,mesh in mesh_levels(key,variant):
            replace(q,mesh_size_mm=mesh).run(native/label,mesh_from=cap_reference(variant,label))
            evidence[label]=native/label
    result=QuestionStudy(q,decision='Choose whether C needs stronger sleeve/cap walls; 10% geometry-response precision, not printed calibration',
        metrics=('max_displacement_mm',),relative_tolerance=.10,mesh_levels=1,mesh_factor=.6 if key.endswith('_cap') and variant=='retention-c2' else .7).run(native,evidence=evidence)
    for label in ('baseline','mesh_sensitivity_1'):
        if (native/label/'result.json').exists():retain_run(native/label,compact/label)
    if (native/'study_result.json').exists():
        (compact/'study_result.json').write_text((native/'study_result.json').read_text())
    result.require_completed()
    print(key,result.status,result.metrics.get('question'),flush=True)


def read(key,variant):
    OUT=study_output(variant)
    records=[]
    for label,mesh in mesh_levels(key,variant):
        path=OUT/'flex'/('cap_half_validation' if key=='pull_pair_cap' and variant=='retention-c2' else key)/label
        answer=replace(question(key,cap_symmetry=key.endswith('_cap') and (key!='pull_pair_cap' or variant=='retention-c2'),variant=variant),mesh_size_mm=mesh).read_evidence(path)
        if not answer.completed:raise ValueError('Incomplete evidence '+key+'/'+label)
        r=json.loads((path/'result.json').read_text())
        assert r['metrics']['question']['numerical_evidence_adequate'],key
        assert r['metrics']['max_force_balance_relative']<.01
        records.append(r)
    return records


def pull_report(variant):
    inputs=hashes(INPUTS)
    OUT=study_output(variant)
    p=build(variant);d=p['dimensions'];members={}
    for key in PULL_KEYS:
        records=read(key,variant)
        values=[abs(r['metrics']['observations']['positive']['mean_mm'][0]) for r in records]
        change=abs(values[1]-values[0])/values[1]
        assert change<.10,(key,'compliance mesh sensitivity',change)
        r=records[1]
        # The actual tooth crest is a complete physical face. Cap tractions
        # use a nominal pressure window, not a known uniform contact patch;
        # retain its mesh-selected area and sensitivity explicitly.
        if key.endswith('_body'):
            expected_area=d.bump_width*.5
        else:
            pocket_start=d.latch_z-1.25-d.axial_play
            lip_top=pocket_start+(d.clearance+.2)/(d.detent+.35)
            expected_area=(d.bump_width+.6)*(lip_top-(d.latch_z-3.2))
            if key!='pull_pair_cap' or variant=='retention-c2':expected_area/=2
        for record in records:
            for load in record['provenance']['loads']:
                assert abs(load['area_mm2']-expected_area)/expected_area<(.02 if key.endswith('_body') else .10), (key,'load patch coverage',load['area_mm2'],expected_area)
        members[key]=dict(full_equivalent_force_N_per_loaded_crest=1.,native_force_fraction=.5 if key.endswith('_cap') and (key!='pull_pair_cap' or variant=='retention-c2') else 1.,expected_load_area_mm2=expected_area,compliance_mm_N=values[1],mesh_relative_change=change,
                          peak_strain_at_1N=r['metrics']['question']['peak_strain'],
                          load_regions=r['provenance']['loads'],balance=r['metrics']['max_force_balance_relative'])
    tooth=bump(d.sleeve_width/2,d,pocket=False).val().rotate((0,0,0),(0,0,1),-90)
    tp,receiver=segments(tooth,d),segments(p['cap'].val(),d)
    travel=np.linspace(0,6,481);paths={};scenarios=[]
    witness_cache={}
    for mode,count in (('pair',2),('single',1)):
        compliance=sum(members[f'pull_{mode}_{member}']['compliance_mm_N'] for member in ('body','cap'))
        for gap in (-.15,0.,.15):
            delta=[profile_retraction(tp,receiver,s,gap) for s in travel]
            path=spring_path(travel,delta,compliance,count)
            path['peak_closing_N']=max(0.,-min(path['force_N']))
            coarse=spring_path(travel[::2],delta[::2],compliance,count)
            path['peak_step_change']=abs(path['peak_force_N']-coarse['peak_force_N'])/path['peak_force_N']
            assert path['peak_step_change']<.10
            witnesses=[]
            for s in (0.,.5,1.,2.,3.,6.):
                cache_key=(s,gap)
                if cache_key not in witness_cache:
                    witness_cache[cache_key]=required_retraction(p['cap'].val(),tooth,s,0,gap)
                direct=witness_cache[cache_key]
                planar=profile_retraction(tp,receiver,s,gap)
                assert abs(direct-planar)<.001,(s,gap,direct,planar)
                witnesses.append(dict(travel_mm=s,CAD_retraction_mm=direct,profile_retraction_mm=planar))
            path.update(travel_mm=travel.tolist(),retraction_mm=delta,CAD_witnesses=witnesses)
            radial=max(delta)/compliance
            path['scaled_peak_strain']={m:members[f'pull_{mode}_{m}']['peak_strain_at_1N']*radial for m in ('body','cap')}
            paths[f'{mode}_{gap}']=path
            for E in (900,1200,1800,2200):
                scenarios.append(dict(mode=mode,E_MPa=E,extra_radial_gap_mm=gap,
                    peak_pull_N=path['peak_force_N']*E/1200,
                    peak_closing_N=path['peak_closing_N']*E/1200,
                    ideal_undamped_release_N=path['undamped_seated_release_force_N']*E/1200))
    assert all(profile_retraction(tp,receiver,s,d.detent+.1)==0 for s in travel),'Missing-bite negative control'
    result=dict(variant=variant,source_sha256=hashes(INPUTS),members=members,paths=paths,scenarios=scenarios,
        material='Isotropic E1200 MPa / nu .38 hypothesis; E900–2200 scenarios are not calibrated bounds',
        scope=__doc__+' Body crop clamped 16mm below seam; cap roof clamped. Pair includes opposed radial loading; half-cap tractions are halved so mean displacement is per full-equivalent 1N. Single is a one-end fixture, not a peel-release prediction.',
        missing_bite_zero_barrier=True,
        provisional_comparison=dict(nominal_centered_pull_8_to_18N=8<=paths['pair_0.0']['peak_force_N']<=18,
            nominal_ideal_threshold_at_least_3_5N=paths['pair_0.0']['undamped_seated_release_force_N']>=3.5,
            scope='Historical agent design targets, not user acceptance or physical bag-retention criteria'))
    assert inputs==hashes(INPUTS),'Inputs changed during pull reporting'
    (OUT/'pull.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{field:v[field] for field in ('peak_force_N','barrier_Nmm','undamped_seated_release_force_N','scaled_peak_strain')} for k,v in paths.items()},indent=2))


def side_report(variant):
    inputs=hashes(INPUTS)
    OUT=study_output(variant)
    p=build(variant);d=p['dimensions'];lower,upper=p['rim_z']+3,d.seam+d.lap-3;cases={}
    for axis,index in (('x',0),('y',1)):
        members={};roofs=[]
        for member in ('body','cap'):
            records=read(f'side_{axis}_{member}',variant)
            members[member]=[{k:v['mean_mm'][index] for k,v in r['metrics']['observations'].items()} for r in records]
        for level in (0,1):
            relative={k:members['body'][level][k]-members['cap'][level][k] for k in ('top','bottom')}
            roof=relative['bottom']+(relative['top']-relative['bottom'])/(upper-lower)*(d.length-lower)
            roofs.append(abs(roof))
        change=abs(roofs[1]-roofs[0])/max(roofs[1],.01)
        cases[axis]=dict(members=members,estimated_extra_roof_motion_mm=roofs[1],coarse_estimated_extra_roof_motion_mm=roofs[0],mesh_relative_change=change)
    comparison={}
    if variant=='retention-c2':
        previous=json.loads((study_output('retention-c1')/'side.json').read_text())
        from closure_research_verification import require_sources
        require_sources(previous['source_sha256'])
        for axis,row in cases.items():
            old=previous['cases'][axis]
            old_range=sorted((old['coarse_estimated_extra_roof_motion_mm'],old['estimated_extra_roof_motion_mm']))
            new_range=sorted((row['coarse_estimated_extra_roof_motion_mm'],row['estimated_extra_roof_motion_mm']))
            comparison[axis]=dict(previous_range_mm=old_range,current_range_mm=new_range,
                improved_across_checked_meshes=max(new_range)<min(old_range),
                fine_response_reduction_fraction=1-row['estimated_extra_roof_motion_mm']/old['estimated_extra_roof_motion_mm'])
    result=dict(variant=variant,source_sha256=hashes(INPUTS),comparison_to_c1=comparison,load_N=2.,seam_moment_Nmm=180.,band_centres_z_mm=[lower,upper],cases=cases,
        numerical_screen_status='PASS' if all(c['mesh_relative_change']<.10 for c in cases.values()) else 'INCONCLUSIVE',
        scope='Independent fixed band tractions on actual C coverage; not contact redistribution, release, impact or safety rating')
    assert inputs==hashes(INPUTS),'Inputs changed during side reporting'
    (OUT/'side.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(cases,indent=2))


def cq_box_half(axis):
    import cadquery as cq
    return cq.Workplane('XY').box(200,200,400,centered=(False,True,False) if axis=='x' else (True,False,False))


def validate_symmetry(variant):
    inputs=hashes(INPUTS)
    OUT=study_output(variant)
    q=question('pull_pair_cap',cap_symmetry=True,variant=variant)
    native=OUT/'native'/('cap_half_validation_v2' if variant=='retention-c2' else 'cap_half_validation');compact=OUT/'flex/cap_half_validation'
    study=QuestionStudy(q,decision='Use exact mirror symmetry for principal-plane cap fixtures; retain C1 full/half comparison and check 10% mesh response precision',
        metrics=('max_displacement_mm',),relative_tolerance=.10,mesh_levels=1,mesh_factor=.6 if variant=='retention-c2' else .7)
    existing=(native/'study_result.json').exists()
    evidence={label:cap_reference(variant,label) for label in ('baseline','mesh_sensitivity_1')} if existing else {}
    if variant=='retention-c2':evidence['baseline']=cap_reference(variant,'baseline')
    result=study.run(evidence=evidence) if existing else study.run(native,evidence=evidence)
    result.require_completed();rows=[]
    for label in ('baseline','mesh_sensitivity_1'):
        source=cap_reference(variant,label)
        r=json.loads((source/'result.json').read_text())
        assert r['metrics']['question']['numerical_evidence_adequate']
        if variant=='retention-c1':
            full=json.loads((OUT/'native/pull_pair_cap_curvature05'/label/'result.json').read_text())
            a=full['metrics']['observations']['positive']['mean_mm'][0]
            b=r['metrics']['observations']['positive']['mean_mm'][0]
            change=abs(a-b)/abs(a)
            assert change<.05,(label,'mirror reduction disagreement',change)
            rows.append(dict(mesh=label,full_compliance_mm_N=a,half_compliance_mm_N=b,relative_change=change))
        else:
            rows.append(dict(mesh=label,half_compliance_mm_N=r['metrics']['observations']['positive']['mean_mm'][0],
                symmetry_basis='C1 full/half comparison and unchanged exact principal-plane mirror symmetry'))
        if not (compact/label/'result.json').is_file():retain_run(source,compact/label)
    assert inputs==hashes(INPUTS),'Inputs changed during symmetry review'
    (OUT/'symmetry.json').write_text(json.dumps(dict(source_sha256=hashes(INPUTS),comparison=rows,relative_limit=.05),indent=2)+'\n')
    print(json.dumps(rows))


def main():
    args=sys.argv[1:]
    if len(args)<2 or args[0] not in OUTPUTS:
        raise SystemExit('Specify retention-c1|retention-c2 followed by batch, solve KEY, validate-symmetry, report-pull or report-side')
    variant=args.pop(0);OUT=study_output(variant)
    if len(args)==2 and args[0]=='solve':solve(args[1],variant);return
    if args==['validate-symmetry']:validate_symmetry(variant);return
    if args in (['batch'],['batch-caps']):
        tasks=[ScriptTask('validate',Path(__file__).resolve(),(variant,'validate-symmetry'),threads=1,
            outputs=(OUT/'native'/('cap_half_validation_v2' if variant=='retention-c2' else 'cap_half_validation'),OUT/'flex/cap_half_validation'))]
        if args==['batch']:
            tasks.extend(ScriptTask(k,Path(__file__).resolve(),(variant,'solve',k),threads=1,
                outputs=(OUT/'native'/k,OUT/'flex'/k)) for k in (*[k for k in PULL_KEYS if k.endswith('_body')],*[k for k in SIDE_KEYS if k.endswith('_body')]))
        tasks.extend(ScriptTask(k,Path(__file__).resolve(),(variant,'solve',k),threads=1,depends_on=('validate',),
            outputs=(OUT/'native'/(k+'_symmetry'),OUT/'flex'/k)) for k in ('pull_single_cap','side_x_cap','side_y_cap'))
        results=batch(tasks,max_concurrent=2);print(json.dumps(results))
        if any(v['exit_code'] for v in results.values()):raise RuntimeError('Inspect retention study')
        return
    if args==['report-pull']:pull_report(variant);return
    if args==['report-side']:side_report(variant);return
    raise SystemExit('Unknown study operation')


if __name__=='__main__':main()
