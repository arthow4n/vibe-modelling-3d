"""Bind C6 experimental print layouts to their actual source and slice receipts."""
import json
from clamshell_study import ROOT,OUT,hashes

MODELS=('c6_body','c6_lid','c6_keeper','c6_latch_test')


def associate():
    cad=json.loads((OUT/'cad.json').read_text())
    assert cad['source_sha256']==hashes(tuple(cad['source_sha256']))
    inputs=('clamshell_design.py','m1_design.py','../sunglasses_case/e_closure.py')+tuple(n+'.py' for n in MODELS)
    record=dict(scope='C6 computational prototype and matching short-loop crop; no physical approval',inputs=hashes(inputs),artifacts={})
    for name in MODELS:
        receipt='notes/clamshell/'+name+'_slice.json'
        report=json.loads((ROOT/receipt).read_text())
        assert report['geometry']['valid'] and report['slice']['ok']
        assert report['slice']['input_sha256']==hashes((name+'.stl',))[name+'.stl']
        record['artifacts'][name]=hashes((name+'.step',name+'.stl',receipt))
    (OUT/'publication.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Associated C6 prototype and short-loop trial exports')


if __name__=='__main__':associate()
