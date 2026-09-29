import json
import cadquery as cq
from physical_analysis import AnalysisCase, Material, Region
from physical_analysis.motion import rigid_driver_clearance

M=Material('fixture',1200,.3,'Explicit numerical fixture assumption')

def drivers():
    c=AnalysisCase('drivers')
    c.add_part('fixed',cq.Workplane('XY').box(2,2,2,centered=False),material=M,mesh_size_mm=1)
    c.add_part('moving',cq.Workplane('XY').box(2,2,2,centered=False).translate((4,0,0)),material=M,mesh_size_mm=1)
    c.fix('fixed')
    return c

def test_crossing_rigid_drivers_rejected_before_solver(tmp_path):
    c=drivers().prescribe_motion('moving',displacement_mm=(-5,0,0))
    r=c.run(tmp_path/'crossing')
    assert r.status=='invalid_rigid_motion' and not r.completed
    assert not (tmp_path/'crossing/analysis.inp').exists()
    report=json.loads((tmp_path/'crossing/rigid_driver_clearance.json').read_text())
    assert not report['ok'] and report['pairs'][0]['first_sampled_overlap']['intersection_mm3']>0

def test_progress_knots_include_out_and_return_not_only_endpoints():
    c=drivers().prescribe_motion('moving',displacement_mm=(-4,0,0),progress=((0,0),(.2,1),(1,0)))
    assert not rigid_driver_clearance(c)['ok']

def test_staged_clear_path_and_minimum_sampled_gap():
    c=drivers().prescribe_motion('moving',displacement_mm=(0,0,5),progress=((0,0),(.5,1),(1,1)))
    r=rigid_driver_clearance(c)
    assert r['ok'] and r['pairs'][0]['minimum_sampled_gap_mm']==2

def test_partial_face_motion_is_not_mistaken_for_a_rigid_part():
    c=drivers().prescribe_motion('moving',Region.plane('x',6),displacement_mm=(-5,0,0))
    assert rigid_driver_clearance(c)['pairs']==[]
