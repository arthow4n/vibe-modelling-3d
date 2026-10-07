"""Qualify the concrete alternate contact route, including native output semantics."""
from dataclasses import replace
import json
import numpy as np
import pytest
import cadquery as cq
from physical_analysis import AnalysisCase,Material,Region
from physical_analysis.backends.febio import FebioBackend
from physical_analysis.backends.tet10_strain import Tet10GreenStrain
from test_physical_analysis import beam,contact_case,MATERIAL


def test_tet10_green_strain_rigid_rotation_and_affine_extension():
    points=np.array(((0,0,0),(1,0,0),(0,1,0),(0,0,1),(.5,0,0),(.5,.5,0),(0,.5,0),(0,0,.5),(.5,0,.5),(0,.5,.5)))
    nodes=dict(enumerate(points,1));recovery=Tet10GreenStrain(nodes,{1:list(nodes)})
    angle=.7;rotation=np.array(((np.cos(angle),-np.sin(angle),0),(np.sin(angle),np.cos(angle),0),(0,0,1)))
    displacement=lambda f:{n:f@p-p+np.array((4,3,2)) for n,p in nodes.items()}
    assert np.max(np.abs(recovery.principal(displacement(rotation))))<1e-13
    stretch=rotation@np.diag((1.02,1,1))
    assert recovery.principal(displacement(stretch))[0,:,2]==pytest.approx([(.02+.02**2/2)]*8)
    with pytest.raises(ValueError,match='deformed'):
        recovery.principal(displacement(np.diag((-1,1,1))))


@pytest.mark.parametrize('two_pass',[False,True])
def test_febio_contact_onset_open_gap_cycle_and_penalty_quality(tmp_path,two_pass):
    backend=FebioBackend(two_pass=two_pass)
    for label,motion,cycle in (('open',.005,False),('close',.02,False),('cycle',.02,True)):
        c=contact_case(motion)
        c.contacts[0]=replace(c.contacts[0],discretization='surface_to_surface')
        if cycle:c.constraints[-1]=replace(c.constraints[-1],progress=((0,0),(.5,1),(1,0)))
        c.observe('block',Region.plane('z',4.01),name='top')
        r=c.run(tmp_path/label,backend=backend).require_completed()
        assert r.metrics['contact_detected'] is (motion>.01)
        assert r.metrics['max_force_balance_relative']<1e-6
        assert r.metrics['max_strain_recovery_mean_discrepancy']<1e-8
        # No reaction while the real gap remains open. Mortar exploratory
        # runs failed this condition despite a plausible final force.
        assert all(abs(h['motion_force_N']['BC2'])<1e-6 for h in r.history if 0<h['load_fraction']<(.25 if cycle else .5))
        assert r.metrics['peak_motion_force_N']['BC2']==pytest.approx(12 if motion>.01 else 0,abs=.06)
        if label=='close':
            from physical_analysis.diagnostics import contact_frames
            data=contact_frames(tmp_path/label,[1],rigid_parts=['floor'])
            frame=data['frames'][0]
            assert frame['selected_face_count']>0
            assert frame['sampled_rigid_CAD']['floor']['maximum_sampled_inside_depth_mm']<1e-5
            witness=frame['native_planar_master_witnesses']['floor']
            assert witness is not None
            assert abs(witness['outward_signed_plane_distance_mm'])<1e-5
            # A long-running native solve may have complete accepted fields
            # and frozen identity before it has a final result. Explicit-frame
            # inspection must preserve that distinction and never promote it.
            result_path=tmp_path/label/'result.json';saved=result_path.read_bytes()
            result_path.unlink()
            partial=contact_frames(tmp_path/label,[1],rigid_parts=['floor'])
            assert partial['result_status']=='no_final_result'
            assert not result_path.exists()
            with pytest.raises(ValueError,match='No saved history'):
                contact_frames(tmp_path/label,rigid_parts=['floor'])
            result_path.write_bytes(saved)
            input_path=tmp_path/label/'analysis.feb';before=input_path.read_bytes()
            input_path.write_bytes(before+b'\n')
            with pytest.raises(ValueError,match='differs from result provenance'):
                contact_frames(tmp_path/label,[1],rigid_parts=['floor'])
            input_path.write_bytes(before)
        if cycle:
            assert abs(r.metrics['observations']['top']['mean_mm'][2])<1e-8
            assert r.history[-1]['contact_area_mm2']==0
            assert any(h['motion_force_N']['BC2']>1 for h in r.history if 0<h['load_fraction']<.5)
            assert any(h['motion_force_N']['BC2']<-1 for h in r.history if .5<h['load_fraction']<.75)
            from physical_analysis.progress import run_progress
            progress=run_progress(tmp_path/label)
            assert progress['last_converged_fraction']==pytest.approx(1)
            assert progress['converged_frames']==len(r.history)
            assert progress['completed']
    c=contact_case(penalty=120)
    c.contacts[0]=replace(c.contacts[0],discretization='surface_to_surface',penetration_limit_mm=.00001)
    r=c.run(tmp_path/'soft',backend=FebioBackend(augmented_lagrange=False))
    assert r.status=='quality_failed' and not r.completed
    assert r.metrics['max_penetration_mm']>.00001


