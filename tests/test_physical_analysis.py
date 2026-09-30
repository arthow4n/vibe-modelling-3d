"""Numerical acceptance and failure-path tests for the physical question API.

These run the real installed solver. Missing dependencies fail with an actionable
result; do not silently skip the evidence used to qualify a backend.
"""
import json
import math
from pathlib import Path
import pytest
import cadquery as cq
from physical_analysis import AnalysisCase, Material, Region

MATERIAL = Material('benchmark',1200,.3,'Explicit numerical benchmark, not filament data')


def beam(mesh=2, nonlinear=False):
    c=AnalysisCase('cantilever',nonlinear=nonlinear)
    c.add_part('beam',cq.Workplane('XY').box(40,8,2,centered=False),material=MATERIAL,mesh_size_mm=mesh)
    c.fix('beam',Region.plane('x',0))
    return c


def test_interrupt_stops_isolated_worker_and_retains_failure(tmp_path, monkeypatch):
    from physical_analysis.backends import structural
    killed=[]
    class InterruptedWorker:
        pid=123456
        calls=0
        def wait(self, timeout=None):
            self.calls+=1
            if self.calls==1:
                raise KeyboardInterrupt
            return -9
    worker=InterruptedWorker()
    def start_worker(*args,**kwargs):
        (kwargs['cwd']/'run_metadata.json').write_text(json.dumps({'backend':'CalculiX','input_sha256':'known-native-input'}))
        return worker
    monkeypatch.setattr(structural.subprocess,'Popen',start_worker)
    monkeypatch.setattr(structural.os,'killpg',lambda pid,sig: killed.append((pid,sig)))
    with pytest.raises(KeyboardInterrupt):
        beam().run(tmp_path/'interrupted')
    assert killed==[(worker.pid,structural.signal.SIGKILL)]
    assert worker.calls==2
    result=json.loads((tmp_path/'interrupted/result.json').read_text())
    assert result['status']=='interrupted' and not result['completed']
    assert 'worker and solver stopped' in result['errors'][0]
    assert result['provenance']['input_sha256']=='known-native-input'


def test_beam_refinement_and_force_balance(tmp_path):
    results=[]
    expected=.1*40**3/(3*1200*(8*2**3/12))
    for size in (2,1):
        c=beam(size)
        c.apply_force('beam',Region.plane('x',40),force_N=(0,0,-.1))
        r=c.run(tmp_path/f'mesh{size}').require_completed()
        assert r.metrics['max_displacement_mm']==pytest.approx(expected,rel=.04)
        assert r.metrics['peak_reaction_force_N']['BC0']==pytest.approx(.1,rel=.001)
        assert r.metrics['force_balance_relative']<1e-5
        results.append(r.metrics['max_displacement_mm'])
    assert abs(results[1]-results[0])/results[1]<.02


def test_mesh_reuse_holds_native_mesh_fixed_and_rejects_changed_inputs(tmp_path):
    source=tmp_path/'source'
    c=beam(nonlinear=False)
    c.apply_force('beam',Region.plane('x',40),force_N=(0,0,-.1))
    first=c.run(source).require_completed()
    c.max_increment=.05
    reused=c.run(tmp_path/'reused',mesh_from=source).require_completed()
    assert reused.provenance['mesh_reuse']['input_sha256']==first.provenance['input_sha256']
    assert reused.metrics['max_displacement_mm']==pytest.approx(first.metrics['max_displacement_mm'],rel=1e-7)
    # Motion resolution may change, but native nodes/elements remain identical.
    decks=[(p/'analysis.inp').read_text().split('*STATIC')[0] for p in (source,tmp_path/'reused')]
    assert decks[0]==decks[1]
    assert (tmp_path/'reused/mesh_source.inp').read_bytes()==(source/'analysis.inp').read_bytes()
    from physical_analysis.evidence import retain_run
    archive=retain_run(tmp_path/'reused',tmp_path/'archive')
    assert (archive/'mesh_source.inp.gz').is_file()
    assert (archive/'mesh_source_case.json').is_file()
    c=beam(mesh=1,nonlinear=False)
    rejected=c.run(tmp_path/'changed_size',mesh_from=source)
    assert not rejected.completed and 'geometry or mesh settings differ' in str(rejected.errors)
    c=beam(nonlinear=False)
    c.parts['beam'].shape=c.parts['beam'].shape.translate((0,0,.1))
    rejected=c.run(tmp_path/'changed_geometry',mesh_from=source)
    assert not rejected.completed and 'geometry or mesh settings differ' in str(rejected.errors)
    (source/'analysis.inp').write_bytes((source/'analysis.inp').read_bytes()+b'\n')
    rejected=beam().run(tmp_path/'changed_deck',mesh_from=source)
    assert not rejected.completed and 'source identity differs' in str(rejected.errors)


