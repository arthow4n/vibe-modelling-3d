"""Regenerate final artifacts; run with CadQuery or evaluate_file.

Reference comparison is optional and only runs if the ignored STEP exists.
"""
from pathlib import Path
import runpy
import json
import cadquery as cq
directory = Path(__file__).resolve().parent if '__file__' in globals() else Path('/home/hevar/git/vibe-modelling-3d/model/macbook_charger_holder')
ns = runpy.run_path(str(directory/'macbook_charger_holder.py'))
result = ns['result']
def bounds(s):
    b=s.val().BoundingBox()
    return [round(v,6) for v in (b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)]
report = {'units':'mm','placement':'XY ring face at Z=0','artifacts':{}}
# A generous local cable envelope from the next groove through the right side.
# This checks added cradle material, not the reference's deliberate cable grip.
path=ns['box'](ns['cradle_center']+ns['groove_pitch']-1.9,
               ns['cradle_center']+ns['head_width']/2+ns['side_clearance']+ns['rail_wall']+1,
               -8.5,-2.5,0,ns['band_width']+0.5)
obstruction=ns['cradle']().intersect(path).val().Volume()
assert obstruction<1e-6, ('right cable passage obstruction',obstruction)
report['right_passage_added_material_mm3']=obstruction
for name in ['macbook_charger_holder','cradle_test']:
    shape=runpy.run_path(str(directory/(name+'.py')))['result']
    cq.exporters.export(shape,str(directory/(name+'.step')))
    cq.exporters.export(shape,str(directory/(name+'.stl')),tolerance=0.025,angularTolerance=0.1)
    loaded=cq.importers.importStep(str(directory/(name+'.step')))
    assert max(abs(a-b) for a,b in zip(bounds(shape),bounds(loaded)))<0.01, (name,bounds(shape),bounds(loaded))
    assert loaded.val().isValid() and len(loaded.solids().vals())==1, (name,'invalid STEP')
    # Inspect STL vertices independently to confirm the exported placement.
    import struct
    data=(directory/(name+'.stl')).read_bytes()
    n=struct.unpack_from('<I',data,80)[0]
    vertices=[]
    for i in range(n):
        v=struct.unpack_from('<12fH',data,84+50*i)
        vertices.extend([v[3:6],v[6:9],v[9:12]])
    mesh_bounds=[min(p[k] for p in vertices) for k in range(3)]+[max(p[k] for p in vertices) for k in range(3)]
    assert max(abs(a-b) for a,b in zip(bounds(shape),mesh_bounds))<0.03, (name,bounds(shape),mesh_bounds)
    report['artifacts'][name]={'bounds':bounds(shape),'volume_mm3':shape.val().Volume(),'triangles':n,'STEP_STL_bounds_agree_within_mm':0.03}
reference=directory/'references/macbook charger 96w cable wrap v1.step'
if reference.exists():
    old=cq.importers.importStep(str(reference))
    new=ns['band']()
    delta=old.cut(new).val().Volume()+new.cut(old).val().Volume()
    report['reference_band_symmetric_difference_mm3']=delta
    assert delta<0.02, delta
# Check a plausible wider connector variant without replacing final source.
src=(directory/'macbook_charger_holder.py').read_text()
alternate={}
exec(compile(src.replace('side_clearance = 0.35','side_clearance = 0.55'),str(directory/'macbook_charger_holder.py'),'exec'),alternate)
assert alternate['result'].val().isValid()
report['alternate_side_clearance_0_55_valid']=True
(directory/'notes/verification.json').write_text(json.dumps(report,indent=2)+'\n')
