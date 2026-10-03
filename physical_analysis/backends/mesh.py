"""Gmsh geometry adapter. Called only inside the isolated worker."""
from collections import Counter
import numpy as np
from execution.telemetry import operation

# Abaqus/CalculiX C3D10 local face nodes (corners followed by midsides).
FACES = ((0,1,2,4,5,6), (0,3,1,7,8,4), (1,3,2,8,9,5), (2,3,0,9,7,6))


@operation("analysis.mesh")
def mesh_part(path, size, node_offset, element_offset):
    import gmsh  # Saved-field geometry helpers need no mesher runtime libraries.
    gmsh.initialize()
    try:
        gmsh.option.setNumber('General.Terminal', 0)
        gmsh.option.setNumber('General.NumThreads', 1)
        gmsh.model.add('part')
        gmsh.model.occ.importShapes(str(path))
        gmsh.model.occ.synchronize()
        if len(gmsh.model.getEntities(3)) != 1:
            raise ValueError('Mesher expects one volume per part')
        gmsh.option.setNumber('Mesh.MeshSizeMin', size)
        gmsh.option.setNumber('Mesh.MeshSizeMax', size)
        gmsh.option.setNumber('Mesh.ElementOrder', 2)
        gmsh.model.mesh.generate(3)
        gmsh.model.mesh.optimize('HighOrder')
        tags, coords, _ = gmsh.model.mesh.getNodes()
        nodes = {int(t)+node_offset: p.tolist() for t,p in zip(tags,np.asarray(coords).reshape(-1,3))}
        kinds, elem_tags, connectivity = gmsh.model.mesh.getElements(3)
        if list(kinds) != [11]:
            raise ValueError(f'Expected quadratic tetrahedra, got {kinds}')
        elements = {}
        for t, con in zip(elem_tags[0], np.asarray(connectivity[0]).reshape(-1,10)):
            # Gmsh uses 2-3 before 1-3; CalculiX uses 1-3 before 2-3.
            order = con[[0,1,2,3,4,5,6,7,9,8]]
            elements[int(t)+element_offset] = [int(n)+node_offset for n in order]
        quality = gmsh.model.mesh.getElementQualities(elem_tags[0], 'minDetJac')
        if not len(quality) or min(quality) <= 0:
            raise ValueError('Non-positive element Jacobian; revise mesh/geometry')
        surface = exterior_faces(elements)
        return nodes, elements, surface, float(min(quality))
    finally:
        gmsh.finalize()


def exterior_faces(elements):
    """Exterior faces from the backend's C3D10 connectivity, retaining ID/order."""
    candidates = [(eid, side, [con[i] for i in indices])
                  for eid, con in elements.items() for side, indices in enumerate(FACES, 1)]
    counts = Counter(tuple(sorted(ns[:3])) for _, _, ns in candidates)
    return [(e, s, ns) for e, s, ns in candidates if counts[tuple(sorted(ns[:3]))] == 1]


def contains(region, point):
    return all((a is None or x >= a-region['tolerance_mm']) and
               (b is None or x <= b+region['tolerance_mm'])
               for x,a,b in zip(point,region['lower'],region['upper']))


def select_nodes(selection, meshes):
    mesh = meshes[selection['part']]
    found = [n for n,p in mesh['nodes'].items() if contains(selection['region'],p)]
    if not found:
        raise ValueError(f'Empty node region: {selection}')
    return found


def select_faces(selection, meshes):
    mesh = meshes[selection['part']]
    faces = [f for f in mesh['surface'] if all(contains(selection['region'],mesh['nodes'][n]) for n in f[2])]
    if not faces:
        raise ValueError(f'Empty surface region: {selection}; select complete exterior element faces')
    return faces


def traction_weights(faces, nodes):
    """Integrate quadratic triangle shape functions (including curved faces).

    Three-point triangle quadrature, exact for planar quadratic shape functions.
    Curved boundaries use the same isoparametric integration approximation.
    """
    # Batch native quadrature; keep the original three-point rule and node order.
    quadrature=np.array(((1/6,1/6),(2/3,1/6),(1/6,2/3)))
    r,s=quadrature.T;a=1-r-s
    shape=np.stack((a*(2*a-1),r*(2*r-1),s*(2*s-1),4*a*r,4*r*s,4*s*a),axis=1)
    dr=np.stack((1-4*a,4*r-1,np.zeros(3),4*(a-r),4*s,-4*s),axis=1)
    ds=np.stack((1-4*a,np.zeros(3),4*s-1,-4*r,4*r,4*(a-s)),axis=1)
    weights={}
    for start in range(0,len(faces),4096):
        ids=np.asarray([face[2] for face in faces[start:start+4096]])
        points=np.asarray([[nodes[n] for n in face] for face in ids])
        jac=np.linalg.norm(np.cross(np.einsum('qn,fnd->fqd',dr,points),
                                   np.einsum('qn,fnd->fqd',ds,points)),axis=2)
        contributions=np.einsum('qn,fq->fn',shape,jac)/6
        unique,inverse=np.unique(ids,return_inverse=True)
        sums=np.bincount(inverse.ravel(),weights=contributions.ravel(),minlength=len(unique))
        for n,value in zip(unique,sums):weights[int(n)]=weights.get(int(n),0)+float(value)
    area=sum(weights.values())
    if area<=0:raise ValueError('Loaded surface has zero area')
    return {n:w/area for n,w in weights.items()},area
