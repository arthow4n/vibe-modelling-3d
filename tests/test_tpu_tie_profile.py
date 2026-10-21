"""Prevent pending-wire transforms from leaving a tie short of a skin."""
from pathlib import Path
import importlib.util
import sys

import cadquery as cq
import pytest

SOURCE = Path(__file__).resolve().parents[1] / 'model/tpu_damping_box/tie_surface_design.py'
SPEC = importlib.util.spec_from_file_location('tpu_tie_profile_test_design', SOURCE)
design = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = design
SPEC.loader.exec_module(design)


@pytest.mark.parametrize('name', ['T05','T09','T13','T08','T12','T16'])
def test_straight_tie_reaches_both_core_faces(name):
    v = design.variant_named(name)
    solid = design.tie_profile(v).extrude(.8).val()
    for y in (.05*v.core, .5*v.core, .95*v.core):
        assert solid.isInside(cq.Vector(0,y,.4),1e-6)


def test_translating_pending_wire_is_the_rejected_recipe():
    broken = (cq.Workplane('XY').rect(.8,.8).translate((0,.3,0)).extrude(.8).val())
    assert not broken.isInside(cq.Vector(0,.57,.4),1e-6)
