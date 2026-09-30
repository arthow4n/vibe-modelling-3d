"""Independent diagnostics plus opt-in real-native IPC qualification.

Run numerical tests with POLYFEM_COMMAND explicitly configured. A skipped
native test is unavailable evidence, never backend qualification.
"""
from dataclasses import replace
import json
import os
import numpy as np
import pytest
from physical_analysis.mesh_witness import inspect_mesh_pair, triangle_distance
from physical_analysis.backends.polyfem import PolyfemBackend, IPCSettings


def test_triangle_witness_crossing_without_vertex_inclusion_and_distance():
    a=np.array([[0,0,0],[1,0,0],[0,1,0]],float)
    b=np.array([[.2,-.2,-1],[.2,.8,1],[.2,1,-1]])
    assert inspect_mesh_pair(a,[[0,1,2]],b,[[0,1,2]])['intersection_detected']
    assert inspect_mesh_pair(a,[[0,1,2]],a,[[0,1,2]])['intersection_detected']
    assert triangle_distance(a,a+[0,0,.1])==pytest.approx(.1)
    near=inspect_mesh_pair(a,[[0,1,2]],a+[0,0,.1],[[0,1,2]],search_distance_mm=.2)
    assert not near['intersection_detected'] and near['minimum_distance_mm']==pytest.approx(.1)
    far=inspect_mesh_pair(a,[[0,1,2]],a+[0,0,.1],[[0,1,2]])
    assert far['minimum_distance_mm'] is None and far['distance_lower_bound_mm']==.001


def test_closed_mesh_containment_and_green_strain():
    from physical_analysis.backends.polyfem_output import principal_strain
    p=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],float)
    faces=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]]
    inner=p*.1+[.1,.1,.1]
    result=inspect_mesh_pair(inner,faces,p,faces)
    assert result['intersection_detected'] and result['contained_vertex_or_centroid_count']>0
    mesh=dict(points_mm=p.tolist(),tets=[[0,1,2,3]])
    angle=.7;rotation=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
    assert np.abs(principal_strain(mesh,p@rotation.T-p+4)).max()<1e-14
    stretch=rotation@np.diag([1.02,1,1])
    assert principal_strain(mesh,p@stretch.T-p)[0,-1]==pytest.approx(.0202)
    with pytest.raises(ValueError,match='inverted'):
        principal_strain(mesh,p*np.array([-1,1,1])-p)


def test_motion_progress_and_explicit_unsupported_features(tmp_path,monkeypatch):
    from physical_analysis.backends.polyfem_worker import progress_expression
    from physical_analysis.backends.ipc_benchmarks import compression
    points=((0,0),(.2,.5),(.5,.5),(1,0))
    expression=progress_expression(points)
    for t,expected in ((0,0),(.1,.25),(.3,.5),(.75,.25),(1,0)):
        assert eval(expression,{'__builtins__':{},'min':min,'max':max,'t':t})==pytest.approx(expected)
    monkeypatch.setenv('POLYFEM_COMMAND','/no/such/PolyFEM_bin')
    r=compression().run(tmp_path/'missing',backend=PolyfemBackend())
    assert not r.completed and 'Set POLYFEM_COMMAND' in str(r.errors)
    c=compression();c.apply_force('block',c.constraints[0].selection.region,force_N=(0,0,1))
    r=c.run(tmp_path/'unsupported',backend=PolyfemBackend())
    assert not r.completed and 'force loading unsupported' in str(r.errors)
    r=compression().run(tmp_path/'reuse',backend=PolyfemBackend(),mesh_from=tmp_path/'missing')
    assert not r.completed and 'IPC mesh source' in str(r.errors)
    with pytest.raises(ValueError):IPCSettings(unit_system='unknown')


def test_double_precision_mesh_contract(tmp_path):
    from physical_analysis.backends.polyfem_worker import write_mesh
    from physical_analysis.backends.polyfem_output import require_native_rest_mesh
    p=np.array([[32.123456789123,0,0],[1,0,0],[0,1,0],[0,0,1]])
    write_mesh(tmp_path/'part_0.mesh',dict(points_mm=p,tets=[[0,1,2,3]]),1)
    assert (tmp_path/'part_0.mesh').read_text().startswith('MeshVersionFormatted 2\n')
    assert require_native_rest_mesh(tmp_path,p,p)['maximum_rest_coordinate_shift_mm']==0
    with pytest.raises(ValueError,match='Double-precision'):
        require_native_rest_mesh(tmp_path,p,p.astype(np.float32).astype(float))


