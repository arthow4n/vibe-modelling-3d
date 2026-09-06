"""Evaluate with CadQuery MCP to regenerate and verify all final artifacts."""
from pathlib import Path
import runpy,json,struct,math
import cadquery as cq
D=Path(globals().get('__file__','/home/hevar/git/vibe-modelling-3d/model/dental_travel_case/export_and_check.py')).resolve().parent
ns=runpy.run_path(str(D/'test_pieces.py'))
main=ns['ns']
from parameters import *
from mechanisms import block
from components import compound,clip,divider_flat

report={'units':'mm','physical_testing':'Not yet printed; nominal reference items only','parts':{}}
def shape(p): return p.val() if isinstance(p,cq.Workplane) else p
def bounds(p):
    b=shape(p).BoundingBox()
    return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def export(name,p,expected):
    s=shape(p)
    assert s.isValid() and len(s.Solids())==expected,(name,'topology')
    bb=bounds(s)
    assert abs(bb[2])<0.001,(name,'bed contact')
    assert bb[3]-bb[0]+6<=260 and bb[4]-bb[1]+6<=260 and bb[5]<=250,(name,'build volume')
    cq.exporters.export(s,str(D/(name+'.step')))
    cq.exporters.export(s,str(D/(name+'.stl')),tolerance=0.025,angularTolerance=0.1)
    step=cq.importers.importStep(str(D/(name+'.step')))
    assert shape(step).isValid() and len(step.solids().vals())==expected
    assert max(abs(a-b) for a,b in zip(bb,bounds(step)))<0.01
    data=(D/(name+'.stl')).read_bytes()
    count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+50*count
    vertices=[]
    for i in range(count):
        v=struct.unpack_from('<12fH',data,84+50*i)
        vertices.extend([v[3:6],v[6:9],v[9:12]])
    mesh_bounds=[min(v[k] for v in vertices) for k in range(3)]+[max(v[k] for v in vertices) for k in range(3)]
    assert max(abs(a-b) for a,b in zip(bb,mesh_bounds))<0.03
    from collections import Counter
    edges=Counter()
    degenerate=0
    for i in range(0,len(vertices),3):
        tri=[tuple(round(c,5) for c in v) for v in vertices[i:i+3]]
        if len(set(tri))<3: degenerate+=1
        for a,b in zip(tri,tri[1:]+tri[:1]): edges[tuple(sorted((a,b)))]+=1
    bad_edges=sum(n!=2 for n in edges.values())
    assert degenerate==0 and bad_edges==0,(name,'mesh topology',degenerate,bad_edges)
    report['parts'][name]={'solids':expected,'bounds_mm':[round(v,4) for v in bb],
                          'solid_volume_cm3':round(s.Volume()/1000,3),'triangles':count,
                          'STEP_STL_bounds_agree_within_mm':0.03,'degenerate_triangles':degenerate,'unpaired_mesh_edges':bad_edges}

# Physical object approximations: these do not identify the user's items.
body,lid=main['body'],main['lid']
from reference_items import reference_items
items=reference_items()
handle=items['handle']
report['nominal_envelope_intersections_mm3']={}
for name,p in items.items():
    for partname,q in [('body',body),('lid',lid),('divider',main['installed_divider'])]:
        v=p.intersect(q).val().Volume()
        report['nominal_envelope_intersections_mm3'][name+'/'+partname]=round(v,6)
        assert v<0.001,(name,partname,v)
# Fixed contents and insert must also clear the moving lid, not only closed pose.
for angle in range(0,181,10):
    moving=lid.rotate((0,HY,SEAM),(1,HY,SEAM),-angle)
    for name,p in list(items.items())+[('divider',main['installed_divider'])]:
        assert moving.intersect(p).val().Volume()<0.001,('Loaded lid sweep',angle,name)
# Brush cannot travel backward into the head-end wall: shoulder meets its stop.
assert handle.translate((-1,0,0)).intersect(body).val().Volume()>0.001
report['loaded_lid_sweep_degrees']=list(range(0,181,10))
report['shoulder_stop_blocks_1mm_backward_travel']=True
for i,c in enumerate(main['installed_clips']):
    assert handle.intersect(c).val().Volume()<0.001,'Nominal handle clashes with clip'
    # The only permitted cartridge/socket intersection is the friction bumps.
    v=body.intersect(c).val().Volume()
    assert v<2.0,('Clip seat interference exceeds small friction points',v)
    report['clip_socket_interference_mm3_'+str(i)]=round(v,6)
closed_bb=bounds(main['closed'])
for name,p,n in [('dental_travel_case',main['result'],2),('accessories',main['accessories'],3),
                 ('handle_clip',clip(),1),('storage_divider',divider_flat(),1),
                 ('hinge_test',ns['hinge_sample'],2),('latch_test',ns['latch_sample'],2),
                 ('handle_test',ns['handle_sample'],3),('test_pieces',ns['result'],7)]:
    export(name,p,n)
cq.exporters.export(main['closed'],str(D/'dental_travel_case_assembled.step'))
report['closed_bounds_mm']=[round(v,4) for v in closed_bb]
report['parameters']={k:v for k,v in vars(__import__('parameters')).items() if k.isupper() and isinstance(v,(int,float,tuple))}
(D/'notes/verification.json').write_text(json.dumps(report,indent=2)+'\n')
result=main['opened']
