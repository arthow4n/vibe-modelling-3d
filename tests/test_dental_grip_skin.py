"""Regression for mirrored ellipsoid axes selecting the back of a finger pad."""
import importlib.util
from pathlib import Path
import mujoco
import myo_sim
import numpy as np
import pytest

PATH=Path(__file__).resolve().parents[1]/'model/dental_travel_case/grip_skin_contacts.py'
spec=importlib.util.spec_from_file_location('dental_grip_skin',PATH)
contacts=importlib.util.module_from_spec(spec);spec.loader.exec_module(contacts)

@pytest.mark.parametrize('anatomy',['myoarms','myohands'])
def test_both_skin_sides_point_out_of_distal_capsules(anatomy):
    model,data=myo_sim.load(anatomy);mujoco.mj_forward(model,data)
    for side,sign in [('r',1),('l',-1)]:
        for prefix in ('distal_thumb','distph2'):
            pad_name=prefix+'_coll_2_'+side;bone_name=prefix+'_coll_'+side
            selection=contacts.outward_pad_sign(model,data,pad_name,bone_name)
            assert selection['sign']==sign
            g=model.geom(pad_name).id;b=model.geom(bone_name).id
            axis=data.geom_xmat[g].reshape(3,3)[:,2]
            chosen=data.geom_xpos[g]+selection['sign']*axis*model.geom_size[g,2]
            rejected=data.geom_xpos[g]-selection['sign']*axis*model.geom_size[g,2]
            # Distances to the capsule's centerline independently establish the
            # selected pole is farther from the bone than the rejected pole.
            def radial_distance(point):
                rot=data.geom_xmat[b].reshape(3,3)[:,2]
                along=np.clip((point-data.geom_xpos[b])@rot,-model.geom_size[b,1],model.geom_size[b,1])
                return np.linalg.norm(point-data.geom_xpos[b]-along*rot)
            assert radial_distance(chosen)>radial_distance(rejected)+.002

@pytest.mark.parametrize('anatomy',['myoarms','myohands'])
def test_grasp_surface_is_flexor_side_not_flattened_dorsal_skin(anatomy):
    model,data=myo_sim.load(anatomy);mujoco.mj_forward(model,data)
    for side in ('r','l'):
        for digit,expected_direction in [('thumb',-1),('index',1)]:
            selected=contacts.palmar_capsule_contact(model,data,digit=digit,side=side)
            assert selected['shortening_joint_direction']==expected_direction
            normal=np.array(selected['local_normal'])
            assert np.linalg.norm(normal)==pytest.approx(1.)
            assert normal[2]==pytest.approx(0.,abs=1e-10)  # actual capsule barrel
            # A reflected local ellipsoid axis changes sign; the actual flexor
            # side stays opposite its outward-facing side on BOTH hands.
            outward=selected['flexor_dot_ellipse_positive_axis']*(1 if side=='r' else -1)
            assert outward<-.8
