"""Read actual deformed C3D10 retaining faces; no contact-force prediction.

The axial-traction fixture does not load the deformed normal. This witnesses the
normal change that a follower/contact formulation would need to resolve.
"""
import argparse
import hashlib
import json
from pathlib import Path
import math
import numpy as np
from physical_analysis.backends.worker import saved_meshes,iter_dat
from physical_analysis.backends.mesh import select_nodes


def witness(run):
    result=json.loads((run/'result.json').read_text())
    if not result['completed']:
        raise ValueError('A completed extracted solve is required')
    for file,key in (('analysis.inp','input_sha256'),('case.json','case_sha256')):
        if hashlib.sha256((run/file).read_bytes()).hexdigest()!=result['provenance'][key]:
            raise ValueError('Saved native input/case differs from result')
    case=json.loads((run/'case.json').read_text())
    if case['name']!='m1_eccentric' or result['case']!='m1_eccentric':
        raise ValueError('This witness is specific to the declared M1 traction case')
    meshes=saved_meshes(case,run/'analysis.inp')
    mesh=meshes['catch']
    last=None
    for time,frame in iter_dat(run/'analysis.dat'):
        last=(time,frame)
    if last is None or abs(last[0]-1)>1e-6:
        raise ValueError('Missing final native frame')
    us={int(row[0]):np.array(row[1:]) for row in last[1]['displacements']}
    if set(us)!=set(mesh['nodes']):
        raise ValueError('Raw displacement nodes differ from guarded input')
    observations={o['name']:o['selection'] for o in case['observations']}
    sampled=np.array([us[i] for i in select_nodes(observations['shoulder'],meshes)])
    expected=result['metrics']['observations']['shoulder']
    for key,value in (('min_mm',sampled.min(axis=0)),('max_mm',sampled.max(axis=0)),('mean_mm',sampled.mean(axis=0))):
        if not np.allclose(value,expected[key],rtol=0,atol=1e-7):
            raise ValueError('Raw final shoulder displacement differs from retained result')
    peak=max(float(np.linalg.norm(u)) for u in us.values())
    if not math.isclose(peak,result['metrics']['max_displacement_mm'],rel_tol=1e-7,abs_tol=1e-7):
        raise ValueError('Raw final displacement summary differs from retained result')
    forces={int(row[0]):np.array(row[1:]) for row in last[1]['forces']}
    for constraint in case['constraints']:
        rf=np.sum([forces[n] for n in select_nodes(constraint['selection'],meshes)],axis=0)
        expected_rf=result['history'][-1]['reactions_N'][constraint['name']]
        active=[i for i,v in enumerate(constraint['displacement_mm']) if v is not None]
        if not np.allclose(rf[active],np.array(expected_rf)[active],rtol=0,atol=1e-7):
            raise ValueError('Raw final reaction differs from retained result')
    # Exact imprinted M1 receiving land, as declared by its original CAD.
    faces=[ids for _,_,ids in mesh['surface'] if all(
        abs(mesh['nodes'][i][2]-178)<1e-6 and mesh['nodes'][i][0]<=-34.4+1e-6 for i in ids)]
    if not faces:
        raise ValueError('Actual M1 retaining face absent from mesh')
    q=np.array(((1/6,1/6),(2/3,1/6),(1/6,2/3)))
    r,s=q.T;a=1-r-s
    dr=np.stack((1-4*a,4*r-1,np.zeros(3),4*(a-r),4*s,-4*s),axis=1)
    ds=np.stack((1-4*a,np.zeros(3),4*s-1,-4*r,4*r,4*(a-s)),axis=1)
    vectors=[];samples=[];initial_area=0.
    for ids in faces:
        p=np.array([mesh['nodes'][i] for i in ids]);deformed=p+np.array([us[i] for i in ids])
        before=np.cross(dr@p,ds@p);after=np.cross(dr@deformed,ds@deformed)
        if np.mean(before[:,2])>0:
            before=-before;after=-after
        initial_area+=np.linalg.norm(before,axis=1).sum()/6
        vectors.extend(after/6)
        samples.extend(after/np.linalg.norm(after,axis=1)[:,None])
    if not math.isclose(initial_area,12,abs_tol=1e-6) or not math.isclose(
        result['provenance']['loads'][0]['area_mm2'],12,abs_tol=1e-6):
        raise ValueError('Expected the actual imprinted12mm² M1 receiving-land traction')
    vector=np.sum(vectors,axis=0);normal=vector/np.linalg.norm(vector)
    ratios=[v[0]/v[2] for v in samples]
    return dict(scope='Deformed normal in fixed-world axial-traction solution; not actual cap contact or pull-off.',
                native_case_sha256=result['provenance']['case_sha256'],native_input_sha256=result['provenance']['input_sha256'],
                raw_results_sha256=hashlib.sha256((run/'analysis.dat').read_bytes()).hexdigest(),
                raw_fields_association='Final shoulder extrema/mean, full displacement norm and support reactions match retained result within1e-7.',
                initial_loaded_land_area_mm2=initial_area,quadratic_triangle_count=len(faces),
                initial_hook_outward_normal=[0,0,-1],deformed_area_weighted_outward_normal=normal.tolist(),
                upward_normal_force_inward_to_axial_ratio=float(normal[0]/normal[2]),
                sampled_ratio_range=[float(min(ratios)),float(max(ratios))],
                deformed_normal_angle_deg=math.degrees(math.acos(float(-normal[2]))),
                interpretation='A normal upward force on this deformed negative-X tooth has positive-X (inward) component. '
                               'That additional component was not applied in this traction fixture. '
                               'Moving contact, receiver deformation and force barrier remain unresolved.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run',type=Path)
    p.add_argument('destination',type=Path)
    a=p.parse_args()
    answer=witness(a.run.resolve())
    a.destination.write_text(json.dumps(answer,indent=2,allow_nan=False)+'\n')
    print(json.dumps(answer,indent=2))
