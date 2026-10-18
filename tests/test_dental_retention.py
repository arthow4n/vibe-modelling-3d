"""Real failed-product controls: obstruction is not useful retaining land.

These regressions use authoritative M1 and M2B CAD rather than synthetic hooks.
They protect diagnostic distinctions and load coverage, not a winning design.
"""
from pathlib import Path
import copy
import json
import sys
import pytest

OBJECT=Path(__file__).resolve().parents[1]/'model/dental_travel_case'
sys.path.insert(0,str(OBJECT))
import m1_design as m1
import retention_geometry as geometry
from m2b_verification import require_guide_evidence
from retention_structure import eccentric_case, design_module, assembly_case


@pytest.fixture(scope='module')
def baseline():
    return m1.cap(m1.D).val()


def test_flat_capture_can_vanish_while_rigid_intersection_remains(baseline):
    """A generic positive-intersection checker misses the rounded-edge trap."""
    d=m1.D
    for sign in (-1,1):
        assert sum(w['area_mm2'] for w in geometry.seated_land(d,baseline,sign))>0
        land=geometry.seated_land(d,baseline,sign,radial_retraction=1.5)
        assert not land
        hook=geometry.hook_shape(d,sign,0).translate((sign*1.5,0,0))
        # At this independently specified offset the remaining rounded corner
        # still obstructs a rigid .9mm pull, despite zero flat retaining land.
        assert geometry.overlap(hook,baseline.translate((0,0,.9)))>geometry.VOLUME_EPS
        fully_retracted=geometry.hook_shape(d,sign,d.release)
        assert geometry.overlap(fully_retracted,baseline.translate((0,0,.9)))<geometry.VOLUME_EPS


def test_guide_play_is_not_automatically_free_hook_return(baseline):
    """The outer pocket skin, not only the guide, limits the seated leaf."""
    d=m1.D
    assert geometry.overlap(geometry.hook_shape(d,1,0),baseline)<geometry.VOLUME_EPS
    # Exact source has .15mm pocket outside clearance but .25mm guide allowance.
    assert geometry.overlap(geometry.hook_shape(d,1,0),baseline.translate((.25,0,0)))>geometry.VOLUME_EPS


def test_removed_hooks_do_not_inherit_unrelated_shell_obstruction(baseline):
    fixed=m1.body_fixed(m1.D).val()
    assert geometry.overlap(fixed,baseline.translate((0,0,.9)))<geometry.VOLUME_EPS


@pytest.mark.parametrize(('variant','expected_area'),(('m1',12.),('m2b',13.5)))
def test_receiving_land_traction_and_observation_cover_whole_actual_face(variant,expected_area):
    """A baseline-width selector must not truncate the wider revised hook.

    Mesh-face selection requires complete faces inside the region. Check the
    authoritative imprinted CAD face first, without relying on a particular
    triangulation that can turn an undersized region into a partial load patch.
    """
    case=eccentric_case(variant=variant,modulus=1200,mesh=1.2,load=12,
        receiving_land=True,mesh_min_size=None,mesh_curvature_points=None,
        root_stub=True)
    d=design_module(variant).D
    receiver_edge=-(d.width/2-d.receiver_wall)
    land=[face for face in case.parts['catch'].shape.val().Faces()
          if face.geomType()=='PLANE' and face.normalAt().z<-.99
          and all(abs(vertex.Center().z-d.hook_bottom)<1e-6
                  and vertex.Center().x<=receiver_edge+1e-6
                  for vertex in face.Vertices())]
    assert sum(face.Area() for face in land)==pytest.approx(expected_area,abs=1e-6)
    for selection in (case.loads[0].selection,case.observations['shoulder']):
        assert all(selection.region.contains(vertex.Center().toTuple())
                   for face in land for vertex in face.Vertices())


@pytest.mark.parametrize('variant',('m1','m2b'))
def test_crop_contact_excludes_artificial_cap_cut_face(variant):
    """A longer guide must not turn the crop's new end into a contact surface."""
    case=assembly_case(variant=variant,modulus=1200,mesh=3,travel=2.5,
        increment=.02,eccentric=0,lateral=0,crop=True,penalty=20000,
        mesh_min_size=None,mesh_curvature_points=None,grip_style='side',pickup=True)
    d=design_module(variant).D
    cap=case.parts['cap'].shape.val()
    cut_z=d.seam+d.lap+18+d.axial_play
    cut_faces=[face for face in cap.Faces() if face.geomType()=='PLANE'
               and all(abs(v.Center().z-cut_z)<1e-6 for v in face.Vertices())]
    assert cut_faces
    master=case.contacts[0].master.region
    assert not any(all(master.contains(v.Center().toTuple()) for v in face.Vertices())
                   for face in cut_faces)
    # Preserve the actual retaining floor when excluding the artificial cut.
    floors=[face for face in cap.Faces() if face.geomType()=='PLANE'
            and face.normalAt().z>.99
            and all(abs(v.Center().z-d.hook_bottom)<1e-6 for v in face.Vertices())]
    assert floors
    assert all(master.contains(v.Center().toTuple()) for face in floors for v in face.Vertices())


@pytest.fixture(scope='module')
def guide_receipt():
    return json.loads((OBJECT/'notes/retention/m2b_geometry.json').read_text())


def test_retained_guide_receipt_has_contact_witnesses(guide_receipt):
    require_guide_evidence(guide_receipt,guide_receipt['dimensions']['axial_play_mm'])


@pytest.mark.parametrize('defect', ('missing_pose','no_contact_result','null_bracket','incomplete_comparison'))
def test_overall_cad_pass_does_not_replace_missing_guide_evidence(guide_receipt,defect):
    """A successful unrelated CAD group cannot establish guide contact."""
    receipt=copy.deepcopy(guide_receipt)
    assert receipt['status']=='PASS'
    if defect=='missing_pose':
        receipt['rigid_guide_angular_freeplay'].pop(0)
    elif defect=='no_contact_result':
        receipt['rigid_guide_angular_freeplay'][0]['angle_deg']=None
    elif defect=='null_bracket':
        receipt['rigid_guide_angular_freeplay'][0]['bracket_deg']=None
    else:
        receipt['baseline_m1_guide_comparison']['m2b_same_pose_samples'].pop()
    with pytest.raises(AssertionError):
        require_guide_evidence(receipt,receipt['dimensions']['axial_play_mm'])
