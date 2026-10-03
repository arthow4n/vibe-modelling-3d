from physical_analysis.manufacturing import orca_linear_paths,section_coverage
import math
import pytest


def test_layer_segments_keep_position_width_role_and_relative_extrusion(tmp_path):
    p=tmp_path/'slice.gcode'
    p.write_text('G90\nM83\nG0 X10 Y20 Z.2\n;LAYER_CHANGE\n;TYPE:Inner wall\n;WIDTH:0.45\nG1 X12 E.1\nG1 E-1\nG0 Y22\n;TYPE:Support interface\nG1 X10 E.2\n')
    assert list(orca_linear_paths(p))==[(10,20,12,20,.2,.45,'Inner wall'),(12,22,10,22,.2,.45,'Support interface')]


def test_spatial_paths_keep_spiral_start_z_after_non_deposited_height_change(tmp_path):
    p=tmp_path/'spiral.gcode'
    p.write_text('G90\nM83\nG0 X1 Y2 Z.2\n;LAYER_CHANGE\n;TYPE:Outer wall\n'
                 ';WIDTH:.42\nG1 X3 Y4 Z.25 E.1\nG1 Z.3\nG1 X5 Y6 Z.35 E.1\n')
    assert list(orca_linear_paths(p,spatial=True))==[
        (1,2,.2,3,4,.25,.42,'Outer wall'),(3,4,.3,5,6,.35,.42,'Outer wall')]
    assert list(orca_linear_paths(p))==[
        (1,2,3,4,.25,.42,'Outer wall'),(3,4,5,6,.35,.42,'Outer wall')]


@pytest.mark.parametrize('unsupported',['M82','G91','G2 X12 Y20 E1'])
def test_incompatible_path_modes_fail_instead_of_inventing_paths(tmp_path,unsupported):
    p=tmp_path/'slice.gcode';p.write_text(';LAYER_CHANGE\n'+unsupported+'\n')
    with pytest.raises(ValueError): list(orca_linear_paths(p))


def test_section_unions_duplicate_strokes_and_keeps_real_gap():
    a=(-1,-.3,1,-.3,.2,.4,'Inner wall')
    b=(-1,.3,1,.3,.2,.4,'Outer wall')
    support=(-1,0,1,0,.2,.4,'Support interface')
    other_layer=(-1,0,1,0,.4,.4,'Inner wall')
    r=section_coverage([a,a,b,support,other_layer],x_mm=0,z_mm=.2,span_mm=(-1,1))
    assert r['filled_width_mm']==pytest.approx(.8)
    assert r['internal_gap_mm']==pytest.approx(.2)
    assert r['uncovered_width_mm']==pytest.approx(1.2)


def test_parallel_section_includes_finite_rounded_stroke():
    r=section_coverage([(0,-1,0,1,.2,.4,'Inner wall')],x_mm=.1,z_mm=.2,span_mm=(-2,2))
    half=math.sqrt(.2**2-.1**2)
    assert r['intervals_mm'][0]==pytest.approx([-1-half,1+half])
    assert r['internal_gap_mm']==0


def test_diagonal_section_and_horizontal_endpoint_cap():
    diagonal=section_coverage([(-1,-1,1,1,.2,.4,'Inner wall')],x_mm=0,z_mm=.2,span_mm=(-1,1))
    assert diagonal['filled_width_mm']==pytest.approx(.4*math.sqrt(2))
    cap=section_coverage([(-1,0,1,0,.2,.4,'Inner wall')],x_mm=1.1,z_mm=.2,span_mm=(-1,1))
    assert cap['filled_width_mm']==pytest.approx(2*math.sqrt(.2**2-.1**2))
    with pytest.raises(ValueError): section_coverage([],x_mm=0,z_mm=.2,span_mm=(1,0))
