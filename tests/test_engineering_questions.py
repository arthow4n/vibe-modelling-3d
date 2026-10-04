"""Question contracts, numerical fixtures, consumer regressions and native answers."""
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys

import cadquery as cq
import pytest
from physical_analysis import (FlexureQuestion, StructuralQuestion, Support, Motion,
    Region, Material, SurfaceForce, BeamApproximation, QuestionStudy, ManufacturingAssumption,
    SnapFitQuestion, ContactQuestion, MatingPart, AnalysisResult)

ROOT = Path(__file__).resolve().parents[1]
from physical_analysis.experiments.ipc.fixtures.rounded_snap.question import question as rounded_question

ROUNDED = ROOT/'physical_analysis/experiments/ipc/fixtures/rounded_snap'
MAT = Material('benchmark',1200,.3,'Numerical qualification only',.01)


def stopped_beam_question():
    return ContactQuestion(name='force_loaded_stop',
        part=cq.Workplane('XY').box(40,8,2,centered=False),material=MAT,
        supports=(Support(Region.plane('x',0)),),
        forces=(SurfaceForce(Region.plane('x',40),(0,0,.1)),),
        contact_region=Region.plane('z',2),
        mating_parts=(MatingPart('stop',cq.Workplane('XY').box(6,12,1,centered=False).translate((36,-2,2.2)),
                                Motion((0,0,0),name='stop_fixed'),Region.plane('z',2.2)),),
        penalty_N_mm3=12000,mesh_size_mm=2,max_increment=.1,
        observations={'tip':Region.plane('x',40)})


def test_force_loaded_contact_stop_and_retained_identity(tmp_path):
    q=stopped_beam_question()
    r=q.run(tmp_path/'stopped')
    a=r.metrics['question']
    assert r.completed and a['numerical_evidence_adequate']
    assert a['contact_engaged'] and a['penetration_ok'] and a['force_balance_ok']
    # Free beam predicts 0.333 mm; the explicit unilateral stop limits it to 0.2.
    assert .19 < a['max_displacement_mm'] < .23
    assert q.read_evidence(tmp_path/'stopped').metrics['question']['contact_quality_ok']
    assert any(frame['max_contact_pressure_MPa']>0 for frame in r.history)
    with pytest.raises(ValueError,match='contact evidence'):
        q.run(tmp_path/'unused',numerical=False)


def test_force_loaded_supported_open_gap_is_explicit(tmp_path):
    q=replace(stopped_beam_question(),contact_expected=False,
              forces=(SurfaceForce(Region.plane('x',40),(0,0,.01)),))
    r=q.run(tmp_path/'open')
    a=r.metrics['question']
    assert r.completed and a['numerical_evidence_adequate']
    assert a['contact_engaged'] is False and a['penetration_ok']
    assert a['max_displacement_mm']==pytest.approx(.0333,rel=.06)
    q.contact_expected=None
    with pytest.raises(ValueError,match='explicit boolean'):q.build_case()


@pytest.mark.parametrize('missing',['contact_detected','max_penetration_mm'])
def test_contact_missing_native_evidence_never_promotes_answer(missing):
    q=stopped_beam_question()
    metrics={'max_force_balance_relative':0,'max_strain_by_part':{'part':.001},
             'contact_detected':True,'max_penetration_mm':.001}
    metrics.pop(missing)
    r=AnalysisResult(q.name,'completed',completed=True,metrics=metrics,
                     history=[{'load_fraction':1}])
    q._answer(r)
    assert not r.metrics['question']['numerical_evidence_adequate']
    assert r.metrics['question']['design_screen_passes'] is None


def test_force_transfer_against_two_independent_mates_uses_one_master_union(tmp_path):
    q=stopped_beam_question()
    q.mating_parts=tuple(MatingPart(f'stop_{i}',
        cq.Workplane('XY').box(6,6,1,centered=False).translate((36,-2+6*i,2.2)),
        Motion((0,0,0),name=f'fixed_{i}'),Region.plane('z',2.2)) for i in range(2))
    c=q.build_case()
    assert len(c.contacts)==1 and len(c.contacts[0].master)==2
    r=q.run(tmp_path/'two_mates')
    assert r.completed and r.metrics['question']['numerical_evidence_adequate']
    assert .19<r.metrics['max_displacement_mm']<.23
    assert r.metrics['max_force_balance_relative']<.01
    assert q.read_evidence(tmp_path/'two_mates').metrics['question']['contact_engaged']


