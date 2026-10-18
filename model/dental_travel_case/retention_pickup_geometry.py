"""Exact M1 first-contact witness; no deformation or holding-force inference."""
from pathlib import Path
import json,hashlib
from retention_structure import assembly_case
from retention_geometry import planar_faces
case=assembly_case(variant='m1',modulus=1200,mesh=3,travel=2.5,increment=.02,eccentric=0,lateral=0,crop=False,penalty=20000,mesh_min_size=.5,mesh_curvature_points=8,grip_style='end',pickup=True)
body=case.parts['body'].shape.val();cap=case.parts['cap'].shape.val()
areas=[]
for h in planar_faces(body,178,-1):
 for r in planar_faces(cap,178,1):
  area=h.intersect(r).Area()
  if area>1e-7:areas.append({'area_mm2':area,'hook_centroid_mm':h.Center().toTuple(),'receiver_centroid_mm':r.Center().toTuple()})
volumes={str(offset):body.intersect(cap.translate((0,0,offset))).Volume() for offset in (-.01,0,.01)}
assert len(areas)==2 and all(abs(x['area_mm2']-12)<1e-6 for x in areas)
assert volumes['0']<1e-5 and volumes['-0.01']<1e-5 and volumes['0.01']>.2
root=Path(__file__).resolve().parent
answer={'scope':'Actual full M1 assembly_case pickup=True exact CAD. Initial unstrained cap shift .15mm omits axial frictionless zero-work freeplay only. No force, off-axis, native-mesh or retention qualification.','source_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('m1_design.py','retention_structure.py','retention_pickup_geometry.py')},'initial_lift_mm':.15,'coincident_retaining_faces':areas,'body_cap_intersection_mm3_by_additional_cap_lift':volumes,'status':'PASS'}
p=root/'notes/retention/m1_pickup_geometry.json';p.write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps(answer,indent=2))
