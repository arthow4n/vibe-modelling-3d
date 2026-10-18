"""Associate paired short-sample exports and their final smoke receipts."""
import json
from closure_research_checks import hashes
from closure_short_checks import OUT, ROOT
from closure_short_design import KINDS


def associate():
    cad=json.loads((OUT/'cad.json').read_text())
    assert cad['source_sha256']==hashes(tuple(cad['source_sha256']))
    inputs=('m1_design.py','closure_research_design.py','closure_short_design.py')+tuple(k+'_short_test.py' for k in KINDS)
    record=dict(scope='Short research specimens only, not the long force-study fixture.',inputs=hashes(inputs),artifacts={})
    for kind in KINDS:
        stem=kind+'_short_test';receipt='notes/closure_short/'+kind+'_slice.json'
        report=json.loads((ROOT/receipt).read_text())
        assert report['ok'] and report['geometry']['valid'] and report['slice']['ok']
        assert report['slice']['input_sha256']==hashes((stem+'.stl',))[stem+'.stl']
        record['artifacts'][kind]=hashes((stem+'.step',stem+'.stl',receipt))
    (OUT/'publication.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Associated all four short specimen pairs')


if __name__=='__main__':associate()
