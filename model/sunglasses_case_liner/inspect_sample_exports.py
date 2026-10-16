"""Investigate reported STEP/STL mismatch; not a routine export audit.

A successful export receipt alone cannot answer whether the file the user opens
contains the old 20 mm crop. Compare delivered STEP to source, STL coordinates
and the prior committed STEP; do not rewrite or reslice accepted geometry.
"""
from pathlib import Path
import json
import struct
import subprocess
import tempfile
import cadquery as cq
import bottom_sample as sample

ROOT=Path(__file__).resolve().parent


def dimensions(shape):
    b=shape.BoundingBox()
    return [b.xlen,b.ylen,b.zlen]


def main():
    step=cq.importers.importStep(str(ROOT/'bottom_sample.step')).val()
    source=sample.result.val()
    residuals=[step.cut(source).Volume(),source.cut(step).Volume()]
    assert max(residuals)<1e-7, 'Delivered STEP differs from current source'
    data=(ROOT/'bottom_sample.stl').read_bytes()
    triangles=struct.unpack_from('<I',data,80)[0]
    vertices=[struct.unpack_from('<3f',data,84+i*50+12+j*12)
              for i in range(triangles) for j in range(3)]
    stl_size=[max(v[a] for v in vertices)-min(v[a] for v in vertices) for a in range(3)]
    step_size=dimensions(step)
    assert all(abs(a-b)<1e-5 for a,b in zip(step_size,stl_size)), 'STEP/STL size mismatch'
    old_bytes=subprocess.run(['git','show','14ecd3c:model/sunglasses_case_liner/bottom_sample.step'],
        cwd=ROOT,check=True,capture_output=True).stdout
    with tempfile.TemporaryDirectory(prefix='sample-step-history-') as tmp:
        old_path=Path(tmp)/'old.step';old_path.write_bytes(old_bytes)
        old_size=dimensions(cq.importers.importStep(str(old_path)).val())
    result=dict(reason='User reports delivered STEP looks unchanged while STL looks correct',
        current_step_mm=step_size,current_stl_mm=stl_size,
        preceding_step_mm=old_size,step_vs_current_source_difference_mm3=residuals,
        conclusion='Delivered local STEP matches current source and STL dimensions; predecessor STEP was 20 mm')
    (ROOT/'notes/sample_export_inspection.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
