"""Summarize D/E diagnostic paths and independently check the printer footprint."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('paths',ROOT/'.codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py')
helper=importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
report={'profile':'../closure_review/review.ini',
        'profile_sha256':hashlib.sha256((HERE.parent/'closure_review'/'review.ini').read_bytes()).hexdigest(),
        'slices':{}}
for name in ('D_firm_side_printed_keeper','E_extra_firm_side_printed_keeper'):
    gcode=HERE/(name+'.gcode')
    log=(HERE/(name+'.log')).read_text()
    assert gcode.stat().st_size>0 and 'Slicing result exported' in log
    assert 'warning' not in log.lower()
    layers,metadata=helper.read_paths(gcode)
    lo=[float('inf')]*2; hi=[-float('inf')]*2
    keeper_roles=set()
    for paths in layers.values():
        for path in paths:
            assert not path['role'].startswith('Support material')
            for p in (path['a'],path['b']):
                for k in (0,1):
                    lo[k]=min(lo[k],p[k]-path['width_mm']/2)
                    hi[k]=max(hi[k],p[k]+path['width_mm']/2)
            # The separate insert occupies X ~164-170, Y ~94-101 on this bed.
            if path['role']!='Skirt/Brim' and all(162<p[0]<172 and 93<p[1]<103 for p in (path['a'],path['b'])):
                keeper_roles.add(path['role'])
    assert min(lo)>=0 and max(hi)<=260 and max(layers)<=250
    assert not keeper_roles.intersection({'Bridge infill','Overhang perimeter'})
    report['slices'][name]={'deposited_xy_bounds_mm':lo+hi,'max_z_mm':max(layers),
        'metadata':metadata,'insert_roles':sorted(keeper_roles),
        'stl_sha256':hashlib.sha256((HERE.parents[1]/(name+'.stl')).read_bytes()).hexdigest(),
        'gcode_sha256':hashlib.sha256(gcode.read_bytes()).hexdigest()}
(HERE/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
