"""Question contracts, real consumer regressions and native structural answers."""
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys

import cadquery as cq
import pytest
from physical_analysis import (FlexureQuestion, StructuralQuestion, Support, Motion,
    Region, Material, SurfaceForce, BeamApproximation, QuestionStudy, ManufacturingAssumption)

ROOT = Path(__file__).resolve().parents[1]
MAT = Material('benchmark',1200,.3,'Numerical qualification only',.01)


def consumer(folder):
    directory = ROOT/'model'/folder
    previous = sys.modules.pop('components', None)
    sys.path.insert(0,str(directory))
    try:
        spec = importlib.util.spec_from_file_location('consumer_'+folder,directory/'analyze.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)
        sys.modules.pop('components', None)
        if previous is not None:
            sys.modules['components'] = previous


def beam_question(force=False):
    kwargs = dict(name='flexure_benchmark',part=cq.Workplane('XY').box(40,8,2,centered=False),
        material=MAT,supports=(Support(Region.plane('x',0)),),mesh_size_mm=2,
        observations={'tip':Region.plane('x',40)},
        beam=BeamApproximation(40,8,2,'Straight rectangular end-loaded benchmark',
            tip_force_N=.1 if force else None,tip_displacement_mm=None if force else 1))
    if force:
        return StructuralQuestion(**kwargs,forces=(SurfaceForce(Region.plane('x',40),(0,0,.1)),),nonlinear=False)
    return FlexureQuestion(**kwargs,motion=Motion((None,None,1),Region.plane('x',40)))


@pytest.mark.parametrize('force',[False,True])
def test_native_questions_match_analytical_response_and_locate_peak(tmp_path,force):
    q = beam_question(force)
    result = q.run(tmp_path/'native')
    answer = result.metrics['question']
    assert result.completed and answer['solver_completed'] and answer['numerical_evidence_adequate']
    assert answer['force_balance_ok'] and answer['design_screen_passes']
    assert answer['analytical_numerical_comparison']['ratio'] == pytest.approx(1,rel=.06)
    assert answer['peak_strain_location_mm'][0] < 3
    assert answer['peak_stress_location_mm'][0] < 3
    assert answer['physical_limits']['physically_validated'] is False
    loaded = q.read_evidence(tmp_path/'native')
    assert loaded.metrics['question']['peak_strain'] == answer['peak_strain']


def test_adequate_beam_screen_avoids_solver_and_bad_screen_escalates(tmp_path):
    q = beam_question()
    q.beam = replace(q.beam,adequate_for_decision=True)
    r = q.run(tmp_path/'unused')
    assert not (tmp_path/'unused').exists()
    assert r.status == 'analytical_screen' and not r.completed
    assert not r.metrics['question']['solver_completed']
    assert r.metrics['question']['design_screen_passes']
    q.beam = replace(q.beam,tip_displacement_mm=10)
    with pytest.raises(ValueError,match='applicable'):
        q.run(tmp_path/'unused',numerical=False)


def test_sliding_snap_retains_passage_and_increment_sensitivity():
    module = consumer('filament_swatch_box')
    q = module.operation(cycle=True,max_increment=.025)
    labels = ['baseline','mesh_sensitivity_1','contact_parameter_sensitivity_1','increment_sensitivity_1','increment_sensitivity_2']
    archives = ['cycle_base','cycle_fine','cycle_penalty','cycle_increment','cycle_small_increment']
    evidence = {key:ROOT/'model/filament_swatch_box/notes/analysis'/value for key,value in zip(labels,archives)}
    r = QuestionStudy(q,'Ten-percent force precision for a conditional prototype screen',
        ('peak_motion_force_N.drive','max_abs_principal_strain'),relative_tolerance=.1,
        motion_levels=2,mesh_levels=1,contact_levels=1).run(evidence=evidence)
    answer = r.metrics['question']
    assert answer['contact_passage_established'] and answer['contact_engaged']
    assert answer['numerical_elastic_return_ok'] and answer['elastic_return_error_mm'] < 1e-6
    assert answer['penetration_ok'] and answer['force_balance_ok']
    assert answer['peak_actuation_force_N'] == pytest.approx(.6114249411)
    assert answer['peak_strain'] == pytest.approx(.01129341959)
    directional = answer['peak_directional_actuation_force_N']['drive']
    assert directional['forward'] > 0 and directional['reverse'] > 0
    assert max(directional.values()) == answer['peak_actuation_force_N']
    assert answer['numerical_confidence'] == dict(increment_sensitivity='unstable',
        mesh_sensitivity='stable',contact_parameter_sensitivity='stable')
    assert answer['selected_metrics_stable'] is False
    assert answer['baseline_quality_adequate'] and not answer['numerical_evidence_adequate']
    assert answer['physical_limits']['printed_recovery_established'] is False


def test_phone_release_preserves_force_and_exposes_approximation():
    q = consumer('analysis_phone_stand').release_case(mesh=1.1)
    r = q.read_evidence(ROOT/'model/analysis_phone_stand/notes/analysis/release')
    a = r.metrics['question']
    assert a['numerical_evidence_adequate'] and a['force_balance_ok']
    assert a['force_balance_source'] == 'computed_from_retained_reactions'
    assert a['peak_actuation_force_N'] == pytest.approx(6.4936093)
    assert a['peak_strain'] == pytest.approx(.01396683197)
    assert a['analytical_screen'] and a['analytical_numerical_comparison']['ratio'] > 1


def test_lift_off_remains_rejected_and_study_does_not_run_refinements(tmp_path):
    q = consumer('filament_swatch_lift_box').snap_question(penalty=12000)
    r = QuestionStudy(q,'Passage must be qualified before force refinement',
        ('max_abs_principal_strain',),motion_levels=1).run(evidence={
            'baseline':ROOT/'model/filament_swatch_lift_box/notes/analysis/window_lead_base'})
    a = r.metrics['question']
    assert r.status == 'quality_failed' and not r.completed
    assert a['solver_completed'] and not a['numerical_evidence_adequate']
    assert not a['contact_passage_established'] and not a['penetration_ok']
    assert a['design_screen_passes'] is None
    assert a['numerical_confidence']['increment_sensitivity'] == 'unresolved'
    assert len(a['study']['runs']) == 1


def test_missing_passage_contract_and_excess_penetration_cannot_be_qualified():
    q = consumer('filament_swatch_box').operation(cycle=True,max_increment=.025)
    archive = ROOT/'model/filament_swatch_box/notes/analysis/cycle_base'
    r = replace(q,contact_free_at=()).read_evidence(archive)
    assert not r.metrics['question']['contact_passage_established']
    assert not r.metrics['question']['numerical_evidence_adequate']
    r = q.read_evidence(archive)
    r.history = r.history[:10]
    q._answer(r)
    assert not r.metrics['question']['solver_completed']
    assert not r.metrics['question']['contact_passage_established']
    r = q.read_evidence(archive)
    r.metrics['max_penetration_mm'] = .2
    q._answer(r)
    assert not r.metrics['question']['contact_passage_established']
    assert not r.metrics['question']['numerical_evidence_adequate']


def test_stale_geometry_motion_material_settings_and_archive_are_rejected(tmp_path):
    q = consumer('filament_swatch_box').operation(cycle=True,max_increment=.025)
    archive = ROOT/'model/filament_swatch_box/notes/analysis/cycle_base'
    for changed in [replace(q,part=q.part.translate((0,0,.1))),
                    replace(q,material=replace(q.material,youngs_modulus_MPa=800)),
                    replace(q,max_increment=.0125),replace(q,penalty_N_mm3=12000),
                    replace(q,mating_parts=(replace(q.mating_parts[0],motion=Motion((-7,0,0))),))]:
        with pytest.raises(ValueError,match='intent or numerical settings'):
            changed.read_evidence(archive)
    import shutil
    shutil.copytree(archive,tmp_path/'tampered')
    (tmp_path/'tampered/case.json').write_text('{}')
    with pytest.raises(ValueError,match='identity'):
        q.read_evidence(tmp_path/'tampered')


def test_manufacturing_reviews_actual_paths_without_material_inference(tmp_path):
    path = tmp_path/'section.gcode'
    path.write_text('G90\nM83\n;LAYER_CHANGE\n;TYPE:Internal solid infill\n;WIDTH:1\nG1 X-1 Y0 Z0.2\nG1 X1 Y0 E1\n')
    review = ManufacturingAssumption('Registered benchmark section',path,((0,.2,(-.5,.5)),)).review()
    assert review['local_solid_paths_established']
    gap = ManufacturingAssumption('Registered benchmark section',path,((0,.2,(-1,1)),)).review()
    assert not gap['local_solid_paths_established']
    assert 'youngs_modulus_MPa' not in review


def test_book_plate_cross_check_runs_known_structural_question(tmp_path):
    module = consumer('book_reading_plate')
    q = module.question(mesh=10,plain_back=True)
    r = q.run(tmp_path/'book')
    assert r.completed
    comparison = module.cross_check(r,plain_back=True)
    assert comparison['order_and_support_response_agree']
    assert comparison['numerical_to_analytical'] == pytest.approx(1,rel=.1)


def test_study_plan_is_opt_in_bounded_and_keeps_one_factor_changes():
    q = beam_question()
    study = QuestionStudy(q,'Force refinement',('peak_motion_force_N.drive',),motion_levels=2)
    plan = study.plan()
    assert not plan['mesh_sensitivity'] and not plan['contact_parameter_sensitivity']
    assert [r.max_increment for _,r in plan['increment_sensitivity']] == [.05,.025]
    assert all(r.mesh_size_mm == q.mesh_size_mm for _,r in plan['increment_sensitivity'])
    with pytest.raises(ValueError,match='unsupported'):
        QuestionStudy(q,'Contact check',('max_displacement_mm',),contact_levels=1).plan()


def test_small_metric_change_crossing_provisional_limit_does_not_stop_as_stable(tmp_path,monkeypatch):
    from physical_analysis import AnalysisResult
    q = beam_question()
    def recorded_response(question,directory,**kwargs):
        strain = .00999 if question.mesh_size_mm == 2 else .01001
        r = AnalysisResult(question.name,'completed',completed=True,
            metrics={'max_force_balance_relative':0,'max_strain_by_part':{'part':strain},
                     'peak_motion_force_N':{'drive':.3}},history=[{'load_fraction':1}])
        return question._answer(r)
    monkeypatch.setattr(FlexureQuestion,'run',recorded_response)
    r = QuestionStudy(q,'Remain below the supplied strain screen',
        ('question.peak_strain',),mesh_levels=1).run(tmp_path/'study')
    assert r.metrics['question']['numerical_confidence']['mesh_sensitivity'] == 'unstable'
    assert r.metrics['question']['study']['acceptance_changed']['mesh_sensitivity_1']
