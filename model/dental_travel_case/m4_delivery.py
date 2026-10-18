"""Associate completed current full/coupon publication, never promote physical use."""
import hashlib
import json
from pathlib import Path
from m4_checks import INPUTS,hashes

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m4'


def associate():
    cad=json.loads((OUT/'cad.json').read_text())
    assert cad['source_sha256']==hashes(INPUTS),'Production or coupon changed after preflight'
    assert cad['producer_sha256']==hashlib.sha256((ROOT/'m4_checks.py').read_bytes()).hexdigest()
    record=dict(scope='Paired current full/coupon exports after guarded publication; no physical acceptance.',
                inputs=hashes(INPUTS),artifacts={})
    for kind,stem in (('case','m4_case'),('joint','m4_joint_test')):
        report='notes/m4/'+kind+'_export_slice.json'
        receipt=json.loads((ROOT/report).read_text())
        assert receipt['ok'] and receipt['geometry']['valid'] and receipt['slice']['ok']
        assert receipt['slice']['input_sha256']==hashes((stem+'.stl',))[stem+'.stl']
        files=(stem+'.step',stem+'.stl',report)
        record['artifacts'][kind]=hashes(files)
    (OUT/'publication.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Associated both full case and joint sample with the same current production sources')


if __name__=='__main__':associate()
