"""Experimental motion/contact worker; all FEBio XML stays behind the API."""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
from execution.telemetry import operation
from execution.process import run as run_command
import sys
import xml.etree.ElementTree as ET
import numpy as np
from importlib.metadata import version as package_version
from ..results import AnalysisResult
from .worker import compile_case


def add(parent, tag, value=None, **attributes):
    child=ET.SubElement(parent,tag,{k:str(v) for k,v in attributes.items()})
    if value is not None: child.text=str(value)
    return child


@operation('analysis.native_input')
def compile_xml(case, directory, meshes, nodes, selections):
    from .mesh import select_faces
    root=ET.Element('febio_spec',version='4.0')
    add(root,'Module',type='solid')
    control=add(root,'Control')
    add(control,'analysis','STATIC')
    add(control,'time_steps',math.ceil(1/case['max_increment']))
    add(control,'step_size',1/math.ceil(1/case['max_increment']))
    solver=add(control,'solver')
    residual_floor=case['febio'].get('force_residual_tolerance_N',1e-6)**2
    for key,value in dict(max_refs=30,dtol=.001,etol=.01,rtol=0,min_residual=residual_floor,
                          reform_each_time_step=1,symmetric_stiffness=0).items():add(solver,key,value)
    add(add(solver,'qn_method',type='BFGS'),'max_ups',0)
    stepper=add(control,'time_stepper')
    for key,value in dict(dtmin=1e-6,dtmax=case['max_increment'],max_retries=10,opt_iter=10).items():add(stepper,key,value)
    material=add(root,'Material')
    for i,part in enumerate(case['parts'],1):
        mat=add(material,'material',id=i,name=part['name'],type='isotropic elastic')
        add(mat,'E',part['material']['youngs_modulus_MPa']);add(mat,'v',part['material']['poisson_ratio'])
    mesh=add(root,'Mesh')
    ns=add(mesh,'Nodes',name='all')
    for n,p in nodes.items():add(ns,'node',','.join(f'{v:.12g}' for v in p),id=n)
    domains=ET.Element('MeshDomains')
    for part in case['parts']:
        name=part['name'];es=add(mesh,'Elements',type='TET10G8_S7',name=name)
        for e,con in meshes[name]['elements'].items():add(es,'elem',','.join(map(str,con)),id=e)
        add(domains,'SolidDomain',name=name,mat=name)
    boundary=ET.Element('Boundary');curves=ET.Element('LoadData');used={}
    for i,c in enumerate(case['constraints'],1):
        curve_id=len(curves)+1
        name=c['name'];selected=selections[name]['nodes']
        for d,value in enumerate(c['displacement_mm']):
            if value is None:continue
            ids=[];signature=(value,c.get('progress') if value else None)
            for n in selected:
                key=(n,d)
                if key in used:
                    if used[key]!=signature:raise ValueError('Conflicting FEBio constraints')
                else:ids.append(n);used[key]=signature
            if not ids:continue
            set_name=f'{name}_{d}';add(mesh,'NodeSet',','.join(map(str,ids)),name=set_name)
            # FEBio's fixed DOFs do not retain nodal Rx/Ry/Rz. Zero-valued
            # prescribed displacements impose the same support and expose RF.
            bc=add(boundary,'bc',type='prescribed displacement',node_set=set_name)
            add(bc,'dof','xyz'[d]);add(bc,'value',value,lc=curve_id);add(bc,'relative',0)
        curve=add(curves,'load_controller',id=curve_id,type='loadcurve')
        add(curve,'interpolate','LINEAR');points=add(curve,'points')
        for t,v in c.get('progress') or ((0,0),(1,1)):add(points,'pt',f'{t},{v}')
    contacts=ET.Element('Contact')
    for i,c in enumerate(case['contacts']):
        for side in ('slave','master'):
            surface=add(mesh,'Surface',name=f'C{i}{side}')
            sels=c[side] if isinstance(c[side],(list,tuple)) else (c[side],)
            count=0
            for sel in sels:
                for e,_,ids in select_faces(sel,meshes):
                    # Native C3D10 and FEBio tet10 have identical edge ordering.
                    # Orient the quadratic surface outward from its parent tet.
                    p=np.array([nodes[n] for n in ids[:3]])
                    center=np.mean([nodes[n] for n in meshes[sel['part']]['elements'][e][:4]],axis=0)
                    if np.dot(np.cross(p[1]-p[0],p[2]-p[0]),center-p.mean(axis=0))>0:
                        ids=[ids[j] for j in (0,2,1,5,4,3)]
                    count+=1;add(surface,'tri6',','.join(map(str,ids)),id=count)
        pair=add(mesh,'SurfacePair',name=f'C{i}')
        add(pair,'primary',f'C{i}slave');add(pair,'secondary',f'C{i}master')
        contact=add(contacts,'contact',type='sliding-elastic',surface_pair=f'C{i}',name=f'C{i}')
        settings=dict(laugon=int(case['febio']['augmented_lagrange']),penalty=c['penalty_N_mm3'],
                      auto_penalty=0,gaptol=c['penetration_limit_mm']/10,tolerance=.01,
                      maxaug=30,seg_up=0,symmetric_stiffness=0,search_radius=case['febio']['search_radius_mm'],
                      search_tol=.001,two_pass=int(case['febio'].get('two_pass',False)),node_reloc=0,tension=0,fric_coeff=0)
        for key,value in settings.items():add(contact,key,value)
    root.extend((domains,boundary,contacts,curves))
    output=add(root,'Output');logs=add(output,'logfile')
    add(logs,'node_data',','.join(map(str,nodes)),data='ux;uy;uz;Rx;Ry;Rz',file='nodes.txt',delim=',')
    es=[e for m in meshes.values() for e in m['elements']]
    add(logs,'element_data',','.join(map(str,es)),data='E1;E2;E3',file='elements.txt',delim=',')
    for i in range(len(case['contacts'])):
        add(logs,'surface_data',data='max contact gap;contact area',surface=f'C{i}slave',file=f'contact_{i}.txt',delim=',')
        if case['febio'].get('two_pass'):
            add(logs,'surface_data',data='max contact gap;contact area',surface=f'C{i}master',file=f'contact_{i}_master.txt',delim=',')
    ET.indent(root)
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)


