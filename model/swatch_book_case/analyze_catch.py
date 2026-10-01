"""Real catch release driven by contact with a thumb proxy, via SnapFitQuestion.

Closing is screened on the exact hinged circular path in check_product.py.
The numerical operation is intentionally release at the fully seated pose:
actual printed catch, a conservative width envelope of the unloaded fixed
keeper, and a translating press proxy. Closing uses the real keeper contact
geometry. There is no prescribed displacement on the flexible catch.
"""
import json, sys, math, tempfile
from dataclasses import replace
from pathlib import Path
from physical_analysis import (SnapFitQuestion, Support, Motion, MatingPart,
    Region, PETG_SCREEN, BeamApproximation, ManufacturingAssumption, QuestionStudy)
from physical_analysis.screening import rectangular_cantilever, circular_cam_detent
from physical_analysis.evidence import retain_run
import swatch_book_case as m

HERE=Path(__file__).parent

def question(mesh=1., increment=.025):
    finger=m.block(12.,m.FRONT_Y-.7,m.LEAF_Z+2,4.,.6,4.)
    # Conservative width envelope (4 mm) of the 2.4 mm keeper for clearance
    # during pressing. It is never loaded in this release operation. Closing
    # below uses the actual narrower keeper contact face.
    cam=m.axial_cylinder(m.BEAD_X0,m.KEEPER_Y,m.KEEPER_Z,m.BEAD_WIDTH,m.BEAD_R)
    return SnapFitQuestion(name='catch_press_return',part=m.latch(),part_name='catch',
        material=PETG_SCREEN,
        supports=(Support(Region(upper=(m.LEAF_ROOT,m.FRONT_Y+8.1,m.RIM_Z+.1)),name='keyed_root'),),
        contact_region=Region(lower=(m.BEAD_X0-.2,m.FRONT_Y-m.BEAD_R-.1,m.LEAF_Z-.1),
                              upper=(m.LEAF_END+.1,m.FRONT_Y+.05,m.RIM_Z+.1)),
        mating_parts=(MatingPart('thumb',finger,Motion.round_trip((0,m.PRESS_TRAVEL+.1,0),name='press'),
                                Region.plane('y',m.FRONT_Y-.1)),
                      MatingPart('keeper',cam,Motion((0,0,0),name='seated_keeper'))),
        observations={'bead':Region(lower=(m.BEAD_X0,m.FRONT_Y-m.BEAD_R-.1,m.BEAD_Z-m.BEAD_R-.1),
                                    upper=(m.BEAD_X0+m.BEAD_WIDTH,m.FRONT_Y+.1,m.BEAD_Z+m.BEAD_R+.1)),
                      'free_leaf':Region(lower=(m.LEAF_ROOT+1,m.FRONT_Y-m.BEAD_R-.1,m.LEAF_Z-.1),
                                         upper=(m.LEAF_END+.1,m.FRONT_Y+m.LEAF_T+.1,m.RIM_Z+.1))},
        beam=BeamApproximation(20,m.LEAF_H,m.LEAF_T,
            'Approximate bending at the bead center; filleted root, distributed press and overhanging tip require numerical release check',
            tip_displacement_mm=.9),
        mesh_size_mm=mesh,max_increment=increment,timeout_seconds=1200,
        penalty_N_mm3=6000,penetration_limit_mm=.03,
        contact_free_at=(1.,),return_observation='free_leaf',return_tolerance_mm=1e-5,
        displacement_limits_mm={'free_leaf':((-.35,.35),(-.03,1.95),(-.15,.15))},
        manufacturing=ManufacturingAssumption(
            'PETG catch printed flat with its 8 mm height in Z; beam bends in XY. Four walls; actual thin-section paths reviewed separately. Homogeneous isotropic 1200 MPa is uncalibrated.'),
        acceptance={'peak_motion_force_N.press':12.})

def closing_question():
    # The actual contact face is an X-axis circular cylinder, invariant under
    # hinge rotation. Use the chord of its real 0..4 degree center path; the
    # chord differs by <=0.045 mm and slightly overstates inward interference.
    # No rails/enclosure in FEA: full rigid assembly sweep checked separately.
    t=math.radians(4)
    dy=m.KEEPER_Y-m.HINGE_Y;dz=m.KEEPER_Z-m.HINGE_Z
    y=m.HINGE_Y+dy*math.cos(t)+dz*math.sin(t)
    z=m.HINGE_Z-dy*math.sin(t)+dz*math.cos(t)
    cam=m.axial_cylinder(m.KEEPER_X0,y,z,m.KEEPER_WIDTH,m.BEAD_R)
    q=question(mesh=1.,increment=.02)
    return replace(q,name='catch_close_return',
        mating_parts=(MatingPart('keeper',cam,Motion((0,m.KEEPER_Y-y,m.KEEPER_Z-z),name='close')),),
        contact_free_at=(1.,),return_observation='free_leaf',require_driver_return=False,
        displacement_limits_mm={'free_leaf':((-.4,.4),(-.05,1.95),(-.35,.35))},
        acceptance={'peak_motion_force_N.close':12.})

