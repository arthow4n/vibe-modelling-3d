"""Compare retained solves and plot the contact-driven cycle; launches no solver."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from physical_analysis.results import AnalysisResult
from physical_analysis.studies import compare_results
from components import RELIEF_INWARD_SCREEN

ROOT = Path(__file__).resolve().parent
LABELS = ('cycle_base', 'cycle_fine', 'cycle_penalty', 'cycle_increment', 'cycle_small_increment')


def summarize():
    results={label:AnalysisResult(**json.loads((ROOT/'notes'/'analysis'/label/'result.json').read_text()))
             for label in LABELS}
    summary={}
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    for label,r in results.items():
        r.require_completed()
        h=r.history
        closing=[f for f in h if f['load_fraction']<=.5]
        opening=[f for f in h if f['load_fraction']>.5]
        middle=min(h,key=lambda f:abs(f['load_fraction']-.5))
        max_inward=max(-f['observations']['tip']['min_mm'][1] for f in h)
        max_axial=max(max(abs(f['observations']['tip'][k][0]) for k in ('min_mm','max_mm')) for f in h)
        max_out_of_plane=max(max(abs(f['observations']['tip'][k][2]) for k in ('min_mm','max_mm')) for f in h)
        return_error=max(abs(v) for k in ('min_mm','max_mm') for v in h[-1]['observations']['tip'][k])
        assert max_inward<RELIEF_INWARD_SCREEN and max_axial<.15
        assert max_out_of_plane<.01  # The cams must pass in-plane, not escape over their ends.
        assert middle['max_contact_pressure_MPa']<1e-8 and h[-1]['max_contact_pressure_MPa']<1e-8
        assert return_error<1e-6
        summary[label]=dict(status=r.status,
            peak_closing_force_N=max(abs(f['motion_force_N']['drive']) for f in closing),
            peak_opening_force_N=max(abs(f['motion_force_N']['drive']) for f in opening),
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
    comparisons={label:compare_results(results['cycle_base'],results[label],
                 metrics=['peak_motion_force_N.drive','max_abs_principal_strain'],relative_tolerance=.05)
                 for label in LABELS[1:]}
    increment_comparison=compare_results(results['cycle_increment'],results['cycle_small_increment'],
        metrics=['peak_motion_force_N.drive','max_abs_principal_strain'],relative_tolerance=.10)
    answer=dict(runs=summary,comparisons=comparisons,final_increment_comparison=increment_comparison,
        limits='Conditional frictionless isotropic elastic local fixture; physical force, bonding, wear, set and creep uncalibrated.')
    (ROOT/'notes'/'numerical_summary.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer,indent=2))


if __name__=='__main__':
    summarize()
