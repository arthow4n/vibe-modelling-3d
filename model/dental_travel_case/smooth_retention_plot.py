"""Export a plain force/displacement comparison from completed C study data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from smooth_retention_study import study_output, ROOT
OUT=study_output('retention-c2')


def main():
    r=json.loads((OUT/'pull.json').read_text())
    pair=r['paths']['pair_0.0'];single=r['paths']['single_0.0']
    fig,ax=plt.subplots(figsize=(10,5.3),layout='constrained')
    ax.plot(pair['travel_mm'],pair['force_N'],label='Both catches aligned',color='#1769a6',linewidth=2.5)
    ax.plot(single['travel_mm'],single['force_N'],label='One-end radial fixture',color='#ce741c',linewidth=2,linestyle='--')
    ax.axhline(0,color='#78909c',linewidth=.7)
    ax.set(xlabel='Cap lift from fully seated position (mm)',ylabel='Conditional axial force (N)',xlim=(0,6))
    ax.grid(alpha=.18);ax.legend(loc='upper right')
    ax.set_title('Strengthened smooth C: estimated slow pull and snap recovery',loc='left',fontweight='bold')
    ax.text(.98,.69,f"Both-end peak: {pair['peak_force_N']:.1f} N\nClosing peak: {pair['peak_closing_N']:.1f} N\nOne-end fixture: {single['peak_force_N']:.1f} N\nIdeal undamped threshold: {pair['undamped_seated_release_force_N']:.1f} N",
            transform=ax.transAxes,ha='right',va='top',bbox=dict(facecolor='#f3f4ef',edgecolor='none',pad=9))
    fig.supxlabel('E = 1200 MPa assumption; nominal fit; no friction. Negative force = elastic snap recovery.\nNot measured print force, hand comfort, peel-release force or bag-impact validation.',fontsize=10)
    folder=ROOT/'renders/assembled';folder.mkdir(exist_ok=True)
    for suffix in ('svg','png'):fig.savefig(folder/('smooth_retention_force.'+suffix),dpi=160)
    plt.close(fig)


if __name__=='__main__':main()
