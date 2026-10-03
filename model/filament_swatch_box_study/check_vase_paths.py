"""V1 only: measured spiral inner wall against the existing four catch pads.

Uses the shared deposited-path reader. It does not recheck printer footprint or
promise force, material strength or optical performance. Retains the diagnostic
paths/profile; the G-code is evidence, not a calibrated production job.
"""
import gzip
import hashlib
import json
import math
import tempfile
from pathlib import Path
import cadquery as cq
import cap_v1_vase_hood_5 as v
from physical_analysis.manufacturing import orca_linear_paths
from revision_checks import sources

root=Path(__file__).parent
report=json.loads((root/'notes/v1_review.json').read_text())
assert report['slice']['ok']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(root/'cap_v1_vase_hood_5.stl')==report['slice']['input_sha256']
saved=root/'notes/v1_slice'
saved.mkdir(exist_ok=True)
run=Path(report['slice']['kept_run_directory'])
gcode=run/'plate_1.gcode'
if gcode.exists():
    data=gcode.read_bytes()
    (saved/'plate_1.gcode.gz').write_bytes(gzip.compress(data,mtime=0))
    for name in ('effective-settings.json',):
        (saved/Path(name).name).write_bytes((run/name).read_bytes())
    (saved/'support_probe.log.gz').write_bytes(gzip.compress((run/'support_probe/slicer.log').read_bytes(),mtime=0))
else:
    data=gzip.decompress((saved/'plate_1.gcode.gz').read_bytes())
probe=gzip.decompress((saved/'support_probe.log.gz').read_bytes()).decode()
assert 'Invalid value when spiral vase mode is enabled' in probe
settings=json.loads((saved/'effective-settings.json').read_text())
for name,value in dict(spiral_mode='1',spiral_mode_smooth='0',wall_loops='1',
                       bottom_shell_layers='4',top_shell_layers='0',layer_height='0.2',
                       outer_wall_line_width='0.42',outer_wall_speed='30').items():
    assert settings[name]==value,('Unexpected effective process',name,settings[name])
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'paths.gcode'
    path.write_bytes(data)
    paths=list(orca_linear_paths(path,spatial=True))
spiral=[p for p in paths if p[5]>1.2]
assert {p[7] for p in spiral}=={'Outer wall'},'Unexpected extra deposited wall/infill'
assert all(abs(p[6]-v.LINE_WIDTH)<1e-6 for p in spiral),'Unexpected mating wall width'

# Exact start/end Z comes from the shared reader, including non-deposited
# motion. Continuity is checked separately rather than used to invent height.
crossings=[]
rim_crossings=[]
max_gap=0
max_z_step=0
previous=None
for p in spiral:
    x0,y0,z0,x1,y1,z1,width,role=p
    if previous is None:
        previous=p
        continue
    gap=math.hypot(x0-previous[3],y0-previous[4])
    max_gap=max(max_gap,gap)
    assert gap<.002,'Spiral path is disconnected; cannot infer start Z'
    assert abs(z0-previous[5])<.002,'Non-deposited height jump in the spiral'
    assert z1>=z0-.0001,'Spiral path reverses height'
    max_z_step=max(max_z_step,z1-z0)
    previous=p
    if abs(y1-y0)<1e-8: continue
    for cy in v.g.detent_centres(v.g.COUNT):
        target_y=v.g.PRINT_ANCHOR[1]-cy
        t=(target_y-y0)/(y1-y0)
        if not 0<=t<1: continue
        x=x0+t*(x1-x0)-v.g.PRINT_ANCHOR[0]
        z=v.g.ROOF_TOP-(z0+t*(z1-z0))
        if abs(x)<v.g.OUTSIDE_X/2-2: continue
        if v.g.SEAM_Z-.001<z<v.g.SEAM_Z+.4:
            rim_crossings.append(dict(side=1 if x>0 else -1,y_mm=cy,z_mm=z,
                                      inner_x_abs_mm=abs(x)-width/2))
        if not 17.0<z<21.3: continue
        inside=abs(x)-width/2
        nominal=v.g.OUTSIDE_X/2-v.neck(z)-v.LINE_WIDTH
        crossings.append(dict(side=1 if x>0 else -1,y_mm=cy,z_mm=z,
                              inner_x_abs_mm=inside,nominal_inner_x_abs_mm=nominal))
