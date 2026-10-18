"""Associate matching M5 full/sample exports after current preflight/publication."""
import json
from pathlib import Path
from m5_checks import INPUTS,hashes

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m5'


def associate():
    cad=json.loads((OUT/'cad.json').read_text())
    assert cad['source_sha256']==hashes(INPUTS),'Production or sample changed after preflight'
    assert cad['producer_sha256']==hashes(('m5_checks.py',))['m5_checks.py']
    record=dict(scope='Same current production source for paired full/sample STEP/STL; no physical qualification.',
                inputs=hashes(INPUTS),artifacts={})
    for kind,stem in (('case','m5_case'),('joint','m5_joint_test')):
        report='notes/m5/'+kind+'_export_slice.json'
        receipt=json.loads((ROOT/report).read_text())
        assert receipt['ok'] and receipt['geometry']['valid'] and receipt['slice']['ok']
        assert receipt['slice']['input_sha256']==hashes((stem+'.stl',))[stem+'.stl']
        record['artifacts'][kind]=hashes((stem+'.step',stem+'.stl',report))
    (OUT/'publication.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Associated current M5 full model and matching joint sample')


if __name__=='__main__':associate()
