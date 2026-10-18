"""A nodal clearance screen can miss a curved quadratic-face crossing."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
from retention_root_study import quadratic_face_coordinate_bounds


def test_quadratic_face_crossing_hidden_between_clear_nodes():
    # Edge endpoints are0/1 and its midpoint is1. The quadratic interpolation
    # along that edge is -2*t²+3*t, reaching1.125 at t=.75. Every node is below
    # a liner at1.1, but the actual quadratic edge passes through the liner.
    nodal_x=[0.,1.,0.,1.,.5,0.]
    liner_x=1.1
    assert max(nodal_x)<liner_x
    actual_edge_x=-2*.75**2+3*.75
    assert actual_edge_x>liner_x
    lower,upper=quadratic_face_coordinate_bounds(nodal_x)
    assert lower<=actual_edge_x<=upper
    assert liner_x-upper<0


def test_separated_linear_faces_keep_their_exact_coordinate_bounds():
    # A linear field on the triangle is also a valid quadratic field. Its
    # extrema are its vertices, so the conservative conversion should preserve
    # an independently chosen0.3mm separating halfspace.
    leaf=[0.,1.,.5,.5,.75,.25]
    liner=[1.3,1.3,1.3,1.3,1.3,1.3]
    assert quadratic_face_coordinate_bounds(leaf)==pytest.approx((0.,1.))
    lower,_=quadratic_face_coordinate_bounds(liner)
    _,upper=quadratic_face_coordinate_bounds(leaf)
    assert lower-upper==pytest.approx(.3)
