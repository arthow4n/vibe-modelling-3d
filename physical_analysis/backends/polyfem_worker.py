"""Private IPC worker: narrow P1 tetrahedral / translating obstacle experiment."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
from fractions import Fraction
import numpy as np
from .mesh import contains
from ..results import AnalysisResult


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def progress_expression(points):
    """Continuous piecewise-linear expression, including reversals and plateaus."""
    points = points or ((0, 0), (1, 1))
    return '+'.join(f'({(b[1]-a[1])/(b[0]-a[0]):.17g})*min(max(t-({a[0]:.17g}),0),{b[0]-a[0]:.17g})'
                    for a, b in zip(points, points[1:]))


def mesh_geometry(path, size, volume):
    import gmsh
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.option.setNumber('General.NumThreads', 1)
        gmsh.model.add('ipc')
        gmsh.model.occ.importShapes(str(path))
        gmsh.model.occ.synchronize()
        if len(gmsh.model.getEntities(3)) != 1:
            raise ValueError('IPC mesher requires one connected CAD solid')
        gmsh.option.setNumber('Mesh.MeshSizeMin', size)
        gmsh.option.setNumber('Mesh.MeshSizeMax', size)
        gmsh.option.setNumber('Mesh.ElementOrder', 1)
        gmsh.model.mesh.generate(3 if volume else 2)
        tags, coords, _ = gmsh.model.mesh.getNodes()
        points = np.asarray(coords).reshape(-1, 3)
        lookup = {int(t): i for i, t in enumerate(tags)}
        def elements(dim, kind, width):
            kinds, ids, conn = gmsh.model.mesh.getElements(dim)
            if list(kinds) != [kind]:
                raise ValueError(f'Unsupported IPC mesh element types: {kinds}')
            return np.array([[lookup[int(n)] for n in row] for row in np.asarray(conn[0]).reshape(-1, width)])
        surface = elements(2, 2, 3)
        tets = elements(3, 4, 4) if volume else np.empty((0, 4), dtype=int)
        if volume:
            p = points[tets]
            determinants = np.linalg.det(np.stack((p[:,1]-p[:,0], p[:,2]-p[:,0], p[:,3]-p[:,0]), axis=2))
            if np.any(determinants <= 0):
                raise ValueError('Non-positive linear tetrahedron Jacobian')
        return dict(points_mm=points.tolist(), triangles=surface.tolist(), tets=tets.tolist())
    finally:
        gmsh.finalize()


def write_mesh(path, mesh, scale):
    # libMeshb version 1 reads coordinates as float32, even in ASCII. IPC gaps
    # can be smaller than that rounding. Version 2 preserves double precision.
    lines = ['MeshVersionFormatted 2', 'Dimension 3', 'Vertices', str(len(mesh['points_mm']))]
    lines += [' '.join(f'{x*scale:.17g}' for x in p)+' 0' for p in mesh['points_mm']]
    lines += ['Tetrahedra', str(len(mesh['tets']))]
    lines += [' '.join(str(n+1) for n in row)+' 1' for row in mesh['tets']]
    lines += ['End']
    path.write_text('\n'.join(lines)+'\n')


def write_obj(path, mesh, scale):
    lines = ['v '+' '.join(f'{x*scale:.17g}' for x in p) for p in mesh['points_mm']]
    lines += ['f '+' '.join(str(n+1) for n in row) for row in mesh['triangles']]
    path.write_text('\n'.join(lines)+'\n')


def compile_scene(case, directory):
    settings = case['ipc']; flexible = settings['deformable']
    scale = .001 if settings['unit_system']=='SI' else 1.
    meshes = {}; geometry = []; bcs = []; obstacles = []; selections = {}
    offset = np.array(settings['initial_offset_mm'])
    reused=json.loads((directory/'mesh_source.json').read_text())['parts'] if case.get('mesh_reuse') else None
    for index, part in enumerate(case['parts']):
        volume = part['name'] == flexible
        size = part['mesh_size_mm'] if volume else settings['obstacle_mesh_size_mm'] or part['mesh_size_mm']
        mesh = reused[part['name']] if reused else mesh_geometry(directory/part['geometry'], size, volume)
        points = np.array(mesh['points_mm']); triangles = np.array(mesh['triangles'])
        if volume:
            surface_selections = []
            constrained_nodes = set()
            # Compile node-region supports to whole-face boundary tags and verify
            # equality. Interior-only constraints must not silently disappear.
            for ci, constraint in enumerate(case['constraints'], 1):
                if constraint['selection']['part'] != flexible:
                    continue
                region = constraint['selection']['region']
                ids = {i for i, p in enumerate(points) if contains(region, p)}
                faces = [tri for tri in triangles if all(int(n) in ids for n in tri)]
                covered = {int(n) for tri in faces for n in tri}
                if not ids or covered != ids:
                    raise ValueError('IPC support region must select complete boundary faces; interior node constraints unsupported')
                if ids & constrained_nodes:
                    raise ValueError('IPC overlapping support regions unsupported')
                constrained_nodes.update(ids)
                selections[constraint['name']] = dict(nodes=sorted(ids), **constraint)
                lo = points.min(axis=0)-1; hi = points.max(axis=0)+1
                tol = region['tolerance_mm']
                lo = [max(a, v-tol) if v is not None else a for a,v in zip(lo,region['lower'])]
                hi = [min(a, v+tol) if v is not None else a for a,v in zip(hi,region['upper'])]
                surface_selections.append(dict(id=ci,box=(np.array([lo,hi])*scale).tolist(),relative=False))
                values = constraint['displacement_mm']; expression = progress_expression(constraint.get('progress'))
                bcs.append(dict(id=ci, dimension=[v is not None for v in values],
                    value=[f'({v*scale:.17g})*({expression})' if v else 0 for v in values]))
            if not bcs:
                raise ValueError('IPC deformable needs an explicit support')
            mesh_path = f'part_{index}.mesh'; write_mesh(directory/mesh_path, mesh, scale)
            geometry.append(dict(mesh=mesh_path,surface_selection=surface_selections,volume_selection=1,
                                 advanced=dict(normalize_mesh=False)))
        else:
            regions = [s['region'] for contact in case['contacts'] for s in
                (contact['master'] if isinstance(contact['master'], list) else [contact['master']]) if s['part']==part['name']]
            if not reused:
                mesh['triangles'] = [tri.tolist() for tri in triangles if any(all(contains(r, points[n]) for n in tri) for r in regions)]
            if not mesh['triangles']:
                raise ValueError('Empty IPC obstacle contact surface')
            # Remove unreferenced vertices: OBJ codimensional points also collide.
            used = sorted({n for tri in mesh['triangles'] for n in tri}); lookup = {n:i for i,n in enumerate(used)}
            mesh['points_mm'] = (points[used]+(0 if reused else offset)).tolist()
            mesh['triangles'] = [[lookup[n] for n in tri] for tri in mesh['triangles']]
            mesh_path = f'part_{index}.obj'; write_obj(directory/mesh_path, mesh, scale)
            ident = 1000+index
            geometry.append(dict(mesh=mesh_path,is_obstacle=True,surface_selection=ident,
                                 advanced=dict(normalize_mesh=False)))
            constraint = next(c for c in case['constraints'] if c['selection']['part']==part['name'])
            expression = progress_expression(constraint.get('progress'))
            obstacles.append(dict(id=ident,value=[f'({v*scale:.17g})*({expression})' if v else 0 for v in constraint['displacement_mm']]))
            selections[constraint['name']] = dict(nodes=list(range(len(mesh['points_mm']))), **constraint)
        meshes[part['name']] = mesh
    mat = next(p['material'] for p in case['parts'] if p['name']==flexible)
    knot_multiple=math.lcm(*(Fraction(str(t)).denominator for c in case['constraints']
        for t,_ in (c.get('progress') or ((0,0),(1,1)))))
    steps=math.ceil(math.ceil(1/case['max_increment'])/knot_multiple)*knot_multiple
    if steps>10000:
        raise ValueError('IPC uniform time grid cannot represent motion knots within 10000 steps')
    nonlinear=dict(grad_norm_tol=settings['gradient_tolerance_N']/steps**2,x_delta_tol=0,
                   rel_grad_norm_tol=0, norm_type='Euclidean', max_iterations=settings['max_iterations'],
                   Newton=dict(force_psd_projection=settings['projected_newton']))
    al_weight=settings['constraint_initial_weight']
    # AL is a nonphysical boundary-feasibility search. This opt-in diagnostic
    # checks projection feasibility after bounded subsolves instead of requiring
    # full AL equilibrium first. Final reduced-space equilibrium still rejects
    # iteration limits and must satisfy the unchanged accepted-state checks.
    al_nonlinear=dict(nonlinear)
    if settings['bounded_feasibility_search']:
        al_nonlinear.update(max_iterations=min(50,settings['max_iterations']),allow_out_of_iterations=True)
    nonlinear['allow_out_of_iterations']=False
    scene = dict(units=dict(length='m' if scale==.001 else 'mm',mass='kg' if scale==.001 else 'tonne',time='s',
                           characteristic_length=steps),geometry=geometry,
        materials=dict(type='SaintVenant',E=mat['youngs_modulus_MPa']/scale**2,nu=mat['poisson_ratio'],rho=1200 if scale==.001 else 1.2e-9),
        space=dict(discr_order=1),time=dict(tend=1,time_steps=steps,quasistatic=True),
        boundary_conditions=dict(rhs=[0,0,0],dirichlet_boundary=bcs,obstacle_displacements=obstacles),
        contact=dict(enabled=True,dhat=settings['activation_distance_mm']*scale,friction_coefficient=0,
                     use_convergent_formulation=settings['convergent_barrier']),
        solver=dict(linear=dict(solver='Eigen::SimplicialLDLT'),
                    nonlinear=nonlinear,augmented_lagrangian=dict(nonlinear=al_nonlinear,
                        initial_weight=al_weight,max_weight=al_weight*1e4),
                    contact=dict(CCD=dict(tolerance=settings['ccd_tolerance_mm']*scale,max_iterations=1000000))),
        output=dict(json='native.json',stats=True,paraview=dict(file_name='state.vtu',high_order_mesh=True,
                    vismesh_rel_area=1,
                    volume=True,surface=False,options=dict(forces=True,contact_forces=True,
                        scalar_values=False,tensor_values=False)),
                    data=dict(advanced=dict(reorder_nodes=True))))
    write_json(directory/'mesh.json',dict(parts=meshes,selections=selections,steps=steps))
    write_json(directory/'scene.json',scene)
    return meshes, selections, scene


def main():
    directory = Path(sys.argv[1]); case = json.loads((directory/'case.json').read_text())
    if '--postprocess-only' in sys.argv:
        from .polyfem_output import recover
        recover(directory)
        return
    r = AnalysisResult(case['name'], 'preparing', assumptions=[
        f"Experimental IPC; native {case['ipc']['unit_system']} mapping; mm/N/MPa metrics.",
        'Incremental quasi-static equilibrium, zero body force, frictionless SaintVenant homogeneous elasticity.',
        'P1 tetrahedra and straight collision triangles, not exact CAD surfaces; mesh refinement required.',
        'All deformable exterior triangles collide; rigid obstacle surfaces follow explicit master selections.',
        'Numerical elastic results do not validate printed material, bonding, friction, creep or wear.'])
    r.provenance = dict(backend='PolyFEM-IPC-experimental',case_sha256=digest(directory/'case.json'),
        backend_sha256=implementation_identity())
    stage='initializing'
    try:
        executable = shutil.which(os.environ['POLYFEM_COMMAND'])
        if not executable:
            raise FileNotFoundError('Set POLYFEM_COMMAND to the external native PolyFEM CLI executable')
        r.provenance.update(executable=str(Path(executable).resolve()),executable_sha256=digest(executable),
            polyfem_commit=os.environ.get('POLYFEM_COMMIT','not exposed'),ipc_settings=case['ipc'])
        if case.get('mesh_reuse'):r.provenance['mesh_reuse']=case['mesh_reuse']
        stage='meshing_and_input'
        meshes, selections, scene = compile_scene(case,directory)
        r.provenance.update(input_sha256=digest(directory/'scene.json'),mesh_sha256=digest(directory/'mesh.json'),
            mesh_files_sha256={p.name:digest(p) for p in directory.iterdir() if p.suffix in ('.obj','.mesh')},
            geometry_sha256={p['name']:p['sha256'] for p in case['parts']},
            unit_mapping=dict(length_mm_to_native=.001 if case['ipc']['unit_system']=='SI' else 1,
                stress_MPa_to_native=1e6 if case['ipc']['unit_system']=='SI' else 1,force_N_to_native=1),
            formulation='P1 SaintVenant, time.quasistatic=true',versions=dict(python=sys.version.split()[0]))
        import gmsh
        r.provenance['versions']['gmsh'] = gmsh.__version__
        from importlib.metadata import version
        r.provenance['versions'].update({name:version(name) for name in ('numpy','vtk','cadquery','cadquery-ocp')})
        write_json(directory/'run_metadata.json',r.provenance)
        from ..mesh_witness import inspect_mesh_pair
        flexible=case['ipc']['deformable'];fm=meshes[flexible]
        initial={name:inspect_mesh_pair(fm['points_mm'],fm['triangles'],m['points_mm'],m['triangles'],
            search_distance_mm=case['ipc']['activation_distance_mm']) for name,m in meshes.items() if name!=flexible}
        write_json(directory/'initial_geometry_witness.json',initial)
        if any(w['intersection_detected'] for w in initial.values()):
            r.status='invalid_initial_contact'
            r.errors.append('IPC initial numerical surfaces intersect/touch; no hidden initial adjustment applied')
            r.write(directory/'answer.json')
            return
        command=[executable,'--json','scene.json','--max_threads','1']
        r.provenance['command']=command
        stage='native_solve'
        with (directory/'solver.log').open('w') as log:
            native=subprocess.run(command,cwd=directory,stdout=log,stderr=subprocess.STDOUT)
        r.provenance['native_exit_code']=native.returncode
        write_json(directory/'run_metadata.json',r.provenance)
        if native.returncode:
            r.status='solver_failed';r.errors.append((directory/'solver.log').read_text()[-4000:])
            from .polyfem_output import extract
            extract(directory,case,meshes,selections,scene,r,partial=True)
        else:
            stage='extraction'
            from .polyfem_output import extract
            extract(directory,case,meshes,selections,scene,r)
    except Exception as exc:
        if r.status!='solver_failed':
            r.status='extraction_failed' if stage=='extraction' else 'failed'
        r.errors.append(f'{stage}: {type(exc).__name__}: {exc}')
    r.artifacts.update(input='scene.json',mesh='mesh.json',solver_log='solver.log')
    r.write(directory/'answer.json')


def implementation_identity():
    paths=[Path(__file__).with_name(name) for name in ('polyfem.py','polyfem_worker.py','polyfem_output.py',
        'polyfem_diagnostics.py','contact_diagnostics.py','mesh.py')]
    paths.append(Path(__file__).parents[1]/'mesh_witness.py')
    return hashlib.sha256(b''.join(p.read_bytes() for p in paths)).hexdigest()


if __name__=='__main__':
    main()
