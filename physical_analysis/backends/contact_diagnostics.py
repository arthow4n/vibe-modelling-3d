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


def contact_frames(directory, fractions=None, *, rigid_parts=()):
    """Read requested existing frames with deformed slave-face samples.

    This function is for diagnostics, including completed quality failures.
    It does not run a solver, alter completion status or qualify penetration.
    Fractions must correspond to saved output; unavailable frames fail.
    """
    from .mesh import FACES
    directory=Path(directory)
    result=json.loads((directory/'result.json').read_text())
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
                samples=list(points)
                for r,s in ((1/3,1/3),(1/6,1/6),(2/3,1/6),(1/6,2/3)):
                    a=1-r-s
                    shape=np.array([a*(2*a-1),r*(2*r-1),s*(2*s-1),4*a*r,4*r*s,4*s*a])
                    samples.append(shape@points)
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
                signed=[]
                shell=cq.Compound.makeCompound(solid.Shells())
                for point in row['deformed_samples_mm']:
                    distance=shell.distance(cq.Vertex.makeVertex(*point))
                    signed.append(-distance if solid.isInside(cq.Vector(*point),1e-7) else distance)
                distances[name]=dict(min_sampled_signed_clearance_mm=min(signed),
                    maximum_sampled_inside_depth_mm=max(0,-min(signed)))
            row['sampled_rigid_CAD']=distances
        found.append(dict(load_fraction=time,faces=list(faces.values())))
    if len(found)!=len(requested): raise ValueError('Requested output fraction is unavailable')
    return dict(**hashes,rigid_geometry_sha256={p['name']:p['sha256'] for p in case['parts'] if p['name'] in drivers},
        frames=found,limits='Ten quadratic slave-face samples, not a maximum intersection or a new solver result. Actual contact quadrature coordinates and matched master faces are not present in CDIS/CSTR. Duplicate face identifiers are not unique point identifiers. Signed CAD distances use the saved BREP and recorded uniform translation; positive means outside, negative means inside. They do not replace native contact gaps or qualify the original result.')
