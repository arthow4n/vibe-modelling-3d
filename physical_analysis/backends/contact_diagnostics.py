"""Read-only location evidence from retained CalculiX contact fields.

Face-to-face rows identify a slave element and face, not a unique integration
point. Repeated identifiers are retained in the count; pressure/gap rows must
be paired in their output order. Locations are face samples, not the solver's
unreported contact integration-point coordinates.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from .worker import iter_dat,saved_meshes


def run_record(directory):
    """Use early frozen identity when a long solve has no final result yet."""
    result=directory/'result.json'
    if result.is_file():return json.loads(result.read_text())
    return dict(provenance=json.loads((directory/'run_metadata.json').read_text()),
                history=[],status='no_final_result')


def quadratic_face_samples(points):
    samples=list(points)
    for r,s in ((1/3,1/3),(1/6,1/6),(2/3,1/6),(1/6,2/3)):
        a=1-r-s
        shape=np.array([a*(2*a-1),r*(2*r-1),s*(2*s-1),4*a*r,4*r*s,4*s*a])
        samples.append(shape@points)
    return np.asarray(samples)


def signed_sample_distances(points,solid):
    import cadquery as cq
    shell=cq.Compound.makeCompound(solid.Shells())
    signed=[]
    for point in points:
        distance=shell.distance(cq.Vertex.makeVertex(*point))
        signed.append(-distance if solid.isInside(cq.Vector(*point),1e-7) else distance)
    return dict(min_sampled_signed_clearance_mm=min(signed),
                maximum_sampled_inside_depth_mm=max(0,-min(signed)),worst_sample_index=int(np.argmin(signed)))


def planar_master_witness(point,faces,nodes,elements):
    """Find a containing straight-sided planar master facet near one sample.

    Only quadratic faces exactly representing a planar triangle qualify.
    This is a geometric witness, not the solver's matched projection or a
    maximum-overlap calculation. Curved facets are deliberately excluded.
    """
    if not faces:return None
    points=np.array([[nodes[n] for n in ids] for _,_,ids in faces])
    centers=np.array([np.mean([nodes[n] for n in elements[e][:4]],axis=0) for e,_,_ in faces])
    a=points[:,0];v=points[:,1]-a;w=points[:,2]-a
    normals=np.cross(v,w);length=np.linalg.norm(normals,axis=1)
    valid=length>1e-12;normals/=np.maximum(length,1e-12)[:,None]
    flip=np.einsum('ij,ij->i',normals,centers-a)>0;normals[flip]*=-1
    midpoints=np.stack(((points[:,0]+points[:,1])/2,(points[:,1]+points[:,2])/2,(points[:,2]+points[:,0])/2),axis=1)
    valid&=np.max(np.abs(points[:,3:]-midpoints),axis=(1,2))<1e-7
    signed=np.einsum('ij,ij->i',np.asarray(point)-a,normals)
    projected=np.asarray(point)-signed[:,None]*normals;q=projected-a
    vv=np.einsum('ij,ij->i',v,v);ww=np.einsum('ij,ij->i',w,w);vw=np.einsum('ij,ij->i',v,w)
    qv=np.einsum('ij,ij->i',q,v);qw=np.einsum('ij,ij->i',q,w);den=vv*ww-vw*vw
    valid&=den>1e-20
    r=(ww*qv-vw*qw)/np.maximum(den,1e-20);s=(vv*qw-vw*qv)/np.maximum(den,1e-20)
    valid&=(r>=-1e-8)&(s>=-1e-8)&(r+s<=1+1e-8)
    candidates=np.flatnonzero(valid)
    if not len(candidates):return None
    index=int(candidates[np.argmin(np.abs(signed[candidates]))]);e,side,ids=faces[index]
    return dict(element=e,face=side,node_ids=ids,point_mm=np.asarray(point).tolist(),
                projected_point_mm=projected[index].tolist(),outward_signed_plane_distance_mm=float(signed[index]),
                corners_mm=points[index,:3].tolist(),
                limits='Projection lies inside a selected planar native master triangle with straight midsides. Negative is behind its outward plane. Not a native matched contact point, global distance, curved-facet check, or full intersection proof.')


def master_faces_by_part(case,meshes):
    from .mesh import select_faces
    result={}
    for contact in case['contacts']:
        sels=contact['master'] if isinstance(contact['master'],(list,tuple)) else (contact['master'],)
        for selection in sels:
            target=result.setdefault(selection['part'],{})
            for e,s,ids in select_faces(selection,meshes):target[(e,s)]=(e,s,ids)
    return {name:list(faces.values()) for name,faces in result.items()}


def contact_frames(directory, fractions=None, *, rigid_parts=()):
    """Read requested existing frames with deformed slave-face samples.

    This function is for diagnostics, including completed quality failures.
    It does not run a solver, alter completion status or qualify penetration.
    Fractions must correspond to saved output; unavailable frames fail.
    """
    from .mesh import FACES
    directory=Path(directory)
    result=run_record(directory)
    if result['provenance'].get('backend')=='FEBio':
        from .febio_diagnostics import contact_frames as febio_frames
        return febio_frames(directory,fractions,rigid_parts=rigid_parts)
    if result['provenance'].get('backend')=='PolyFEM-IPC-experimental':
        from .polyfem_diagnostics import contact_frames as ipc_frames
        return ipc_frames(directory,fractions,rigid_parts=rigid_parts)
    if fractions is None:
        if not result['history']: raise ValueError('No saved history to select a diagnostic frame')
        fractions=[max(result['history'],key=lambda h:h['max_penetration_mm'])['load_fraction']]
    requested={float(t) for t in fractions}
    if not requested or not all(np.isfinite(t) and 0<=t<=1 for t in requested):
        raise ValueError('Choose saved load fractions in 0..1')
    case=json.loads((directory/'case.json').read_text())
    hashes={key:hashlib.sha256((directory/name).read_bytes()).hexdigest()
            for key,name in (('input_sha256','analysis.inp'),('case_sha256','case.json'))}
    for key,value in hashes.items():
        if result['provenance'].get(key)!=value:
            raise ValueError(f'Saved {key} differs from result provenance')
    drivers={}
    import cadquery as cq
    for name in rigid_parts:
        part=next((p for p in case['parts'] if p['name']==name),None)
        if part is None: raise ValueError(f'Unknown rigid part: {name}')
        path=directory/part['geometry']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=part['sha256']:
            raise ValueError(f'Saved geometry differs: {name}')
        drivers[name]=cq.Shape.importBrep(str(path))
    meshes=saved_meshes(case,directory/'analysis.inp')
    nodes={n:p for mesh in meshes.values() for n,p in mesh['nodes'].items()}
    parts={e:name for name,mesh in meshes.items() for e in mesh['elements']}
    found=[]
    for time,frame in iter_dat(directory/'analysis.dat'):
        match=next((t for t in requested if abs(t-time)<1e-8),None)
        if match is None:
            if time>max(requested)+1e-8: break
            continue
        us={int(row[0]):np.array(row[1:]) for row in frame['displacements']}
        if set(us)!=set(nodes) or not all(np.isfinite(v).all() for v in us.values()):
            raise ValueError('Missing or non-finite nodal displacement fields')
        poses={}
        for name,shape in drivers.items():
            translations=np.array([us[n] for n in meshes[name]['nodes']])
            shift=translations.mean(axis=0)
            if np.max(np.abs(translations-shift))>1e-8:
                raise ValueError(f'{name} is not a uniform rigid translation at {time}')
            poses[name]=shape.translate(tuple(shift))
        gaps=frame.get('relative contact displacement',[])
        stresses=frame.get('contact stress',[])
        if len(gaps)!=len(stresses): raise ValueError('Contact output row counts differ')
        if not all(np.isfinite(row).all() for row in gaps+stresses):
            raise ValueError('Non-finite contact fields')
        faces={}
        for gap,stress in zip(gaps,stresses):
            if gap[:2]!=stress[:2]: raise ValueError('Contact output row order differs')
            element,face=map(int,gap[:2])
            if face==0: raise ValueError('Face diagnostics require face-to-face contact')
            part=parts[element]
            key=(element,face)
            if key not in faces:
                con=meshes[part]['elements'][element]
                ids=[con[i] for i in FACES[face-1]]
                points=np.array([nodes[n]+us[n] for n in ids])
                samples=quadratic_face_samples(points)
                faces[key]=dict(part=part,element=element,face=face,contact_output_rows=0,
                    peak_penetration_mm=0.,peak_pressure_MPa=0.,
                    initial_node_positions_mm=[nodes[n] for n in ids],
                    deformed_samples_mm=np.asarray(samples).tolist())
            row=faces[key];row['contact_output_rows']+=1
            row['peak_penetration_mm']=max(row['peak_penetration_mm'],max(0,-gap[2]))
            row['peak_pressure_MPa']=max(row['peak_pressure_MPa'],stress[2])
        for row in faces.values():
            distances={}
            for name,solid in poses.items():
                distances[name]=signed_sample_distances(row['deformed_samples_mm'],solid)
            row['sampled_rigid_CAD']=distances
        found.append(dict(load_fraction=time,faces=list(faces.values())))
    if len(found)!=len(requested): raise ValueError('Requested output fraction is unavailable')
    return dict(**hashes,result_status=result['status'],rigid_geometry_sha256={p['name']:p['sha256'] for p in case['parts'] if p['name'] in drivers},
        frames=found,limits='Ten quadratic slave-face samples, not a maximum intersection or a new solver result. Actual contact quadrature coordinates and matched master faces are not present in CDIS/CSTR. Duplicate face identifiers are not unique point identifiers. Signed CAD distances use the saved BREP and recorded uniform translation; positive means outside, negative means inside. They do not replace native contact gaps or qualify the original result.')
