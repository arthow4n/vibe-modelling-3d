"""Record actual deposited path bounds, including brim, for diagnostic slices."""
from pathlib import Path
import importlib.util
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('paths', ROOT / '.codex/skills/prusa-slicer-printability/scripts/inspect_gcode.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
report = {}
for name in ('A_twin_hinge_loop_1p8', 'B_twin_hinge_loop_2p6', 'C_located_loop_2p6'):
    gcode = HERE / (name + '.gcode')
    log = (HERE / (name + '.log')).read_text()
    assert 'Slicing result exported' in log and 'warning:' not in log.lower()
    layers, metadata = helper.read_paths(gcode)
    low, high = [float('inf')] * 2, [-float('inf')] * 2
    for segments in layers.values():
        for segment in segments:
            assert not segment['role'].startswith('Support material')
            for point in (segment['a'], segment['b']):
                for k in (0, 1):
                    low[k] = min(low[k], point[k] - segment['width_mm'] / 2)
                    high[k] = max(high[k], point[k] + segment['width_mm'] / 2)
    assert min(low) >= 0 and max(high) <= 260 and max(layers) <= 250
    report[name] = {'deposition_xy_bounds_mm': low + high, 'max_z_mm': max(layers),
                    'metadata': metadata,
                    'stl_sha256': hashlib.sha256((HERE.parents[1] / (name + '.stl')).read_bytes()).hexdigest(),
                    'gcode_sha256': hashlib.sha256(gcode.read_bytes()).hexdigest()}
(HERE / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
