"""Historical synthetic-anatomy numerical counterexamples, not current product evidence."""
import copy
import importlib
import json
from pathlib import Path

import mujoco
import numpy as np
import pytest
from product_verification import Status

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def modules():
    import sys
    folder=ROOT/'model/analysis_phone_stand'
    sys.path.insert(0,str(folder))
    try:
        yield importlib.import_module('synthetic_human_interaction'),None
    finally:
        sys.path.remove(str(folder))
        # Avoid leaking the common object-owned verification module name.
        for name in ('synthetic_human_interaction',):
            sys.modules.pop(name,None)


@pytest.fixture(scope='module')
def receipt(modules):
    return json.loads((ROOT/'model/analysis_phone_stand/notes/v3_human_interaction.json').read_text())


def run_for(receipt,scale):
    return next(r for r in receipt['runs'] if r['setup']['scale']==scale)


def model_for(human,run):
    return human.Interaction(human.Setup(run['setup']['angle_deg'],run['setup']['scale'],tuple(run['setup']['shoulder_mm'])))


def test_native_distance_with_disabled_contact_masks_is_signed():
    # Analytic sphere/box penetration: box rear at y=10 mm; r=7 mm
    # sphere centre at y=15 mm -> 2 mm penetration. Automatic contacts disabled.
    m=mujoco.MjModel.from_xml_string('''<mujoco><worldbody>
    <geom name="box" type="box" size=".01 .01 .01" contype="0" conaffinity="0"/>
    <geom name="pad" type="sphere" size=".007" pos="0 .015 0" contype="0" conaffinity="0"/>
    </worldbody></mujoco>''')
    d=mujoco.MjData(m)
    mujoco.mj_forward(m,d)
    assert d.ncon==0
    assert mujoco.mj_geomDistance(m,d,0,1,1.,None)==pytest.approx(-.002,abs=1e-9)


def test_real_endpoint_does_not_establish_valid_approach(modules,receipt):
    h,_=modules
    run=run_for(receipt,1.)
    c=run['candidates'][0]
    m=model_for(h,run)
    pre,q=np.array(c['approach_q_rad']),np.array(c['q_rad'])
    assert m.diagnostics(pre,offset_mm=40.)['accepted']
    assert m.diagnostics(q)['accepted']
    path=m.segment(pre,q)
    assert not path['accepted']
    bad=path['first_invalid']
    assert 0 < bad['fraction'] < 1
    assert any(p['other']=='desk' and p['distance_mm']<0 for p in bad['diagnostics']['penetrations'])
    # A two-endpoint-only screen would have missed the nonlinear sweep.
    assert m.data.ncon==0


def test_valid_press_endpoints_hide_invalid_held_transition(modules,receipt):
    h,_=modules
    run=run_for(receipt,1.)
    c=run['candidates'][1]
    m=model_for(h,run)
    a,b=np.array(c['press']['q_rad'][:2])
    assert m.diagnostics(a,stroke_mm=0.)['accepted']
    assert m.diagnostics(b,stroke_mm=.5)['accepted']
    path=m.segment(a,b,stroke_a=0.,stroke_b=.5,contact=True)
    assert not path['accepted']
    assert any(p['other']=='button' and p['distance_mm'] < -h.TOUCH_PENETRATION_MM
               for p in path['first_invalid']['diagnostics']['penetrations'])


def test_limit_coupling_and_constant_max_stroke(modules,receipt):
    h,_=modules
    run=run_for(receipt,.9)
    m=model_for(h,run)
    q=np.array(run['candidates'][0]['press']['q_rad'][-1])
    assert m.segment(q,q,stroke_a=h.cad.RELEASE,stroke_b=h.cad.RELEASE,contact=True)['accepted']
    m.state(q,h.cad.RELEASE)
    assert m.data.qpos[m.names.index('index_dip')]==pytest.approx(h.COUPLING*m.data.qpos[m.names.index('index_pip')])
    # Independent native limit check must reject out-of-range submitted states.
    q[m.free.index(m.names.index('elbow'))]=np.radians(146)
    d=m.diagnostics(q)
    assert not d['accepted'] and d['joint_margins_deg']['elbow']<0
    with pytest.raises(ValueError,match='Stroke'):
        m.state(q,h.cad.RELEASE+.1)


def test_contact_allowance_does_not_license_penetrating_button(modules,receipt):
    h,_=modules
    run=run_for(receipt,.9)
    m=model_for(h,run)
    q=np.array(run['candidates'][0]['q_rad'])
    assert m.diagnostics(q)['accepted']
    button=next(b for b in m.boxes if b['name']=='button')
    # Actual opposing surface advances 1 mm while hand stays fixed.
    button['centre_mm'][1]+=1
    d=m.diagnostics(q)
    assert not d['accepted']
    assert any(p['human']=='pad' and p['other']=='button' and p['distance_mm']<-.9 for p in d['penetrations'])


def test_fixture_follows_actual_product_builder(modules,monkeypatch):
    h,_=modules
    _,surface=h.product_fixture(60.)
    original=h.cad.slider
    monkeypatch.setattr(h.cad,'slider',lambda:original().translate((0,0,3)))
    _,changed=h.product_fixture(60.)
    assert changed-surface==pytest.approx((0,0,3),abs=1e-7)
    with pytest.raises(ValueError):
        h.Setup(61.)
    with pytest.raises(ValueError):
        h.Setup(60.,scale=float('nan'))
