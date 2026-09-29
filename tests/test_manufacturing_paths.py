from physical_analysis.manufacturing import orca_linear_paths
import pytest


def test_layer_segments_keep_position_width_role_and_relative_extrusion(tmp_path):
    p=tmp_path/'slice.gcode'
    p.write_text('G90\nM83\nG0 X10 Y20 Z.2\n;LAYER_CHANGE\n;TYPE:Inner wall\n;WIDTH:0.45\nG1 X12 E.1\nG1 E-1\nG0 Y22\n;TYPE:Support interface\nG1 X10 E.2\n')
    assert list(orca_linear_paths(p))==[(10,20,12,20,.2,.45,'Inner wall'),(12,22,10,22,.2,.45,'Support interface')]


@pytest.mark.parametrize('unsupported',['M82','G91','G2 X12 Y20 E1'])
def test_incompatible_path_modes_fail_instead_of_inventing_paths(tmp_path,unsupported):
    p=tmp_path/'slice.gcode';p.write_text(';LAYER_CHANGE\n'+unsupported+'\n')
    with pytest.raises(ValueError): list(orca_linear_paths(p))