def test_prescribed_flexure_force_and_strain(tmp_path):
    c=beam(nonlinear=True)
    c.prescribe_motion('beam',Region.plane('x',40),displacement_mm=(None,None,1))
    r=c.run(tmp_path/'flexure').require_completed()
    # End face is translated in z but free in x/y: it may rotate in bending.
    assert r.metrics['peak_reaction_force_N']['BC1']==pytest.approx(.3,rel=.06)
    assert r.metrics['max_abs_principal_strain']==pytest.approx(3*2/(2*40**2),rel=.25)
    assert len(r.history)>=10


def contact_case(motion=.02, penalty=120000):
    c=AnalysisCase('contact',max_increment=.1)
    m=Material('uniaxial',1200,0,'Poisson-zero uniaxial benchmark')
    c.add_part('block',cq.Workplane('XY').box(2,2,4,centered=False).translate((0,0,.01)),material=m,mesh_size_mm=.8)
    c.add_part('floor',cq.Workplane('XY').box(4,4,1,centered=False).translate((-1,-1,-1)),material=m,mesh_size_mm=1)
    c.fix('floor').constrain('block',displacement_mm=(0,0,None))
    c.prescribe_motion('block',Region.plane('z',4.01),displacement_mm=(None,None,-motion))
    c.contact('block',Region.plane('z',.01),'floor',Region.plane('z',0),penalty_N_mm3=penalty)
    return c


def test_contact_engagement_penalty_and_open_gap(tmp_path):
    r=contact_case().run(tmp_path/'contact').require_completed()
    assert r.metrics['contact_detected'] is True
    assert r.metrics['peak_reaction_force_N']['BC2']==pytest.approx(12,rel=.02)
    assert r.metrics['peak_reaction_force_N']['BC1']<1e-5  # unconstrained z excluded
    assert r.metrics['max_penetration_mm']==pytest.approx(3/120000,rel=.03)
    assert r.history[0]['max_contact_pressure_MPa']==0
    softer=contact_case(penalty=12000).run(tmp_path/'soft').require_completed()
    assert softer.metrics['max_penetration_mm']>r.metrics['max_penetration_mm']*8
    assert softer.metrics['peak_reaction_force_N']['BC2']==pytest.approx(12,rel=.04)
    opened=contact_case(motion=.005).run(tmp_path/'open').require_completed()
    assert opened.metrics['contact_detected'] is False
    assert opened.metrics['peak_reaction_force_N']['BC2']<1e-5


def test_empty_and_conflicting_regions_fail(tmp_path):
    c=beam()
    c.apply_force('beam',Region.plane('x',90),force_N=(0,0,1))
    r=c.run(tmp_path/'empty')
    assert not r.completed and 'Empty surface region' in str(r.errors)
    c=beam()
    c.prescribe_motion('beam',Region.plane('x',0),displacement_mm=(0,0,1))
    r=c.run(tmp_path/'conflict')
    assert not r.completed and 'Conflicting constraints' in str(r.errors)


def test_missing_solver_timeout_and_no_overwrite(tmp_path,monkeypatch):
    c=beam()
    monkeypatch.setenv('CALCULIX_COMMAND','/nonexistent/calculix')
    r=c.run(tmp_path/'missing')
    assert not r.completed
    assert (tmp_path/'missing/result.json').exists()
    with pytest.raises(FileExistsError): c.run(tmp_path/'missing')
    c.timeout_seconds=.01
    r=c.run(tmp_path/'timeout')
    assert r.status=='timeout' and not r.completed


def test_validation():
    for value in (0,-1,math.nan,math.inf):
        with pytest.raises(ValueError): Material('bad',value,.3,'test')
    with pytest.raises(ValueError): Region.plane('q',1)
    with pytest.raises(ValueError): AnalysisCase('../escape')
    with pytest.raises(ValueError): beam().fix('absent')


