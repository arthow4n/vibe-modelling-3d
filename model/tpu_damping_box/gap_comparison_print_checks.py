"""Actual fixed-skin and variable-core paths under the shared TPU process."""
from pathlib import Path
from collections import defaultdict
import hashlib,json
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
import gap_comparison_design as d
ROOT=Path(__file__).resolve().parent


def check(name):
    v=d.variant_named(name);directory=ROOT/'notes/gap_comparison'/name
    r=json.loads((directory/'native.json').read_text());assert r['ok'] and r['slice']['ok']
    run=Path(r['slice']['kept_run_directory']);gcode=run/'plate_1.gcode'
    settings=json.loads((run/'effective-settings.json').read_text())
    assert settings['wall_generator']=='classic' and settings['detect_thin_wall']=='0'
    assert settings['top_shell_layers']=='4' and settings['bottom_shell_layers']=='4'
    layers=defaultdict(list)
    for q in orca_linear_paths(gcode):
        if not q[-1].startswith(('Support','Brim')):layers[round(q[4],5)].append(q)
    rows=[]
    roof=[round(d.SKIN+v.gap+.2*i,5) for i in (1,2,3,4)]
    for cx,part in ((60.,'cup'),(102.,'pad')):
        for z in [.2,.4,.6,.8]+roof:
            c=section_coverage(layers[z],x_mm=cx+1.1,z_mm=z,span_mm=(60.7,61.5))
            assert c['uncovered_width_mm']<.06,(name,part,z,c)
            rows.append(dict(part=part,kind='skin',z_mm=z,coverage=c))
        for z in (round(d.SKIN+.2,5),round(d.SKIN+v.gap,5)):
            c=section_coverage(layers[z],x_mm=cx+1.1,z_mm=z,span_mm=(60.7,61.5))
            assert c['filled_width_mm']<.01,(name,part,z,c)
            rows.append(dict(part=part,kind='air',z_mm=z,coverage=c))
    low,high=d.wall_rows(name)[2:4];height=round(round(((low+high)/2)/.2)*.2,5)
    for sign in (-1,1):
        spans=((17.,17.-d.SKIN),(17.-d.SKIN-v.gap,17.-v.total))
        for span in spans:
            c=section_coverage(layers[height],x_mm=55.6,z_mm=height,
                span_mm=tuple(sorted(60+sign*i for i in span)))
            assert c['uncovered_width_mm']<.06,(name,height,c)
            rows.append(dict(part='wall',kind='skin',z_mm=height,coverage=c))
        span=tuple(sorted(60+sign*i for i in (17-d.SKIN,17-d.SKIN-v.gap)))
        c=section_coverage(layers[height],x_mm=55.6,z_mm=height,span_mm=span)
        assert c['uncovered_width_mm']>=v.gap-.05,(name,height,c)
        rows.append(dict(part='wall',kind='air',z_mm=height,coverage=c))
    support=[]
    if r['slice']['support_probe']['generated']:
        support=[q for q in orca_linear_paths(run/'support_probe/plate_1.gcode') if q[-1].startswith('Support')]
        # Expected probe signal lies in the enclosed horizontal roof core.
        # A new signal higher up is left unresolved for separate inspection.
        assert all(d.SKIN-1e-5<=q[4]<=d.SKIN+v.gap+1e-5 for q in support),'Support outside floor core; inspect before delivery'
        for q in support:
            cx=min((60.,102.),key=lambda x:abs(x-(q[0]+q[2])/2))
            half=(d.SIZE if cx==60. else d.PAD_SIZE)/2-d.LAND
            assert min(q[0],q[2])-q[5]/2>=cx-half-1e-5,q
            assert max(q[0],q[2])+q[5]/2<=cx+half+1e-5,q
            assert min(q[1],q[3])-q[5]/2>=60.-half-1e-5,q
            assert max(q[1],q[3])+q[5]/2<=60.+half+1e-5,q
    out=dict(source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
        ('gap_comparison_design.py','gap_comparison_print_checks.py','l20_standard.py','../../physical_analysis/manufacturing.py')},
        sections=rows,variant=name,profile_mm=[d.SKIN,v.gap,d.SKIN],
        support_segments=len(support),support_z_mm=[min(q[4] for q in support),max(q[4] for q in support)] if support else None,
        support_review='Any proposed supports confined to enclosed floor cores; primary supports off. Roof stays a physical bridge trial.',
        review_complete=True,gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),input_sha256=r['slice']['input_sha256'],
        limits='Selected-profile path presence/open core, not measured sag, bond quality, damping or stiffness')
    (directory/'paths.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(variant=name,sections=len(rows),support_segments=len(support))))


if __name__=='__main__':
    for name in ('G08','G16'):check(name)