def consumer(folder,entry='analyze.py'):
    directory = ROOT/'model'/folder
    previous = sys.modules.pop('components', None)
    sys.path.insert(0,str(directory))
    try:
        spec = importlib.util.spec_from_file_location('consumer_'+folder,directory/entry)
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


def test_local_rounded_snap_retains_passage_and_increment_sensitivity():
    q = rounded_question()
    labels = ['baseline','mesh_sensitivity_1','contact_parameter_sensitivity_1','increment_sensitivity_1','increment_sensitivity_2']
    archives = ['cycle_base','cycle_fine','cycle_penalty','cycle_increment','cycle_small_increment']
    evidence = {key:ROUNDED/'evidence/calculix'/value for key,value in zip(labels,archives)}
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


def recovery_contract(*, one_way=False):
    """Independent boxes and synthetic history; no claimed native/physical solve.

    Test only interpretation of driver pose and sampled unloaded deformation,
    without reassigning retained solver evidence to a different physical intent.
    """
    motion = Motion((0,0,-1)) if one_way else Motion.round_trip((0,0,-1))
    q = SnapFitQuestion(name='recovery_contract',
        part=cq.Workplane('XY').box(4,1,1,centered=False),material=MAT,
        supports=(Support(Region.plane('x',0)),),contact_region=Region.plane('z',1),
        mating_parts=(MatingPart('driver',cq.Workplane('XY').box(1,1,1),motion),),
        observations={'tip':Region.plane('x',4)},penalty_N_mm3=1000,
        return_observation='tip',require_driver_return=not one_way,contact_free_at=(1,),
        displacement_limits_mm={'tip':((-.2,.2),)*3})
    def frame(time, pressure, displacement):
        return dict(load_fraction=time,max_contact_pressure_MPa=pressure,
            observations={'tip':{'min_mm':[0,0,displacement],'max_mm':[0,0,displacement]}})
    r = AnalysisResult(q.name,'completed',completed=True,
        metrics={'max_force_balance_relative':0,'max_strain_by_part':{'part':.001},
                 'max_penetration_mm':.001,'contact_detected':True},
        history=[frame(.5,.1,-.1),frame(1,0,0)])
    return q,r


def test_snap_return_accepts_stationary_mate_but_rejects_nonreturning_motion():
    q,r = recovery_contract()
    fixed = MatingPart('stationary',cq.Workplane('XY').box(1,1,1),
                       Motion((0,0,0),name='stationary'))
    q.mating_parts += (fixed,)
    assert len(q.build_case().parts) == 3
    q._answer(r)
    assert r.metrics['question']['contact_passage_established']
    assert r.metrics['question']['numerical_elastic_return_ok']
    assert r.metrics['question']['elastic_return_driver_policy'] == 'initial_pose'
    q.mating_parts = q.mating_parts[:-1]+(replace(fixed,motion=Motion((0,1,0))),)
    with pytest.raises(ValueError,match='return to their initial pose'):
        q._answer(r)


def test_one_way_unloaded_return_requires_explicit_policy_and_final_free_checkpoint():
    q,r = recovery_contract(one_way=True)
    q.require_driver_return = True
    with pytest.raises(ValueError,match='return to their initial pose'):
        q._answer(r)
    q.require_driver_return = False
    q.contact_free_at = (.5,)
    with pytest.raises(ValueError,match='final contact-free checkpoint'):
        q._answer(r)
    q.contact_free_at = (1,)
    q._answer(r)
    assert r.metrics['question']['contact_passage_established']
    assert r.metrics['question']['numerical_elastic_return_ok']
    assert r.metrics['question']['elastic_return_driver_policy'] == 'final_contact_free_pose'
    assert not r.metrics['question']['physical_limits']['printed_recovery_established']


