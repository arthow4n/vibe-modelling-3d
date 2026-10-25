"""Locate Orca's proposed supports, without claiming they are needed or removable.

Run: ./execute.py model/double_ended_connector/notes/review_d_slice.py RUN_DIRECTORY
Uses the existing relative-extrusion reader; never changes CAD or exports.
"""
from pathlib import Path
import sys, json, hashlib
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'tpu_coil_cord'))
from gcode_paths import extrusions


def main(run):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    primary_path=run/'plate_1.gcode';probe_path=run/'support_probe/plate_1.gcode'
    primary=list(extrusions(primary_path)); probe=list(extrusions(probe_path))
    support=[p for p in probe if p['role'] in ('Support','Support interface')]
    if not support:raise ValueError('This diagnostic expects a generated support probe')
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    def draw(ax,paths,color,xz=False,width=.4):
        segments=[[(p['x'][0],p['z'] if xz else p['y'][0]),
                   (p['x'][1],p['z'] if xz else p['y'][1])] for p in paths]
        ax.add_collection(LineCollection(segments,colors=color,linewidths=width))
        ax.autoscale_view()
    draw(axes[0],[p for p in primary if abs(p['z']-.2)<1e-5],'#aebbc7')
    draw(axes[0],support,'#cc6f29')
    draw(axes[1],primary,'#d1d9df',True,.15)
    draw(axes[1],support,'#cc6f29',True,.6)
    axes[0].set(title='D: bed paths gray; all proposed support orange',xlabel='Bed X (mm)',ylabel='Bed Y (mm)')
    axes[1].set(title='D: primary paths gray; support probe orange',xlabel='Bed X (mm)',ylabel='Z (mm)')
    for ax in axes:ax.set_aspect('equal')
    fig.savefig(ROOT/'notes/d_support_review.png',dpi=150)
    plt.close(fig)
    info={'scope':'Visual support-location diagnostic only, not support necessity or contact/removal proof.',
          'support_segments_by_role':dict(Counter(p['role'] for p in support)),
          'support_z_range_mm':[min(p['z'] for p in support),max(p['z'] for p in support)],
          'gcode_sha256':{str(p.relative_to(run)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (primary_path,probe_path)}}
    (ROOT/'notes/d_support_review.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps(info))


if __name__=='__main__':
    if len(sys.argv)!=2:raise ValueError('Pass the retained Orca run directory')
    main(Path(sys.argv[1]))
