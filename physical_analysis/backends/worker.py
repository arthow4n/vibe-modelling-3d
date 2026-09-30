"""Private process entry point. Retains input deck and raw solver evidence."""
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import numpy as np
import cadquery as cq
from ..results import AnalysisResult


def chunks(values, count=12):
    return [','.join(map(str,values[i:i+count])) for i in range(0,len(values),count)]


def saved_meshes(case, path):
    """Read NODE/C3D10 records from our own generated deck, not arbitrary decks.

    Reprocessing must use the original node/element IDs. Remeshing can differ
    even with unchanged geometry. compile_case still requires byte-identical
    regenerated input before old fields are accepted.
    """
    from .mesh import exterior_faces
    meshes={}; group=None; mode=None
    for line in path.read_text().splitlines():
        if line.startswith('*NODE') and line=='*NODE':
            mode='nodes'; group=dict(nodes={},elements={},min_jacobian=None)
        elif line.startswith('*ELEMENT,TYPE=C3D10,ELSET=P'):
            index=int(line.split('ELSET=P')[1])
            if index>=len(case['parts']) or group is None:
                raise ValueError('Unrecognized saved mesh part')
            meshes[case['parts'][index]['name']]=group;mode='elements'
        elif line.startswith('*'):
            mode=None
        elif mode=='nodes':
            fields=line.split(',');group['nodes'][int(fields[0])]=[float(v) for v in fields[1:]]
        elif mode=='elements':
            fields=[int(v) for v in line.split(',')];group['elements'][fields[0]]=fields[1:]
    if set(meshes)!={p['name'] for p in case['parts']}:
        raise ValueError('Saved input does not contain all case meshes')
    for mesh in meshes.values():
        if not mesh['nodes'] or any(len(c)!=10 for c in mesh['elements'].values()):
            raise ValueError('Saved input needs complete C3D10 meshes')
        mesh['surface']=exterior_faces(mesh['elements'])
    return meshes


