"""Locate C6's actual support suggestions and bridge strokes, without guessing."""
import json
import hashlib
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths
from clamshell_study import ROOT,OUT


def inspect():
    records={};fig,axes=plt.subplots(1,3,figsize=(15,5),layout='constrained')
    for ax,name in zip(axes,('c6_body','c6_lid','c6_latch_test')):
        receipt=json.loads((OUT/(name+'_slice.json')).read_text())
        directory=Path(receipt['slice']['kept_run_directory'])
        primary=directory/'plate_1.gcode';probe=directory/'support_probe/plate_1.gcode'
        paths=list(orca_linear_paths(primary));suggested=list(orca_linear_paths(probe))
        bridge=[p for p in paths if 'Bridge' in p[-1] or 'Overhang' in p[-1]]
        support=[p for p in suggested if p[-1].startswith('Support')]
        def bounds(rows):
            if not rows:return None
            return dict(x_mm=[min(min(p[0],p[2]) for p in rows),max(max(p[0],p[2]) for p in rows)],
                y_mm=[min(min(p[1],p[3]) for p in rows),max(max(p[1],p[3]) for p in rows)],
                z_mm=[min(p[4] for p in rows),max(p[4] for p in rows)])
        layers={}
        for p in bridge:
            key=str(round(p[4],4));row=layers.setdefault(key,dict(strokes=0,max_stroke_mm=0.))
            row['strokes']+=1;row['max_stroke_mm']=max(row['max_stroke_mm'],((p[2]-p[0])**2+(p[3]-p[1])**2)**.5)
        for rows,color in ((support,'#d44b55'),(bridge,'#1875af')):
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in rows],colors=color,linewidths=.5,alpha=.45))
        ax.autoscale_view()
        ax.set(title=name+'\nblue bridge/overhang; red suggested support',xlabel='Printer X mm',ylabel='Printer Y mm',aspect='equal')
        records[name]=dict(STL_sha256=receipt['slice']['input_sha256'],
            primary_gcode_sha256=hashlib.sha256(primary.read_bytes()).hexdigest(),
            probe_gcode_sha256=hashlib.sha256(probe.read_bytes()).hexdigest(),
            bridge_roles=dict(Counter(p[-1] for p in bridge)),support_roles=dict(Counter(p[-1] for p in support)),
            bridge_bounds=bounds(bridge),support_bounds=bounds(support),bridge_layers=layers)
    fig.savefig(OUT/'support_locations.png',dpi=130);plt.close(fig)
    data=dict(scope='Native path location witness only; CAD support and review interpretation belong in the object record.',
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=records)
    (OUT/'support_locations.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data),flush=True)


if __name__=='__main__':inspect()