def analytical():
    rows=[]
    # Nominal circular straight-path upper bound is .9 mm; true hinge arc is
    # screened separately. +/- .2 mm transverse size/clearance error is not a
    # measured Q2C tolerance. Modulus bracket is an explicit sensitivity only.
    for modulus in (800,1200,1800):
        for interference in (.7,.9,1.1):
            beam=rectangular_cantilever(length_mm=20,width_mm=m.LEAF_H,
                thickness_mm=m.LEAF_T,youngs_modulus_MPa=modulus,tip_displacement_mm=interference)
            cam=circular_cam_detent(stiffness_N_mm=beam['stiffness_N_mm'],radius_sum_mm=2*m.BEAD_R,
                                    transverse_spacing_mm=2*m.BEAD_R-interference)
            release=rectangular_cantilever(length_mm=24,width_mm=m.LEAF_H,thickness_mm=m.LEAF_T,
                youngs_modulus_MPa=modulus,tip_displacement_mm=m.PRESS_TRAVEL)
            rows.append(dict(modulus_MPa=modulus,interference_mm=interference,
                closing_slide_force_N=cam['peak_slide_force_N'],
                bead_transverse_force_N=beam['force_N'],approximate_release_force_N=release['force_N'],
                stiffness_at_bead_N_mm=beam['stiffness_N_mm'],root_strain=beam['root_strain']))
    report={'scope':'Uncalibrated beam and frictionless circular-cam CLOSING screens; flat retaining underside prevents cam-only opening. Not actual force or printed strain limits',
            'clearance_variation_mm':.2,'rows':rows}
    (HERE/'notes/analytical_screen.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def run(directory,operation='release',archive=None):
    out=Path(archive) if archive is not None else HERE/'notes/analysis'/operation
    if out.exists():
        raise FileExistsError(f'Choose a new archive destination: {out}')
    analytical()
    # Before solving: whole-product architecture and geometry record must exist.
    checks=json.loads((HERE/'notes/product_checks.json').read_text())
    assert checks['all_checks_pass']
    q=question() if operation=='release' else closing_question()
    study=QuestionStudy(q, decision=('Does contact-driven thumb release provide clearance with modest force and provisional strain?' if operation=='release' else
        'Does the real lead-in reach seated/unloaded state on the conservative hinge chord; what contact strain/wear remains for the coupon?'),
        metrics=('question.peak_actuation_force_N','question.peak_strain'),
        relative_tolerance=.12,absolute_tolerances={'question.peak_actuation_force_N':.3,'question.peak_strain':.001},
        motion_levels=1 if operation=='release' else 0,
        mesh_levels=1 if operation=='release' else 0,mesh_factor=.85,contact_levels=0)
    result=study.run(directory)
    for name in result.metrics['question']['study']['runs']:
        retain_run(Path(directory)/name,out/name)
    result.write(out/'study_result.json')
    print(json.dumps({'status':result.status,'question':result.metrics['question'],'errors':result.errors},indent=2))

def bind_paths(gcode):
    """Identity-check existing native evidence and attach actual spring paths.

    No solver is launched. QuestionStudy reuses every retained run, preserving
    native status/history and the bounded comparisons while updating only the
    explicit manufacturing and question interpretation.
    """
    for operation in ('release','closing'):
        directory=HERE/'notes/analysis'/operation
        q=question() if operation=='release' else closing_question()
        q.manufacturing=replace(q.manufacturing,gcode=Path(gcode),
            sections=tuple((x,z,(2*m.DEPTH+40,2*m.DEPTH+40+m.LEAF_T))
                           for x in (32.,42.) for z in (.6,2.2,4.2,6.2)))
        old=json.loads((directory/'study_result.json').read_text())
        evidence={label:directory/label for label in old['metrics']['question']['study']['runs']}
        for label,path in evidence.items():
            # Match the explicit numerical controls for the saved native case.
            saved=replace(q,max_increment=q.max_increment*.5) if label=='increment_sensitivity_1' else (
                replace(q,mesh_size_mm=q.mesh_size_mm*.85) if label=='mesh_sensitivity_1' else q)
            interpreted=saved.read_evidence(path)
            interpreted.write(path/'result.json')
        study=QuestionStudy(q,decision=old['metrics']['question']['study']['decision'],
            metrics=('question.peak_actuation_force_N','question.peak_strain'),relative_tolerance=.12,
            absolute_tolerances={'question.peak_actuation_force_N':.3,'question.peak_strain':.001},
            motion_levels=1 if operation=='release' else 0,
            mesh_levels=1 if operation=='release' else 0,mesh_factor=.85)
        with tempfile.TemporaryDirectory(prefix='swatch_evidence_interpretation_') as temp:
            answer=study.run(temp,evidence=evidence)
            answer.write(directory/'study_result.json')
        print(operation,answer.status,answer.metrics['question']['manufacturing']['local_solid_paths_established'],
              answer.metrics['question']['design_screen_passes'])

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--bind-paths':bind_paths(sys.argv[2])
    elif len(sys.argv)>1: run(Path(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else 'release',sys.argv[3] if len(sys.argv)>3 else None)
    else: print(json.dumps(analytical(),indent=2))
