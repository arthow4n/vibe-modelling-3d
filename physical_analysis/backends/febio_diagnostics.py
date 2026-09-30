"""Inspect FEBio's deformed interface against the actual rigid-driver CAD.

The native maximum gap is a solver projection quantity. All selected slave
faces are sampled here, including faces for which that projection finds no
contact. This helps localize finite-edge passage errors without inventing a
correspondence between a CAD sample and a native contact integration point.
"""
import hashlib
import json
from pathlib import Path
import cadquery as cq
import numpy as np
from .worker import saved_meshes
from .mesh import select_faces
from .febio_worker import read_records
from .contact_diagnostics import quadratic_face_samples,signed_sample_distances,master_faces_by_part,planar_master_witness,run_record


def contact_frames(directory,fractions=None,*,rigid_parts=()):
    directory=Path(directory)
    result=run_record(directory)
    case=json.loads((directory/'case.json').read_text())
    hashes={key:hashlib.sha256((directory/name).read_bytes()).hexdigest()
            for key,name in (('input_sha256','analysis.inp'),('native_input_sha256','analysis.feb'),('case_sha256','case.json'))}
    if any(result['provenance'].get(k)!=v for k,v in hashes.items()):raise ValueError('FEBio saved input/case differs from result provenance')
    if fractions is None:
        if not result['history']:raise ValueError('No saved history to select a frame')
        fractions=[max(result['history'],key=lambda h:h['max_penetration_mm'])['load_fraction']]
    requested=set(map(float,fractions))
    if not requested or not all(np.isfinite(t) and 0<=t<=1 for t in requested):raise ValueError('Choose saved fractions in 0..1')
    meshes=saved_meshes(case,directory/'analysis.inp')
    nodes={n:p for m in meshes.values() for n,p in m['nodes'].items()}
    elements={e:con for m in meshes.values() for e,con in m['elements'].items()}
    masters=master_faces_by_part(case,meshes)
    faces={}
    for contact in case['contacts']:
        part=contact['slave']['part']
        for e,s,ids in select_faces(contact['slave'],meshes):faces[(e,s)]=(part,ids)
    drivers={};geometry_hashes={}
    for name in rigid_parts:
        part=next((p for p in case['parts'] if p['name']==name),None)
        if part is None:raise ValueError(f'Unknown rigid part: {name}')
        path=directory/part['geometry'];actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=part['sha256']:raise ValueError(f'Saved geometry differs: {name}')
        drivers[name]=cq.Shape.importBrep(str(path));geometry_hashes[name]=actual
    found=[]
    contact_tables=[dict(read_records(directory/f'contact_{i}.txt')) for i in range(len(case['contacts']))]
    if case['febio'].get('two_pass'):
        contact_tables.extend(dict(read_records(directory/f'contact_{i}_master.txt')) for i in range(len(case['contacts'])))
    for time,rows in read_records(directory/'nodes.txt'):
        if time>max(requested)+1e-8:break
        if not any(abs(time-t)<1e-8 for t in requested):continue
        us={int(r[0]):np.array(r[1:4]) for r in rows}
        if set(us)!=set(nodes) or not all(np.isfinite(v).all() for v in us.values()):raise ValueError('Missing or non-finite nodal fields')
        poses={}
        for name,solid in drivers.items():
            translations=np.array([us[n] for n in meshes[name]['nodes']]);shift=translations.mean(axis=0)
            if np.max(np.abs(translations-shift))>1e-8:raise ValueError(f'{name} is not a uniform rigid translation')
            poses[name]=solid.translate(tuple(shift))
        worst={};distances={name:float('inf') for name in poses}
        for (e,s),(part,ids) in faces.items():
            samples=quadratic_face_samples(np.array([nodes[n]+us[n] for n in ids]))
            clearance={name:signed_sample_distances(samples,solid) for name,solid in poses.items()}
            row=dict(part=part,element=e,face=s,node_ids=ids,deformed_samples_mm=samples.tolist(),sampled_rigid_CAD=clearance)
            for name,c in clearance.items():
                if c['min_sampled_signed_clearance_mm']<distances[name]:
                    distances[name]=c['min_sampled_signed_clearance_mm'];worst[name]=row
        deformed={n:nodes[n]+us[n] for n in nodes}
        witnesses={name:planar_master_witness(row['deformed_samples_mm'][row['sampled_rigid_CAD'][name]['worst_sample_index']],
                    masters.get(name,[]),deformed,elements) for name,row in worst.items()}
        gaps=[]
        for table in contact_tables:
            values=next((rows for t,rows in table.items() if abs(t-time)<1e-8),None)
            if values is None or len(values)!=1 or len(values[0])!=3 or not np.isfinite(values).all():raise ValueError('Missing native contact frame')
            gaps.append(values[0][1])
        found.append(dict(load_fraction=time,selected_face_count=len(faces),solver_max_penetration_mm=max(gaps,default=0),
                          sampled_rigid_CAD={name:dict(min_sampled_signed_clearance_mm=d,maximum_sampled_inside_depth_mm=max(0,-d)) for name,d in distances.items()},
                          worst_faces_by_driver=worst,native_planar_master_witnesses=witnesses))
    if len(found)!=len(requested):raise ValueError('Requested fraction is unavailable')
    return dict(**hashes,rigid_geometry_sha256=geometry_hashes,frames=found,result_status=result['status'],
        limits='Ten samples on every selected quadratic slave face; only worst faces per driver retained. Not a maximum intersection, continuous path check, native contact gap, or matched projection point. Signed CAD distance positive outside, negative inside. Native max contact gap is a separate projection-dependent integration-point quantity. These diagnostics never change the original completion status.')
