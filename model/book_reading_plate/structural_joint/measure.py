"""Actual solid cross-sections and thread stripping surfaces; run through MCP."""
from pathlib import Path
from dataclasses import replace,asdict
import json,hashlib,math
import cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from joint import halves,P,box,screw,female_tool
root=Path(__file__).resolve().parent
out={}
for label,p in [('full_section',replace(P,sample_height=260,back_hole_y=220)),('coupon',P)]:
    a,b=halves(p,threaded=False)
    data={}
    for name,part in [('rear',a),('front',b)]:
        assert part.val().isValid() and len(part.solids().vals())==1
        sections=[]
        xs=sorted(set([i*.5 for i in range(-int(2*p.overlap_half)+1,int(2*p.overlap_half))]+[-p.hole_x,p.hole_x]))
        for x in xs:
            s=part.intersect(box(x-.05,x+.05,-1,p.sample_height+1,-1,p.lip_height+1)).val()
            pr=GProp_GProps();BRepGProp.VolumeProperties_s(s.wrapped,pr)
            I=(pr.MatrixOfInertia().Value(2,2)-pr.Mass()*.1**2/12)/.1
            bb=s.BoundingBox();cz=pr.CentreOfMass().Z();S=I/max(bb.zmax-cz,cz-bb.zmin)
            sections.append({'x_mm':x,'area_mm2':pr.Mass()/.1,'Iy_mm4':I,'Sy_mm3':S,'centroid_z_mm':cz})
        data[name]={'minimum_section':min(sections,key=lambda t:t['Sy_mm3']),'minimum_Iy_mm4':min(s['Iy_mm4'] for s in sections),'sections':sections,'volume_mm3':part.val().Volume()}
    assert a.val().intersect(b.val()).Volume()<1e-5
    out[label]={'parameters':asdict(p),'parts':data}
# Restrict to the interval of complete engagement; excludes lead and runout.
bolt=screw();female=box(-14,14,-14,14,5,10).cut(female_tool())
surfaces={}
r=P.thread_root/2+P.thread_clearance
estimates={}
for dr in [.02,.01]:
    ring=cq.Workplane('XY',origin=(0,0,5.3)).circle(r+dr/2).circle(r-dr/2).extrude(3.7)
    estimates[str(dr)]=bolt.intersect(ring).val().Volume()/dr
assert abs(estimates['0.02']-estimates['0.01'])/estimates['0.01']<.01
surfaces['male']={'radius_mm':r,'area_estimates_mm2':estimates,'screening_area_mm2':min(estimates.values())*.95}
# Surface quadrature avoids an OCC thin-ring boolean failure on the female helix.
# Classify actual solid points on the cylindrical stripping surface; refine grid.
r=P.thread_major/2
samples={}
for n in [36,72]:
    nz=2
    count=sum(female.val().isInside((r*math.cos(2*math.pi*(i+.5)/n),r*math.sin(2*math.pi*(i+.5)/n),5.3+3.7*(j+.5)/nz)) for i in range(n) for j in range(nz))
    samples[str(n)]=2*math.pi*r*3.7*count/(n*nz)
assert min(samples.values())>0
assert abs(samples['36']-samples['72'])/samples['72']<.03
surfaces['female']={'radius_mm':r,'area_quadrature_mm2':samples,'screening_area_mm2':min(samples.values())*.95}
out['thread_stripping_surfaces']=surfaces
out['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'joint.py',Path(__file__)]}
(root/'notes/sections.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:{n:v['minimum_section'] for n,v in out[k]['parts'].items()} for k in ['full_section','coupon']})
print(surfaces)
a,b=halves();result=cq.Compound.makeCompound([a.val(),b.translate((8,8,0)).val()])
