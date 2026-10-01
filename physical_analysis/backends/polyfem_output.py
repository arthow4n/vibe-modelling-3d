"""Identity-bound native VTU extraction; unavailable evidence fails explicitly."""
import csv
import json
from pathlib import Path
import numpy as np
from .polyfem_worker import digest, write_json
from .mesh import contains
from ..mesh_witness import inspect_mesh_pair


def recover(directory):
    """Use saved meshes/fields only, checking all original generated identities.

    This adapter's native meshes are complete independent files; regeneration
    does not require remeshing. No incomplete solve is promoted to completion.
    """
    from ..results import AnalysisResult
    from .polyfem_worker import implementation_identity
    r=AnalysisResult(**json.loads((directory/'result.json').read_text()))
    for key,file in (('case_sha256','case.json'),('input_sha256','scene.json'),('mesh_sha256','mesh.json')):
        if digest(directory/file)!=r.provenance.get(key):
            raise ValueError('Saved IPC input/mesh/case differs from recorded identity')
    case=json.loads((directory/'case.json').read_text())
    for p in case['parts']:
        if digest(directory/p['geometry'])!=p['sha256']:
            raise ValueError('Saved IPC CAD geometry differs from recorded identity')
    for file,identity in r.provenance['mesh_files_sha256'].items():
        if digest(directory/file)!=identity:
            raise ValueError('Saved native mesh differs from recorded identity')
    native_path=directory/'native.json'
    if not native_path.is_file() or r.provenance.get('native_exit_code') not in (0,None):
        raise ValueError('IPC recovery requires a complete original native solve')
    native=json.loads(native_path.read_text());scene=json.loads((directory/'scene.json').read_text())
    if (not native.get('solver_info') or max(row['t'] for row in native['solver_info'])!=scene['time']['time_steps']
            or 'Saving json...' not in (directory/'solver.log').read_text()):
        raise ValueError('Original IPC completion record missing')
    r.history=[];r.metrics={};r.errors=[];r.completed=False
    data=json.loads((directory/'mesh.json').read_text())
    extract(directory,case,data['parts'],data['selections'],scene,r)
    r.provenance.update(postprocess_only=True,original_backend_sha256=r.provenance['backend_sha256'],
                        backend_sha256=implementation_identity())
    r.write(directory/'answer.json')


def read_vtu(path, length_to_mm=1):
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy
    if not path.is_file():
        raise ValueError(f'Missing native frame: {path.name}')
    reader=vtk.vtkXMLUnstructuredGridReader();reader.SetFileName(str(path));reader.Update()
    grid=reader.GetOutput()
    points=vtk_to_numpy(grid.GetPoints().GetData()).copy()*length_to_mm
    fields={grid.GetPointData().GetArrayName(i):vtk_to_numpy(grid.GetPointData().GetArray(i)).copy()
            for i in range(grid.GetPointData().GetNumberOfArrays())}
    if not all(np.isfinite(v).all() for v in (points,*fields.values())):
        raise ValueError('Nonfinite native point/field data')
    return points, fields


def map_points(wanted, actual, length_to_mm=1):
    import vtk
    from ..mesh_witness import polydata
    data=polydata(actual,[]);locator=vtk.vtkStaticPointLocator();locator.SetDataSet(data);locator.BuildLocator()
    index=np.array([locator.FindClosestPoint(p) for p in wanted])
    # Early experimental MEDIT version 1 inputs were read as float32. This is
    # a real mesh conversion, not VTU rounding. Permit only that known legacy
    # mapping for diagnostics; current version 2 input preserves doubles.
    quantized=(np.asarray(wanted)/length_to_mm).astype(np.float32).astype(float)*length_to_mm
    error=np.minimum(np.linalg.norm(np.asarray(actual)[index]-wanted,axis=1),
                     np.linalg.norm(np.asarray(actual)[index]-quantized,axis=1))
    if np.max(error)>1e-8:
        raise ValueError('Native output does not preserve input mesh vertices')
    return index


def require_native_rest_mesh(directory, reference, actual):
    version1='MeshVersionFormatted 1' in next(directory.glob('*.mesh')).read_text().splitlines()[0]
    shift=float(np.linalg.norm(actual-reference,axis=1).max())
    if shift>1e-8 and not version1:
        raise ValueError('Double-precision input mesh differs from native rest geometry')
    return dict(maximum_rest_coordinate_shift_mm=shift,
                legacy_single_precision_input=version1,
                qualification_limit='Version 1 conversion invalidates unqualified input-mesh/contact comparisons; retain both geometries' if version1 else None)


def progress_value(points, t):
    points=points or ((0,0),(1,1))
    a,b=next(((a,b) for a,b in zip(points,points[1:]) if t<=b[0]+1e-10),points[-2:])
    return a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0])


