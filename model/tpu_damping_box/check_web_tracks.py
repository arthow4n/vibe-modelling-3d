"""Regression: the robust-web review must reject retained single-track cores."""
import json
from pathlib import Path
from execution.identity import digest
from physical_analysis.manufacturing import orca_linear_paths
from review_thin_paths import crossing_tracks, require_multiple_tracks

ROOT=Path(__file__).resolve().parent


def main():
    old=json.loads((ROOT/'notes/retired_thin_r4.json').read_text())
    gcode=Path(old['slice']['kept_run_directory'])/'plate_1.gcode'
    paths=list(orca_linear_paths(gcode))
    rows=[]
    for name,x,h,depth in (('I24',135.,1.4,.7),('I20',177.,1.2,.5)):
        a=.5*h/2.6
        shift=-a+4*a*min(depth/h,1-depth/h)
        px=x-1.8+shift
        start,end=(px-.85,117.1),(px+.85,117.1)
        z=round(.4+depth+.1,3)
        tracks=crossing_tracks(paths,start,end,z)
        try:
            require_multiple_tracks(paths,start,end,z,name,'retired floor core')
        except AssertionError:
            rows.append({'retired_variant':name,'z_mm':z,'tracks':tracks,'rejected':True})
        else:
            raise AssertionError(f'Negative control {name} incorrectly passes the replacement criterion')
    current=json.loads((ROOT/'notes/thin_path_review.json').read_text())
    witnesses=current['replacement_web_tracks']
    assert len(witnesses)==26 and {w['variant'] for w in witnesses}=={'I22','I10'}
    assert all(w['substantial_track_count']>=2 for w in witnesses)
    result={'scope':'Toolpath-review regression only; not a universal printability or acoustic verdict',
        'retired_source_commit':'5efd0e2','retired_receipt':'notes/retired_thin_r4.json',
        'retired_gcode_sha256':digest(gcode),'old_single_track_controls':rows,
        'current_review_sha256':digest(ROOT/'notes/thin_path_review.json'),
        'current_multi_track_witnesses':len(witnesses)}
    (ROOT/'notes/web_track_regression.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
