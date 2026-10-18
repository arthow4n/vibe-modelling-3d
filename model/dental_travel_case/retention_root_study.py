"""Production-root press study; scoped local compliance/strain, not retention.

The isolated tongue's fixed-stub edge omits the production R0.8 root blend. This
fixture crops the actual complete M2B body, including both roots, liner, guard and
circumference, and grips the annular cut 12 mm below the beam roots. Force-loaded
pads may rotate; no pad displacement or desired release travel is imposed.

Prepare first, then coordinate native resource use before solve. Example:
 ./execute.py --threads 1 model/dental_travel_case/retention_root_study.py prepare --load 3.2 --modulus 1200
 ./execute.py --threads 1 model/dental_travel_case/retention_root_study.py solve --load 3.2 --modulus 1200 --linear-solver default --destination /tmp/dental_m2b_production_root

The retained 4 N case is an overtravel counterexample: its leaf/liner clearance
screen is nonpositive. Its completed contact-free solve cannot qualify that pose.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cadquery as cq
import numpy as np
from physical_analysis import AnalysisCase,Material,Region
from physical_analysis.backends.structural import CalculixBackend
from physical_analysis.evidence import retain_run
import m1_design as m1
import m2b_design as design

ROOT=Path(__file__).resolve().parent


def quadratic_face_coordinate_bounds(values):
    """Conservative scalar bounds for shared C3D10 six-node face ordering."""
    coords=np.asarray(values,dtype=float)
    if coords.shape!=(6,) or not np.isfinite(coords).all():
        raise ValueError('Provide six finite face coordinates')
    controls=np.concatenate((coords[:3],
        2*coords[3:]-(coords[[0,1,2]]+coords[[1,2,0]])/2))
    return float(controls.min()),float(controls.max())


def guarded_root_record(path):
    answer=json.loads((path/'result.json').read_text())
    case=json.loads((path/'case.json').read_text())
    if case['name']!='m2b_production_root_press':
        raise ValueError('Expected an actual-production-root pressure fixture')
    if not answer['completed']:
        raise ValueError('Comparison requires completed native records')
    for filename,key in (('analysis.inp','input_sha256'),('case.json','case_sha256')):
        if hashlib.sha256((path/filename).read_bytes()).hexdigest()!=answer['provenance'][key]:
            raise ValueError('Saved native input/case differs from result')
    return answer,case


def compare_mesh_runs(directory,reference):
    """One actual-root mesh refinement, keeping loading and support fixed."""
    from physical_analysis.results import AnalysisResult
    from physical_analysis.studies import compare_results
    coarse,oldcase=guarded_root_record(reference)
    refined,newcase=guarded_root_record(directory)
    for key in ('constraints','contacts','observations','nonlinear','loads','max_increment'):
        if oldcase[key]!=newcase[key]:
            raise ValueError('Mesh comparison changed '+key)
    def physical_parts(case):
        return [{key:value for key,value in part.items() if key not in
                 ('mesh_size_mm','mesh_min_size_mm','mesh_curvature_points')}
                for part in case['parts']]
    if physical_parts(oldcase)!=physical_parts(newcase):
        raise ValueError('Mesh comparison changed geometry or material')
    a,b=AnalysisResult(**coarse),AnalysisResult(**refined)
    for answer in (a,b):
        answer.metrics['minimum_inward_tooth_displacement_mm']={
            label:(answer.metrics['observations'][label+'_tooth']['min_mm'][0] if label=='negative'
                   else -answer.metrics['observations'][label+'_tooth']['max_mm'][0])
            for label in ('negative','positive')}
    comparisons=compare_results(a,b,metrics=('max_displacement_mm',
        'minimum_inward_tooth_displacement_mm.negative',
        'minimum_inward_tooth_displacement_mm.positive'),relative_tolerance=.05)
    comparisons.update(compare_results(a,b,metrics=('max_abs_principal_strain','max_von_mises_MPa'),relative_tolerance=.10))
    witness_records={}
    for path in (reference,directory):
        witness=json.loads((path/'channel_witness.json').read_text())
        if witness['raw_native_result_sha256']!=hashlib.sha256((path/'result.json').read_bytes()).hexdigest():
            raise ValueError('Channel witness identifies a different native result')
        witness_records[path.name]=dict(status=witness['status'],
            minimum_face_gap_lower_bound_mm=witness['minimum_continuous_face_gap_lower_bound_mm'])
    return dict(scope='One-level graded-mesh sensitivity of the actual production-root pressure fixture. Five-percent displacement and ten-percent strain/stress tolerances are numerical diagnostics; they are not asymptotic convergence, material acceptance, or retention qualification.',
        reference_directory=reference.name,new_directory=directory.name,
        comparisons=comparisons,channel_witnesses=witness_records,
        mesh={path.name:answer['provenance']['mesh'] for path,answer in ((reference,coarse),(directory,refined))},
        strain_peak_centroids_mm={path.name:answer['metrics']['max_strain_element_centroid_mm'] for path,answer in ((reference,coarse),(directory,refined))},
        final_minimum_tooth_inward_displacement_mm={path.name:{label:(answer['metrics']['observations'][label+'_tooth']['min_mm'][0] if label=='negative' else -answer['metrics']['observations'][label+'_tooth']['max_mm'][0]) for label in ('negative','positive')} for path,answer in ((reference,coarse),(directory,refined))},
        raw_native_source_result_sha256={path.name:hashlib.sha256((path/'result.json').read_bytes()).hexdigest() for path in (reference,directory)})


def compare_increment_runs(directory,reference):
    """Reuse an earlier matching-load frame as a scoped increment control."""
    from physical_analysis.backends.worker import saved_meshes
    from physical_analysis.results import AnalysisResult
    from physical_analysis.studies import compare_results
    records=[]
    for path in (reference,directory):
        records.append(guarded_root_record(path))
    (coarse,oldcase),(refined,newcase)=records
    for key in ('parts','constraints','contacts','observations','nonlinear'):
        if oldcase[key]!=newcase[key]:
            raise ValueError('Increment control changed '+key)
    if saved_meshes(oldcase,reference/'analysis.inp')!=saved_meshes(newcase,directory/'analysis.inp'):
        raise ValueError('Increment control changed the actual native mesh')
    fractions=[]
    if len(oldcase['loads'])!=len(newcase['loads']):
        raise ValueError('Increment control changed loading selections')
    for a,b in zip(oldcase['loads'],newcase['loads'],strict=True):
        if a['selection']!=b['selection']:
            raise ValueError('Increment control changed loading selections')
        for old,new in zip(a['force_N'],b['force_N'],strict=True):
            if old:
                fractions.append(new/old)
            elif new:
                raise ValueError('Increment control changed force direction')
    fraction=fractions[0]
    if not 0<fraction<=1 or any(abs(value-fraction)>1e-12 for value in fractions):
        raise ValueError('Loads are not proportional within the earlier saved load path')
    matched=next((frame for frame in coarse['history'] if abs(frame['load_fraction']-fraction)<1e-8),None)
    if matched is None:
        raise ValueError('Earlier run has no saved frame at the new final load')
    channel_bounds={}
    for path,answer,limit in ((reference,coarse,fraction),(directory,refined,1.)):
        witness=json.loads((path/'channel_witness.json').read_text())
        if witness['raw_native_result_sha256']!=hashlib.sha256((path/'result.json').read_bytes()).hexdigest():
            raise ValueError('Channel witness identifies a different native result')
        if witness['case_sha256']!=answer['provenance']['case_sha256']:
            raise ValueError('Channel witness identifies a different native case')
        prefix=[frame for frame in witness['history'] if frame['load_fraction']<=limit+1e-8]
        bound=min(value for frame in prefix for value in frame['continuous_quadratic_face_gap_lower_bound_mm'].values())
        if bound<=0:
            raise ValueError('The compared load path does not exclude selected-face contact')
        channel_bounds[path.name]=bound
    final=refined['history'][-1]
    metrics=('max_displacement_mm','max_abs_principal_strain')
    # 1% is a numerical increment-resolution diagnostic, not PETG strain or
    # product acceptance. This is far below the demonstrated ~0.2 mm radial
    # retraction margin and leaves mesh/material questions completely separate.
    comparisons=compare_results(
        AnalysisResult('earlier_matching_load', 'completed',True,{k:matched[k] for k in metrics}),
        AnalysisResult('new_final_load','completed',True,{k:final[k] for k in metrics}),
        metrics=metrics,relative_tolerance=.01)
    observation_difference=max(abs(float(a)-float(b))
        for name in matched['observations']
        for kind in ('min_mm','max_mm','mean_mm')
        for a,b in zip(matched['observations'][name][kind],final['observations'][name][kind],strict=True))
    return dict(scope='Same native mesh, material, grip, pressure selection and matching actual load; earlier saved frame versus new final frame. Later frames in the earlier run do not alter this equilibrium. Increment qualification only; no mesh, contact, material or product acceptance.',
        reference_directory=reference.name,new_directory=directory.name,
        reference_fraction=fraction,
        matching_final_force_vectors_N=[load['force_N'] for load in newcase['loads']],
        minimum_selected_face_channel_bound_over_compared_subpaths_mm=channel_bounds,
        reference_maximum_load_increment_N=max(abs(v) for load in oldcase['loads'] for v in load['force_N'])*oldcase['max_increment'],
        new_maximum_load_increment_N=max(abs(v) for load in newcase['loads'] for v in load['force_N'])*newcase['max_increment'],
        comparisons=comparisons,
        maximum_observation_summary_component_difference_mm=observation_difference,
        final_strain_peak_centroid_mm=refined['metrics']['max_strain_element_centroid_mm'],
        final_strain_peak_is_over_full_new_run=True,
        raw_native_source_result_sha256={path.name:hashlib.sha256((path/'result.json').read_bytes()).hexdigest() for path in (reference,directory)})


def channel_witness(directory):
    """Bound complete quadratic faces, rather than just their sampled nodes.

    Degree-two triangular Bernstein controls are the three vertex coordinates
    and 2*midpoint-(endpoint_a+endpoint_b)/2 on each edge. Their convex hull
    contains the complete isoparametric face. Disjoint X halfspaces therefore
    establish separation of the selected FEM faces, including nodal overshoot.
    This does not make a nonpositive bound a proof of actual intersection.
    """
    from physical_analysis.backends.worker import saved_meshes,iter_dat
    from physical_analysis.backends.mesh import select_nodes
    result=json.loads((directory/'result.json').read_text())
    description=json.loads((directory/'root_fixture.json').read_text())
    if not result['completed']:
        raise ValueError('The witness requires a completed extracted native run')
    for filename,key in (('analysis.inp','input_sha256'),('case.json','case_sha256')):
        if hashlib.sha256((directory/filename).read_bytes()).hexdigest()!=result['provenance'][key]:
            raise ValueError('Native input/case no longer matches the extracted result')
    for name,module in (('m1_design',m1),('m2b_design',design)):
        if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()!=description['source_sha256'][name]:
            raise ValueError('Current production geometry differs from native fixture')
    case=json.loads((directory/'case.json').read_text())
    if case['name']!='m2b_production_root_press':
        raise ValueError('Expected the actual-production-root pressure fixture')
    meshes=saved_meshes(case,directory/'analysis.inp')
    mesh=meshes['body_coupon'];d=design.D
    observations={o['name']:o['selection'] for o in case['observations']}
    selected={}
    for label,sign in (('negative',-1),('positive',1)):
        for surface,plane,width,z_min in (
            ('leaf_inner',sign*(d.beam_outer-d.beam_thickness),d.beam_width/2,d.beam_root+.799),
            ('liner_front',sign*(d.beam_outer-d.beam_thickness-(d.release+.3)),d.beam_width/2+2.8,d.beam_root-2.001)):
            faces=[ids for _,_,ids in mesh['surface'] if all(
                abs(mesh['nodes'][i][0]-plane)<1e-6 and
                abs(mesh['nodes'][i][1])<=width+1e-6 and
                mesh['nodes'][i][2]>=z_min for i in ids)]
            if not faces:
                raise ValueError(label+' '+surface+' planar faces absent')
            selected[label+'_'+surface]=faces
        tooth_nodes=set(select_nodes(observations[label+'_tooth'],meshes))
        selected[label+'_tooth']=[ids for _,_,ids in mesh['surface'] if set(ids)<=tooth_nodes]
        if not selected[label+'_tooth']:
            raise ValueError('Selected actual tooth surface patch is absent')
    history=[]
    for time,frame in iter_dat(directory/'analysis.dat'):
        us={int(row[0]):np.array(row[1:]) for row in frame['displacements']}
        if set(us)!=set(mesh['nodes']):
            raise ValueError('Incomplete raw native displacement field')
        expected=next((f for f in result['history'] if abs(f['load_fraction']-time)<1e-8),None)
        if expected is None:
            raise ValueError('Raw field frame is absent from extracted result')
        gaps={};withdrawal={}
        for label,direction in (('negative',1),('positive',-1)):
            bounds={}
            for surface in ('leaf_inner','liner_front','tooth'):
                key=label+'_'+surface
                samples=np.array([us[i] for i in select_nodes(observations[key],meshes)])
                for name,value in (('min_mm',samples.min(axis=0)),('max_mm',samples.max(axis=0)),('mean_mm',samples.mean(axis=0))):
                    if not np.allclose(value,expected['observations'][key][name],rtol=0,atol=1e-7):
                        raise ValueError('Raw surface displacement differs from extracted frame')
                lower=[];upper=[]
                for ids in selected[key]:
                    coords=np.array([mesh['nodes'][i][0]+us[i][0] for i in ids])*direction
                    minimum,maximum=quadratic_face_coordinate_bounds(coords)
                    lower.append(minimum);upper.append(maximum)
                bounds[surface]=dict(min_inward_coordinate_mm=min(lower),
                                     max_inward_coordinate_mm=max(upper))
            gaps[label]=bounds['liner_front']['min_inward_coordinate_mm']-bounds['leaf_inner']['max_inward_coordinate_mm']
            nominal=d.width/2-d.receiver_wall+bounds['tooth']['min_inward_coordinate_mm']
            withdrawal[label]=dict(nominal_receiver_mm=nominal,
                receiver_at_adverse_guide_offset_mm=nominal-d.lap_clearance,
                deformed_tooth_outward_coordinate_upper_bound_mm=-bounds['tooth']['min_inward_coordinate_mm'])
        history.append(dict(load_fraction=time,continuous_quadratic_face_gap_lower_bound_mm=gaps,
            selected_tooth_withdrawal_clearance_to_frozen_receiver_mm=withdrawal))
    if len(history)!=len(result['history']) or not history or abs(history[-1]['load_fraction']-1)>1e-8:
        raise ValueError('Raw displacement frame sequence differs from completed result')
    minimum=min(v for frame in history for v in frame['continuous_quadratic_face_gap_lower_bound_mm'].values())
    with (directory/'analysis.dat').open('rb') as raw:
        field_hash=hashlib.file_digest(raw,'sha256').hexdigest()
    return dict(status='SELECTED_QUADRATIC_FACES_SEPARATED' if minimum>0 else 'CONTACT_NOT_EXCLUDED',
        scope='Convex-hull separation of actual deformed quadratic FEM planar inner-leaf and liner-front faces across all saved frames. Other faces, cap interaction, continuous load time between frames, exact CAD deformation and printed properties remain outside this witness.',
        minimum_continuous_face_gap_lower_bound_mm=minimum,history=history,
        final_selected_tooth_withdrawal_clearance_to_frozen_receiver_mm=history[-1]['selected_tooth_withdrawal_clearance_to_frozen_receiver_mm'],
        withdrawal_scope='Coordinate bound on the selected actual tooth surface patch versus the frozen CAD receiver plane at each side independently adverse guide offset. Positive values indicate radial clearance of this selected FEM patch; early negative values are intentional retained engagement. This omits unselected faces, cap deformation, tilt, friction and external opening load.',
        selected_face_counts={key:len(value) for key,value in selected.items()},
        source_sha256=description['source_sha256'],
        raw_native_result_sha256=hashlib.sha256((directory/'result.json').read_bytes()).hexdigest(),
        input_sha256=result['provenance']['input_sha256'],
        case_sha256=result['provenance']['case_sha256'],
        raw_displacement_field_sha256=field_hash,
        nonpositive_bound_interpretation='A conservative bound crossing zero does not prove contact, but prevents a contact-free conclusion from this witness.')


def pad_region(d,sign):
    x=sign*(d.beam_outer+1.2)
    return Region((x,-d.beam_width/2,d.press_z-1),
                  (x,d.beam_width/2,d.press_z+1))


def fixture(*,load,modulus,mesh_size,mesh_min,curvature,increment):
    if load<=0 or modulus<=0:
        raise ValueError('Provide positive load and effective modulus')
    identity={name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
              for name,module in (('m1_design',m1),('m2b_design',design))}
    parts=design.build()
    d=parts['dimensions']
    support_z=d.beam_root-12
    top=d.seam+d.lap
    coupon=parts['body'].intersect(m1.box(0,0,(support_z+top)/2,
                  d.width+4,d.depth+4,top-support_z))
    mat=Material('PETG effective isotropic hypothesis',modulus,.38,
        'Uncalibrated homogeneous effective stiffness; no measured layer strength, '
        'infill, yield, fatigue or recovery. No strain acceptance threshold supplied.',None)
    # StructuralQuestion does not expose curvature mesh controls. AnalysisCase
    # retains the same force/support semantics and native execution lifecycle.
    case=AnalysisCase('m2b_production_root_press',nonlinear=True,max_increment=increment)
    case.add_part('body_coupon',coupon,material=mat,mesh_size_mm=mesh_size,
                  mesh_min_size_mm=mesh_min,mesh_curvature_points=curvature)
    case.fix('body_coupon',Region.plane('z',support_z),name='annular_grip')
    pads=[]
    for sign,label in ((-1,'negative'),(1,'positive')):
        region=pad_region(d,sign)
        force=(-sign*load,0,0)
        case.apply_force('body_coupon',region,force_N=force)
        case.observe('body_coupon',region,name=label+'_pad')
        lo,hi=sorted((sign*(d.beam_outer-d.beam_thickness-.1),
                      sign*(d.beam_outer+d.hook_projection+.1)))
        case.observe('body_coupon',Region((lo,-d.hook_width/2,d.hook_bottom-.1),
            (hi,d.hook_width/2,d.beam_tip+.1)),name=label+'_tooth')
        case.observe('body_coupon',Region((lo,-d.hook_width/2,d.beam_tip-.1),
            (hi,d.hook_width/2,d.beam_tip+.1)),name=label+'_tip')
        case.observe('body_coupon',Region((lo,-d.beam_width/2,d.beam_root-1),
            (hi,d.beam_width/2,d.beam_root+3)),name=label+'_root_near')
        leaf_inner=sign*(d.beam_outer-d.beam_thickness)
        liner_front=sign*(d.beam_outer-d.beam_thickness-(d.release+.3))
        for name,x in (('leaf_inner',leaf_inner),('liner_front',liner_front)):
            case.observe('body_coupon',Region((x,-d.beam_width/2,d.beam_root+2),
                (x,d.beam_width/2,d.beam_tip+.1)),name=label+'_'+name)
        selected=[f for f in coupon.val().Faces() if f.geomType()=='PLANE'
                  and all(region.contains(v.Center().toTuple()) for v in f.Vertices())]
        area=sum(f.Area() for f in selected)
        if not selected or area<=0:
            raise ValueError(label+' pad surface is absent from actual production crop')
        pads.append(dict(name=label,region=dict(lower=region.lower,upper=region.upper),
            actual_CAD_planar_area_mm2=area,force_N=list(force),
            nominal_uniform_traction_MPa=load/area,
            actual_surface_normals=[list(f.normalAt().toTuple()) for f in selected]))
    case.observe('body_coupon',Region.plane('z',support_z),name='annular_grip')
    case.observe('body_coupon',Region((-d.width/2,d.depth/2,support_z+2),
        (d.width/2,d.depth/2,d.seam-2)),name='remote_broad_wall')
    description=dict(scope='Local production-root press compliance and strain. No cap, retention prediction, finger anatomy, or printed elastic-acceptance claim.',
        source_sha256=identity,geometry='Actual m2b.build()[body] full-circumference crop; no reconstructed leaf/root approximation.',
        support_z_mm=support_z,nominal_beam_root_z_mm=d.beam_root,
        upper_crop_z_mm=top,root_blend_radius_mm=.8,
        support='All three translations fixed only on annular bottom cut 12 mm below nominal beam root.',
        force='Equal opposite global-X tractions initially normal to each pad, total load per pad; fixed world directions rather than follower pressure. Pads retain all rotational/compliance degrees of freedom.',
        pads=pads,material=dict(effective_modulus_MPa=modulus,poisson_ratio=.38,strain_limit=None),
        mesh=dict(max_size_mm=mesh_size,min_size_mm=mesh_min,curvature_points=curvature),
        increment=increment,nominal_leaf_liner_gap_mm=d.release+.3,
        contact_policy='No contact assumed for this initial press fixture. Every saved frame is screened for sampled leaf/liner relative motion. Nonpositive sampled clearance blocks any contact-free interpretation; native self-contact is outside the current AnalysisCase interface and must not be silently omitted.',
        limitations=['Annular grip is a local root fixture, not full-size handling.',
            'Printed properties, recovery and permanent set are unmeasured.',
            'Root peak strain needs mesh qualification; no arbitrary 1% material acceptance is applied.',
            'Sampled nodal channel separation cannot bound quadratic-surface overshoot or continuous contact.'])
    return case,description


def assess(result,description):
    d=design.D
    frames=[]
    for frame in result['history']:
        gaps={}
        observations=frame['observations']
        for label,direction in (('negative',1),('positive',-1)):
            leaf=observations[label+'_leaf_inner']
            liner=observations[label+'_liner_front']
            leaf_inward_max=leaf['max_mm'][0] if direction==1 else -leaf['min_mm'][0]
            liner_inward_min=liner['min_mm'][0] if direction==1 else -liner['max_mm'][0]
            gaps[label]=description['nominal_leaf_liner_gap_mm']+liner_inward_min-leaf_inward_max
        frames.append(dict(load_fraction=frame['load_fraction'],sampled_channel_x_gap_lower_bound_mm=gaps))
    minimum=min((v for f in frames for v in f['sampled_channel_x_gap_lower_bound_mm'].values()),default=None)
    metrics=result['metrics']
    final_observations=metrics.get('observations',{})
    tooth_retractions={}
    for label,direction in (('negative',1),('positive',-1)):
        tooth=final_observations.get(label+'_tooth')
        if tooth:
            tooth_retractions[label]=(tooth['min_mm'][0] if direction==1 else
                                       -tooth['max_mm'][0])
    location=metrics.get('max_strain_element_centroid_mm')
    return dict(status=('INCONCLUSIVE' if not result['completed'] or minimum is None else
                        'CONTACT_REPRESENTATION_REQUIRED' if minimum<=0 else 'SAMPLED_CHANNEL_CLEAR'),
        scope='Native peak location and saved-frame nodal channel-separation interpretation; not mesh convergence, material acceptance or exact deformed-surface clearance.',
        native_status=result['status'],native_completed=result['completed'],
        native_evidence_identity={key:result.get('provenance',{}).get(key)
            for key in ('case_sha256','input_sha256','backend_sha256')},
        geometry_source_sha256=description['source_sha256'],
        max_abs_principal_strain=metrics.get('max_abs_principal_strain'),
        max_strain_element_centroid_mm=location,
        strain_peak_distance_from_nominal_root_z_mm=None if location is None else abs(location[2]-d.beam_root),
        strain_peak_distance_from_annular_clamp_z_mm=None if location is None else abs(location[2]-description['support_z_mm']),
        minimum_sampled_channel_x_gap_mm=minimum,channel_history=frames,
        final_minimum_inward_tooth_displacement_mm=tooth_retractions,
        both_pad_and_tooth_observations=metrics.get('observations'),
        force_balance=metrics.get('max_force_balance_relative'),
        contact_consequence='A nonpositive bound is potential leaf/liner contact requiring stronger local witness or self-contact treatment before interpreting root strain. Positive nodal bounds remain sampled evidence only.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=('prepare','solve','witness','compare','compare-mesh'))
    parser.add_argument('--load',type=float)
    parser.add_argument('--modulus',type=float)
    parser.add_argument('--mesh',type=float,default=3.)
    parser.add_argument('--mesh-min',type=float,default=.5)
    parser.add_argument('--curvature',type=int,default=8)
    parser.add_argument('--increment',type=float,default=.1)
    parser.add_argument('--linear-solver',choices=('default','iterative_scaling','iterative_cholesky'))
    parser.add_argument('--destination',type=Path)
    parser.add_argument('--mesh-from',type=Path)
    parser.add_argument('--reference',type=Path)
    args=parser.parse_args()
    if args.operation in ('witness','compare','compare-mesh'):
        if args.destination is None:
            parser.error('--destination must identify an existing raw native run')
        directory=args.destination.resolve()
        if args.operation in ('compare','compare-mesh') and args.reference is None:
            parser.error('--reference is required for the earlier native run')
        if args.operation=='witness':
            witnessed=channel_witness(directory);filename='channel_witness.json'
        elif args.operation=='compare':
            witnessed=compare_increment_runs(directory,args.reference.resolve());filename='increment_comparison.json'
        else:
            witnessed=compare_mesh_runs(directory,args.reference.resolve());filename='mesh_comparison.json'
        retained=ROOT/'notes/retention'/directory.name
        if retained.is_dir():
            witnessed['retained_result_sha256']=hashlib.sha256((retained/'result.json').read_bytes()).hexdigest()
            (retained/filename).write_text(json.dumps(witnessed,indent=2)+'\n')
        (directory/filename).write_text(json.dumps(witnessed,indent=2)+'\n')
        print(json.dumps(witnessed,indent=2))
        return
    if args.load is None or args.modulus is None:
        parser.error('--load and --modulus are required for prepare and solve')
    case,description=fixture(load=args.load,modulus=args.modulus,mesh_size=args.mesh,
                             mesh_min=args.mesh_min,curvature=args.curvature,
                             increment=args.increment)
    if args.operation=='prepare':
        print(json.dumps(description,indent=2))
        return
    if args.destination is None:
        parser.error('--destination is required for solve')
    directory=args.destination.resolve()
    if args.linear_solver is None:
        parser.error('Select --linear-solver explicitly before native execution')
    result=case.run(directory,backend=CalculixBackend(linear_solver=args.linear_solver),mesh_from=args.mesh_from)
    (directory/'root_fixture.json').write_text(json.dumps(description,indent=2)+'\n')
    interpreted=assess(result.to_dict(),description)
    interpreted['native_result_sha256']=hashlib.sha256((directory/'result.json').read_bytes()).hexdigest()
    (directory/'root_assessment.json').write_text(json.dumps(interpreted,indent=2)+'\n')
    retained=ROOT/'notes/retention'/directory.name
    retain_run(directory,retained)
    interpreted['retained_result_sha256']=hashlib.sha256((retained/'result.json').read_bytes()).hexdigest()
    (retained/'root_fixture.json').write_text(json.dumps(description,indent=2)+'\n')
    (retained/'root_assessment.json').write_text(json.dumps(interpreted,indent=2)+'\n')
    print(json.dumps(interpreted,indent=2))


if __name__=='__main__':
    main()
