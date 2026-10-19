"""Locate actual suggested supports for both complete mini-box layouts."""
import json
import hashlib
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/internal_hinge'


def inspect():
    fig,axes=plt.subplots(1,2,figsize=(13,6),layout='constrained');data={}
    for name,ax in zip(('c7_mini_screw','c7_mini_pip'),axes):
        r=json.loads((OUT/(name+'_slice.json')).read_text())
        directory=Path(r['slice']['kept_run_directory'])
        rows=list(orca_linear_paths(directory/'plate_1.gcode'))
        supports=list(orca_linear_paths(directory/'support_probe/plate_1.gcode'))
        support=[p for p in supports if p[-1].startswith('Support')]
        bridge=[p for p in rows if 'Bridge' in p[-1] or 'Overhang' in p[-1]]
        for subset,color in ((rows,'#9da9af'),(support,'#d34b55')):
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in subset],colors=color,linewidths=.4,alpha=.4))
        ax.autoscale_view();ax.set(title=name+'; red = suggested supports',aspect='equal',xlabel='Printer X mm',ylabel='Printer Y mm')
        layers={}
        for p in bridge:
            key=str(round(p[4],3));v=layers.setdefault(key,dict(strokes=0,max_stroke_mm=0))
            v['strokes']+=1;v['max_stroke_mm']=max(v['max_stroke_mm'],((p[0]-p[2])**2+(p[1]-p[3])**2)**.5)
        data[name]=dict(STL_sha256=r['slice']['input_sha256'],support_roles=dict(Counter(p[-1] for p in support)),bridge_layers=layers,
            support_z_range_mm=[min(p[4] for p in support),max(p[4] for p in support)] if support else None,
            gcode_sha256={n:hashlib.sha256((directory/n).read_bytes()).hexdigest() for n in ('plate_1.gcode','support_probe/plate_1.gcode')})
    fig.savefig(OUT/'support_locations.png',dpi=130);plt.close(fig)
    record=dict(scope='Native support-location witness; support necessity/removability remains separately reviewed',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=data)
    (OUT/'toolpaths.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))


if __name__=='__main__':inspect()