assert crossings,'No actual mating-wall crossings found'
error=max(abs(p['inner_x_abs_mm']-p['nominal_inner_x_abs_mm']) for p in crossings)
# Orca interpolates between whole-layer contours while Z rises around each turn.
# Bound that geometric phase difference by one layer times the maximum waist
# slope. This is not printer tolerance; the actual catch checks below still
# require seated overlap, increased opening interference and eventual release.
phase_bound=v.NECK_DEPTH*math.pi/(2*v.NECK_HALF_SPAN)*.2+.002
assert error<phase_bound,('Sliced mating wall exceeds a one-layer contour phase',error,
    max(crossings,key=lambda p:abs(p['inner_x_abs_mm']-p['nominal_inner_x_abs_mm'])))

pad=v.g.pad(0).val()
contacts=[]
for side in (-1,1):
    for cy in v.g.detent_centres(v.g.COUNT):
        phases=[]
        for lift in (0,.8,3):
            samples=[]
            for p in crossings:
                z=p['z_mm']+lift
                if p['side']!=side or p['y_mm']!=cy or not 19.4<z<20.2: continue
                section=pad.intersect(cq.Workplane('XY').box(70,2,.002).translate((0,0,z)).val())
                if section.isNull(): continue
                # Specific catch radial reach at this height, not generic bounds.
                reach=section.BoundingBox().xmax
                samples.append(dict(base_z_mm=z,inner_x_mm=p['inner_x_abs_mm'],
                                    pad_x_mm=reach,overlap_mm=reach-p['inner_x_abs_mm']))
            assert samples,'Missing wall evidence at a catch phase'
            phases.append(dict(hood_lift_mm=lift,max_radial_overlap_mm=max(p['overlap_mm'] for p in samples),samples=samples))
        assert phases[0]['max_radial_overlap_mm']>.02,'Printed-path screen lacks closed engagement'
        assert phases[1]['max_radial_overlap_mm']>phases[0]['max_radial_overlap_mm']+.05,'No opening deformation increase'
        assert phases[2]['max_radial_overlap_mm']<0,'Catch does not release'
        contacts.append(dict(side=side,y_mm=cy,phases=phases))
rim_end=[min((p for p in rim_crossings if p['side']==side and p['y_mm']==cy),key=lambda p:p['z_mm'])
         for side in (-1,1) for cy in v.g.detent_centres(v.g.COUNT)]
flat_base_x=v.g.FOOT_X/2-v.g.FOOT_TOP_ROUND
assert all(abs(p['z_mm']-v.g.SEAM_Z)<.001 for p in rim_end),'Final contour does not level the rim'
assert all(flat_base_x-p['inner_x_abs_mm']>.2 for p in rim_end),'Actual rim lacks a positive radial landing'
record=dict(ok=True,question='Does the single spiral wall actually engage all four existing catches?',
    stl_sha256=sha(root/'cap_v1_vase_hood_5.stl'),gcode_sha256=hashlib.sha256(data).hexdigest(),
    process_sha256=sha(root/'notes/vase_process.json'),sources_sha256=sources(('cap_v1_vase_hood_5.py','check_vase_paths.py','../../physical_analysis/manufacturing.py')),
    deposited_roles_above_roof=['Outer wall'],line_width_mm=v.LINE_WIDTH,
    maximum_contiguous_path_gap_mm=max_gap,maximum_spiral_segment_z_step_mm=max_z_step,
    maximum_local_wall_error_mm=error,one_layer_contour_phase_bound_mm=phase_bound,contacts=contacts,
    rim_last_turn_crossings=rim_end,
    rim_flat_base_x_mm=flat_base_x,minimum_sampled_rim_landing_mm=min(flat_base_x-p['inner_x_abs_mm'] for p in rim_end),
    support_probe='N/A: Orca rejects enable_support=1 in spiral vase mode; primary slice succeeds.',
    limits='XY radial wall offset; .002 mm pad sections. No as-printed force/compliance/strength or optical validation.')
(root/'notes/v1_path_checks.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(ok=True,maximum_local_wall_error_mm=error,
    contacts=[dict(side=c['side'],y_mm=c['y_mm'],overlap_mm=[p['max_radial_overlap_mm'] for p in c['phases']]) for c in contacts])))
