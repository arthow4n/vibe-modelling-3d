"""Read-only accepted-frame mesh and sampled exact-CAD witnesses for IPC."""
import json
from pathlib import Path
import numpy as np
from .polyfem_worker import digest
from .polyfem_output import read_vtu, map_points, progress_value, require_native_rest_mesh
from .mesh import contains
from ..mesh_witness import inspect_mesh_pair


def prefix_diagnostics(directory):
    """Inspect all available accepted states without promoting an incomplete run.

    The output is a separate diagnostic record. Identity-check original input
    and native meshes; record saved-field identities, never change result.json.
    """
    from .contact_diagnostics import run_record
    from .polyfem_output import extract
    from .polyfem_worker import write_json, implementation_identity
    from ..results import AnalysisResult
    directory=Path(directory);r=AnalysisResult(**run_record(directory))
    for key,file in (('input_sha256','scene.json'),('case_sha256','case.json'),('mesh_sha256','mesh.json')):
        if digest(directory/file)!=r.provenance.get(key):
            raise ValueError('Saved IPC input/case/mesh identity differs')
    for file,identity in r.provenance['mesh_files_sha256'].items():
        if digest(directory/file)!=identity:
            raise ValueError('Saved IPC numerical mesh identity differs')
    case=json.loads((directory/'case.json').read_text());data=json.loads((directory/'mesh.json').read_text())
    scene=json.loads((directory/'scene.json').read_text())
    r.history=[];r.metrics={};r.completed=False
    extract(directory,case,data['parts'],data['selections'],scene,r,partial=True)
    r.provenance['diagnostic_implementation_sha256']=implementation_identity()
    r.provenance['accepted_field_sha256']={p.name:digest(p) for p in directory.glob('step_*.vtu')
        if p.stem.removeprefix('step_').isdigit() or p.name.endswith('_surf_contact.vtu')}
    r.assumptions.append('Diagnostic prefix only; no operation completion or contact passage established.')
    r.write(directory/'prefix_diagnostics.json')
    return r


def contact_frames(directory, fractions=None, *, rigid_parts=()):
    from .contact_diagnostics import run_record, signed_sample_distances
    import cadquery as cq
    directory=Path(directory);result=run_record(directory);provenance=result['provenance']
    hashes={key:digest(directory/file) for key,file in (
        ('input_sha256','scene.json'),('case_sha256','case.json'),('mesh_sha256','mesh.json'))}
    if any(provenance.get(k)!=v for k,v in hashes.items()):
        raise ValueError('Saved IPC input/case/mesh differs from result provenance')
    for file,identity in provenance['mesh_files_sha256'].items():
        if digest(directory/file)!=identity:
            raise ValueError('Saved IPC numerical mesh differs from result provenance')
    case=json.loads((directory/'case.json').read_text());data=json.loads((directory/'mesh.json').read_text())
    scene=json.loads((directory/'scene.json').read_text());scale=1000 if scene['units']['length']=='m' else 1
    flexible=case['ipc']['deformable'];mesh=data['parts'][flexible];reference=np.asarray(mesh['points_mm'])
    if fractions is None:
        if not result['history']:raise ValueError('Choose explicit accepted fractions for an unfinished IPC run')
        fractions=[max(result['history'],key=lambda h:h['max_abs_principal_strain'])['load_fraction']]
    found=[]
    for time in fractions:
        index=round(time*data['steps'])
        if not np.isfinite(time) or not 0<=time<=1 or abs(time-index/data['steps'])>1e-8:
            raise ValueError('Requested IPC fraction is not a saved grid point')
        points,fields=read_vtu(directory/f'step_{index}.vtu',scale)
        mapping=map_points(reference,points,scale)
        u=fields['solution'][mapping]*scale
        rest_mapping=require_native_rest_mesh(directory,reference,points[mapping])
        cp,cf=read_vtu(directory/f'step_{index}_surf_contact.vtu',scale)
        regions=[c['slave']['region'] for c in case['contacts']]
        faces=np.asarray([tri for tri in mesh['triangles'] if any(all(contains(r,reference[n]) for n in tri) for r in regions)])
        if not len(faces):raise ValueError('Empty selected IPC slave sample surface')
        deformed=reference+u
        samples=np.vstack((deformed[np.unique(faces)],deformed[faces].mean(axis=1)))
        geometry={};native_rest_geometry={};cad={};poses={}
        for name,obstacle in data['parts'].items():
            if name==flexible:continue
            op=np.asarray(obstacle['points_mm']);oi=map_points(op,cp,scale);du=cf['solution'][oi]*scale
            c=next(c for c in case['constraints'] if c['selection']['part']==name)
            expected=np.asarray(c['displacement_mm'])*progress_value(c.get('progress'),time)
            if np.max(np.abs(du-expected))>1e-5:
                raise ValueError('IPC obstacle pose does not match prescribed motion')
            geometry[name]=inspect_mesh_pair(deformed,mesh['triangles'],op+du,obstacle['triangles'],
                                            search_distance_mm=case['ipc']['activation_distance_mm'])
            native_rest_geometry[name]=inspect_mesh_pair(points[mapping]+u,mesh['triangles'],cp[oi]+du,obstacle['triangles'],
                                            search_distance_mm=case['ipc']['activation_distance_mm'])
            poses[name]=(du.mean(axis=0)+np.asarray(case['ipc']['initial_offset_mm'])).tolist()
        for name in rigid_parts:
            part=next(p for p in case['parts'] if p['name']==name)
            if digest(directory/part['geometry'])!=part['sha256']:
                raise ValueError('Saved IPC CAD identity differs')
            solid=cq.Shape.importBrep(str(directory/part['geometry'])).translate(tuple(poses[name]))
            row=signed_sample_distances(samples,solid)
            row['worst_sample_point_mm']=samples[row['worst_sample_index']].tolist()
            cad[name]=row
        force=cf['contact_forces']
        found.append(dict(load_fraction=time,native_ipc=dict(force_active=bool(np.abs(force).max()>1e-8),
            maximum_vertex_force_N=float(np.linalg.norm(force,axis=1).max()),native_gap_mm=None,
            evidence='Accepted collision-surface field from IPC; no native penetration bound exposed by this extractor'),
            independent_mesh=geometry,independent_native_rest_mesh=native_rest_geometry,
            native_rest_mapping=rest_mapping,sampled_rigid_CAD=cad,selected_CAD_sample_count=len(samples)))
    return dict(**hashes,result_status=result['status'],frames=found,
        limits='All numerical surface triangle pairs checked independently; exact-CAD comparison samples selected slave vertices and centroids only. CAD samples are not a global proof. CAD solids include faces intentionally omitted from an open obstacle patch: interpret witnesses against the recorded contact selection. Accepted saved states, not continuous-path proof; no completion/status changes.')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory');parser.add_argument('--prefix',action='store_true',required=True)
    args=parser.parse_args();r=prefix_diagnostics(args.directory)
    print(json.dumps(dict(status=r.status,completed=r.completed,metrics=r.metrics),indent=2))
