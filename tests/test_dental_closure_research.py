"""Research must preserve useful counterexamples and invalidate stale samples."""
import hashlib
import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'model/dental_travel_case'))
import closure_research_design as design
import closure_research_verification as verification
from product_verification import CalculationInconclusive


def test_invalid_concept_does_not_fall_back_to_a_printable_variant():
    with pytest.raises(ValueError,match='Unknown research closure'):design.sample('shell-wide-typo')


def test_actual_CAD_retains_long_rubbing_counterexample_and_released_runouts():
    verification.cad()
    data=json.loads((verification.OUT/'cad.json').read_text())['cases']
    for name in ('shell_broad','shell_end','perimeter_bead'):
        case=data[name]
        assert case['no_runout_overlap_at_30mm_mm3']>0
        assert all(p['retaining_overlap_mm3']<1e-5 for p in case['poses'] if p['lift_mm']>=6)
    assert data['slide_wall']['lift_obstruction_without_detent_mm3']>0


def test_actual_shell_response_distinguishes_wall_orientation():
    data=verification.flex()['cases']
    assert data['shell_broad']['pad_mean_displacement_at_1N_mm']>data['shell_end']['pad_mean_displacement_at_1N_mm']
    for case in data.values():
        assert case['mesh']['part']['min_jacobian']>0
        assert case['load_patch'][0]['area_mm2']>0


def test_shared_builder_edit_invalidates_every_specimen_pair(tmp_path,monkeypatch):
    monkeypatch.setattr(verification,'ROOT',tmp_path)
    monkeypatch.setattr(verification,'OUT',tmp_path/'evidence')
    verification.OUT.mkdir()
    source=tmp_path/'closure_research_design.py'
    source.write_text('detent=.65\n')
    record=dict(inputs={source.name:hashlib.sha256(source.read_bytes()).hexdigest()},artifacts={})
    for kind in design.KINDS:
        output=tmp_path/(kind+'.stl');output.write_text('current specimen')
        record['artifacts'][kind]={output.name:hashlib.sha256(output.read_bytes()).hexdigest()}
    (verification.OUT/'publication.json').write_text(json.dumps(record))
    for kind in design.KINDS:verification.current_publication(kind)
    source.write_text('detent=.85\n')
    for kind in design.KINDS:
        with pytest.raises(CalculationInconclusive,match=source.name):verification.current_publication(kind)
