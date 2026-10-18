"""Plot retained diagnostic responses; none is a pull-off resistance curve."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent/'notes/retention'

def read(name):
    return json.loads((ROOT/name/'result.json').read_text())


def main():
    fig,axes=plt.subplots(1,3,figsize=(13,4.3),constrained_layout=True)
    for name,label in [('dental_m1_stub_land_12','M1'),('dental_m2b_land_fullwidth_12','M2B')]:
        result=read(name)
        if not result['completed']:
            raise ValueError('Incomplete traction fixture: '+name)
        history=result['history']
        axes[0].plot([0]+[12*f['load_fraction'] for f in history],
            [0]+[f['observations']['shoulder']['mean_mm'][0] for f in history],label=label)
    axes[0].set(xlabel='Applied axial land traction (N / leaf)',ylabel='Mean inward shoulder motion (mm)',
                title='Eccentric traction; fixed root stub\nE = 1200 MPa; no receiver contact')
    axes[0].legend()
    geometry=json.loads((ROOT/'m2b_geometry.json').read_text())
    for samples,label in [(geometry['baseline_m1_guide_comparison']['samples'],'M1'),
                           (geometry['baseline_m1_guide_comparison']['m2b_same_pose_samples'],'M2B')]:
        chosen=sorted((s for s in samples if s['axis']=='y' and s['direction']==1
                       and s['lift_mm'] in (.325,.65,.9)),key=lambda s:s['lift_mm'])
        axes[1].plot([s['lift_mm'] for s in chosen],[s['angle_deg'] for s in chosen],'o-',label=label)
    axes[1].set(xlabel='Cap axial lift (mm)',ylabel='Guide contact angle (degrees)',
                title='Rigid seam-pivot Y rotation\nHooks omitted; no loaded stiffness')
    axes[1].legend()
    result=read('dental_m2b_press_force')
    history=result['history']
    for observation,label in [('pad','Pad'),('shoulder','Shoulder'),('tip','Tip')]:
        axes[2].plot([0]+[3.6*f['load_fraction'] for f in history],
            [0]+[f['observations'][observation]['mean_mm'][0] for f in history],label=label)
    axes[2].set(xlabel='Applied inward pad force (N / leaf)',ylabel='Mean inward motion (mm)',
                title='M2B conforming-traction pad\nIsolated stub; strain unqualified')
    axes[2].legend()
    for ax in axes:
        ax.grid(alpha=.25)
    fig.suptitle('Diagnostic comparisons — not holding-force or physical acceptance evidence',fontsize=12)
    fig.savefig(ROOT/'diagnostic_comparison.png',dpi=160)
    plt.close(fig)

if __name__=='__main__':
    main()
