"""Evaluate with the shared CadQuery command to export and verify production geometry."""
from pathlib import Path
import runpy, json
import cadquery as cq
D = Path('/home/hevar/git/vibe-modelling-3d/model/vaseline_container')
m = runpy.run_path(str(D/'vaseline_container.py'))
base, lid, result = m['base'], m['lid'], m['result']
# Follow the screw trajectory from closed through release (clockwise to close).
motion = []
for angle in range(0, 1081, 30):
    moved = lid.rotate((0,0,0),(0,0,1),angle).translate((0,0,m['THREAD_PITCH']*angle/360))
    overlap = base.val().intersect(moved.val()).Volume()
    motion.append({'opening_degrees':angle,'intersection_mm3':overlap})
assert max(x['intersection_mm3'] for x in motion) < 1e-5
# Axial pull without turning must meet the thread flanks.
retention = base.val().intersect(lid.translate((0,0,0.8)).val()).Volume()
assert retention > 1
for name, shape in [('vaseline_container',result),('base',base.val()),('lid',m['print_lid'].val())]:
    cq.exporters.export(shape,str(D/(name+'.step')))
    cq.exporters.export(shape,str(D/(name+'.stl')),tolerance=0.015,angularTolerance=0.08)
cq.exporters.export(cq.Compound.makeCompound([base.val(),lid.val()]),str(D/'vaseline_container_assembled.step'))
report = {'motion_samples': motion, 'axial_pull_intersection_mm3': retention,
          'closed_height_mm': 25}
(D/'notes/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'motion_sample_count': len(motion),
                  'maximum_motion_intersection_mm3': max(x['intersection_mm3'] for x in motion),
                  'axial_pull_intersection_mm3': retention}))