def read_records(path):
    """FEBio data logging: one complete table per converged time, streaming."""
    time=None;rows=[]
    with path.open() as source:
        for line in source:
            if re.match(r'^\*?Time\s*=',line):
                if time is not None:yield time,rows
                time=float(line.split('=',1)[1]);rows=[]
            elif time is not None and re.match(r'^\d+[, ]',line):
                rows.append([float(v) for v in re.split(r'[,\s]+',line.strip())])
    if time is not None:yield time,rows


@operation('analysis.extraction')
def summarize(directory,case,meshes,selections):
    from .tet10_strain import Tet10GreenStrain,POINTS
    nodes={n:p for m in meshes.values() for n,p in m['nodes'].items()}
    elements={e:con for m in meshes.values() for e,con in m['elements'].items()}
    part_for_element={e:name for name,m in meshes.items() for e in m['elements']}
    recovery=Tet10GreenStrain(nodes,elements)
    part_strains={name:0. for name in meshes};peak=(-1,None,None,None,None)
    element_frames=iter(read_records(directory/'elements.txt'))
    contact_frames=[(iter(read_records(directory/f'contact_{i}.txt')),True) for i in range(len(case['contacts']))]
    if case['febio'].get('two_pass'):
        contact_frames.extend((iter(read_records(directory/f'contact_{i}_master.txt')),False) for i in range(len(case['contacts'])))
    expected_nodes={n for m in meshes.values() for n in m['nodes']}
    expected_elements={e for m in meshes.values() for e in m['elements']}
    history=[]
    for time,rows in read_records(directory/'nodes.txt'):
        if {int(r[0]) for r in rows}!=expected_nodes:raise ValueError('Incomplete FEBio nodal fields')
        t,ers=next(element_frames)
        if abs(t-time)>1e-8 or {int(r[0]) for r in ers}!=expected_elements:raise ValueError('Incomplete FEBio element fields')
        if any(len(r)!=7 for r in rows) or any(len(r)!=4 for r in ers):raise ValueError('Unexpected FEBio field width')
        if not np.isfinite(rows).all() or not np.isfinite(ers).all():raise ValueError('Non-finite FEBio fields')
        # FEBio node.get_load is the internal-force sign. Normalize to the
        # required external constraint force used by the shared API/CalculiX.
        us={int(r[0]):np.array(r[1:4]) for r in rows};rf={int(r[0]):-np.array(r[4:]) for r in rows}
        principal=recovery.principal(us)
        native={int(r[0]):sorted(r[1:]) for r in ers}
        discrepancy=float(np.max(np.abs(principal.mean(axis=1)-np.array([native[e] for e in recovery.elements]))))
        if discrepancy>1e-6:raise ValueError(f'Recovered tet10 principal-strain means differ from FEBio by {discrepancy:g}')
        absolute=np.max(np.abs(principal),axis=2)
        index,q=np.unravel_index(np.argmax(absolute),absolute.shape)
        value=float(absolute[index,q]);e=recovery.elements[index];part=part_for_element[e]
        if value>peak[0]:peak=(value,part,e,int(q+1),time)
        for name,m in meshes.items():
            ids=[j for j,e in enumerate(recovery.elements) if e in m['elements']]
            part_strains[name]=max(part_strains[name],float(absolute[ids].max()))
        reactions={};observations={};motion_forces={};prescribed=set()
        for name,sel in selections.items():
            if name.startswith('@observe:'):
                samples=np.array([us[n] for n in sel['nodes']])
                observations[name[9:]]=dict(min_mm=samples.min(axis=0).tolist(),max_mm=samples.max(axis=0).tolist(),mean_mm=samples.mean(axis=0).tolist());continue
            values=sel['displacement_mm'];total=np.sum([rf[n] for n in sel['nodes']],axis=0)
            reactions[name]=[float(v) if values[d] is not None else 0 for d,v in enumerate(total)]
            prescribed.update((n,d) for n in sel['nodes'] for d,v in enumerate(values) if v is not None)
            motion=np.array([v or 0 for v in values])
            if np.linalg.norm(motion)>0:
                sign=1
                if sel.get('progress'):
                    a,b=next(((a,b) for a,b in zip(sel['progress'],sel['progress'][1:]) if time<=b[0]+1e-9))
                    sign=np.sign(b[1]-a[1])
                motion_forces[name]=float(sign*np.dot(total,motion)/np.linalg.norm(motion))
        gaps=[];areas=[]
        for frames,primary in contact_frames:
            t,crs=next(frames)
            if abs(t-time)>1e-8 or len(crs)!=1 or len(crs[0])!=3 or not np.isfinite(crs).all():raise ValueError('Missing FEBio contact fields')
            gaps.append(crs[0][1])
            if primary:areas.append(crs[0][2])
        net=np.zeros(3)
        for n,d in prescribed:net[d]+=rf[n][d]
        balance=float(np.linalg.norm(net));reference=max(1,sum(float(np.linalg.norm(v)) for v in reactions.values()))
        history.append(dict(load_fraction=time,reactions_N=reactions,motion_force_N=motion_forces,observations=observations,
                            max_displacement_mm=max(float(np.linalg.norm(v)) for v in us.values()),
                            max_penetration_mm=max(gaps,default=0),contact_area_mm2=sum(areas),
                            max_element_mean_abs_principal_green_strain=max(abs(v) for r in ers for v in r[1:]),
                            max_abs_principal_strain=value,strain_recovery_mean_discrepancy=discrepancy,
                            force_balance_residual_N=balance,force_balance_relative=balance/reference))
    if not history or abs(history[-1]['load_fraction']-1)>1e-6:raise ValueError('FEBio load interval did not complete')
    if next(element_frames,None) is not None or any(next(f,None) is not None for f,_ in contact_frames):raise ValueError('Unmatched FEBio frames')
    metrics=dict(max_penetration_mm=max(h['max_penetration_mm'] for h in history),
                 max_displacement_mm=history[-1]['max_displacement_mm'],
                 contact_detected=any(h['contact_area_mm2']>1e-8 for h in history) if case['contacts'] else None,
                 max_element_mean_abs_principal_green_strain=max(h['max_element_mean_abs_principal_green_strain'] for h in history),
                 max_force_balance_relative=max(h['force_balance_relative'] for h in history),
                 observations=history[-1]['observations'],
                 peak_reaction_force_N={name:max(float(np.linalg.norm(h['reactions_N'][name])) for h in history) for name in history[-1]['reactions_N']},
                 peak_motion_force_N={name:max(abs(h['motion_force_N'][name]) for h in history) for name in history[-1]['motion_force_N']})
    metrics.update(max_abs_principal_strain=peak[0],max_strain_part=peak[1],max_strain_element=peak[2],
                   max_strain_integration_point=peak[3],max_strain_load_fraction=peak[4],
                   max_strain_integration_point_natural_coordinates=POINTS[peak[3]-1].tolist(),
                   max_strain_by_part=part_strains,strain_limits={p['name']:p['material']['strain_limit'] for p in case['parts']},
                   max_strain_element_centroid_mm=np.mean([nodes[n] for n in elements[peak[2]][:4]],axis=0).tolist(),
                   max_strain_recovery_mean_discrepancy=max(h['strain_recovery_mean_discrepancy'] for h in history))
    return metrics,history


