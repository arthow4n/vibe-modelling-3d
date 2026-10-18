"""Inspect actual suspect bridge/support locations; no generic G-code audit."""
import hashlib
import json
from pathlib import Path
import re
import sys
from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
NUMBER=r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'


def selected_paths(path):
    position={'X':None,'Y':None,'Z':None}
    relative=False
    extrusion_relative=False
    e_previous=0.
    role=''
    for line in path.open():
        if line.startswith(';TYPE:'):
            role=line[6:].strip()
        code=line.split(';')[0].strip()
        if not code:continue
        command=code.split()[0]
        if command=='G90':relative=False
        if command=='G91':relative=True
        if command=='M83':extrusion_relative=True
        if command=='M82':extrusion_relative=False
        values={axis:float(value) for axis,value in re.findall(r'([XYZEF])('+NUMBER+r')',code)}
        if command=='G92' and 'E' in values:e_previous=values['E']
        if command not in ('G0','G1'):continue
        previous=position.copy()
        for axis in position:
            if axis in values:position[axis]=(position[axis]+values[axis] if relative and position[axis] is not None else values[axis])
        extrusion=values.get('E',0.) if extrusion_relative else values.get('E',e_previous)-e_previous
        if 'E' in values:e_previous=values['E']
        if extrusion<=0 or not ('X' in values or 'Y' in values):continue
        if any(v is None for v in (*previous.values(),*position.values())):continue
        z=position['Z']
        if role in ('Support','Support interface','Bridge') or abs(z-178.2)<.01:
            yield dict(role=role,x=[previous['X'],position['X']],y=[previous['Y'],position['Y']],z=z)


def run(directory):
    files={'primary':directory/'plate_1.gcode','auto_support':directory/'support_probe/plate_1.gcode'}
    paths={k:list(selected_paths(p)) for k,p in files.items()}
    output={}
    for name,segments in paths.items():
        grouped=defaultdict(list)
        for s in segments:
            if s['role'] in ('Support','Support interface','Bridge'):
                grouped[(s['role'],'body' if sum(s['x'])/2<135 else 'cap')].append(s)
        output[name]={role+' / '+part:dict(segment_count=len(v),z_mm=[min(x['z'] for x in v),max(x['z'] for x in v)],
            deposition_layers_mm=sorted({round(x['z'],3) for x in v})) for (role,part),v in grouped.items()}
    fig,axes=plt.subplots(1,3,figsize=(13,4.5),layout='constrained')
    configurations=[('auto_support',lambda s:s['role']=='Support interface','Auto-support interface: X vs Z'),
        ('primary',lambda s:s['role']=='Bridge' and abs(s['z']-86.4)<.01,'Cap receiving ledge, Z86.4'),
        ('primary',lambda s:abs(s['z']-178.2)<.01,'Body first retaining layer, Z178.2')]
    for ax,(name,select,title) in zip(axes,configurations):
        selected=[s for s in paths[name] if select(s)]
        for s in selected:
            y=[s['z'],s['z']] if name=='auto_support' else s['y']
            ax.plot(s['x'],y,color='#366ba3',lw=.45,alpha=.8)
        ax.set(title=title,xlabel='Printer X (mm)',ylabel='Z (mm)' if name=='auto_support' else 'Printer Y (mm)')
        if name!='auto_support':ax.set_aspect('equal')
    out=ROOT/'notes/m3'
    fig.savefig(out/'toolpaths.svg')
    vector=out/'toolpaths.svg'
    vector.write_text('\n'.join(line.rstrip() for line in vector.read_text().splitlines())+'\n')
    fig.savefig(out/'toolpaths.png',dpi=150)
    plt.close(fig)
    record=dict(scope='Actual selected-profile paths at suspect features and support interfaces, not bed-fit rechecking or physical bridge qualification.',
        input_sha256={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in files.items()},summary=output)
    (out/'toolpaths.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({name:{k:{a:b for a,b in v.items() if a!='deposition_layers_mm'} for k,v in data.items()} for name,data in output.items()}))


if __name__=='__main__':
    run(Path(sys.argv[1]))
