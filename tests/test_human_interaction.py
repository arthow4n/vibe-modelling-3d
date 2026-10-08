"""MyoArm qualification: imported constraints, skin contacts and scoped replay."""
import copy
import importlib
import json
from pathlib import Path
import sys

import mujoco
import myo_sim
import numpy as np
import pytest
from product_verification import Status

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def modules():
    sys.path.insert(0,str(ROOT/'model/analysis_phone_stand'))
    try:
        yield importlib.import_module('human_interaction'),importlib.import_module('verification')
    finally:
        sys.path.pop(0)
        for name in ('human_interaction','verification'):
            sys.modules.pop(name,None)


@pytest.fixture(scope='module')
def receipt(modules):
    return json.loads(modules[1].RECEIPT.read_text())


@pytest.fixture(scope='module')
def model(modules):
    h,_=modules
    return h.Interaction(h.Setup(60.))


def test_imported_model_structure_ranges_and_exact_constraints(model):
    reference,_=myo_sim.load('myoarm_r')
    m=model.model
    assert m.nq==reference.nq==38 and m.neq==reference.neq==11
    assert len(model.free)==27 and m.nu==reference.nu==63
    assert np.all(m.jnt_limited) and np.array_equal(m.jnt_limited,reference.jnt_limited)
    assert m.ntendon==reference.ntendon==67 and not np.any(m.tendon_limited)
    assert model.names==[reference.joint(j).name for j in range(reference.njnt)]
    assert np.array_equal(m.jnt_range,reference.jnt_range)
    assert np.array_equal(m.jnt_axis,reference.jnt_axis)
    assert np.array_equal(m.eq_data,reference.eq_data)
    for name in ('humerus_r','radius_r','distph2_r','distph3_r','distph4_r','distph5_r','distal_thumb_r'):
        assert m.body(name).id>0
    # No old invented DIP/PIP coupling: both imported index hinges are free.
    assert all(model.names.index(n) in model.free for n in ('pm2_flexion_r','md2_flexion_r'))
    assert m.opt.disableflags & mujoco.mjtDisableBit.mjDSBL_ACTUATION
    rng=np.random.default_rng(21)
    for _ in range(20):
        q=rng.uniform(model.bounds[0],model.bounds[1]);model.state(q,0.)
        for a,b,c in model.couplings:
            assert model.data.qpos[a]==pytest.approx(np.polynomial.polynomial.polyval(model.data.qpos[b],c),abs=1e-12)
        assert np.all(model.data.qpos>=m.jnt_range[:,0]-1e-9)
        assert np.all(model.data.qpos<=m.jnt_range[:,1]+1e-9)
    q=model.bounds[0].copy();q[model.free.index(model.names.index('elbow_flexion_r'))]=-0.1
    d=model.diagnostics(q)
    assert not d['accepted'] and d['joint_margins_deg']['elbow_flexion_r']<0


def test_imported_contact_geometry_and_setup_transform(model):
    reference,_=myo_sim.load('myoarm_r')
    for name in ('distph2_coll_r','distph2_coll_2_r','radius_coll_r','5mcskin_r'):
        a,b=model.model.geom(name),reference.geom(name)
        assert np.array_equal(a.size,b.size) and np.array_equal(a.pos,b.pos)
        assert np.array_equal(a.quat,b.quat)
    model.state(model.model.qpos0[model.free],0.)
    shoulder=model.data.xpos[model.model.body('humerus_r').id]*1000
    assert shoulder==pytest.approx(model.setup.shoulder_mm,abs=1e-8)
    point,direction=model.contact_geometry()
    assert point==pytest.approx(model.data.geom_xpos[model.pad]+direction*model.model.geom_size[model.pad,2])
    assert np.linalg.norm(point-model.data.site_xpos[model.tip])>.001  # marker is not skin contact
    assert model.target(0.,3.)*1000==pytest.approx(model.surface_mm+(0,-3,0))


