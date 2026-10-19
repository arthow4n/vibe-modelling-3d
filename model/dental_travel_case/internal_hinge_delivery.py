"""Associate the two complete C7 samples with current builders and native slices."""
import json
from clamshell_study import ROOT, hashes

OUT=ROOT/'notes/internal_hinge'
MODELS=('c7_mini_screw','c7_mini_pip')
INPUTS=('internal_hinge_design.py','clamshell_design.py','m1_design.py',
    '../sunglasses_case/e_closure.py')+tuple(n+'.py' for n in MODELS)


def associate():
    data=dict(scope='Two unprinted complete mini-box trials; no full-case adoption or physical approval',
        source_sha256=hashes(INPUTS),artifacts={})
    for n in MODELS:
        r=json.loads((OUT/(n+'_slice.json')).read_text())
        assert r['geometry']['valid'] and r['slice']['ok']
        assert r['slice']['input_sha256']==hashes((n+'.stl',))[n+'.stl']
        data['artifacts'][n]=hashes((n+'.step',n+'.stl','notes/internal_hinge/'+n+'_slice.json'))
    (OUT/'publication.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Associated both complete C7 mini-box layouts')


if __name__=='__main__':associate()