def test_partial_result_parser(tmp_path):
    # Parser must preserve the actual final fraction, never manufacture time=1.
    from physical_analysis.backends.worker import parse_dat
    path=tmp_path/'partial.dat'
    path.write_text(' displacements (vx,vy,vz) for set ALLN and time 0.5\n\n 1 0 0 0\n')
    assert max(parse_dat(path))==.5


def test_streamed_frames_group_fields_without_mixing_times(tmp_path):
    from physical_analysis.backends.worker import iter_dat
    path=tmp_path/'frames.dat'
    path.write_text(' displacements (vx,vy,vz) for set ALLN and time 0.2\n 1 0 1 0\n'
                    ' forces (fx,fy,fz) for set ALLN and time 0.2\n 1 0 2 0\n'
                    ' displacements (vx,vy,vz) for set ALLN and time 0.4\n 1 0 3 0\n')
    frames=iter_dat(path)
    first_time,first=next(frames)
    second_time,second=next(frames)
    assert first_time==.2 and second_time==.4
    assert first['displacements'][0][2]==1 and first['forces'][0][2]==2
    assert second['displacements'][0][2]==3 and 'forces' not in second
    with pytest.raises(StopIteration): next(frames)


def test_streamed_results_reject_backwards_time(tmp_path):
    from physical_analysis.backends.worker import iter_dat
    path=tmp_path/'backwards.dat'
    path.write_text(' displacements (vx,vy,vz) for set ALLN and time 0.5\n 1 0 0 0\n'
                    ' displacements (vx,vy,vz) for set ALLN and time 0.2\n 1 0 0 0\n')
    with pytest.raises(ValueError,match='not increasing'): list(iter_dat(path))


def test_three_parts_named_regions_and_limits(tmp_path):
    c=AnalysisCase('three_parts',nonlinear=False)
    material=Material('limit',1200,.3,'deliberately low acceptance threshold',1e-5)
    for i in range(3):
        c.add_part(f'p{i}',cq.Workplane('XY').box(10,2,2,centered=False).translate((0,i*5,0)),material=material,mesh_size_mm=1)
        c.fix(f'p{i}',Region.plane('x',0),name=f'root{i}')
        c.apply_force(f'p{i}',Region.plane('x',10),force_N=(0,0,-.1*(i+1)))
    r=c.run(tmp_path/'three').require_completed()
    assert set(r.metrics['max_strain_by_part'])=={'p0','p1','p2'}
    for i in range(3):
        assert r.metrics['peak_reaction_force_N'][f'root{i}']==pytest.approx(.1*(i+1),rel=.001)
    assert all(x['passes'] is False for x in r.check_strain_limits().values())
    assert all('nodes' not in x for x in r.provenance['regions'].values())


def test_observations_and_scalar_screens(tmp_path):
    from physical_analysis.screening import rectangular_cantilever
    from physical_analysis.studies import compare_results
    c=beam(nonlinear=False)
    c.prescribe_motion('beam',Region.plane('x',40),displacement_mm=(None,None,1),name='tip')
    c.observe('beam',Region.plane('x',40),name='tip')
    r=c.run(tmp_path/'observe').require_completed()
    assert r.metrics['observations']['tip']['mean_mm'][2]==pytest.approx(1)
    assert r.metrics['peak_motion_force_N']['tip']==pytest.approx(.3,rel=.06)
    assert compare_results(r,r,metrics=['peak_motion_force_N.tip'])['peak_motion_force_N.tip']['passes']
    s=rectangular_cantilever(length_mm=40,width_mm=8,thickness_mm=2,youngs_modulus_MPa=1200,tip_force_N=.1)
    assert s['tip_displacement_mm']==pytest.approx(1/3)
    assert s['root_strain']==pytest.approx(.000625)


def test_unknown_solver_parameter_is_failure(tmp_path,monkeypatch):
    executable=tmp_path/'fake_ccx'
    executable.write_text('#!/bin/sh\necho "*WARNING reading *CONTACT PAIR: parameter not recognized:"\necho "Job finished"\n')
    executable.chmod(0o755)
    monkeypatch.setenv('CALCULIX_COMMAND',str(executable))
    r=beam().run(tmp_path/'unknown')
    assert not r.completed and r.status=='failed'
    assert 'parameter not recognized' in str(r.warnings)


