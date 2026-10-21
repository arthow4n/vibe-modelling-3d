"""Qualify the native hand transforms and band/corner contact representation."""
from pathlib import Path
import sys
import mujoco
import myo_sim
import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
from grip_human_study import GripScene,Setup,fixture,build_three_line,Rotation

@pytest.fixture(scope='module')
def scene():
    return GripScene(Setup('balanced',0.,350.,1150.),build_three_line()['dimensions'],local_hands=True)


def test_imported_hand_geometry_and_limits_are_not_rescaled(scene):
    reference,_=myo_sim.load('myohands')
    assert scene.model.nq==reference.nq==46
    assert np.array_equal(scene.model.jnt_range,reference.jnt_range)
    assert np.array_equal(scene.model.jnt_axis,reference.jnt_axis)
    for name in ('distph2_coll_r','distph2_coll_l','distal_thumb_coll_r','distal_thumb_coll_l'):
        assert np.array_equal(scene.model.geom(name).size,reference.geom(name).size)
        assert np.array_equal(scene.model.geom(name).pos,reference.geom(name).pos)
        assert np.array_equal(scene.model.geom(name).quat,reference.geom(name).quat)
    assert len(scene.free)==40  # finger articulation, neutral imported wrists


def test_requested_points_are_actual_palmar_capsule_surfaces(scene):
    scene.state(scene.initial(0),0.)
    for contact in scene.contacts:
        point,normal=scene.pad(contact);g=contact['geom']
        R=scene.data.geom_xmat[g].reshape(3,3)
        local=R.T@(point-scene.data.geom_xpos[g])
        assert local[2]==pytest.approx(0.,abs=1e-12)
        assert np.linalg.norm(local[:2])==pytest.approx(scene.model.geom_size[g,0])
        assert np.linalg.norm(normal)==pytest.approx(1.)


def test_projection_reaches_full_wall_from_inside_core(scene,monkeypatch):
    c=scene.contacts[0]
    local=np.array((0.,0.,c['center']))
    world=scene.origin+scene.rotation@(local-np.array((0,0,scene.d.seam)))/1000
    monkeypatch.setattr(scene,'pad',lambda contact:(world,np.array((0.,1.,0.))))
    error,*_=scene.contact_geometry(c,0.)
    assert np.linalg.norm(error)==pytest.approx(scene.d.depth/2-.7)


def test_native_rounded_corner_does_not_fill_the_box_corner(scene):
    d=scene.d;s=mujoco.MjSpec()
    pieces=fixture(d,(50.,-30.))[:6]
    for item in pieces:
        s.worldbody.add_geom(name=item['name'],type=mujoco.mjtGeom.mjGEOM_BOX if item['shape']=='box' else mujoco.mjtGeom.mjGEOM_CYLINDER,
            pos=np.array(item['center_mm'])/1000,size=np.array(item['half_mm'])/1000,contype=0,conaffinity=0)
    probe=s.worldbody.add_geom(name='probe',type=mujoco.mjtGeom.mjGEOM_SPHERE,pos=(.037,.0255,.05),size=(.0001,0,0),contype=0,conaffinity=0)
    model=s.compile();data=mujoco.MjData(model);mujoco.mj_forward(model,data)
    def gap():return min(mujoco.mj_geomDistance(model,data,model.geom('probe').id,model.geom(p['name']).id,1.,None) for p in pieces)
    assert gap()>.002  # A filled 74.2 x 51.2 box would falsely collide here.
    model.geom_pos[model.geom('probe').id]=[0.,d.depth/2000,.05]
    mujoco.mj_forward(model,data)
    assert gap()==pytest.approx(-.0001,abs=1e-8)
