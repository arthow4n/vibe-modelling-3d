"""Bind C8's two material plates and retain scoped native path witnesses."""
import json
import hashlib
from pathlib import Path
from clamshell_study import ROOT,hashes

OUT=ROOT/'notes/spine'
MODELS=('c8_mini_shells','c8_spines')
INPUTS=('spine_design.py','clamshell_design.py','m1_design.py','../sunglasses_case/e_closure.py',
    '../tpu_damping_box/profiles/tpu-solid-process.json','../tpu_damping_box/profiles/tpu95a.json')+tuple(n+'.py' for n in MODELS)


def publish():
    from collections import Counter
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from physical_analysis.manufacturing import orca_linear_paths
    data=dict(scope='C8 complete mini-box plates: PETG shells and TPU spines; no physical approval',
        source_sha256=hashes(INPUTS),producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),artifacts={},native={})
    fig,axes=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for n,ax in zip(MODELS,axes):
        r=json.loads((OUT/(n+'_slice.json')).read_text())
        assert r['geometry']['valid'] and r['slice']['ok']
        assert r['slice']['input_sha256']==hashes((n+'.stl',))[n+'.stl']
        data['artifacts'][n]=hashes((n+'.step',n+'.stl','notes/spine/'+n+'_slice.json'))
        directory=Path(r['slice']['kept_run_directory'])
        primary=directory/'plate_1.gcode';probe=directory/'support_probe/plate_1.gcode'
        rows=list(orca_linear_paths(primary));prows=list(orca_linear_paths(probe))
        supports=[p for p in prows if p[-1].startswith('Support')]
        bridge=[p for p in rows if 'Bridge' in p[-1] or 'Overhang' in p[-1]]
        for subset,color in ((rows,'#91a5ad'),(supports,'#d34b55')):
            ax.add_collection(LineCollection([[(p[0],p[1]),(p[2],p[3])] for p in subset],colors=color,linewidths=.45,alpha=.45))
        ax.autoscale_view();ax.set(title=n+'; red = suggested supports',aspect='equal',xlabel='Printer X mm',ylabel='Printer Y mm')
        layers={}
        for p in bridge:
            v=layers.setdefault(str(round(p[4],3)),dict(strokes=0,max_stroke_mm=0))
            v['strokes']+=1;v['max_stroke_mm']=max(v['max_stroke_mm'],((p[0]-p[2])**2+(p[1]-p[3])**2)**.5)
        data['native'][n]=dict(support_roles=dict(Counter(p[-1] for p in supports)),bridge_layers=layers,
            support_z_range_mm=[min(p[4] for p in supports),max(p[4] for p in supports)] if supports else None,
            gcode_sha256={p.name if p==primary else 'probe':hashlib.sha256(p.read_bytes()).hexdigest() for p in (primary,probe)},
            extrusion_layers_mm=sorted({round(p[4],3) for p in rows}),effective_settings=r['slice']['effective_settings'])
    fig.savefig(OUT/'support_locations.png',dpi=130);plt.close(fig)
    (OUT/'publication.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Associated PETG and TPU plates and native path witnesses')


if __name__=='__main__':publish()
