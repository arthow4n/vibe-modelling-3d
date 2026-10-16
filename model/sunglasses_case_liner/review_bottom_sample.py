"""Local baseline path review for the 20 mm bottom-panel ironing coupon."""
from collections import defaultdict
from pathlib import Path
import json
from physical_analysis.manufacturing import orca_linear_paths, section_coverage
from review_paths import multiple_tracks

ROOT=Path(__file__).resolve().parent


def main():
    receipt=json.loads((ROOT/'notes/bottom_sample_final.json').read_text())
    run=Path(receipt['slice']['kept_run_directory'])
    settings=json.loads((run/'effective-settings.json').read_text())
    assert settings['ironing_type']=='no ironing', 'Baseline must have ironing disabled'
    assert settings['layer_height']=='0.1' and settings['enable_support']=='0'
    layers=defaultdict(list)
    for p in orca_linear_paths(run/'plate_1.gcode'):
        layers[round(p[4],3)].append(p)
    channels=tracks=0
    for z in (.5,.8,1.2):
        for offset in (-6.6,-2.2,2.2,6.6):
            air=section_coverage(layers[z],x_mm=135+offset,z_mm=z,span_mm=(130,140))
            assert air['filled_width_mm']<.01, 'Sample core channel filled'
            channels+=1
        for offset in (-4.4,0,4.4):
            multiple_tracks(layers[z],135+offset,137.3,z,'x')
            tracks+=1
    roof=[p for p in layers[1.3] if abs((p[0]+p[2])/2-135)<7 and abs((p[1]+p[3])/2-135)<7]
    assert roof and all(abs(p[2]-p[0])>3*abs(p[3]-p[1]) for p in roof), 'First contact skin does not bridge across ribs'
    assert any(p[-1]=='Top surface' for p in layers[1.6]), 'Exposed top surface absent'
    report=dict(scope='Baseline slicer paths only; ironing comparison requires user prints',
                ironing='off',open_channel_samples=channels,multiple_track_rib_sections=tracks,
                first_contact_skin_z_mm=1.3,top_z_mm=1.6,
                minimum_rib_tracks=2,substantial_track_width_range_mm=[.38,.65])
    (ROOT/'notes/bottom_sample_paths.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