def compile_case(case, directory, *, expected_input_sha256=None):
    from .mesh import mesh_part, select_nodes, select_faces, traction_weights
    meshes={}; nodes={}; elements={}; deck=['*HEADING', case['name']]; selections={}
    original=saved_meshes(case,directory/'analysis.inp') if expected_input_sha256 is not None else None
    reuse=case.get('mesh_reuse')
    if reuse:
        for key,name in (('input_sha256',reuse['input']),('case_sha256',reuse['case'])):
            if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=reuse[key]:
                raise ValueError('Copied mesh source identity differs')
        if original is None:
            original=saved_meshes(case,directory/reuse['input'])
    for i,part in enumerate(case['parts']):
        if original is None:
            ns,es,surface,jac = mesh_part(directory/part['geometry'],part['mesh_size_mm'],
                                         max(nodes,default=0),max(elements,default=0))
        else:
            m=original[part['name']]
            ns,es,surface,jac=m['nodes'],m['elements'],m['surface'],None
            if reuse: jac=reuse['mesh'].get(part['name'],{}).get('min_jacobian')
        meshes[part['name']]=dict(nodes=ns,elements=es,surface=surface,min_jacobian=jac)
        nodes.update(ns); elements.update(es)
        deck+=['*NODE']+[f'{n},'+','.join(f'{v:.12g}' for v in p) for n,p in ns.items()]
        deck += [f'*ELEMENT,TYPE=C3D10,ELSET=P{i}'] + [f'{e},'+','.join(map(str,con)) for e,con in es.items()]
        mat=part['material']
        deck += [f'*MATERIAL,NAME=M{i}', '*ELASTIC',
                 f"{mat['youngs_modulus_MPa']},{mat['poisson_ratio']}",
                 f'*SOLID SECTION,ELSET=P{i},MATERIAL=M{i}']
    deck+=['*NSET,NSET=ALLN']+chunks(list(nodes))
    deck+=['*ELSET,ELSET=ALLE']+chunks(list(elements))
    constraints={}; boundary=[]
    for i,c in enumerate(case['constraints']):
        ns=select_nodes(c['selection'],meshes)
        name=c['name']
        selections[name]=dict(part=c['selection']['part'],nodes=ns,displacement_mm=c['displacement_mm'],progress=c.get('progress'))
        if c.get('progress'):
            deck += [f'*AMPLITUDE,NAME=A{i}']+[f'{t:.12g},{v:.12g}' for t,v in c['progress']]
        boundary.append('*BOUNDARY'+(f',AMPLITUDE=A{i}' if c.get('progress') else ''))
        deck += [f'*NSET,NSET=BC{i}']+chunks(ns)
        for n in ns:
            for dof,value in enumerate(c['displacement_mm'],1):
                if value is None: continue
                key=(n,dof)
                signature=(value,c.get('progress') if value else None)
                if key in constraints and constraints[key] != signature:
                    raise ValueError(f'Conflicting constraints at node {n}, DOF {dof}')
                if key not in constraints:
                    boundary.append(f'{n},{dof},{dof},{value:.12g}')
                constraints[key]=signature
    loads=defaultdict(float); load_records=[]
    for load in case['loads']:
        faces=select_faces(load['selection'],meshes)
        weights,area=traction_weights(faces,nodes)
        for n,w in weights.items():
            for dof,force in enumerate(load['force_N'],1):
                loads[n,dof]+=w*force
        load_records.append(dict(part=load['selection']['part'],area_mm2=area,force_N=load['force_N']))
    contact_records=[]
    for i,c in enumerate(case['contacts']):
        record={}
        for side in ('slave','master'):
            faces=select_faces(c[side],meshes)
            name=f'C{i}{side.upper()}'
            deck += [f'*SURFACE,NAME={name},TYPE=ELEMENT']+[f'{e},S{s}' for e,s,_ in faces]
            record[side]=dict(part=c[side]['part'],face_count=len(faces))
        contact_type = {'node_to_surface': 'NODE TO SURFACE', 'surface_to_surface': 'SURFACE TO SURFACE'}[c.get('discretization', 'node_to_surface')]
        record['discretization'] = c.get('discretization', 'node_to_surface')
        record['pairing_update'] = ('once_per_increment' if record['discretization']=='surface_to_surface'
                                    else 'per_iteration_until_iteration_eight_then_frozen')
        deck += [f'*SURFACE INTERACTION,NAME=I{i}', '*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR',
                 f"{c['penalty_N_mm3']},1e-10",
                 f'*CONTACT PAIR,INTERACTION=I{i},TYPE={contact_type}',f'C{i}SLAVE,C{i}MASTER']
        contact_records.append(record)
    deck += ['*STEP'+(',NLGEOM' if case['nonlinear'] else '')+',INC=1000','*STATIC',
             f"{case['max_increment']},1,1e-6,{case['max_increment']}"]+boundary
    if loads:
        deck+=['*CLOAD']+[f'{n},{d},{v:.12g}' for (n,d),v in loads.items() if abs(v)>1e-14]
    deck += ['*NODE PRINT,NSET=ALLN,FREQUENCY=1','U,RF','*EL PRINT,ELSET=ALLE,FREQUENCY=1','S,E']
    if case['contacts']:
        deck += ['*CONTACT PRINT,FREQUENCY=1','CDIS,CSTR']
    deck += ['*END STEP']
    for obs in case['observations']:
        selections['@observe:'+obs['name']]=dict(part=obs['selection']['part'],nodes=select_nodes(obs['selection'],meshes),displacement_mm=(None,None,None))
    input_text='\n'.join(deck)+'\n'
    if expected_input_sha256 is not None:
        if hashlib.sha256(input_text.encode()).hexdigest()!=expected_input_sha256:
            raise ValueError('Regenerated input differs from saved input; cannot reuse solver fields')
    else:
        (directory/'analysis.inp').write_text(input_text)
    return meshes,nodes,elements,selections,load_records,contact_records


HEADER = re.compile(r'^\s*(displacements|forces|stresses|strains|relative contact displacement|contact stress)\s+.*?time\s+([\d.Ee+\-]+)')


FORTRAN_EXPONENT = re.compile(r'^([+-]?(?:\d+\.\d*|\.\d+))([+-]\d+)$')


def solver_number(value):
    # CalculiX's fixed-width Fortran output omits E for three-digit exponents,
    # e.g. 3.732985-100 after an elastic return. Keep every field, including these
    # tiny residuals, so completeness checks remain meaningful.
    return float(FORTRAN_EXPONENT.sub(r'\1E\2', value.replace('D', 'E')))


