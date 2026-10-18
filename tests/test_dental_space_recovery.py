"""Interior evidence must exclude hidden channels and preserve mechanism regressions."""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import m1_design as m1
import m5_verification as verification
from m5_space_study import central_slice,THICKNESS
from product_verification import CalculationInconclusive


def test_central_storage_measurement_excludes_disconnected_latch_channel():
    outer=m1.prism(20,10,1,0,20)
    central=m1.box(0,0,10,10,8,22)
    hidden=m1.box(8.5,0,10,1,4,22)
    parts=dict(dimensions=SimpleNamespace(width=20,depth=10,corner=1),
               body=outer.cut(central).cut(hidden),cap=m1.box(40,0,10,1,1,1))
    assert central_slice(parts,10).Volume()/THICKNESS==pytest.approx(80,abs=1e-6)


def test_current_comparison_preserves_rejected_mouth_and_weak_guide_controls():
    data=verification.space()['cases']
    assert data['flat75']['individual_tube_overlap_mm3']>0
    assert data['thin_sleeve']['nominal_local_guide_plate_rigidity_ratio']<.5
    assert data['flat77']['guide_cap_bending_sections']['cap']['Ixx_mm4']>data['flat77_light_cap']['guide_cap_bending_sections']['cap']['Ixx_mm4']
    verification.contact()
    verification.cad()


def test_shared_production_edit_invalidates_both_current_export_pairs(tmp_path,monkeypatch):
    monkeypatch.setattr(verification,'ROOT',tmp_path)
    monkeypatch.setattr(verification,'OUT',tmp_path/'notes/m5')
    verification.OUT.mkdir(parents=True)
    source=tmp_path/'m5_design.py'
    source.write_text('guard_lap=16\n')
    record={'inputs':{'m5_design.py':hashlib.sha256(source.read_bytes()).hexdigest()},'artifacts':{}}
    for kind in ('case','joint'):
        path=tmp_path/(kind+'.stl')
        path.write_text('current geometry')
        record['artifacts'][kind]={path.name:hashlib.sha256(path.read_bytes()).hexdigest()}
    (verification.OUT/'publication.json').write_text(json.dumps(record))
    for kind in ('case','joint'):verification.current_publication(kind)
    source.write_text('guard_lap=20\n')
    for kind in ('case','joint'):
        with pytest.raises(CalculationInconclusive,match='m5_design.py'):
            verification.current_publication(kind)
