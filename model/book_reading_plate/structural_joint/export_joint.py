from pathlib import Path
from dataclasses import replace,asdict
import hashlib,json,math
import cadquery as cq
from joint import P,halves,screw,driver,posed,box,female_tool
ROOT=Path(__file__).resolve().parent

def solid(s):return s.val() if isinstance(s,cq.Workplane) else s
def overlap(a,b):return solid(a).intersect(solid(b)).Volume()
def bed(s):
    b=solid(s).BoundingBox();return s.translate((-b.xmin,-b.ymin,-b.zmin))
def compound(items):return cq.Compound.makeCompound([solid(s) for s in items])
def build():
    a,b=halves(threaded=True);bolt=screw()
    assert all(s.val().isValid() and len(s.solids().vals())==1 for s in [a,b,bolt])
    assert overlap(a,b)<1e-5
    bolts=[posed(bolt,x,0,z,True) for x in [-P.hole_x,P.hole_x] for z in P.hole_z]
    bolts += [posed(bolt,x,P.back_hole_y,0) for x in [-P.hole_x,P.hole_x]]
    for s in bolts:
        assert overlap(s,a)<1e-5 and overlap(s,b)<1e-5
        bb=s.val().BoundingBox()
        assert bb.zmin>=-1e-6 and bb.ymin>=-1e-6
    # Direct translation without turning is obstructed by the threads.
    tool=female_tool();female=box(-14,14,-14,14,5,10).cut(tool)
    assert overlap(bolt.translate((0,0,-.5)),female)>.01
    helix=[]
    for lift in [0,.1,.3,.6,1.2,2.4,3.6,4.8,6]:
        moved=bolt.rotate((0,0,0),(0,0,1),-360*lift/P.thread_pitch).translate((0,0,-lift))
        v=overlap(moved,female); assert v<1e-5,(lift,v)
        helix.append({'withdrawal_mm':lift,'interference_mm3':v})
    # Coupons assemble laterally; no screw is present until the shoulders meet.
    for dx in [0,1,5,15,35,70,80]:
        assert overlap(a.translate((-dx,0,0)),b)<1e-5,(dx,overlap(a.translate((-dx,0,0)),b))
    # Bolts stand in for bearings after their declared clearances are consumed.
    contacts={}
    for axis in [(0,1,0),(1,0,0),(0,0,1)]:
        origin=(0,25,10);end=tuple(origin[i]+axis[i] for i in range(3))
        for angle in [-1,1]:
            moved=a.rotate(origin,end,angle)
            v=sum(overlap(moved,s) for s in bolts)
            assert v>.01,(axis,angle,v)
            contacts[f'{axis}:{angle}']=v
    ap=bed(a.rotate((0,0,0),(0,1,0),-90))
    bp=bed(b.rotate((0,0,0),(0,1,0),90)).translate((65,0,0))
    screws=[bed(bolt).translate((i*25,70,0)) for i in range(4)]
    layouts={'joint_test':compound([ap,bp]+screws),'hex_driver':bed(driver())}
    fits=[]
    fit_results={}
    for i,gap in enumerate([.12,.24]):
        p=replace(P,thread_clearance=gap)
        # Exactly the same female and shoulder surfaces, printed on an X end.
        rear=box(-14,14,-14,14,0,5).cut(cq.Workplane('XY',origin=(0,0,-1)).circle((p.shoulder_diameter+p.shoulder_clearance)/2).extrude(7))
        recess=cq.Workplane('XY',origin=(0,0,-1)).circle((p.head_diameter+.4)/2).extrude(1+p.head_recess+p.head_thickness)
        rear=rear.cut(recess)
        front=box(-14,14,-14,14,5,10).cut(female_tool(p))
        label=str(round(gap*100))
        mark=cq.Workplane('XY',origin=(0,11,9.6)).text(label,3,.6)
        front=front.cut(mark)
        for n,item in enumerate([rear,front]):
            assert item.val().isValid() and len(item.solids().vals())==1
            fits.append(bed(item.rotate((0,0,0),(0,1,0),90)).translate((i*42+n*14,0,0)))
        fits.append(bed(bolt).translate((i*42,40,0)))
        fit_results[label]={'clearance_radial_mm':gap,'seated_overlap_mm3':overlap(bolt,front)+overlap(bolt,rear)}
        assert fit_results[label]['seated_overlap_mm3']<1e-5
    layouts['thread_fit']=compound(fits)
    report={'parameters':asdict(P),'helical_removal':helix,'rotation_bearing_contacts_mm3':contacts,'fit_coupons':fit_results,'layouts':{}}
    for name,s in layouts.items():
        s=solid(s)
        assert s.isValid()
        bb=s.BoundingBox();size=[bb.xlen,bb.ylen,bb.zlen]
        assert all(x<=lim for x,lim in zip(size,[260,260,250]))
        for ext in ['step','stl']:
            cq.exporters.export(s,str(ROOT/f'{name}.{ext}'),**({'tolerance':.012,'angularTolerance':.07} if ext=='stl' else {}))
        report['layouts'][name]={'size_mm':size,'solids':len(s.Solids()),'volume_mm3':s.Volume()}
    cq.exporters.export(compound([a,b]+bolts),str(ROOT/'joint_test_assembled.step'))
    report['source_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'joint.py',Path(__file__)]}
    (ROOT/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['layouts'])
    return layouts['joint_test']
result=build()
