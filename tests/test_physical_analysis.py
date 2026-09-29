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
