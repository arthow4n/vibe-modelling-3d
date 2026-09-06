"""Summarize diagnostic slices, retaining hashes and actual deposited path bounds."""
from pathlib import Path
import importlib.util,json,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('inspect_gcode',ROOT/'.codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
report={'slicer':'PrusaSlicer 2.9.6+flathub.org','profile_sha256':hashlib.sha256((HERE/'review.ini').read_bytes()).hexdigest(),'slices':{}}
for name in ('dental_travel_case','test_pieces','accessories'):
    gcode=HERE/'run'/(name+'.gcode')
    log=(HERE/'run'/(name+'.log')).read_text()
    assert gcode.stat().st_size>0 and 'Slicing result exported' in log
    assert 'warning:' not in log.lower(),(name,log)
    layers,metadata=helper.read_paths(gcode)
    # Conservative XY bound: extend every straight segment endpoint by half
    # its reported extrusion width. Includes brim; not a physical flow model.
    low=[float('inf')]*2; high=[-float('inf')]*2
    for segments in layers.values():
        for segment in segments:
            assert not segment['role'].startswith('Support material')
            for point in (segment['a'],segment['b']):
                for k in (0,1):
                    low[k]=min(low[k],point[k]-segment['width_mm']/2)
                    high[k]=max(high[k],point[k]+segment['width_mm']/2)
    assert min(low)>=0 and max(high)<=260 and max(layers)<=250
    report['slices'][name]={'STL_sha256':hashlib.sha256((HERE.parents[1]/(name+'.stl')).read_bytes()).hexdigest(),
        'Gcode_sha256':hashlib.sha256(gcode.read_bytes()).hexdigest(),
        'nonempty_gcode_bytes':gcode.stat().st_size,'warnings':[],
        'xy_deposition_bounds_including_half_width_mm':[round(v,4) for v in low+high],
        'max_layer_z_mm':max(layers),'metadata':metadata}
(HERE/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
