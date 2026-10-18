"""Inspect suspect sample bridges and the automatic support probe headlessly."""
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from m3_toolpaths import selected_paths

ROOT=Path(__file__).resolve().parent


def inspect(directory):
    files={'primary':directory/'plate_1.gcode',
           'auto_support':directory/'support_probe/plate_1.gcode'}
    paths={name:list(selected_paths(path)) for name,path in files.items()}
    groups={}
    for name,segments in paths.items():
        for part in ('body','cap'):
            for role in ('Bridge','Support interface'):
                values=[s for s in segments if s['role']==role and
                        ('body' if sum(s['x'])/2<135 else 'cap')==part]
                if values:
                    groups[f'{name} / {part} / {role}']=dict(segment_count=len(values),
                        layers_mm=sorted({round(s['z'],3) for s in values}),
                        max_segment_length_mm=max(((s['x'][1]-s['x'][0])**2+
                                                   (s['y'][1]-s['y'][0])**2)**.5 for s in values))
    fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
    for ax,part in zip(axes[:2],('body','cap')):
        for s in paths['primary']:
            if s['role']=='Bridge' and ('body' if sum(s['x'])/2<135 else 'cap')==part:
                ax.plot(s['x'],s['y'],color='#366ba3',lw=.6)
        ax.set(title=part+' bridge paths',xlabel='Printer X (mm)',ylabel='Printer Y (mm)')
        ax.set_aspect('equal')
    for s in paths['auto_support']:
        if s['role']=='Support interface':axes[2].plot(s['x'],[s['z'],s['z']],color='#c06c26',lw=.6)
    axes[2].set(title='Auto-support interfaces',xlabel='Printer X (mm)',ylabel='Z (mm)')
    output=ROOT/'notes/m3/joint_sample_toolpaths.svg'
    fig.savefig(output)
    output.write_text('\n'.join(line.rstrip() for line in output.read_text().splitlines())+'\n')
    fig.savefig(output.with_suffix('.png'),dpi=140)
    plt.close(fig)
    answer=dict(scope='Selected actual bridge/support locations; not measured printing quality.',
        gcode_sha256={name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in files.items()},groups=groups)
    output.with_suffix('.json').write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps(answer))


if __name__=='__main__':inspect(Path(sys.argv[1]))
