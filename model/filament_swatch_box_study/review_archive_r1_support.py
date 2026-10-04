"""Locate generated support contacts, using the shared Orca path reader.

This answers removal/feature-access questions only, not printer footprint or
deposited strength. The native automatic-support report owns support presence.
"""
import hashlib
import json
from pathlib import Path
from physical_analysis.manufacturing import orca_linear_paths

root = Path(__file__).parent
report = json.loads((root/'notes/archive_r1_support_review.json').read_text())
slice_report = report['slice']
model = root/'archive_r1_base_15.stl'
assert hashlib.sha256(model.read_bytes()).hexdigest()==slice_report['input_sha256']
run = Path(slice_report['kept_run_directory'])
path = run/'support_probe/plate_1.gcode'
groups = {}
for x0,y0,z0,x1,y1,z1,width,role in orca_linear_paths(path,spatial=True):
    if role!='Support interface':
        continue
    z = round(z1,3)
    points = groups.setdefault(z,[])
    points.extend(((x0-80,y0-135),(x1-80,y1-135)))
summary = []
for z,points in sorted(groups.items()):
    summary.append(dict(z_mm=z,x_range_mm=[min(p[0] for p in points),max(p[0] for p in points)],
        y_range_mm=[min(p[1] for p in points),max(p[1] for p in points)]))
record = dict(input_sha256=slice_report['input_sha256'],
    gcode_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),interface_locations=summary,
    scope='Interface strokes in source-relative coordinates; location review only, not physical contact forces or print-footprint validation.')
(root/'notes/archive_r1_support_locations.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
