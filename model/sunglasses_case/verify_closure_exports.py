"""Evaluate with CadQuery MCP to check actual exported STEP and STL files."""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import struct
import cadquery as cq

ROOT=Path('/home/hevar/git/vibe-modelling-3d/model/sunglasses_case')
checks={}
for name in ('A_twin_hinge_loop_1p8','B_twin_hinge_loop_2p6','C_located_loop_2p6'):
    step=cq.importers.importStep(str(ROOT/(name+'.step')))
    solids=step.solids().vals()
    assert len(solids)==2 and all(s.isValid() for s in solids)
    assert all(abs(s.BoundingBox().zmin)<0.001 for s in solids)
    raw=(ROOT/(name+'.stl')).read_bytes()
    count=struct.unpack_from('<I',raw,80)[0]
    assert len(raw)==84+50*count
    edges=Counter(); owners=defaultdict(list); points=[]; parent=list(range(count))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]; i=parent[i]
        return i
    for i in range(count):
        values=struct.unpack_from('<12f',raw,84+50*i)
        tri=[tuple(values[3+j*3:6+j*3]) for j in range(3)]
        assert len(set(tri))==3
        points.extend(tri)
        for j in range(3):
            edge=tuple(sorted((tri[j],tri[(j+1)%3])))
            edges[edge]+=1; owners[edge].append(i)
    assert set(edges.values())=={2}
    for a,b in owners.values(): parent[root(a)]=root(b)
    assert len({root(i) for i in range(count)})==2
    bb=step.val().BoundingBox()
    lows=[min(p[k] for p in points) for k in range(3)]
    highs=[max(p[k] for p in points) for k in range(3)]
    for value,actual in zip(lows+highs,[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]):
        assert abs(value-actual)<0.03
    checks[name]={'triangles':count,'components':2,'valid_step_solids':2,
                  'paired_mesh_edges':True,'both_step_solids_on_bed':True,
                  'step_stl_bounds_agree_mm':0.03,
                  'stl_sha256':hashlib.sha256(raw).hexdigest(),
                  'bounds_mm':[hi-lo for lo,hi in zip(lows,highs)]}
    result=step
(ROOT/'notes'/'closure_review'/'export_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