def iter_dat(path):
    """Yield one time frame at a time; memory does not grow with increments."""
    frame={}; kind=None; time=None
    with path.open() as source:
        for line in source:
            match=HEADER.match(line)
            if match:
                new_time=solver_number(match[2])
                if time is not None and new_time!=time:
                    if new_time<time: raise ValueError('Solver output times are not increasing')
                    yield time,frame
                    frame={}
                kind,time=match[1],new_time
                frame[kind]=[]
                continue
            fields=line.split()
            if not fields: continue
            if kind and fields[0].isdigit():
                try: row=[solver_number(x) for x in fields]
                except ValueError: kind=None; continue
                expected=4 if kind in ('displacements','forces') else (5 if kind in ('relative contact displacement','contact stress') else 8)
                if kind in ('relative contact displacement','contact stress') and len(row)==4:
                    row=[row[0],0,*row[1:]]
                if len(row)==expected:
                    frame[kind].append(row)
                else: kind=None
            else:
                kind=None
    if time is not None: yield time,frame


def parse_dat(path):
    """Compatibility table reader; the solver worker uses streaming iter_dat."""
    return dict(iter_dat(path))


def tensor(values):
    # CalculiX E reports tensor shear strain (not engineering shear).
    xx,yy,zz,xy,xz,yz=values
    return np.array([[xx,xy,xz],[xy,yy,yz],[xz,yz,zz]])


