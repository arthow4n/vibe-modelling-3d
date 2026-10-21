"""Review the fast two-cup layout using existing local path checks."""
from pathlib import Path
import gzip,json
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths
from review_t_skin import local,section,point_section,MARGIN,PROFILES
from review_thin_gap import SOURCES
import thin_gap_design as d
ROOT=Path(__file__).resolve().parent
NOTES=ROOT/'notes/thin_gap'


def main():
    native=json.loads((NOTES/'cups_final.json').read_text())
    assert native['geometry']['valid'] and all(e['ok'] for e in native['exports'])
    smoke=native['slice'];assert smoke['ok'] and not smoke['log_notices']
    assert smoke['input_sha256']==digest(ROOT/'thin_gap_cups.stl')
    run=Path(smoke['kept_run_directory']);settings=json.loads((run/'effective-settings.json').read_text())
    for k,v in {'wall_generator':'classic','detect_thin_wall':'0','layer_height':'0.2',
                'initial_layer_print_height':'0.2','outer_wall_line_width':'0.42','inner_wall_line_width':'0.45','enable_support':'0'}.items():assert settings[k]==v
    raw=run/'plate_1.gcode';paths=list(orca_linear_paths(raw));rows={}
    for name,cx in (('L20',60),('L18',102)):
        v=d.variant_named(name);part=local(paths,cx,60,34);faces=[]
        for a in (0,90,180,270):
            sec=section(part,10.,2.2,(-17,-17+v.wall),a)
            assert len(sec['intervals_mm'])==2 and sec['internal_gap_mm']>=v.gap-MARGIN
            assert min(b-a for a,b in sec['intervals_mm'])>=.8-MARGIN
            tie=section(part,3.,0,(-17+.8,-17+.8+v.gap),a)
            assert tie['uncovered_width_mm']<MARGIN
            faces.append({'face_deg':a,'gap_section':sec,'tie_section':tie})
        cut=point_section(part,17-1.7,-17+3.75,.2)
        backed=point_section(part,17-1.7,-17+3.75,.4)
        assert cut['filled_width_mm']<.01 and backed['uncovered_width_mm']<MARGIN
        rows[name]={'faces':faces,'label_cut':cut,'backing':backed}
    probe=[p for p in orca_linear_paths(run/'support_probe/plate_1.gcode') if p[-1].startswith('Support')]
    zs=sorted(set(p[4] for p in probe));assert zs==[1.0],zs
    (NOTES/'cups_paths.gcode.gz').write_bytes(gzip.compress(raw.read_bytes(),mtime=0))
    result={'checks_passed':True,'artifact_identity':native['reuse']['artifact_identity'],
      'input_sha256':smoke['input_sha256'],'gcode_sha256':digest(raw),'cup_checks':rows,
      'source_sha256':{f:digest(ROOT/f) for f in (*SOURCES,'thin_gap_cups.py','review_thin_gap_cups.py')},
      'export_sha256':{f'thin_gap_cups.{e}':digest(ROOT/f'thin_gap_cups.{e}') for e in ('step','stl')},
      'profile_sha256':{f:digest(ROOT/f) for f in PROFILES},'support_interface_z_mm':zs,
      'support_decision':'Only existing horizontal floor cores flagged; retain approved T08 supports-off strategy. Printed sag remains a physical question.'}
    (NOTES/'cups_paths.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'checks_passed':True,'support_interface_z_mm':zs}))

if __name__=='__main__':main()