def main(directory, *, postprocess_only=False):
    case=json.loads((directory/'case.json').read_text())
    r=AnalysisResult(case['name'],'failed',assumptions=[
        'mm, N, MPa; isotropic St Venant–Kirchhoff elastic solid using the recorded E and Poisson ratio.',
        'St Venant–Kirchhoff law matches the CalculiX *ELASTIC/NLGEOM intent; eight rather than four volume quadrature points. No printed-layer calibration.',
        'Frictionless sliding-elastic contact; projections update during iteration, no node relocation.',
        'Peak absolute principal Green strain recovered from tet10 nodal fields at eight native quadrature points; means must agree with native element logs.',
        'The provisional strain screen is conditional on the uncalibrated material and Green strain measure; numerical completion does not qualify a physical print.'])
    r.provenance=dict(backend='FEBio',backend_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')})
    try:
        expected=hashlib.sha256((directory/'analysis.inp').read_bytes()).hexdigest() if postprocess_only else None
        if postprocess_only:
            original=json.loads((directory/'result.json').read_text())['provenance']
            for key,name in (('input_sha256','analysis.inp'),('native_input_sha256','analysis.feb'),('case_sha256','case.json')):
                if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=original.get(key):
                    raise ValueError('Saved FEBio input/case identity differs from its result')
        meshes,nodes,elements,selections,loads,contacts=compile_case(case,directory,expected_input_sha256=expected)
        r.provenance.update(gmsh=package_version('gmsh'),cadquery=package_version('cadquery'),python=sys.version.split()[0])
        xml=compile_xml(case,directory,meshes,nodes,selections)
        if postprocess_only:
            if xml!=(directory/'analysis.feb').read_bytes():raise ValueError('Regenerated FEBio input differs; cannot reuse native fields')
        else:(directory/'analysis.feb').write_bytes(xml)
        command=[os.environ['FEBIO_COMMAND'],'-i','analysis.feb','-o','analysis.log']
        r.provenance.update(command=command,executable_sha256=hashlib.sha256(Path(command[0]).read_bytes()).hexdigest(),
                            input_sha256=hashlib.sha256((directory/'analysis.inp').read_bytes()).hexdigest(),
                            native_input_sha256=hashlib.sha256((directory/'analysis.feb').read_bytes()).hexdigest(),
                            case_sha256=hashlib.sha256((directory/'case.json').read_bytes()).hexdigest(),
                            mesh={name:dict(nodes=len(m['nodes']),elements=len(m['elements']),min_jacobian=m['min_jacobian']) for name,m in meshes.items()},contacts=contacts)
        library=Path(command[0]).resolve().parent.parent/'lib'
        r.provenance['native_libraries_sha256']={name:hashlib.sha256((library/name).read_bytes()).hexdigest()
            for name in ('libfecore.so','libfebiomech.so','libnumcore.so') if (library/name).is_file()}
        if case.get('mesh_reuse'):r.provenance['mesh_reuse']=case['mesh_reuse']
        code=0
        if not postprocess_only:
            (directory/'run_metadata.json').write_text(json.dumps(r.provenance,indent=2)+'\n')
            with (directory/'solver.log').open('w') as log:
                code=run_command(command,cwd=directory,stdout=log,stderr=subprocess.STDOUT).returncode
        r.provenance['postprocess_only']=postprocess_only
        if postprocess_only:
            r.provenance['original_backend_sha256']=original.get('backend_sha256',{})
            for key in ('executable_sha256','native_libraries_sha256','command'):
                r.provenance[key]=original.get(key)
        log=(directory/'solver.log').read_text(errors='replace')
        r.warnings=list(dict.fromkeys(line.strip() for line in log.splitlines() if 'WARNING' in line.upper()))
        version=re.search(r'version (4\.\S+)',log);r.provenance['version']=version[1] if version else 'unknown'
        if code or 'N O R M A L   T E R M I N A T I O N' not in log:
            r.errors.append(f'FEBio failed or did not finish (exit {code}); see solver.log')
        else:
            r.metrics,r.history=summarize(directory,case,meshes,selections)
            r.metrics['path_completed']=True
            if r.metrics['max_penetration_mm']>min((c['penetration_limit_mm'] for c in case['contacts']),default=math.inf):
                r.status='quality_failed';r.errors.append('FEBio contact penetration exceeds the recorded limit')
            elif r.metrics['max_force_balance_relative']>.01:
                r.status='quality_failed';r.errors.append('FEBio force balance exceeds 1%')
            else:
                r.status='completed_with_warnings' if r.warnings else 'completed';r.completed=True
    except Exception as exc:r.errors.append(f'{type(exc).__name__}: {exc}')
    r.artifacts=dict(input='analysis.feb',solver_log='solver.log',raw_results='nodes.txt')
    r.write(directory/'answer.json')


if __name__=='__main__':
    from execution.lifecycle import watch_owner
    watch_owner()
    if len(sys.argv) not in (2,3) or (len(sys.argv)==3 and sys.argv[2]!='--postprocess-only'):
        raise SystemExit('Usage: febio_worker DIRECTORY [--postprocess-only]')
    main(Path(sys.argv[1]),postprocess_only=len(sys.argv)==3)