def summarize(case, frames, meshes, nodes, elements, selections):
    history=[]; part_for_element={e:name for name,m in meshes.items() for e in m['elements']}
    peak_strain=(-1,None,None,None); peak_stress=0
    part_strains={p['name']:0.0 for p in case['parts']}
    for time,frame in sorted(frames.items()) if isinstance(frames,dict) else frames:
        for field in ('displacements','forces','stresses','strains'):
            if not frame.get(field): raise ValueError(f'Missing {field} at load fraction {time}')
        us={int(r[0]):np.array(r[1:]) for r in frame['displacements']}
        forces={int(r[0]):np.array(r[1:]) for r in frame['forces']}
        if set(us)!=set(nodes) or set(forces)!=set(nodes):
            raise ValueError('Incomplete nodal output')
        for kind in ('strains','stresses'):
            expected={(e,ip) for e in elements for ip in range(1,5)}
            actual={(int(r[0]),int(r[1])) for r in frame[kind]}
            if actual!=expected: raise ValueError(f'Incomplete integration-point {kind}')
        if not all(np.isfinite(np.asarray(rows)).all() for rows in frame.values()):
            raise ValueError('Non-finite solver output')
        reactions={}
        observations={}
        motion_forces={}
        for name,sel in selections.items():
            if name.startswith('@observe:'):
                samples=np.array([us[n] for n in sel['nodes']])
                observations[name[9:]]=dict(min_mm=samples.min(axis=0).tolist(),max_mm=samples.max(axis=0).tolist(),mean_mm=samples.mean(axis=0).tolist())
                continue
            total=np.sum([forces[n] for n in sel['nodes']],axis=0)
            reactions[name]=[float(v) if sel['displacement_mm'][d] is not None else 0.0 for d,v in enumerate(total)]
            motion=np.array([v or 0 for v in sel['displacement_mm']])
            if np.linalg.norm(motion)>0:
                direction=1
                if sel.get('progress'):
                    points=sel['progress']
                    a,b=next(((a,b) for a,b in zip(points,points[1:]) if time<=b[0]+1e-9),(points[-2],points[-1]))
                    direction=float(np.sign(b[1]-a[1]))
                motion_forces[name]=direction*float(np.dot(total,motion)/np.linalg.norm(motion))
        max_displacement=max(float(np.linalg.norm(u)) for u in us.values())
        strain_rows=np.asarray(frame['strains'])
        values=strain_rows[:,2:]
        tensors=np.empty((len(values),3,3))
        tensors[:,0,0],tensors[:,1,1],tensors[:,2,2]=values[:,0],values[:,1],values[:,2]
        tensors[:,0,1]=tensors[:,1,0]=values[:,3]
        tensors[:,0,2]=tensors[:,2,0]=values[:,4]
        tensors[:,1,2]=tensors[:,2,1]=values[:,5]
        principal=np.max(np.abs(np.linalg.eigvalsh(tensors)),axis=1)
        peak=int(np.argmax(principal)); frame_strain=float(principal[peak])
        parts=np.array([part_for_element[int(e)] for e in strain_rows[:,0]])
        for part in part_strains:
            part_strains[part]=max(part_strains[part],float(principal[parts==part].max()))
        if frame_strain>peak_strain[0]:
            row=strain_rows[peak]
            peak_strain=(frame_strain,part_for_element[int(row[0])],int(row[0]),int(row[1]))
        stress=np.asarray(frame['stresses'])[:,2:]
        vm=np.sqrt(((stress[:,0]-stress[:,1])**2+(stress[:,1]-stress[:,2])**2+
                    (stress[:,2]-stress[:,0])**2)/2+3*np.sum(stress[:,3:]**2,axis=1))
        peak_stress=max(peak_stress,float(vm.max()))
        prescribed={(n,d) for sel in selections.values() for n in sel['nodes']
                    for d,v in enumerate(sel['displacement_mm']) if v is not None}
        net=np.zeros(3)
        for n,d in prescribed: net[d]+=forces[n][d]
        applied=time*np.sum([x['force_N'] for x in case['loads']],axis=0) if case['loads'] else np.zeros(3)
        residual=float(np.linalg.norm(net+applied))
        reference=max(float(np.linalg.norm(applied)),sum(float(np.linalg.norm(v)) for v in reactions.values()),1)
        history.append(dict(load_fraction=time,max_displacement_mm=max_displacement,
                            force_balance_residual_N=residual,force_balance_relative=residual/reference,
                            max_abs_principal_strain=frame_strain,reactions_N=reactions,observations=observations,motion_force_N=motion_forces,
                            contact_points=len(frame.get('contact stress',[])),
                            max_contact_pressure_MPa=max((r[2] for r in frame.get('contact stress',[])),default=0),
                            max_penetration_mm=max((max(0,-r[2]) for r in frame.get('relative contact displacement',[])),default=0)))
    if not history: raise ValueError('Missing solver output frames')
    last=history[-1]
    # Internal nodal forces cancel globally. Only prescribed DOFs are reactions.
    force_map=forces
    prescribed={(n,d) for sel in selections.values() for n in sel['nodes']
                for d,v in enumerate(sel['displacement_mm']) if v is not None}
    reaction=np.zeros(3)
    for n,d in prescribed: reaction[d]+=force_map[n][d]
    applied=np.sum([x['force_N'] for x in case['loads']],axis=0) if case['loads'] else np.zeros(3)
    residual=float(np.linalg.norm(reaction+applied))
    ref=max(float(np.linalg.norm(applied)),sum(float(np.linalg.norm(v)) for v in last['reactions_N'].values()),1)
    metrics=dict(max_displacement_mm=last['max_displacement_mm'],
        max_abs_principal_strain=peak_strain[0],max_strain_part=peak_strain[1],
        max_strain_element=peak_strain[2],max_strain_integration_point=peak_strain[3],
        max_strain_element_centroid_mm=np.mean([nodes[n] for n in elements[peak_strain[2]][:4]],axis=0).tolist(),
        max_von_mises_MPa=peak_stress, max_strain_by_part=part_strains, force_balance_residual_N=residual,
        force_balance_relative=residual/ref,
        max_force_balance_relative=max(h['force_balance_relative'] for h in history),
        peak_reaction_force_N={name:max(float(np.linalg.norm(h['reactions_N'][name])) for h in history)
                               for name in last['reactions_N']},
        observations=last['observations'],
        peak_motion_force_N={name:max(abs(h['motion_force_N'][name]) for h in history) for name in last['motion_force_N']},
        strain_limits={p['name']:p['material']['strain_limit'] for p in case['parts']},
        contact_detected=any(h['max_contact_pressure_MPa']>1e-8 for h in history) if case['contacts'] else None,
        max_penetration_mm=max(h['max_penetration_mm'] for h in history))
    return metrics,history


