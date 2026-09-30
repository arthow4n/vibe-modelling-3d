"""Independent straight-triangle collision witness (VTK, not IPC Toolkit).

Tests all AABB-overlapping triangle pairs, plus closed-obstacle containment.
Distance search is bounded: no candidate certifies only the search lower bound.
Accepted frames only; not continuous CCD, curved FE, or global exact-CAD proof.
"""
import numpy as np


def polydata(points, triangles):
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk
    data = vtk.vtkPolyData(); vertices = vtk.vtkPoints()
    vertices.SetData(numpy_to_vtk(np.asarray(points, dtype=float), deep=True)); data.SetPoints(vertices)
    faces = vtk.vtkCellArray()
    for tri in triangles:
        faces.InsertNextCell(3, [int(n) for n in tri])
    data.SetPolys(faces)
    return data


def segment_distance(a, b, c, d):
    """Closest points of two finite segments, including parallel/end cases."""
    u = b-a; v = d-c; w = a-c
    aa=u@u; bb=u@v; cc=v@v; dd=u@w; ee=v@w
    if aa <= 1e-24 or cc <= 1e-24:
        raise ValueError('Degenerate mesh edge')
    det=aa*cc-bb*bb
    s=np.clip((bb*ee-cc*dd)/det,0,1) if det > 1e-14*aa*cc else 0.
    t=(bb*s+ee)/cc
    if t < 0:s=np.clip(-dd/aa,0,1);t=0.
    elif t > 1:s=np.clip((bb-dd)/aa,0,1);t=1.
    return float(np.linalg.norm(w+s*u-t*v))


def triangle_distance(a, b):
    import vtk
    if vtk.vtkTriangle.TrianglesIntersect(*a,*b):
        return 0.
    # Point-to-triangle distance, including edges; VTK closest point handles
    # outside barycentric projections. Edge/edge minima complete the test.
    distances=[]
    for source, target in ((a,b),(b,a)):
        cell=vtk.vtkTriangle()
        for i,p in enumerate(target):cell.GetPoints().SetPoint(i,p)
        for p in source:
            closest=[0.,0.,0.];sub=vtk.reference(0);dist=vtk.reference(0.);pc=[0.,0.,0.];weights=[0.]*3
            cell.EvaluatePosition(p,closest,sub,pc,dist,weights)
            distances.append(float(dist)**.5)
    distances += [segment_distance(a[i],a[(i+1)%3],b[j],b[(j+1)%3]) for i in range(3) for j in range(3)]
    return min(distances)


def inspect_mesh_pair(points, triangles, obstacle_points, obstacle_triangles, *, search_distance_mm=.001):
    import vtk
    from collections import Counter
    points=np.asarray(points,dtype=float);faces=np.asarray(triangles,dtype=int)
    other=np.asarray(obstacle_points,dtype=float);ofaces=np.asarray(obstacle_triangles,dtype=int)
    if (not len(faces) or not len(ofaces) or search_distance_mm <= 0 or
            not all(np.isfinite(p).all() for p in (points,other))):
        raise ValueError('Nonempty finite triangle surfaces and positive search distance required')
    data=polydata(other,ofaces);locator=vtk.vtkStaticCellLocator();locator.SetDataSet(data);locator.BuildLocator()
    crossed=[];minimum=None;candidates=0
    other_tris=other[ofaces];other_lo=other_tris.min(axis=1);other_hi=other_tris.max(axis=1)
    all_triangles=points[faces];all_lo=all_triangles.min(axis=1);all_hi=all_triangles.max(axis=1)
    relevant=np.flatnonzero(np.all(all_hi+search_distance_mm>=other.min(axis=0),axis=1)&
                           np.all(all_lo-search_distance_mm<=other.max(axis=0),axis=1))
    for i in relevant:
        a=all_triangles[i];lo=all_lo[i]-search_distance_mm;hi=all_hi[i]+search_distance_mm
        ids=vtk.vtkIdList();locator.FindCellsWithinBounds([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]],ids)
        for n in range(ids.GetNumberOfIds()):
            j=ids.GetId(n)
            if np.any(other_hi[j]<lo) or np.any(other_lo[j]>hi):
                continue
            b=other_tris[j];candidates+=1
            if vtk.vtkTriangle.TrianglesIntersect(*a,*b):
                if len(crossed)<8:crossed.append(dict(deformable_triangle=int(i),obstacle_triangle=j,
                    deformable_points_mm=a.tolist(),obstacle_points_mm=b.tolist()))
                minimum=0.
            elif minimum!=0.:
                distance=triangle_distance(a,b)
                minimum=distance if minimum is None else min(minimum,distance)
    counts=Counter(tuple(sorted((int(tri[i]),int(tri[(i+1)%3])))) for tri in ofaces for i in range(3))
    closed=all(v==2 for v in counts.values())
    contained=0
    if closed:
        samples=np.vstack((points[np.unique(faces)],points[faces].mean(axis=1)))
        inputs=polydata(samples,[]);inside=vtk.vtkSelectEnclosedPoints();inside.SetInputData(inputs)
        inside.SetSurfaceData(data);inside.SetTolerance(1e-10);inside.Update()
        contained=sum(inside.IsInside(i) for i in range(len(samples)))
    return dict(intersection_detected=bool(crossed or contained),triangle_intersection_witnesses=crossed,
        contained_vertex_or_centroid_count=contained,obstacle_surface_closed=closed,
        triangle_pairs_tested=candidates,search_distance_mm=search_distance_mm,
        minimum_distance_mm=minimum if minimum is not None and minimum <= search_distance_mm else None,
        distance_lower_bound_mm=search_distance_mm if minimum is None or minimum>search_distance_mm else minimum,
        scope='All straight-triangle pairs with overlapping expanded AABBs; closed-obstacle vertex/centroid containment. Touching counts as intersection. Bounded distance search, accepted states only; no exact CAD or continuous-path proof.')