@pytest.mark.parametrize('failure',['loaded','residual','missing_observation','missing_final_frame'])
def test_one_way_recovery_does_not_promote_failed_or_missing_evidence(failure):
    q,r = recovery_contract(one_way=True)
    if failure == 'loaded':
        r.history[-1]['max_contact_pressure_MPa'] = .1
    elif failure == 'residual':
        r.history[-1]['observations']['tip']['max_mm'][2] = .001
    elif failure == 'missing_observation':
        r.history[-1]['observations'] = {}
    else:
        r.history.pop()
    q._answer(r)
    assert not r.metrics['question']['contact_passage_established']
    assert not r.metrics['question']['numerical_elastic_return_ok']
    assert not r.metrics['question']['numerical_evidence_adequate']


def test_phone_release_preserves_force_and_exposes_approximation():
    q = consumer('analysis_phone_stand').release_case(mesh=1.1)
    r = q.read_evidence(ROOT/'model/analysis_phone_stand/notes/analysis/release')
    a = r.metrics['question']
    assert a['numerical_evidence_adequate'] and a['force_balance_ok']
    assert a['force_balance_source'] == 'computed_from_retained_reactions'
    assert a['peak_actuation_force_N'] == pytest.approx(6.4936093)
    assert a['peak_strain'] == pytest.approx(.01396683197)
    assert a['analytical_screen'] and a['analytical_numerical_comparison']['ratio'] > 1


def test_rejected_quality_baseline_does_not_run_refinements(tmp_path,monkeypatch):
    # Synthetic contract failure, not a claimed mechanical outcome for a product.
    q = rounded_question()
    r = q.read_evidence(ROUNDED/'evidence/calculix/cycle_base')
    r.status = 'quality_failed'
    r.completed = False
    r.metrics['max_penetration_mm'] = .2
    q._answer(r)
    calls = []
    def rejected_response(question,directory,**kwargs):
        calls.append(directory)
        return r
    monkeypatch.setattr(SnapFitQuestion,'run',rejected_response)
    r = QuestionStudy(q,'Passage must be qualified before force refinement',
        ('max_abs_principal_strain',),motion_levels=1).run(tmp_path/'study')
    a = r.metrics['question']
    assert r.status == 'quality_failed' and not r.completed
    assert a['solver_completed'] and not a['numerical_evidence_adequate']
    assert not a['contact_passage_established'] and not a['penetration_ok']
    assert a['design_screen_passes'] is None
    assert a['numerical_confidence']['increment_sensitivity'] == 'unresolved'
    assert len(a['study']['runs']) == len(calls) == 1


def test_missing_passage_contract_and_excess_penetration_cannot_be_qualified():
    q = rounded_question()
    archive = ROUNDED/'evidence/calculix/cycle_base'
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
    q = rounded_question()
    archive = ROUNDED/'evidence/calculix/cycle_base'
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


def test_k_mesh_study_reuses_bound_evidence_without_solving(monkeypatch):
    module=consumer('filament_swatch_box_study','analyze_cap_k.py')
    def no_solve(*args,**kwargs):
        pytest.fail('Retained K review must not launch a new solve')
    monkeypatch.setattr(SnapFitQuestion,'run',no_solve)
    result=module.review_evidence()
    answer=result.metrics['question']
    assert result.completed and answer['evidence_method']=='retained_numerical'
    assert answer['numerical_evidence_adequate'] and answer['design_screen_passes']
    assert answer['physical_limits']['physically_validated'] is False
    assert answer['numerical_confidence']==dict(
        increment_sensitivity='not_run',mesh_sensitivity='stable',
        contact_parameter_sensitivity='not_run')
    comparison=answer['study']['comparisons']['mesh_sensitivity_1']
    assert answer['study']['relative_tolerance']==.1
    assert answer['study']['absolute_tolerances']=={}
    assert comparison['question.peak_actuation_force_N']['refined']==pytest.approx(2.55445949)
    assert comparison['question.peak_strain']['refined']==pytest.approx(.01030824113)
    assert not answer['study']['acceptance_changed']['mesh_sensitivity_1']
    assert len(answer['study']['runs'])==2
    assert all(run['input_sha256'] and run['case_sha256'] for run in answer['study']['runs'].values())
