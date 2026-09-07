"""CadQuery MCP checks of production interfaces, dimensions and final exports."""
from pathlib import Path
from collections import Counter, defaultdict
import ast
import hashlib
import json
import runpy
import struct
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

ROOT=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/verify_production_case.py')).resolve().parent
model=runpy.run_path(str(ROOT/'sunglasses_case.py'),init_globals={'EXPORT':False})
# Load the historical E definitions without executing its export/build loop.
# This is a verification-only reference, not the production geometry dependency.
old_file=ROOT/'keeper_latch_trials.py'
nodes=[]
for node in ast.parse(old_file.read_text()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='metrics' for t in node.targets):
        break
    nodes.append(node)
else:
    raise AssertionError('E reference definition boundary not found')
old={'__file__':str(old_file)}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(old_file),'exec'),old)
differences={}
for name,args in [('receiver',()),('keeper',()),('loop',(2.8,))]:
    a=getattr(model['closure'],name)(*args); b=old[name](*args)
    difference=a.cut(b).val().Volume()+b.cut(a).val().Volume()
    assert difference<0.001,(name,difference)
    differences[name]=difference
new_hinge=model['hinge'](0)
old_hinge=old['hinge'](0)
for i,(a,b) in enumerate(zip(new_hinge,old_hinge)):
    b=b.translate((0,model['HY']-old['HY'],model['SEAM']-old['SEAM']))
    difference=a.cut(b).val().Volume()+b.cut(a).val().Volume()
    assert difference<0.001,('hinge',i,difference)
    differences['hinge_'+str(i)]=difference
# Exercise a likely size change without changing source or final exports.
alternate=runpy.run_path(str(ROOT/'sunglasses_case.py'),init_globals={
    'EXPORT':False,'INNER_LENGTH':168.0,'INNER_WIDTH':88.0,'INNER_HEIGHT':68.0})
assert alternate['INNER_LENGTH']==168 and len(alternate['print_layout'].Solids())==3

step=cq.importers.importStep(str(ROOT/'sunglasses_case.step'))
solids=step.solids().vals()
assert len(solids)==3 and all(s.isValid() for s in solids)
def exact_bounds(shape):
    b=Bnd_Box(); BRepBndLib.AddOptimal_s(shape.wrapped,b,False,False)
    return list(b.Get())
order=lambda b:tuple(round(v,2) for v in b[:2])
step_bounds=sorted([exact_bounds(s) for s in solids],key=order)
raw=(ROOT/'sunglasses_case.stl').read_bytes()
count=struct.unpack_from('<I',raw,80)[0]
assert len(raw)==84+50*count
edges=Counter();owners=defaultdict(list);triangles=[];parent=list(range(count))
def root(i):
    while parent[i]!=i:
        parent[i]=parent[parent[i]];i=parent[i]
    return i
for i in range(count):
    values=struct.unpack_from('<12f',raw,84+50*i)
    tri=[tuple(values[3+j*3:6+j*3]) for j in range(3)]
    u=[tri[1][k]-tri[0][k] for k in range(3)]
    v=[tri[2][k]-tri[0][k] for k in range(3)]
    cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    assert sum(c*c for c in cross)>1e-16,('degenerate triangle',i)
    triangles.append(tri)
    for j in range(3):
        edge=tuple(sorted((tri[j],tri[(j+1)%3])))
        edges[edge]+=1;owners[edge].append(i)
assert set(edges.values())=={2},'unpaired mesh edges'
for a,b in owners.values():parent[root(a)]=root(b)
components=defaultdict(list)
for i,tri in enumerate(triangles):components[root(i)].extend(tri)
assert len(components)==3
mesh_bounds=sorted([[min(p[k] for p in pts) for k in range(3)]+[max(p[k] for p in pts) for k in range(3)] for pts in components.values()],key=order)
for mesh,cad in zip(mesh_bounds,step_bounds):
    assert abs(mesh[2])<0.001 and abs(cad[2])<0.001,('bed',mesh,cad)
    assert max(abs(a-b) for a,b in zip(mesh,cad))<0.035,('placement',mesh,cad)
checks={'E_interface_symmetric_difference_mm3':differences,
        'alternate_interior_checked_mm':[168,88,68],
        'valid_step_solids':3,'watertight_mesh_components':3,'triangles':count,
        'nondegenerate_triangles':True,'all_components_on_bed':True,
        'step_stl_individual_bounds_agree_mm':0.035,'step_component_bounds_mm':step_bounds,
        'STL_sha256':hashlib.sha256(raw).hexdigest(),
        'STEP_sha256':hashlib.sha256((ROOT/'sunglasses_case.step').read_bytes()).hexdigest()}
(ROOT/'notes'/'production_e_review'/'geometry_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
result=step
