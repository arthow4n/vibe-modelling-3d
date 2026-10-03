"""Numerical equivalence against the original quadrature and mapping policies."""
import numpy as np
import pytest
from physical_analysis.backends.mesh import traction_weights
from physical_analysis.backends.polyfem_output import map_points,Tet4GreenStrain,principal_strain


def reference_traction(faces,nodes):
    weights={}
    for _,_,ids in faces:
        points=np.array([nodes[n] for n in ids])
        for r,s in ((1/6,1/6),(2/3,1/6),(1/6,2/3)):
            a=1-r-s
            N=np.array([a*(2*a-1),r*(2*r-1),s*(2*s-1),4*a*r,4*r*s,4*s*a])
            dr=np.array([1-4*a,4*r-1,0,4*(a-r),4*s,-4*s])
            ds=np.array([1-4*a,0,4*s-1,-4*r,4*r,4*(a-s)])
            jac=np.linalg.norm(np.cross(dr@points,ds@points))
            for n,w in zip(ids,N*jac/6):weights[n]=weights.get(n,0)+float(w)
    area=sum(weights.values())
    return {n:w/area for n,w in weights.items()},area


def test_curved_traction_batch_matches_original_rule_and_shared_nodes():
    rng=np.random.default_rng(91)
    nodes={i*17+3:p for i,p in enumerate(rng.random((120,3)))}
    ids=list(nodes);faces=[(i,1,ids[(i%20)*6:(i%20)*6+6]) for i in range(5000)]
    expected,area=reference_traction(faces,nodes)
    actual,measured=traction_weights(faces,nodes)
    assert measured==pytest.approx(area,rel=1e-13)
    assert actual==pytest.approx(expected,rel=1e-12,abs=1e-15)
    assert sum(actual.values())==pytest.approx(1,abs=1e-14)
    with pytest.raises(ValueError,match='zero area'):traction_weights([],nodes)


def test_batched_mapping_preserves_exact_legacy_and_rejection():
    rng=np.random.default_rng(19);points=rng.random((1000,3));order=rng.permutation(len(points))
    assert np.array_equal(map_points(points,points[order]),np.argsort(order))
    quantized=points.astype(np.float32).astype(float)
    assert np.array_equal(map_points(points,quantized[order]),np.argsort(order))
    with pytest.raises(ValueError,match='vertices'):map_points(points,points+1e-4)


def test_prepared_strain_matches_reference_and_rejects_inversion():
    mesh={'points_mm':[[0,0,0],[1,0,0],[0,1,0],[0,0,1]],'tets':[[0,1,2,3]]}
    prepared=Tet4GreenStrain(mesh)
    for scale in (.001,.01,.2):
        d=np.asarray(mesh['points_mm'])*scale
        expected=np.full((1,3),((1+scale)**2-1)/2)
        assert prepared.principal(d)==pytest.approx(expected,abs=1e-15)
        assert principal_strain(mesh,d)==pytest.approx(expected,abs=1e-15)
    d=np.zeros((4,3));d[1,0]=-2
    with pytest.raises(ValueError,match='inverted'):prepared.principal(d)
