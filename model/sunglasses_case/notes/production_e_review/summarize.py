"""Hash and footprint checks for the final case's diagnostic PrusaSlicer paths."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('paths',ROOT/'.codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
gcode=HERE/'case.gcode';log=(HERE/'case.log').read_text()
assert gcode.stat().st_size>0 and 'Slicing result exported' in log and 'warning' not in log.lower()
layers,metadata=helper.read_paths(gcode)
lo=[float('inf')]*2;hi=[-float('inf')]*2;keeper_roles=set()
for paths in layers.values():
    for path in paths:
        assert not path['role'].startswith('Support material')
        for point in (path['a'],path['b']):
            for k in (0,1):
                lo[k]=min(lo[k],point[k]-path['width_mm']/2)
                hi[k]=max(hi[k],point[k]+path['width_mm']/2)
        if path['role']!='Skirt/Brim' and all(214<p[0]<224 and 71<p[1]<81 for p in (path['a'],path['b'])):
            keeper_roles.add(path['role'])
assert min(lo)>=0 and max(hi)<=260 and max(layers)<=250
assert not keeper_roles.intersection({'Overhang perimeter','Bridge infill'})
stl_hash=hashlib.sha256((HERE.parents[1]/'sunglasses_case.stl').read_bytes()).hexdigest()
checks=json.loads((HERE/'geometry_checks.json').read_text())
assert stl_hash==checks['STL_sha256']
summary={'slicer':'PrusaSlicer 2.9.6','profile':'../closure_review/review.ini',
    'profile_sha256':hashlib.sha256((HERE.parent/'closure_review'/'review.ini').read_bytes()).hexdigest(),
    'STL_sha256':stl_hash,'gcode_sha256':hashlib.sha256(gcode.read_bytes()).hexdigest(),
    'deposited_xy_bounds_including_half_width_mm':lo+hi,'max_z_mm':max(layers),
    'metadata':metadata,'separate_keeper_roles':sorted(keeper_roles),'warnings':[]}
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
