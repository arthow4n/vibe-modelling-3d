"""Evaluate through CadQuery MCP; verify actual D/E STEP and STL exports."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import struct
import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

ROOT=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/sunglasses_case/verify_keeper_exports.py')).resolve().parent
checks={}
def exact_bounds(shape):
    bounds=Bnd_Box()
    BRepBndLib.AddOptimal_s(shape.wrapped,bounds,False,False)
    return list(bounds.Get())

for name in ('D_firm_side_printed_keeper','E_extra_firm_side_printed_keeper'):
    step=cq.importers.importStep(str(ROOT/(name+'.step')))
    solids=step.solids().vals()
    assert len(solids)==3 and all(s.isValid() for s in solids)
    order=lambda b: tuple(round(v,2) for v in b[:2])
    step_bounds=sorted([exact_bounds(s) for s in solids],key=order)
    raw=(ROOT/(name+'.stl')).read_bytes()
    count=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*count
    edges=Counter(); owners=defaultdict(list); triangles=[]; parent=list(range(count))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]; i=parent[i]
        return i
    for i in range(count):
        values=struct.unpack_from('<12f',raw,84+50*i)
        tri=[tuple(values[3+j*3:6+j*3]) for j in range(3)]
        u=[tri[1][k]-tri[0][k] for k in range(3)]
        v=[tri[2][k]-tri[0][k] for k in range(3)]
        cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        assert sum(c*c for c in cross)>1e-16, ('degenerate',i)
        triangles.append(tri)
        for j in range(3):
            edge=tuple(sorted((tri[j],tri[(j+1)%3])))
            edges[edge]+=1; owners[edge].append(i)
    assert set(edges.values())=={2}, 'unpaired edges'
    for a,b in owners.values(): parent[root(a)]=root(b)
    components=defaultdict(list)
    for i,tri in enumerate(triangles): components[root(i)].extend(tri)
    assert len(components)==3
    mesh_bounds=sorted([[min(p[k] for p in pts) for k in range(3)]+[max(p[k] for p in pts) for k in range(3)] for pts in components.values()],key=order)
    for mesh,cad in zip(mesh_bounds,step_bounds):
        assert abs(mesh[2])<0.001 and abs(cad[2])<0.001, ('bed',mesh,cad)
        assert max(abs(a-b) for a,b in zip(mesh,cad))<0.035, ('bounds',mesh,cad)
    checks[name]={'triangles':count,'valid_step_solids':3,'watertight_mesh_components':3,
                  'nondegenerate_triangles':True,'each_component_on_bed':True,
                  'individual_step_stl_bounds_agree_mm':0.035,'step_component_bounds':step_bounds,
                  'stl_sha256':hashlib.sha256(raw).hexdigest(),
                  'step_sha256':hashlib.sha256((ROOT/(name+'.step')).read_bytes()).hexdigest()}
    result=step
(ROOT/'notes'/'keeper_review'/'export_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
