"""Mechanical controls for the product-local reduction, not product acceptance."""
from dataclasses import replace
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
from retention_proxy import Leaf, rod, from_dimensions, first_capture_loss, receiver_stiffness, guide_response
import m1_design as m1
import m3_design as m3


def test_elastica_recovers_linear_eccentric_beam_at_small_load():
    leaf=Leaf(35,14,1.6,1.8,1200)
    P=1e-4
    expected=P*leaf.eccentricity*leaf.length**2/(2*leaf.rigidity)
    assert rod(leaf,P,follower=False)['inward_mm']==pytest.approx(expected,rel=1e-4)
    assert rod(leaf,P,follower=True)['inward_mm']==pytest.approx(expected,rel=1e-4)


def test_zero_eccentricity_removes_this_weakening_mechanism():
    leaf=Leaf(35,14,1.6,0,1200)
    for follow in (False,True):
        result=rod(leaf,12,follower=follow)
        assert result['inward_mm']==pytest.approx(0,abs=1e-10)
        assert result['radial_contact_force_N']==pytest.approx(0,abs=1e-10)


def test_contact_direction_changes_answer_and_refinement_is_small():
    leaf=from_dimensions(m1.D,1200)
    fixed=rod(leaf,4,follower=False)
    moving=rod(leaf,4,follower=True,points=33,tolerance=1e-6)
    refined=rod(leaf,4,follower=True,points=129,tolerance=1e-9)
    assert moving['inward_mm']>fixed['inward_mm']
    assert moving['inward_mm']==pytest.approx(refined['inward_mm'],rel=1e-5)
    assert moving['tip_angle_rad']==pytest.approx(refined['tip_angle_rad'],rel=1e-5)
    assert abs(moving['radial_contact_force_N']-4*np.tan(moving['tip_angle_rad']))<1e-7


def test_weaker_receiver_and_fit_loss_reduce_first_capture_load():
    leaf=from_dimensions(m1.D,1200)
    def threshold(k,fit):
        return first_capture_loss(leaf,engagement=1.5,fit_loss=fit,receiver_k=k,follower=True)
    assert threshold(2,.5)<threshold(20,.5)<threshold(20,0)
    assert first_capture_loss(leaf,engagement=0,fit_loss=0,receiver_k=20,follower=True)==0


def test_thicker_leaf_improves_margin_without_hardcoded_winner():
    leaf=from_dimensions(m1.D,1200)
    thick=replace(leaf,thickness=2.)
    kw=dict(engagement=1.5,fit_loss=.25,receiver_k=10,follower=True)
    assert first_capture_loss(thick,**kw)>first_capture_loss(leaf,**kw)


def test_guide_length_reduces_bearing_force_but_invalid_bending_is_visible():
    short=guide_response(m1.D,800,500,end_fixity=1,load_spread_fraction=.25)
    long=guide_response(m3.D,800,500,end_fixity=1,load_spread_fraction=.25)
    assert long['guide_reaction_N']<short['guide_reaction_N']
    assert long['joint_rotation_bound_deg']<short['joint_rotation_bound_deg']
    assert not short['within_small_bending_scope']


def test_fixed_world_proxy_independently_agrees_in_order_with_actual_cad_fem():
    # Previously retained actual-CAD fixed-plane/root stub fixture. Agreement is
    # a check of local bending representation, not a fit or contact validation.
    cases=[(m1.D,1.0462093),(m3.D,.52987438)]
    for d,actual in cases:
        predicted=rod(from_dimensions(d,1200),12,follower=False)['inward_mm']
        assert abs(predicted/actual-1)<.15