def main(directory, *, postprocess_only=False):
    import gmsh
    # Snapshot implementation identity before the long native solve. Hashing
    # afterward can incorrectly attribute edits made while the solver runs.
    backend_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}
    case=json.loads((directory/'case.json').read_text())
    result=AnalysisResult(case['name'],'failed',assumptions=[
        'Units mm, N, MPa. Isotropic homogeneous linear-elastic material; geometric nonlinearity='+str(case['nonlinear']),
        'No printed infill/layer failure, plastic set, creep, fatigue, or friction prediction.',
        'Strain is maximum absolute principal mechanical strain at integration points, over all saved increments.',
        'Frictionless penalty contact. Surface-to-surface pairing is fixed within each increment; node-to-surface re-pairs through iteration eight then freezes. Completion alone does not prove engagement.',
        'Loads ramp over normalized time 0..1; translations follow their recorded progress curves or a linear ramp.',
        'Peak values are sampled at converged increments, not continuous extrema.'])
    # Recovery from a parser failure may reuse a completed expensive solve.
    # Use the saved mesh and regenerate a byte-identical deck before
    # attaching old node/element fields to the current extractor.
    expected=hashlib.sha256((directory/'analysis.inp').read_bytes()).hexdigest() if postprocess_only else None
    meshes,nodes,elements,selections,loads,contacts=compile_case(case,directory,expected_input_sha256=expected)
    env=os.environ.copy(); command=[env['CALCULIX_COMMAND'],'-i','analysis']
    if not postprocess_only:
        with (directory/'solver.log').open('w') as log:
            run=subprocess.run(command,cwd=directory,env=env,stdout=log,stderr=subprocess.STDOUT)
        solver_exit=run.returncode
    else:
        solver_exit=0  # completion/errors are checked from the immutable saved log below
    log=(directory/'solver.log').read_text(errors='replace')
    version=re.search(r'This is Version\s+(\S+)',log)
    (directory/'regions.json').write_text(json.dumps(selections,indent=2)+'\n')
    result.provenance=dict(backend='CalculiX',version=version[1] if version else 'unknown',
        gmsh=gmsh.__version__,cadquery=cq.__version__,python=sys.version.split()[0],
        input_sha256=hashlib.sha256((directory/'analysis.inp').read_bytes()).hexdigest(),
        case_sha256=hashlib.sha256((directory/'case.json').read_bytes()).hexdigest(),
        backend_sha256=backend_hashes,
        command=command,postprocess_only=postprocess_only,mesh={name:dict(nodes=len(m['nodes']),elements=len(m['elements']),
                   min_jacobian=m['min_jacobian']) for name,m in meshes.items()},
        regions={k:dict(part=v['part'],node_count=len(v['nodes']),displacement_mm=v['displacement_mm']) for k,v in selections.items()},loads=loads,contacts=contacts)
    if case.get('mesh_reuse'): result.provenance['mesh_reuse']=case['mesh_reuse']
    result.artifacts=dict(case='case.json',input='analysis.inp',solver_log='solver.log',
                          raw_results='analysis.dat',increments='analysis.sta',regions='regions.json')
    lines=log.splitlines()
    result.warnings=[]
    for i,line in enumerate(lines):
        if '*WARNING' in line.upper():
            block=[line.strip()]
            for extra in lines[i+1:i+7]:
                if not extra.strip() or extra.startswith(' *'): break
                block.append(extra.strip())
            result.warnings.append(' '.join(block))
    if solver_exit != 0 or '*ERROR' in log.upper() or 'Job finished' not in log or 'parameter not recognized' in log.lower():
        result.errors.append(f'Solver failed or did not finish (exit {solver_exit}); see solver.log')
    else:
        metrics,history=summarize(case,iter_dat(directory/'analysis.dat'),meshes,nodes,elements,selections)
        if abs(history[-1]['load_fraction']-1)>1e-6:
            result.errors.append('Requested load interval did not complete')
        else:
            result.metrics,result.history=metrics,history
            limit=min((c['penetration_limit_mm'] for c in case['contacts']),default=float('inf'))
            if result.metrics['max_penetration_mm']>limit:
                result.status='quality_failed'
                result.errors.append(f'Contact penetration exceeds {limit:g} mm; refine increments/mesh/contact penalty')
            elif result.metrics['max_force_balance_relative']>.01:
                result.errors.append('Force balance residual exceeds 1% at a saved increment')
            else:
                result.completed=True
                result.status='completed_with_warnings' if result.warnings else 'completed'
    result.write(directory/'answer.json')

if __name__=='__main__':
    if len(sys.argv) not in (2,3) or (len(sys.argv)==3 and sys.argv[2]!='--postprocess-only'):
        raise SystemExit('Usage: worker DIRECTORY [--postprocess-only]')
    main(Path(sys.argv[1]),postprocess_only=len(sys.argv)==3)