def test_collision_coverage_and_intentional_imported_overlaps(model):
    audit=model.audit()
    assert len(audit['imported_self_pairs'])==4
    assert set(tuple(p) for p in audit['imported_self_pairs'])<=set(tuple(p) for p in audit['screened_self_pairs'])
    assert all(g['conaffinity']==0 for g in audit['collision_geoms'])
    model.state(model.model.qpos0[model.free],0.)
    a,b=(model.model.geom(n).id for n in ('proxph3_coll_r','proxph4_coll_r'))
    assert mujoco.mj_geomDistance(model.model,model.data,a,b,1.,None)<-.001
    assert (a,b) in model.exclusions or (b,a) in model.exclusions
    assert not any({c.geom1,c.geom2}=={a,b} for c in model.data.contact)
    # Forearm/metacarpal wrist composites also overlap; geoms are not shrunk.
    a,b=(model.model.geom(n).id for n in ('radius_coll_r','3mcskin_coll_r'))
    assert mujoco.mj_geomDistance(model.model,model.data,a,b,1.,None)<-.006
    assert (a,b) in model.exclusions or (b,a) in model.exclusions
    # Distant segments of different digits ARE supplemental self checks.
    a,b=(model.model.geom(n).id for n in ('distph2_coll_2_r','distph3_coll_2_r'))
    assert (a,b) in model.self_pairs or (b,a) in model.self_pairs


def test_fixture_tracks_authoritative_slider(modules,monkeypatch):
    h,_=modules
    _,surface=h.product_fixture(60.)
    original=h.cad.slider
    monkeypatch.setattr(h.cad,'slider',lambda:original().translate((0,0,3)))
    _,changed=h.product_fixture(60.)
    assert changed-surface==pytest.approx((0,0,3),abs=1e-7)
    with pytest.raises(ValueError):h.Setup(61.)
    with pytest.raises(ValueError):h.Setup(60.,(0,float('nan'),0))


def first_endpoint(receipt,h):
    for run in receipt['runs']:
        m=h.Interaction(h.Setup(60.,tuple(run['setup']['shoulder_mm'])))
        for c in run['candidates']:
            q=np.array(c['q_rad'])
            if m.diagnostics(q)['accepted']:return m,q,c,run
    pytest.fail('Qualification must retain an independently valid contact witness')


def test_retained_contact_and_unrelated_penetration(modules,receipt):
    h,_=modules
    m,q,_,_=first_endpoint(receipt,h)
    assert m.diagnostics(q)['accepted']
    button=next(b for b in m.boxes if b['name']=='button')
    button['centre_mm'][1]+=1
    d=m.diagnostics(q)
    assert not d['accepted']
    assert any(p['other']=='button' and p['distance_mm']<-h.TOUCH_PENETRATION_MM for p in d['penetrations'])
    with pytest.raises(ValueError,match='Stroke'):m.state(q,h.cad.RELEASE+.1)


def test_optimizer_flags_do_not_supply_evidence(modules,receipt,tmp_path):
    h,v=modules
    modified=copy.deepcopy(receipt)
    path=tmp_path/'report.json'
    baseline=v.read_receipt('nominal')[2]
    for run in modified['runs']:
        for c in run['candidates']:
            c['endpoint']['solver_terminated']=False
            c['endpoint']['diagnostics']['accepted']=False
    path.write_text(json.dumps(modified))
    assert v.read_receipt('nominal',path)[2]==baseline
    m=h.Interaction(h.Setup(60.))
    elbow=m.free.index(m.names.index('elbow_flexion_r'))
    for run in modified['runs']:
        for c in run['candidates']:
            c['endpoint']['solver_terminated']=False
            c['endpoint']['diagnostics']['accepted']=False
            c['q_rad'][elbow]=-1.
        run['endpoint_count']=100
        run['complete_count']=100
        run['status']='PASS'
    path=tmp_path/'report.json';path.write_text(json.dumps(modified))
    assert v.read_receipt('nominal',path)[2]==(0,0)


