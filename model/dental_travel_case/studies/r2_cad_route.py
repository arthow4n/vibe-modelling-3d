"""Route search on triangulated CAD sections; shortlisted route needs CAD checks.

Sections cover curved axial ends, bearings, pocket barriers and the central shell.
No dynamics/force claim. Triangle chord accuracy is not native-CAD clearance.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cadquery as cq
import numpy as np
import json
from collections import deque
import heapq
from r2_geometry import rough, AXIS_Y,AXIS_Z,LID_AXIS_Y,LINK_SPACING,CLOSED_LINK_ANGLE,HEIGHT
from studies.support_free_r2_c import collide

case=rough()

def section(part,x):
    plane=cq.Face.makeFromWires(cq.Workplane('YZ',origin=(x,0,30)).rect(180,100).val())
    cut=part.val().intersect(plane)
    polygons=[]
    for face in cut.Faces():
        vertices,triangles=face.tessellate(.02,.1)
        vertices=np.array([[v.y,v.z] for v in vertices])
        for triangle in triangles:
            a,b,c=vertices[list(triangle)]
            ab,ac=b-a,c-a
            if abs(ab[0]*ac[1]-ab[1]*ac[0])>1e-8:
                polygons.append([a,b,c,(c+a)/2])
    if not polygons:
        raise ValueError('Empty selected CAD section: '+str(x))
    return np.array(polygons)

sections=[]
for x in (0,110,116,123.2,126,126.4,126.8,128,129,130,131):
    fixed=section(case['body'],x)
    moving=section(case['lid'],x)
    sections.append((fixed,moving))
    print('Section',x,len(fixed),len(moving),flush=True)
    if collide(fixed,moving):
        print('CLOSED SECTION COLLISION',x,flush=True)

def pose(cells,phi,theta):
    p,t=np.radians([phi,theta])
    r=np.array([[np.cos(p),np.sin(p)],[-np.sin(p),np.cos(p)]])
    target=np.array([AXIS_Y+LINK_SPACING*np.cos(t),AXIS_Z+LINK_SPACING*np.sin(t)])
    return (cells-np.array([LID_AXIS_Y,HEIGHT-AXIS_Z]))@r.T+target

def failure(phi,theta):
    for body,lid in sections:
        moved=pose(lid,phi,theta)
        if moved[:,:,1].min() < -1e-5 or collide(moved,body):
            return True
    return False

phis=list(range(0,181,3))
thetas=sorted(set(list(range(0,int(CLOSED_LINK_ANGLE)+1,3))+[CLOSED_LINK_ANGLE]))
legal=np.zeros((len(phis),len(thetas)),bool)
for i,phi in enumerate(phis):
    for j,theta in enumerate(thetas):
        legal[i,j]=not failure(phi,theta)
    if i%10==0:
        print('Grid lid angle',phi,'legal',int(legal[i].sum()),flush=True)
start=(0,len(thetas)-1);end=(len(phis)-1,0)
# Discrete clearance bias: avoid routes hugging colliding angle pairs. This is
# a grid search heuristic, not a physical clearance or actuation-effort model.
distance=np.full(legal.shape,999,dtype=int)
wave=deque()
for i,j in np.ndindex(legal.shape):
    if not legal[i,j]:
        distance[i,j]=0;wave.append((i,j))
while wave:
    i,j=wave.popleft()
    for u,v in ((i+1,j),(i-1,j),(i,j+1),(i,j-1)):
        if 0<=u<len(phis) and 0<=v<len(thetas) and distance[u,v]>distance[i,j]+1:
            distance[u,v]=distance[i,j]+1;wave.append((u,v))
prev={start:None} if legal[start] else {}
cost={start:0} if legal[start] else {}
queue=[(0,start)] if legal[start] else []
while queue:
    current_cost,(i,j)=heapq.heappop(queue)
    if current_cost!=cost[(i,j)]: continue
    if (i,j)==end: break
    for nxt in ((i+1,j),(i,j+1),(i,j-1),(i+1,j+1),(i+1,j-1)):
        u,v=nxt
        if not (0<=u<len(phis) and 0<=v<len(thetas)): continue
        if u==0 and thetas[v]<99: continue
        # Lift the latch grip above the rim before drawing the lid inward.
        if 0<phis[u]<=6 and thetas[v]<99-phis[u]: continue
        if 0<=u<len(phis) and 0<=v<len(thetas) and legal[nxt]:
            proposed=current_cost+1+4/max(1,int(distance[nxt]))**2
            if proposed>=cost.get(nxt,float('inf')): continue
            if any(failure(phis[i]+(phis[u]-phis[i])*f,thetas[j]+(thetas[v]-thetas[j])*f)
                   for f in np.linspace(0,1,7)[1:-1]):
                continue
            prev[nxt]=(i,j);cost[nxt]=proposed;heapq.heappush(queue,(proposed,nxt))
route=[]
if end in prev:
    cell=end
    while cell is not None:
        route.append(dict(lid_degrees=phis[cell[0]],link_degrees=thetas[cell[1]]))
        cell=prev[cell]
    route.reverse()
result=dict(scope='CAD tessellated sections only; native CAD route confirmation required',
            legal=int(legal.sum()),reachable=len(prev),route=route,
            max_phi=max((phis[i] for i,j in prev),default=None))
Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
