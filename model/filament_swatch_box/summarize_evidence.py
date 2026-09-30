"""Compare retained solves and plot the contact-driven cycle; launches no solver."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from physical_analysis import QuestionStudy
from analyze import operation
from components import RELIEF_INWARD_SCREEN

ROOT = Path(__file__).resolve().parent
LABELS = ('cycle_base', 'cycle_fine', 'cycle_penalty', 'cycle_increment', 'cycle_small_increment')


def summarize():
    questions={}
    for label in LABELS:
        case=json.loads((ROOT/'notes/analysis'/label/'case.json').read_text())
        questions[label]=operation(mesh=case['parts'][0]['mesh_size_mm'],
            penalty=case['contacts'][0]['penalty_N_mm3'],cycle=True,max_increment=case['max_increment'])
    results={label:questions[label].read_evidence(ROOT/'notes/analysis'/label) for label in LABELS}
    summary={}
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    for label,r in results.items():
        r.require_completed()
        h=r.history
        max_inward=max(-f['observations']['tip']['min_mm'][1] for f in h)
        max_axial=max(max(abs(f['observations']['tip'][k][0]) for k in ('min_mm','max_mm')) for f in h)
        max_out_of_plane=max(max(abs(f['observations']['tip'][k][2]) for k in ('min_mm','max_mm')) for f in h)
        question=r.metrics['question']
        return_error=question['elastic_return_error_mm']
        assert max_inward<RELIEF_INWARD_SCREEN and max_axial<.15
        assert max_out_of_plane<.01  # The cams must pass in-plane, not escape over their ends.
        assert question['contact_passage_established'] and question['numerical_elastic_return_ok']
        summary[label]=dict(status=r.status,
            peak_closing_force_N=question['peak_directional_actuation_force_N']['drive']['forward'],
            peak_opening_force_N=question['peak_directional_actuation_force_N']['drive']['reverse'],
            peak_mean_tip_inward_mm=max(-f['observations']['tip']['mean_mm'][1] for f in h),
            peak_nodal_tip_inward_mm=max_inward,peak_nodal_tip_axial_mm=max_axial,
            peak_nodal_tip_out_of_plane_mm=max_out_of_plane,
            return_error_mm=return_error,closed_and_open_end_contact_free=True,
            peak_strain=r.metrics['max_abs_principal_strain'],
            peak_strain_location_mm=r.metrics['max_strain_element_centroid_mm'],
            peak_penetration_mm=r.metrics['max_penetration_mm'],
            max_force_balance_relative=r.metrics['max_force_balance_relative'],
            strain_screen=r.check_strain_limits()['arm'])
        t=[f['load_fraction'] for f in h]
        axes[0].plot(t,[f['motion_force_N']['drive'] for f in h],label=label)
        axes[1].plot(t,[-f['observations']['tip']['mean_mm'][1] for f in h])
        axes[2].plot(t,[100*f['max_abs_principal_strain'] for f in h])
    for ax,title,ylabel in zip(axes,('Sliding reaction along travel','Snap head mean inward movement','Peak strain at saved increments'),
                              ('N','mm','%')):
        ax.set(title=title,xlabel='Normalized path: close 0–0.5, reopen 0.5–1',ylabel=ylabel)
        ax.axvline(.5,color='.6',linestyle=':');ax.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    axes[2].axhline(1.5,color='red',linestyle='--',label='Provisional 1.5% screen');axes[2].legend(fontsize=8)
    fig.tight_layout();fig.savefig(ROOT/'renders'/'contact_cycle.png',dpi=180)
    study=QuestionStudy(questions['cycle_base'],
        'Ten-percent actuation-force/strain precision for a conditional prototype screen',
        ('peak_motion_force_N.drive','max_abs_principal_strain'),relative_tolerance=.10,
        motion_levels=2,mesh_levels=1,contact_levels=1).run(evidence={
            key:ROOT/'notes/analysis'/label for key,label in zip(
                ('baseline','mesh_sensitivity_1','contact_parameter_sensitivity_1','increment_sensitivity_1','increment_sensitivity_2'),
                LABELS)})
    answer=dict(runs=summary,
        engineering_question=study.metrics['question'],
        limits='Conditional frictionless isotropic elastic local fixture; physical force, bonding, wear, set and creep uncalibrated.')
    (ROOT/'notes'/'numerical_summary.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer,indent=2))


if __name__=='__main__':
    summarize()