def test_contact_drives_flexure_and_penetration_guard(tmp_path):
    from dataclasses import replace
    c=beam(mesh=1.5,nonlinear=True)
    c.add_part('pusher',cq.Workplane('XY').box(2,8,2,centered=False).translate((38,0,2.1)),material=MATERIAL,mesh_size_mm=1.5)
    c.prescribe_motion('pusher',displacement_mm=(0,0,-1.1),name='push')
    c.contact('beam',Region(lower=(38,0,2),upper=(40,8,2)),
              'pusher',Region.plane('z',2.1),penalty_N_mm3=60000)
    r=c.run(tmp_path/'contact_flexure').require_completed()
    assert r.metrics['contact_detected']
    assert r.metrics['peak_motion_force_N']['push']==pytest.approx(.34,rel=.2)
    c=contact_case()
    c.contacts[0]=replace(c.contacts[0],penetration_limit_mm=1e-6)
    r=c.run(tmp_path/'penetration')
    assert not r.completed and r.status=='quality_failed'
    assert 'penetration' in str(r.errors).lower()


def test_surface_contact_compression_and_gap(tmp_path):
    """Qualify pressure/penetration reporting for the snap's new formulation."""
    from dataclasses import replace
    for motion, engaged in ((.02, True), (.005, False)):
        c=contact_case(motion=motion)
        c.contacts[0]=replace(c.contacts[0],discretization='surface_to_surface')
        r=c.run(tmp_path/f'surface_{motion}').require_completed()
        assert r.metrics['contact_detected'] is engaged
        if engaged:
            assert r.metrics['peak_motion_force_N']['BC2']==pytest.approx(12,rel=.03)
            assert r.metrics['max_penetration_mm']==pytest.approx(3/120000,rel=.05)
            from physical_analysis.diagnostics import contact_frames
            directory=tmp_path/f'surface_{motion}'
            diagnostics=contact_frames(directory,[1],rigid_parts=['floor'])
            faces=diagnostics['frames'][0]['faces']
            assert max(f['peak_penetration_mm'] for f in faces)==pytest.approx(r.metrics['max_penetration_mm'])
            assert max(f['peak_pressure_MPa'] for f in faces)==pytest.approx(3,rel=.03)
            # Native output has multiple rows per face; retaining those rows
            # must not accidentally pair one quadrature gap with another force.
            assert any(f['contact_output_rows']>1 for f in faces)
            for face in faces:
                assert len(face['deformed_samples_mm'])==10
                assert face['sampled_rigid_CAD']['floor']['maximum_sampled_inside_depth_mm']==pytest.approx(3/120000,rel=.05)
            with pytest.raises(ValueError,match='unavailable'):
                contact_frames(directory,[.999])
            with pytest.raises(ValueError,match='not a uniform rigid translation'):
                contact_frames(directory,[1],rigid_parts=['block'])
            # Read-only diagnostics cannot silently attach fields to changed
            # geometry or a different native input.
            before=(directory/'part_1.brep').read_bytes()
            (directory/'part_1.brep').write_bytes(before+b'\n')
            with pytest.raises(ValueError,match='geometry differs'):
                contact_frames(directory,[1],rigid_parts=['floor'])
            (directory/'part_1.brep').write_bytes(before)
            before=(directory/'analysis.inp').read_bytes()
            (directory/'analysis.inp').write_bytes(before+b'\n')
            with pytest.raises(ValueError,match='differs from result provenance'):
                contact_frames(directory,[1])
            (directory/'analysis.inp').write_bytes(before)
        else:
            assert r.metrics['peak_motion_force_N']['BC2']<1e-5
    with pytest.raises(ValueError, match='discretization'):
        c.contact('block',Region(),'floor',Region(),penalty_N_mm3=1,discretization='unknown')


