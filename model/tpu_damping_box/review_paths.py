"""Explicit headless review of support locations and hidden roof bridge paths."""
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
from physical_analysis.manufacturing import orca_linear_paths

ROOT=Path(__file__).resolve().parent


def main():
    summary={}
    fig,axes=plt.subplots(1,2,figsize=(13,7))
    for ax,stem in zip(axes,('petg_final','tpu_final')):
        report=json.loads((ROOT/f'notes/{stem}.json').read_text())
        directory=Path(report['slice']['kept_run_directory'])
        primary=list(orca_linear_paths(directory/'plate_1.gcode'))
        probe=list(orca_linear_paths(directory/'support_probe/plate_1.gcode'))
        support=[p for p in probe if p[-1].startswith('Support')]
        summary[stem]={'primary_support_segments':sum(p[-1].startswith('Support') for p in primary),
                       'probe_support_z_range_mm':[min(p[4] for p in support),max(p[4] for p in support)]}
        ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in support],colors='#16a0b6',linewidths=.45))
        if stem=='tpu_final':
            cases=[]
            for i,name in enumerate('ABCDEF'):
                x=93+(i%3)*42; y=73+(i//3)*84
                for kind,cy,size,z in [('cup',y,34,3.6 if name=='F' else 3.4),('pad',y+41,32,3.8 if name=='F' else 3.6)]:
                    ax.add_patch(Rectangle((x-size/2,cy-size/2),size,size,fill=False,edgecolor='#334252',linewidth=.8))
                    ax.text(x,cy+size/2+1,f'{name} {kind}',ha='center',fontsize=8)
                    if name=='A':
                        continue
                    local=[p for p in primary if abs(p[4]-z)<1e-5 and abs((p[0]+p[2])/2-x)<12 and abs((p[1]+p[3])/2-cy)<12]
                    cases.append({'variant':name,'part':kind,'first_roof_layer_z_mm':z,
                      'roles':dict(Counter(p[-1] for p in local)),
                      'transverse_segments':sum(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in local),
                      'longitudinal_segments':sum(abs(p[3]-p[1])>3*abs(p[2]-p[0]) for p in local)})
                    assert cases[-1]['transverse_segments'] > 0, f'{name} {kind}: missing transverse roof paths'
                    assert cases[-1]['longitudinal_segments'] == 0, f'{name} {kind}: roof bridges along channels'
                    ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in local],colors='#a65cb8',linewidth=.35))
            summary[stem]['roof_layers']=cases
        else:
            for x,name in ((109,'body'),(161,'lid')):
                ax.add_patch(Rectangle((x-24,111),48,48,fill=False,edgecolor='#334252'))
                ax.text(x,161,name,ha='center')
        ax.autoscale();ax.set_aspect('equal');ax.set_title(stem.replace('_final','').upper())
        ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)')
    fig.suptitle('Automatic support probe (cyan); first hidden TPU roof paths (purple)')
    fig.tight_layout()
    fig.savefig(ROOT/'renders/path_review.png',dpi=150)
    (ROOT/'notes/path_review.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