def test_febio_bending_contact_recovery_and_strain_screen(tmp_path):
    c=beam(mesh=1.5,nonlinear=True)
    c.parts['beam'].material=Material('provisional',1200,.3,'Deliberately low screen',.00001)
    c.add_part('pusher',cq.Workplane('XY').box(2,8,2,centered=False).translate((38,0,2.1)),material=MATERIAL,mesh_size_mm=1.5)
    c.prescribe_motion('pusher',displacement_mm=(0,0,-1.1),name='push',progress=((0,0),(.5,1),(1,0)))
    c.contact('beam',Region(lower=(38,0,2),upper=(40,8,2)),'pusher',Region.plane('z',2.1),
              penalty_N_mm3=60000,discretization='surface_to_surface', penetration_limit_mm=.05)
    c.observe('beam',Region.plane('x',40),name='tip')
    r=c.run(tmp_path/'flexure',backend=FebioBackend()).require_completed()
    assert r.metrics['peak_motion_force_N']['push']==pytest.approx(.34,rel=.2)
    assert r.metrics['max_abs_principal_strain']==pytest.approx(.001875,rel=.3)
    # The explicit residual floor permits sub-micron elastic-return error.
    assert abs(r.metrics['observations']['tip']['mean_mm'][2])<1e-6
    assert r.check_strain_limits()['beam']['passes'] is False
    assert r.metrics['max_strain_recovery_mean_discrepancy']<1e-8
    from physical_analysis.recovery import recover_run
    recovered=recover_run(tmp_path/'flexure')
    assert recovered.provenance['postprocess_only']
    assert recovered.metrics['peak_motion_force_N']==r.metrics['peak_motion_force_N']
    from physical_analysis.evidence import retain_run
    retain_run(tmp_path/'flexure',tmp_path/'retained')
    archived=json.loads((tmp_path/'retained/result.json').read_text())
    assert archived['artifacts']['native_input']=='analysis.feb.gz'
    assert archived['provenance']['native_input_sha256']==r.provenance['native_input_sha256']


@pytest.mark.parametrize('backend',[None,FebioBackend()])
def test_union_master_keeps_independent_obstacle_motion(tmp_path,backend):
    c=contact_case()
    c.parts['floor'].shape=cq.Workplane('XY').box(2,4,1,centered=False).translate((-1,-1,-1))
    c.add_part('right',cq.Workplane('XY').box(2,4,1,centered=False).translate((1,-1,-1)),material=c.parts['floor'].material,mesh_size_mm=1)
    c.prescribe_motion('right',displacement_mm=(0,0,-.003),name='right')
    c.contacts=[]
    c.contact('block',Region.plane('z',.01),
              (c.select('floor',Region.plane('z',0)),c.select('right',Region.plane('z',0))),
              penalty_N_mm3=120000,discretization='surface_to_surface', penetration_limit_mm=.05)
    c.observe('right',Region(),name='right_pose')
    r=c.run(tmp_path/'union',backend=backend).require_completed()
    assert r.metrics['contact_detected']
    assert r.provenance['contacts'][0]['master']['parts']==['floor','right']
    assert r.history[-1]['reactions_N']['BC0'][2]>r.history[-1]['reactions_N']['right'][2]>.01
    assert r.metrics['observations']['right_pose']['mean_mm']==pytest.approx([0,0,-.003])
    assert r.metrics['max_force_balance_relative']<1e-3


def test_mortar_missing_fields_remain_explicit_failure(tmp_path):
    c=contact_case();c.contacts[0]=replace(c.contacts[0],discretization='mortar')
    r=c.run(tmp_path/'mortar')
    assert not r.completed and r.status=='unsupported_output'
    assert 'Missing contact output' in str(r.errors)
    assert r.provenance['backend']=='CalculiX'
    assert not r.metrics
