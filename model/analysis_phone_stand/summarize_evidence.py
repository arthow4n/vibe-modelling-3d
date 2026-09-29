"""Compare retained numerical evidence and write the current design decision record."""
from pathlib import Path
import hashlib
import json
import math
from physical_analysis import AnalysisResult
from physical_analysis.studies import compare_results
from components import *
from concept import screen

ROOT=Path(__file__).resolve().parent

def result(name):
    return AnalysisResult(**json.loads((ROOT/'notes/analysis'/name/'result.json').read_text()))

release=result('release');coarse=result('release_coarse');holding=result('holding');hc=result('holding_coarse');structure=result('structure')
for r in (release,coarse,holding,hc,structure): r.require_completed()
concept=screen()
force=max(c['tooth_tangential_force_N'] for c in concept['cases'])
# Simple bearing rejection screens for the explicit M3/M4 hardware load path.
weight=(PHONE_MASS_KG+.1)*9.81
cradle_lever=CRADLE_BOTTOM+6+PHONE_HEIGHT/2-CRADLE_BOLT_Y[0]
bolt_force=2*weight*(1+cradle_lever/(CRADLE_BOLT_Y[1]-CRADLE_BOLT_Y[0]))
hardware=dict(scope='Conservative projected-area screens, 2x local load allowance; no whole-stand 2x rating.',
    pivot_bearing_MPa=2*(force+weight)/(4*min(ARM_WIDTH,2*CHEEK_THICKNESS)),
    cradle_bolt_bearing_MPa=bolt_force/(3*(CRADLE_THICKNESS-1.5)),
    assumed_bearing_limit_MPa=7,cradle_bolt_force_bound_N=bolt_force,
    assumptions='M4 steel pivot, two M3 steel cradle screws; countersink leaves 2.5 mm. No fastener preload or joint-slip prediction.')
summary=dict(
    conditions=dict(phone_kg=PHONE_MASS_KG,moving_mass_allowance_kg=.1,
        measured_moving_volume_mm3=68398.85657656274,
        mass_g_at_assumed_density_1_27_g_cm3=86.86654785223469,
        print='Solid PETG, 0.4 mm nozzle, 0.2 mm layers, two walls, 100% rectilinear infill'),
    release=dict(force_N=release.metrics['peak_motion_force_N']['thumb'],
        thumb_travel_mm=RELEASE_TRAVEL,
        least_tooth_downward_travel_mm=-release.metrics['observations']['tooth']['max_mm'][2],
        strain_screen=release.check_strain_limits()),
    holding=dict(checked_tangential_force_N=holding.metrics['peak_motion_force_N']['drive'],
        required_service_force_N=force,
        ratio_of_checked_force_to_service=holding.metrics['peak_motion_force_N']['drive']/force,
        max_penetration_mm=holding.metrics['max_penetration_mm'],
        scope='Local tangential tooth translation, not full rotating assembly; no friction credit. E=800 MPa.'),
    structure=dict(max_displacement_mm=structure.metrics['max_displacement_mm'],
        scope='E=800 MPa, 300 g phone + conservative 100 g moving-part allowance. Bonded arm/cradle; fixed sector cut; excludes hinge and latch rotation.'),
    release_refinement=compare_results(coarse,release,metrics=['peak_motion_force_N.thumb','max_abs_principal_strain']),
    holding_mesh_and_penalty_sensitivity=compare_results(hc,holding,metrics=['peak_motion_force_N.drive','max_abs_principal_strain']),
    hardware=hardware,
    limitations=['Release force and tooth travel are stable under the sampled refinement; peak root strain remains mesh sensitive near the idealized clamp.',
                 'Final peak strain is below the assumed 1.5% screen, but this is not a converged local-yield or permanent-set prediction.',
                 'Sharp-tooth pass-over did not converge on the retained earlier fixture; use press-adjust-release. No full rotational/contact or fatigue model.',
                 'Material properties, printed anisotropy, creep, real fit and durability need physical calibration. No tablet or load certification.'],
    source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},
    export_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for pattern in ('*.step','*.stl') for p in ROOT.glob(pattern)},
)
assert 2<=summary['release']['force_N']<=12
assert summary['release']['least_tooth_downward_travel_mm']>=TOOTH_RELEASE_TRAVEL
assert all(x['passes'] for x in summary['release']['strain_screen'].values())
assert summary['holding']['ratio_of_checked_force_to_service']>1.4
assert summary['structure']['max_displacement_mm']<2
assert max(hardware['pivot_bearing_MPa'],hardware['cradle_bolt_bearing_MPa'])<hardware['assumed_bearing_limit_MPa']
(ROOT/'notes/verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ('release','holding','structure','release_refinement','holding_mesh_and_penalty_sensitivity','hardware')},indent=2))
