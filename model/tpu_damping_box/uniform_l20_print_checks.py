"""Actual floor/pad/wall paths for the revised standard, not strength qualification."""
from pathlib import Path
from collections import defaultdict
import json,hashlib
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from model.tpu_damping_box.l20_standard import SKIN,CORE,TOTAL

ROOT=Path(__file__).resolve().parent


def main():
    n=ROOT/'notes/uniform_l20';r=json.loads((n/'native.json').read_text())
    assert r['ok'] and r['slice']['ok']
    run=Path(r['slice']['kept_run_directory']);gcode=run/'plate_1.gcode'
    settings=json.loads((run/'effective-settings.json').read_text())
    assert settings['wall_generator']=='classic' and settings['detect_thin_wall']=='0'
    assert settings['top_shell_layers']=='4' and settings['bottom_shell_layers']=='4'
    layers=defaultdict(list)
    for q in orca_linear_paths(gcode):
        if not q[-1].startswith(('Support','Brim')):layers[round(q[4],5)].append(q)
    rows=[]
    for cx,part in ((60.,'cup'),(102.,'pad')):
        for z in (.2,.4,.6,.8,1.4,1.6,1.8,2.):
            c=section_coverage(layers[z],x_mm=cx+1.1,z_mm=z,span_mm=(60.7,61.5))
            assert c['uncovered_width_mm']<.06,(part,z,c)
            rows.append(dict(part=part,z_mm=z,kind='skin',coverage=c))
        c=section_coverage(layers[1.],x_mm=cx+1.1,z_mm=1.,span_mm=(60.7,61.5))
        assert c['filled_width_mm']<.01,(part,c)
        rows.append(dict(part=part,z_mm=1.,kind='air',coverage=c))
    for z in (5.,10.,15.,20.,25.):
        for span in ((43.,43.8),(44.2,45.)):
            c=section_coverage(layers[z],x_mm=55.6,z_mm=z,span_mm=span)
            assert c['uncovered_width_mm']<.06,(z,c)
            rows.append(dict(part='upright wall',z_mm=z,coverage=c))
        c=section_coverage(layers[z],x_mm=55.6,z_mm=z,span_mm=(43.8,44.2))
        assert c['uncovered_width_mm']>=.35,(z,c)
    support=[]
    if r['slice']['support_probe']['generated']:
        for q in orca_linear_paths(run/'support_probe/plate_1.gcode'):
            if not q[-1].startswith('Support'):continue
            assert SKIN-1e-5<=q[4]<=SKIN+CORE+1e-5,('Unexpected support outside floor/pad core',q)
            support.append(q)
    out=dict(source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
            for p in ('l20_standard.py','uniform_l20_design.py','uniform_l20_print_checks.py','../../physical_analysis/manufacturing.py')},
        sections=rows,profile_mm=[SKIN,CORE,SKIN],
        support_segments=len(support),support_review='Any forced probe support confined to enclosed floor/pad air cores; primary supports off',
        effective_settings={k:settings[k] for k in ('layer_height','wall_generator','top_shell_layers','bottom_shell_layers','ironing_type','ironing_flow')},
        gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),input_sha256=r['slice']['input_sha256'],
        review_complete=True,limits='Selected-setup path coverage/open air only; printed sag, bond quality, damping and integrity unknown')
    (n/'paths.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(sections=len(rows),support_segments=len(support))))


if __name__=='__main__':
    main()
