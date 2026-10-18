"""Read one accepted FEBio frame as a partial diagnostic, never completion."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from physical_analysis.backends.contact_diagnostics import run_record
from physical_analysis.backends.febio_worker import read_records
from physical_analysis.backends.mesh import select_faces,select_nodes
from physical_analysis.backends.worker import saved_meshes


def accepted_frame(path, fraction):
    for time, rows in read_records(path):
        if abs(time-fraction)<1e-8:
            return rows
        if time>fraction:
            break
    raise ValueError(f'No accepted frame {fraction} in {path.name}')


def inspect(directory, fraction):
    record=run_record(directory)
    hashes={key:hashlib.sha256((directory/name).read_bytes()).hexdigest()
            for key,name in (('input_sha256','analysis.inp'),
                             ('native_input_sha256','analysis.feb'),('case_sha256','case.json'))}
    if any(record['provenance'].get(k)!=v for k,v in hashes.items()):
        raise ValueError('Frozen FEBio input/case identity differs')
    case=json.loads((directory/'case.json').read_text())
    meshes=saved_meshes(case,directory/'analysis.inp')
    nodes={n:p for mesh in meshes.values() for n,p in mesh['nodes'].items()}
    elements={e for mesh in meshes.values() for e in mesh['elements']}
    rows=accepted_frame(directory/'nodes.txt',fraction)
    if any(len(row)!=7 for row in rows) or not np.isfinite(rows).all() or {int(r[0]) for r in rows}!=set(nodes):
        raise ValueError('Incomplete or invalid accepted nodal frame')
    displacement={int(r[0]):np.asarray(r[1:4]) for r in rows}
    # Match the existing backend's external-constraint force convention.
    reaction={int(r[0]):-np.asarray(r[4:]) for r in rows}
    frame_hashes={'nodes.txt':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()}
    reactions={};prescribed=set();observations={}
    for constraint in case['constraints']:
        selected=select_nodes(constraint['selection'],meshes)
        values=constraint['displacement_mm']
        total=np.sum([reaction[n] for n in selected],axis=0)
        reactions[constraint['name']]=[float(v) if values[d] is not None else 0. for d,v in enumerate(total)]
        prescribed.update((n,d) for n in selected for d,v in enumerate(values) if v is not None)
    for observation in case['observations']:
        selected=select_nodes(observation['selection'],meshes)
        values=np.array([displacement[n] for n in selected])
        observations[observation['name']]=dict(node_count=len(selected),
            min_mm=values.min(axis=0).tolist(),max_mm=values.max(axis=0).tolist(),mean_mm=values.mean(axis=0).tolist(),
            free_internal_force_sum_N=np.sum([[reaction[n][d] if (n,d) not in prescribed else 0.
                                               for d in range(3)] for n in selected],axis=0).tolist())
    net=np.zeros(3)
    for n,d in prescribed:
        net[d]+=reaction[n][d]
    reference=max(1.,sum(np.linalg.norm(v) for v in reactions.values()))
    # Native build 3ef378562 logs node.get_load: the negative assembled internal
    # force at free DOFs, not the converged total residual including contact.
    # With this static no-external-force case, its negation witnesses the nodal
    # force balancing contact. It is not a native contact-pressure projection.
    if case['loads']:
        raise ValueError('Free-node internal-force interpretation requires no applied forces')
    if 'version 4.13.0.3ef378562' not in (directory/'solver.log').read_text(errors='replace'):
        raise ValueError('Free-node force semantics were inspected for native build 3ef378562 only')
    free_contact={}
    for part,mesh in meshes.items():
        selections=[]
        for pair in case['contacts']:
            selections.append(pair['slave'])
            selections.extend(pair['master'] if isinstance(pair['master'],list) else [pair['master']])
        contact_nodes={n for selection in selections if selection['part']==part
                       for _,_,ids in select_faces(selection,meshes) for n in ids}
        free={n:np.array([reaction[n][d] if (n,d) not in prescribed else 0. for d in range(3)])
              for n in mesh['nodes']}
        ranked=sorted(contact_nodes,key=lambda n:np.linalg.norm(free[n]),reverse=True)
        free_contact[part]=dict(
            selected_contact_node_count=len(contact_nodes),
            contact_region_free_nodal_force_sum_N=np.sum([free[n] for n in contact_nodes],axis=0).tolist(),
            largest_free_nodal_force_outside_contact_N=max((float(np.linalg.norm(f)) for n,f in free.items() if n not in contact_nodes),default=0.),
            strongest_selected_contact_nodes=[dict(node=n,position_mm=nodes[n],force_N=free[n].tolist()) for n in ranked[:12]])
    contact={}
    for i in range(len(case['contacts'])):
        names=[f'contact_{i}.txt']
        if case['febio'].get('two_pass'):
            names.append(f'contact_{i}_master.txt')
        for name in names:
            values=accepted_frame(directory/name,fraction)
            if len(values)!=1 or len(values[0])!=3 or not np.isfinite(values).all():
                raise ValueError('Incomplete accepted contact frame')
            frame_hashes[name]=hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()
            contact[name]=dict(max_gap_mm=values[0][1],contact_area_mm2=values[0][2])
    strain=accepted_frame(directory/'elements.txt',fraction)
    if any(len(r)!=4 for r in strain) or not np.isfinite(strain).all() or {int(r[0]) for r in strain}!=elements:
        raise ValueError('Incomplete accepted element frame')
    frame_hashes['elements.txt']=hashlib.sha256(json.dumps(strain,separators=(',',':')).encode()).hexdigest()
    return dict(status='PARTIAL_ACCEPTED_FRAME_DIAGNOSTIC',completed=False,
        source_run_status=record['status'],load_fraction=fraction,input_identity=hashes,
        accepted_numeric_frame_sha256=frame_hashes,
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        reactions_N=reactions,force_balance_vector_N=net.tolist(),
        force_balance_relative=float(np.linalg.norm(net)/reference),
        free_contact_internal_force_witness=free_contact,
        native_force_semantics_sources=[
            'https://github.com/febiosoftware/FEBio/blob/3ef378562/FEBioMech/FEBioMechData.cpp',
            'https://github.com/febiosoftware/FEBio/blob/3ef378562/FEBioMech/FESolidSolver2.cpp',
            'https://github.com/febiosoftware/FEBio/blob/3ef378562/FEBioMech/FEResidualVector.cpp'],
        observations=observations,native_contact=contact,
        native_max_element_mean_abs_principal_green_strain=max(abs(v) for row in strain for v in row[1:]),
        limits='One complete accepted native output frame under frozen input hashes. Not a completed path, retention barrier, local integration-point peak strain, numerical qualification, or physical acceptance. Native contact area/gap are projection-dependent. Free-node internal-force witnesses localize equivalent nodal loads under inspected solver semantics; they are not integration-point contact-pressure maps. Equivalent quadratic nodal forces may change sign without implying tensile contact.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--fraction',type=float,required=True)
    parser.add_argument('--destination',type=Path,required=True)
    args=parser.parse_args()
    if not np.isfinite(args.fraction) or not 0<=args.fraction<=1:
        parser.error('Choose a saved fraction in [0,1]')
    answer=inspect(args.directory.resolve(),args.fraction)
    args.destination.write_text(json.dumps(answer,indent=2,allow_nan=False)+'\n')
    print(json.dumps(answer,indent=2,allow_nan=False))
