"""Measure final CAD sections and thread stripping surfaces through MCP."""
from pathlib import Path
from dataclasses import asdict
import json,hashlib,math
import cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from components import P,halves,base,box,screw,female_tool
ROOT=Path(__file__).resolve().parent

def section(part,x):
    slab=part.intersect(box(x-.05,x+.05,-1,P.height+1,-1,P.lip_height+1)).val()
    pr=GProp_GProps();BRepGProp.VolumeProperties_s(slab.wrapped,pr)
    I=(pr.MatrixOfInertia().Value(2,2)-pr.Mass()*.1**2/12)/.1
    bb=slab.BoundingBox();cz=pr.CentreOfMass().Z()
    return {'x_mm':x,'area_mm2':pr.Mass()/.1,'Iy_mm4':I,'Sy_mm3':I/max(bb.zmax-cz,cz-bb.zmin),'centroid_z_mm':cz}

def measure():
    a,b=halves(threaded=False);data={}
    xs=[i*.5 for i in range(-int(2*P.overlap_half)+1,int(2*P.overlap_half))]
    for name,part in [('rear',a),('front',b)]:
        assert part.val().isValid() and len(part.solids().vals())==1
        sections=[section(part,x) for x in xs]
        data[name]={'minimum_section':min(sections,key=lambda t:t['Sy_mm3']),'minimum_Iy_mm4':min(t['Iy_mm4'] for t in sections),'root_section':sections[0],'sections':sections}
    bolt=screw();female=box(-14,14,-14,14,P.split+P.lap_gap/2,P.thickness).cut(female_tool())
    z0=P.thread_start+.2;z1=P.screw_tip-P.lead_length;engagement=z1-z0
    r=P.thread_root/2+P.thread_clearance
    estimates={}
    for dr in [.02,.01]:
        ring=cq.Workplane('XY',origin=(0,0,z0)).circle(r+dr/2).circle(r-dr/2).extrude(engagement)
        estimates[str(dr)]=bolt.intersect(ring).val().Volume()/dr
    assert abs(estimates['0.02']-estimates['0.01'])/estimates['0.01']<.01
    surfaces={'male':{'area_estimates_mm2':estimates,'screening_area_mm2':min(estimates.values())*.95}}
    r=P.thread_major/2;samples={}
    for n in [36,72]:
        count=sum(female.val().isInside((r*math.cos(2*math.pi*(i+.5)/n),r*math.sin(2*math.pi*(i+.5)/n),z0+engagement*(j+.5)/2)) for i in range(n) for j in range(2))
        samples[str(n)]=2*math.pi*r*engagement*count/(n*2)
    assert abs(samples['36']-samples['72'])/samples['72']<.03
    surfaces['female']={'area_quadrature_mm2':samples,'screening_area_mm2':min(samples.values())*.95}
    report={'parameters':asdict(P),'parts':data,'whole_L_section':section(base(),100),'thread_engagement_interval_mm':[z0,z1],'thread_stripping_surfaces':surfaces,
            'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'components.py',Path(__file__)]}}
    (ROOT/'notes/sections.json').write_text(json.dumps(report,indent=2)+'\n')
    print({name:d['minimum_section'] for name,d in data.items()});print(surfaces)
    return cq.Compound.makeCompound([a.val(),b.val()])
result=measure()
