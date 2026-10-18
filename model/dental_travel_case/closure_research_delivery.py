"""Bind all four specimen STEP/STL pairs to their current shared builder."""
import json
from pathlib import Path
from closure_research_checks import hashes
from closure_research_design import KINDS

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_research'


def associate():
    cad=json.loads((OUT/'cad.json').read_text())
    assert cad['source_sha256']==hashes(tuple(cad['source_sha256']))
    inputs=('m1_design.py','closure_research_design.py')+tuple(k+'_test.py' for k in KINDS)
    record=dict(scope='Current research specimen pairs only; not full-product or physical qualification.',
                inputs=hashes(inputs),artifacts={})
    for kind in KINDS:
        stem=kind+'_test';receipt='notes/closure_research/'+kind+'_slice.json'
        report=json.loads((ROOT/receipt).read_text())
        assert report['ok'] and report['geometry']['valid'] and report['slice']['ok']
        assert report['slice']['input_sha256']==hashes((stem+'.stl',))[stem+'.stl']
        record['artifacts'][kind]=hashes((stem+'.step',stem+'.stl',receipt))
    (OUT/'publication.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Associated all four current research specimen pairs')


if __name__=='__main__':associate()