def test_receipt_identity_missing_malformed_historical_assets_and_candidate(modules,receipt,tmp_path,monkeypatch):
    h,v=modules
    path=tmp_path/'report.json'
    assert v.read_receipt('nominal',path)[0]==Status.UNKNOWN
    path.write_text('{')
    assert v.read_receipt('nominal',path)[0]==Status.INCONCLUSIVE
    old=ROOT/'model/analysis_phone_stand/notes/v3_human_interaction.json'
    assert v.read_receipt('nominal',old)[0]==Status.UNKNOWN
    for key in ('sources','anatomy','tools'):
        record=copy.deepcopy(receipt);record[key]['changed']='different'
        path.write_text(json.dumps(record))
        assert v.read_receipt('nominal',path)[0]==Status.UNKNOWN
    record=copy.deepcopy(receipt);record['runs'][0]['candidates'][0]['q_rad'][0]=float('nan')
    path.write_text(json.dumps(record))
    assert v.read_receipt('nominal',path)[0]==Status.INCONCLUSIVE
    path.write_text(json.dumps(receipt))
    original=h.anatomy_identity()
    monkeypatch.setattr(h,'anatomy_identity',lambda:dict(original,package_sha256='edited XML'))
    assert v.read_receipt('nominal',path)[0]==Status.UNKNOWN


def test_plan_preserves_physical_unknown_and_finite_search_semantics(modules):
    _,v=modules
    with pytest.raises(TypeError):v.make_plan()
    with pytest.raises(ValueError):v.make_plan('v3-60-scale-0.9')
    for variant in v.VARIANTS:
        report=v.make_plan(variant).evaluate()
        questions={q['id']:q['status'] for r in report['requirements'] for q in r['questions']}
        assert questions['operation']=='UNKNOWN'
        assert questions['endpoint'] in ('PASS','INCONCLUSIVE')
        assert questions['access'] in ('PASS','INCONCLUSIVE')


def test_unrelated_collision_is_not_allowed_contact(modules,receipt):
    h,_=modules
    m,q,_,_=first_endpoint(receipt,h)
    d=m.diagnostics(q)
    hood=next(b for b in m.boxes if b['name']=='hood')
    hood['centre_mm']=d['elbow_mm']
    moved=h.Interaction(m.setup,(m.boxes,m.surface_mm))
    invalid=moved.diagnostics(q)
    assert invalid['contact_error_mm']<h.CONTACT_MM
    assert not invalid['accepted']
    assert any(p['other']=='hood' and p['distance_mm']<0 for p in invalid['penetrations'])


def test_imported_anatomy_valid_endpoints_can_hide_invalid_transition(modules,receipt):
    h,_=modules
    record=json.loads((h.ROOT/'notes/myoarm_withdrawal_counterexample.json').read_text())
    assert record['anatomy']==h.anatomy_identity()
    assert record['geometry_source']==h.sources()['model/analysis_phone_stand/v3_components.py']
    m=h.Interaction(h.Setup(60.,tuple(record['setup']['shoulder_mm'])))
    a,b=np.array(record['a_rad']),np.array(record['b_rad'])
    assert m.diagnostics(a,stroke_mm=3.)['accepted']
    assert m.diagnostics(b,offset_mm=40.,stroke_mm=3.)['accepted']
    path=m.segment(a,b,stroke_a=3.,stroke_b=3.)
    assert not path['accepted'] and 0<path['first_invalid']['fraction']<1
    assert any(p['other']=='floor' and p['distance_mm']<0
               for p in path['first_invalid']['diagnostics']['penetrations'])