def test_intermediate_search_cannot_relax_final_equilibrium_policy():
    from physical_analysis.backends.polyfem_output import require_final_equilibrium_policy
    policy=dict(allow_out_of_iterations=False,allow_non_grad_convergence=False,grad_norm_tol=1e-8)
    native=dict(args=dict(solver=dict(nonlinear=policy,
        augmented_lagrangian=dict(nonlinear=dict(allow_out_of_iterations=True)))))
    require_final_equilibrium_policy(native,1e-6,10)
    for key in ('allow_out_of_iterations','allow_non_grad_convergence'):
        policy[key]=True
        with pytest.raises(ValueError,match='Final native equilibrium'):
            require_final_equilibrium_policy(native,1e-6,10)
        policy[key]=False
    policy['grad_norm_tol']=1e-6
    with pytest.raises(ValueError,match='tolerance exceeds'):
        require_final_equilibrium_policy(native,1e-6,10)


native=pytest.mark.skipif(not os.environ.get('POLYFEM_COMMAND'),reason='Optional external IPC CLI not configured; no qualification claimed')


@native
def test_native_open_gap_compression_units_settings_return_and_recovery(tmp_path):
    from physical_analysis.backends.ipc_benchmarks import compression
    from physical_analysis.evidence import retain_run
    from physical_analysis.recovery import recover_run
    rows=[]
    for label,motion,settings in (
        ('open',.005,IPCSettings()),('compression',.02,IPCSettings()),
        ('activation',.02,IPCSettings(activation_distance_mm=.0005)),
        ('SI',.02,IPCSettings(unit_system='SI'))):
        r=compression(motion).run(tmp_path/label,backend=PolyfemBackend(settings)).require_completed()
        assert r.metrics['independent_mesh_intersection'] is False
        assert r.metrics['max_inertia_force_N']==0
        assert r.provenance['native_mesh_mapping']['maximum_rest_coordinate_shift_mm']<1e-8
        assert r.metrics['max_force_balance_relative']<1e-4
        assert r.metrics['peak_motion_force_N']['push']==pytest.approx(12 if motion>.01 else 0,abs=.1)
        assert r.metrics['contact_detected'] is (motion>.01)
        if motion>.01:assert r.metrics['max_abs_principal_strain']==pytest.approx(.0025,rel=.05)
        else:
            assert abs(r.metrics['peak_motion_force_N']['push'])<1e-6
            assert r.metrics['max_abs_principal_strain']<1e-8
        rows.append(r)
    c=compression();c.constraints[0]=replace(c.constraints[0],progress=((0,0),(.5,1),(1,0)))
    r=c.run(tmp_path/'return',backend=PolyfemBackend()).require_completed()
    assert abs(r.metrics['observations']['bottom']['mean_mm'][2])<1e-5
    recovered=recover_run(tmp_path/'return')
    assert recovered.provenance['postprocess_only'] and recovered.metrics==r.metrics
    retain_run(tmp_path/'return',tmp_path/'archive')
    saved=json.loads((tmp_path/'archive/result.json').read_text())
    assert saved['artifacts']['geometry_witness']=='geometry_witness.json.gz'
    path=tmp_path/'return/part_0.mesh';path.write_bytes(path.read_bytes()+b'\n')
    with pytest.raises(RuntimeError,match='original result preserved'):
        recover_run(tmp_path/'return')


@native
def test_native_contact_driven_beam(tmp_path):
    from physical_analysis.backends.ipc_benchmarks import flexible_beam
    c=flexible_beam(mesh=.5);c.timeout_seconds=3600
    r=c.run(tmp_path/'beam',backend=PolyfemBackend()).require_completed()
    assert r.metrics['independent_mesh_intersection'] is False
    assert r.metrics['peak_motion_force_N']['push']==pytest.approx(.34,rel=.4)
    assert r.metrics['max_abs_principal_strain']==pytest.approx(.001875,rel=.5)
    assert abs(r.metrics['observations']['tip']['mean_mm'][2])<1e-5
    bent=min(r.history,key=lambda h:h['observations']['tip']['mean_mm'][2])
    assert bent['observations']['tip']['mean_mm'][2]<-.9
