"""Protect physically meaningful motion witnesses and synchronized sample delivery."""
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import m4_verification as verification
from overlap_exploration import peel,point_after_peel
from m4_design import D
from product_verification import CalculationInconclusive


@pytest.mark.parametrize('angle',(0,.2,1.4))
def test_drawn_motion_matches_actual_cad_transform(angle):
    point=(36.3,0,177.7)
    expected=peel(cq.Vertex.makeVertex(*point),D,angle).Center().toTuple()
    assert point_after_peel(point,D,angle)==pytest.approx(expected,abs=1e-10)


def test_contact_witness_rejects_old_blocked_pose_and_identifies_new_load_path():
    data=verification.visual_evidence()
    old,new=data['cases']['M3'],data['cases']['M4']
    assert old['demanded_far_land_axial_motion_mm']>0
    assert new['demanded_far_land_axial_motion_mm']<0
    for case in data['cases'].values():
        lo,hi=case['guide_only_onset']['bracket_deg']
        assert hi-lo<=data['angle_resolution_deg']


def test_one_production_edit_invalidates_both_full_and_joint_publications(tmp_path,monkeypatch):
    monkeypatch.setattr(verification,'ROOT',tmp_path)
    (tmp_path/'notes/m4').mkdir(parents=True)
    source=tmp_path/'m4_design.py'
    source.write_text('overlap=72\n')
    record={'inputs':{'m4_design.py':hashlib.sha256(source.read_bytes()).hexdigest()},'artifacts':{}}
    for kind in ('case','joint'):
        path=tmp_path/(kind+'.stl')
        path.write_text('current exported geometry')
        record['artifacts'][kind]={path.name:hashlib.sha256(path.read_bytes()).hexdigest()}
    (tmp_path/'notes/m4/publication.json').write_text(json.dumps(record))
    for kind in ('case','joint'):verification.current_publication(kind)
    source.write_text('overlap=60\n')
    for kind in ('case','joint'):
        with pytest.raises(CalculationInconclusive,match='m4_design.py'):
            verification.current_publication(kind)