def test_held_contact_and_constant_max_stroke_are_independently_checked(modules,receipt):
    h,_=modules
    valid=False
    for run in receipt['runs']:
        m=h.Interaction(h.Setup(60.,tuple(run['setup']['shoulder_mm'])))
        for c in run['candidates']:
            if not m.diagnostics(np.array(c['q_rad']))['accepted']:continue
            press=np.array(c['press']['q_rad'])
            strokes=np.linspace(0,h.cad.RELEASE,len(press))
            for a,b,ta,tb in zip(press[:-1],press[1:],strokes[:-1],strokes[1:]):
                path=m.segment(a,b,stroke_a=float(ta),stroke_b=float(tb),contact=True)
                if path['accepted']:
                    assert path['max_contact_error_mm']<=h.CONTACT_MM
                    valid=True
            q=press[-1]
            if m.diagnostics(q,stroke_mm=h.cad.RELEASE)['accepted']:
                assert m.segment(q,q,stroke_a=h.cad.RELEASE,stroke_b=h.cad.RELEASE,contact=True)['accepted']
    assert valid, 'Qualify at least one held-contact transition, without requiring a full interaction'


def test_receipt_rejects_misdeclared_screens_and_duplicate_starts(modules,receipt,tmp_path):
    _,v=modules
    path=tmp_path/'record.json'
    bad=copy.deepcopy(receipt);bad['screens']['contact_mm']=100.
    path.write_text(json.dumps(bad))
    assert v.read_receipt('nominal',path)[0]==Status.INCONCLUSIVE
    bad=copy.deepcopy(receipt)
    bad['runs'][0]['candidates'][1]=copy.deepcopy(bad['runs'][0]['candidates'][0])
    path.write_text(json.dumps(bad))
    assert v.read_receipt('nominal',path)[0]==Status.INCONCLUSIVE


def test_native_scene_failure_is_not_an_engineering_outcome(modules,receipt,tmp_path,monkeypatch):
    h,v=modules
    path=tmp_path/'record.json';path.write_text(json.dumps(receipt))
    def broken(*args):raise ValueError('native model compile failed')
    monkeypatch.setattr(h,'Interaction',broken)
    with pytest.raises(ValueError,match='native model compile failed'):
        v.read_receipt('nominal',path)


def test_asset_digest_detects_actual_xml_edit(modules,tmp_path,monkeypatch):
    h,_=modules
    package=tmp_path/'myo_sim';package.mkdir()
    (package/'__init__.py').write_text('')
    asset=package/'chain.xml'
    asset.write_bytes((myo_sim.MODELS_DIR/'arm/assets/myoarm_r_chain.xml').read_bytes())
    monkeypatch.setattr(myo_sim,'__file__',str(package/'__init__.py'))
    before=h.anatomy_identity()
    assert before==h.anatomy_identity()
    asset.write_text(asset.read_text()+'\n<!-- changed anatomy -->\n')
    assert before['package_sha256']!=h.anatomy_identity()['package_sha256']


def test_unexpected_replay_bug_is_not_malformed_evidence(modules,receipt,tmp_path,monkeypatch):
    h,v=modules
    path=tmp_path/'record.json';path.write_text(json.dumps(receipt))
    def broken(*args,**kwargs):raise KeyError('programming defect')
    monkeypatch.setattr(h.Interaction,'diagnostics',broken)
    with pytest.raises(KeyError,match='programming defect'):
        v.read_receipt('nominal',path)


def test_historical_setup_height_has_fixed_torso_plane_overlap(modules):
    h,_=modules
    m=h.Interaction(h.Setup(60.,(80.,500.,330.)))
    desk=m.model.geom('desk').id
    fixed=[g for g in m.human if m.model.body_weldid[m.model.geom_bodyid[g]]==0]
    before=[mujoco.mj_geomDistance(m.model,m.data,g,desk,1.,None) for g in fixed]
    assert min(before)<-.1  # setup mismatch, not unsuccessful arm search
    m.state((m.bounds[0]+m.bounds[1])/2,0.)
    after=[mujoco.mj_geomDistance(m.model,m.data,g,desk,1.,None) for g in fixed]
    assert after==pytest.approx(before,abs=1e-12)
