"""Evidence cannot be promoted by a saved PASS flag or a stale receipt."""
import json
from pathlib import Path
import sys
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
from product_verification import Status
import grip_human_verification as verification
import grip_human_record as study


@pytest.fixture
def receipt(monkeypatch):
    monkeypatch.setattr(study,'record_sources',lambda:{'source':'current'})
    monkeypatch.setattr(study,'anatomy_identity',lambda:{'anatomy':'current'})
    return dict(schema_version=1,sources=study.record_sources(),anatomy=study.anatomy_identity(),tools=study.tools(),
        screens=study.screens(),search=dict(starts=study.STARTS,seed=study.SEED,max_nfev=study.MAX_NFEV),
        setup=dict(candidate='balanced',tilt_deg=-25.,forward_mm=350.,seam_height_mm=1150.),
        attempts=[dict(start=0,result=dict(cost=0.,diagnostics=dict(accepted=True,q_rad=[0.]*52)))])


def test_missing_and_stale_receipts_are_unknown(tmp_path,receipt):
    path=tmp_path/'study.json'
    assert verification.read_record(path)[0]==Status.UNKNOWN
    receipt['sources']={'source':'old'};path.write_text(json.dumps(receipt))
    assert verification.read_record(path)[0]==Status.UNKNOWN


def test_malformed_coordinates_are_inconclusive(tmp_path,receipt):
    receipt['attempts'][0]['result']['diagnostics']['q_rad']=[0.]*51
    path=tmp_path/'study.json';path.write_text(json.dumps(receipt))
    assert verification.read_record(path)[0]==Status.INCONCLUSIVE


def test_saved_pass_cannot_override_native_replay(tmp_path,receipt,monkeypatch):
    path=tmp_path/'study.json';path.write_text(json.dumps(receipt))
    monkeypatch.setattr(study,'replay_candidates',lambda r:(None,0,[],[dict(diagnostics=dict(accepted=False))]))
    assert verification.evaluate(path)[0]==Status.INCONCLUSIVE


def test_partial_search_saved_pass_is_not_a_native_witness():
    # No expensive search: native FK must reject a stored accepted flag on the
    # neutral seed. A partial finite search can be recorded, never called a witness.
    scene=study.GripScene(study.Setup('balanced',-25.,350.,1150.),study.build_three_line()['dimensions'],local_hands=True)
    raw=dict(setup=study.asdict(scene.setup),attempts=[dict(start=0,result=dict(cost=0.,diagnostics=dict(accepted=True,q_rad=scene.initial(0).tolist())))])
    _,_,replayed,runs=study.replay_candidates(raw)
    assert not any(d['accepted'] for d in replayed)
    assert not any(r['diagnostics']['accepted'] for r in runs)


def test_upright_diagonal_is_rigid_hand_replay():
    dimensions=study.build_three_line()['dimensions']
    base=study.GripScene(study.Setup('balanced',-25.,350.,1150.),dimensions,local_hands=True)
    upright=study.GripScene(study.Setup('separated',0.,350.,1150.),dimensions,local_hands=True)
    q=base.initial(0);base.state(q,0.)
    points=[base.rotation.T@(base.pad(c)[0]-base.origin)*1000 for c in base.contacts]
    upright.state(study.translated(q,base,upright),0.)
    for before,c in zip(points,upright.contacts):
        after=upright.rotation.T@(upright.pad(c)[0]-upright.origin)*1000
        shift=upright.centers[0 if c['side']=='r' else 1]-base.centers[0 if c['side']=='r' else 1]
        assert after==pytest.approx(before+np.array((0.,0.,shift)),abs=1e-8)
