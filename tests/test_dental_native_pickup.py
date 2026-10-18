"""Planar native witness must distinguish overlap, gap and face ordering."""
import numpy as np
import pytest
from model.dental_travel_case.retention_native_pickup import triangle_intersection_area


def test_planar_triangle_capture_and_disjoint_control():
    triangle = np.array(((0., 0.), (2., 0.), (0., 2.)))
    shifted = triangle + (1., 0.)
    assert triangle_intersection_area(triangle, triangle) == pytest.approx(2.)
    assert triangle_intersection_area(triangle, triangle[::-1]) == pytest.approx(2.)
    assert triangle_intersection_area(triangle, shifted) == pytest.approx(.5)
    assert triangle_intersection_area(shifted, triangle) == pytest.approx(.5)
    assert triangle_intersection_area(triangle, triangle+(3., 0.)) == 0