def test_motion_cycle_preserves_contact_then_unloads(tmp_path):
    """Compression/release in one solve: amplitude, force sign, recovery, balance."""
    from dataclasses import replace
    c=contact_case()
    c.contacts[0]=replace(c.contacts[0],discretization='surface_to_surface')
    c.constraints[-1]=replace(c.constraints[-1],displacement_mm=(0,0,-.02),progress=((0,0),(.5,1),(1,0)))
    # Zero-valued DOFs remain compatible with existing constant supports even
    # when the moving constraint has a reversing progress curve.
    c.observe('block',Region.plane('z',4.01),name='top')
    r=c.run(tmp_path/'cycle').require_completed()
    assert r.metrics['peak_motion_force_N']['BC2']==pytest.approx(12,rel=.03)
    assert abs(r.metrics['observations']['top']['mean_mm'][2])<1e-8
    assert r.metrics['max_force_balance_relative']<.001
    assert r.history[-1]['max_contact_pressure_MPa']<1e-8
    assert any(h['motion_force_N']['BC2']>1 for h in r.history if h['load_fraction']<.5)
    assert any(h['motion_force_N']['BC2']<-1 for h in r.history if .5<h['load_fraction']<.75)
    # Result extraction can be repaired without rerunning this expensive solve.
    # The private recovery path requires byte-identical regenerated input.
    import subprocess
    import sys
    from physical_analysis.backends.structural import runtime_environment
    directory=tmp_path/'cycle'
    before=(directory/'analysis.inp').read_bytes()
    recovered=subprocess.run([sys.executable,'-m','physical_analysis.backends.worker',
        str(directory),'--postprocess-only'],env=runtime_environment(),capture_output=True,text=True)
    assert recovered.returncode==0, recovered.stderr
    answer=json.loads((directory/'answer.json').read_text())
    assert answer['completed'] and answer['provenance']['postprocess_only']
    assert answer['metrics']['peak_motion_force_N']==r.metrics['peak_motion_force_N']
    # Recovery preserves all numerical decisions, not just a force summary.
    centroid='max_strain_element_centroid_mm'
    assert {k:v for k,v in answer['metrics'].items() if k!=centroid}=={k:v for k,v in r.metrics.items() if k!=centroid}
    assert answer['metrics'][centroid]==pytest.approx(r.metrics[centroid],abs=1e-8)
    assert answer['history']==r.history
    assert (directory/'analysis.inp').read_bytes()==before
    (directory/'analysis.inp').write_bytes(before+b'\n')
    rejected=subprocess.run([sys.executable,'-m','physical_analysis.backends.worker',
        str(directory),'--postprocess-only'],env=runtime_environment(),capture_output=True,text=True)
    assert rejected.returncode!=0 and 'differs from saved input' in rejected.stderr
    assert (directory/'analysis.inp').read_bytes()==before+b'\n'
    for progress in (((0,0),(.5,1)), ((0,1),(1,0)), ((0,0),(.8,1),(.7,0),(1,0))):
        with pytest.raises(ValueError,match='progress'):
            beam().prescribe_motion('beam',displacement_mm=(0,0,1),progress=progress)


def test_fortran_three_digit_exponents_preserve_fields(tmp_path):
    from physical_analysis.backends.worker import parse_dat, solver_number
    assert solver_number('3.732985-100')==pytest.approx(3.732985e-100,abs=0)
    assert solver_number('-9.960957-100')==pytest.approx(-9.960957e-100,abs=0)
    assert solver_number('1.0D+003')==1000
    path=tmp_path/'residual.dat'
    path.write_text(' strains (exx,eyy,ezz,exy,exz,eyz) for set ALLE and time 1.0\n'
                    ' 1781 2 -3.623533E-94 1.405042E-94 1.363908E-94 -2.432368E-95 -9.779253E-95 3.732985-100\n')
    frames=parse_dat(path)
    assert len(frames[1]['strains'])==1
    assert frames[1]['strains'][0][-1]==pytest.approx(3.732985e-100,abs=0)


def test_circular_cam_screen_against_sampled_contact_geometry():
    from physical_analysis.screening import circular_cam_detent
    k,r,g=2.3,4.8,4.0
    answer=circular_cam_detent(stiffness_N_mm=k,radius_sum_mm=r,transverse_spacing_mm=g)
    # Independent angular geometry/spring-force projection over the contact arc.
    forces=[]
    for i in range(10001):
        angle=math.acos(g/r)*i/10000
        spring_travel=r*math.cos(angle)-g
        forces.append(k*spring_travel*math.tan(angle))
    assert answer['peak_slide_force_N']==pytest.approx(max(forces),rel=1e-6)
    assert answer['maximum_spring_travel_mm']==pytest.approx(.8)
    gap=circular_cam_detent(stiffness_N_mm=k,radius_sum_mm=r,transverse_spacing_mm=5)
    assert not gap['contact_possible'] and gap['peak_slide_force_N']==0
    with pytest.raises(ValueError):
        circular_cam_detent(stiffness_N_mm=k,radius_sum_mm=r,transverse_spacing_mm=0)