def principal_strain(mesh, displacement):
    ids=np.asarray(mesh['tets']);reference=np.asarray(mesh['points_mm'])[ids]
    current=reference+displacement[ids]
    edges=lambda p:np.stack((p[:,1]-p[:,0],p[:,2]-p[:,0],p[:,3]-p[:,0]),axis=2)
    F=edges(current)@np.linalg.inv(edges(reference))
    if np.any(np.linalg.det(F)<=0):
        raise ValueError('Deformed tetrahedron inverted')
    green=(np.swapaxes(F,1,2)@F-np.eye(3))*.5
    return np.linalg.eigvalsh(green)


def require_final_equilibrium_policy(native, tolerance_N, steps, *, dt=None):
    """A bounded intermediate AL search cannot relax final native equilibrium."""
    policy=native['args']['solver']['nonlinear']
    if policy['allow_out_of_iterations'] or policy['allow_non_grad_convergence']:
        raise ValueError('Final native equilibrium must reject iteration-limit/non-gradient completion')
    dt=1/steps if dt is None else dt
    if policy['grad_norm_tol']>tolerance_N*dt**2*(1+1e-10):
        raise ValueError('Effective final native gradient tolerance exceeds the recorded request')


def extract(directory, case, meshes, selections, scene, result, *, partial=False):
    result.provenance['extractor_sha256']=digest(__file__)
    steps=scene['time']['time_steps'];flexible=case['ipc']['deformable'];mesh=meshes[flexible]
    start=scene['time'].get('t0',0);dt=(scene['time']['tend']-start)/steps
    length_to_mm=1000 if scene['units']['length']=='m' else 1
    reference=np.asarray(mesh['points_mm']);tets=np.asarray(mesh['tets'])
    native=json.loads((directory/'native.json').read_text()) if (directory/'native.json').is_file() else None
    if not partial and (not native or native['args']['time']['quasistatic'] is not True):
        raise ValueError('Native quasi-static formulation not confirmed')
    if not partial:
        require_final_equilibrium_policy(native,case['ipc']['gradient_tolerance_N'],steps,dt=dt)
    if native:
        result.provenance['effective_parameters']=native['args']
    forces_peak={name:0. for name in selections};strain_peak=0.;strain_location=None;maximum_balance=0.;intersection=False
    witnesses=[];max_inertia=0.;max_free_residual=0.;contact_detected=False;max_displacement=0.
    constraints=[c for c in case['constraints'] if c['selection']['part']==flexible]
    fixed=np.zeros((len(reference),3),dtype=bool)
    for c in constraints:
        ids=selections[c['name']]['nodes']
        for axis,v in enumerate(c['displacement_mm']):
            if v is not None:fixed[ids,axis]=True
    available=[i for i in range(steps+1) if (directory/f'step_{i}.vtu').is_file()]
    if not available or (not partial and available!=list(range(steps+1))):
        raise ValueError('Incomplete native accepted-state deformation history')
    for i in available:
        time=start+i*dt;points,fields=read_vtu(directory/f'step_{i}.vtu',length_to_mm)
        needed=('solution','elastic_forces','contact_forces','inertia_forces')
        if any(k not in fields for k in needed):
            raise ValueError('Missing native displacement/variational force fields')
        mapping=map_points(reference,points,length_to_mm)
        result.provenance['native_mesh_mapping']=require_native_rest_mesh(directory,reference,points[mapping])
        displacement=fields['solution'][mapping]*length_to_mm
        max_displacement=max(max_displacement,float(np.linalg.norm(displacement,axis=1).max()))
        elastic=fields['elastic_forces'][mapping];contact=fields['contact_forces'][mapping]
        inertia=fields['inertia_forces'][mapping]
        max_inertia=max(max_inertia,float(np.abs(inertia).max()))
        residual=-(elastic+contact);free_norm=float(np.linalg.norm(residual[~fixed]))
        max_free_residual=max(max_free_residual,free_norm)
        principal=principal_strain(mesh,displacement);peak=float(np.abs(principal).max())
        if peak>strain_peak:
            strain_peak=peak;where=np.unravel_index(np.abs(principal).argmax(),principal.shape)
            strain_location=dict(part=flexible,element_index=int(where[0]),reference_centroid_mm=reference[tets[where[0]]].mean(axis=0).tolist(),load_fraction=time)
        reactions={};motion_forces={};observations={};frame_witness={};frame_intersects=False
        contact_points,contact_fields=read_vtu(directory/f'step_{i}_surf_contact.vtu',length_to_mm)
        if 'contact_forces' not in contact_fields or 'solution' not in contact_fields:
            raise ValueError('Missing IPC surface force/deformation history')
        for c in case['constraints']:
            part=c['selection']['part'];name=c['name'];region=c['selection']['region']
            values=np.asarray([v or 0 for v in c['displacement_mm']]);factor=progress_value(c.get('progress'),time)
            if part==flexible:
                ids=selections[name]['nodes'];reaction=np.zeros(3)
                for axis,v in enumerate(c['displacement_mm']):
                    if v is not None:
                        if np.max(np.abs(displacement[ids,axis]-values[axis]*factor))>1e-5:
                            raise ValueError('Accepted support displacement differs from prescribed motion')
                        reaction[axis]=residual[ids,axis].sum()
            else:
                obstacle=meshes[part];op=np.asarray(obstacle['points_mm'])
                ci=map_points(op,contact_points,length_to_mm)
                du=contact_fields['solution'][ci]*length_to_mm
                if np.max(np.abs(du-values*factor))>1e-5:
                    raise ValueError('Accepted obstacle displacement differs from prescribed motion')
                # Collision VTU gradients are exported independently of FE
                # interpolation; validate this force convention on compression.
                reaction=-contact_fields['contact_forces'][ci].sum(axis=0)
                witness=inspect_mesh_pair(reference+displacement,mesh['triangles'],op+du,obstacle['triangles'],
                    search_distance_mm=case['ipc']['activation_distance_mm'])
                frame_witness[part]=witness
                frame_intersects |= witness['intersection_detected']
            reactions[name]=reaction.tolist()
            norm=np.linalg.norm(values)
            curve=c.get('progress') or ((0,0),(1,1))
            a,b=next(((a,b) for a,b in zip(curve,curve[1:]) if time<=b[0]+1e-10),curve[-2:])
            force=float(reaction@values/norm*np.sign(b[1]-a[1])) if norm else 0.
            motion_forces[name]=force;forces_peak[name]=max(forces_peak[name],abs(force))
        # Deduplicate overlapping support DOFs in the balance, matching the
        # stable backend contract. Obstacles have disjoint input vertices.
        total=np.where(fixed,residual,0).sum(axis=0)
        total+=sum((np.asarray(reactions[c['name']]) for c in case['constraints'] if c['selection']['part']!=flexible),np.zeros(3))
        scale=max(1.,sum(np.linalg.norm(v) for v in reactions.values()))
        balance=float(np.linalg.norm(total)/scale);maximum_balance=max(maximum_balance,balance)
        for obs in case['observations']:
            if obs['selection']['part']!=flexible:
                raise ValueError('IPC experiment observations currently require deformable part')
            ids=[j for j,p in enumerate(reference) if contains(obs['selection']['region'],p)]
            if not ids:raise ValueError('Empty IPC observation region')
            us=displacement[ids]
            observations[obs['name']]=dict(min_mm=us.min(axis=0).tolist(),max_mm=us.max(axis=0).tolist(),mean_mm=us.mean(axis=0).tolist())
        active=float(np.abs(contact_fields['contact_forces']).max())>1e-8
        contact_detected|=active;intersection|=frame_intersects
        witnesses.append(dict(load_fraction=time,obstacles=frame_witness))
        result.history.append(dict(load_fraction=time,reactions_N=reactions,motion_force_N=motion_forces,
            max_abs_principal_strain=peak,observations=observations,force_balance_relative=balance,
            free_dof_residual_norm_N=free_norm,native_ipc_force_active=active,
            independent_mesh_intersection=frame_intersects))
    write_json(directory/'geometry_witness.json',dict(frames=witnesses,
        input_sha256=digest(directory/'scene.json'),mesh_sha256=digest(directory/'mesh.json'),
        exact_CAD='Not evaluated globally; straight numerical surface witness only.'))
    result.metrics.update(peak_motion_force_N=forces_peak,max_abs_principal_strain=strain_peak,
        max_strain_by_part={flexible:strain_peak},strain_limits={flexible:next(p['material']['strain_limit'] for p in case['parts'] if p['name']==flexible)},
        peak_strain_location=strain_location,max_force_balance_relative=maximum_balance,
        max_free_dof_residual_norm_N=max_free_residual, max_inertia_force_N=max_inertia,
        max_displacement_mm=max_displacement,max_displacement_scope='Deformable solid across accepted frames; rigid obstacle travel excluded',
        contact_detected=contact_detected,independent_mesh_intersection=intersection,
        observations=result.history[-1]['observations'],native_penetration_mm=None,
        contact_evidence='IPC barrier forces, verified prescribed poses and independent accepted-frame triangle geometry; no native penetration metric fabricated.')
    result.metrics['diagnostic_prefix_only']=partial
    result.metrics['native_operation_completed']=not partial and start==0 and scene['time']['tend']==1
    result.metrics['accepted_time_interval']=[start,result.history[-1]['load_fraction']]
    result.artifacts['geometry_witness']='geometry_witness.json'
    adequate=(not intersection and maximum_balance<.01 and max_inertia<1e-12
              and max_free_residual <= max(1e-5,10*case['ipc']['gradient_tolerance_N']))
    if not partial:
        result.status='completed' if adequate else 'quality_failed';result.completed=adequate
        if not adequate:result.errors.append('IPC accepted-state geometry, equilibrium or quasi-static quality rejected')
