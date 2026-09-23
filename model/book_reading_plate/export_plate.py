"""Build, check and export final plate halves and four head-up printed screws."""
from pathlib import Path
from dataclasses import asdict,replace
import hashlib,json
import cadquery as cq
from components import P,halves,screw,posed,stations,solid,print_half,print_screw,box,female_tool,base
ROOT=Path(__file__).resolve().parent

def overlap(a,b): return solid(a).intersect(solid(b)).Volume()
def compound(items): return cq.Compound.makeCompound([solid(s) for s in items])

def build():
    a,b=halves(); bolt=screw()
    assert all(s.val().isValid() and len(s.solids().vals())==1 for s in [a,b,bolt])
    assert overlap(a,b)<1e-5
    bolts=[posed(bolt,x,y,z,lip) for x,y,z,lip in stations()]
    assert all(overlap(s,a)<1e-5 and overlap(s,b)<1e-5 for s in bolts)
    # Four explicit seating rings touch the female half without moving exterior faces.
    seats=[]
    for x,y,z,lip in stations():
        q=(x+10.8,P.split+P.lap_gap/2,z) if lip else (x+10.8,y,P.split+P.lap_gap/2)
        eps=.001; direction=(0,eps,0) if lip else (0,0,eps)
        assert a.val().isInside(tuple(q[i]-direction[i] for i in range(3)))
        assert b.val().isInside(tuple(q[i]+direction[i] for i in range(3)))
        seats.append({'contact_point_mm':q,'gap_mm':0})
    female=box(-14,14,-14,14,P.split+P.lap_gap/2,P.thickness).cut(female_tool())
    assert overlap(bolt.translate((0,0,-.5)),female)>.01
    helix=[]
    for lift in [0,.1,.3,.6,1.2,2.4,3.6,4.8,6]:
        moved=bolt.rotate((0,0,0),(0,0,1),-360*lift/P.thread_pitch).translate((0,0,-lift))
        v=overlap(moved,female);assert v<1e-5,(lift,v)
        helix.append({'withdrawal_mm':lift,'interference_mm3':v})
    # Lift diagonally to clear the raised seats, align X, then lower onto seats.
    for gap in [0,.02,.06,.12,.3,1,5]:
        assert overlap(a,b.translate((0,gap,gap)))<1e-5
    for dx in [0,1,5,20,70,100,240]:
        assert overlap(a,b.translate((dx,.3,.3)))<1e-5
    contacts={}
    for axis in [(0,1,0),(1,0,0),(0,0,1)]:
        origin=(0,100,10);end=tuple(origin[i]+axis[i] for i in range(3))
        for angle in [-1,1]:
            v=sum(overlap(a.rotate(origin,end,angle),s) for s in bolts)
            assert v>.01
            contacts[f'{axis}:{angle}']=v
    # Standard key enters the open socket; socket floor limits engagement to 2.6 mm.
    key=(cq.Workplane('XY',origin=(0,0,-12)).polygon(6,8/(3**.5/2))
         .extrude(12+P.end_recess+P.hex_depth-.01))
    assert overlap(key,bolt)<1e-5
    bb=bolt.val().BoundingBox()
    assert abs(bb.zmin-P.end_recess)<1e-5 and abs(P.thickness-bb.zmax-P.end_recess)<1e-5
    # One representative width/height change checks parameter derivation, not print fit.
    alternate=replace(P,width=360,inner_height=230)
    assert all(v.val().isValid() for v in halves(alternate,threaded=False))
    layouts={'plate_left':print_half(a,True),'plate_right':print_half(b,False),
             'screws':compound([print_screw().translate((i*26,0,0)) for i in range(4)])}
    report={'parameters':asdict(P),'seat_contacts':seats,'helical_removal':helix,
            'rotation_contacts_mm3':contacts,'screw_head_recess_mm':P.end_recess,
            'screw_tip_recess_mm':P.thickness-bb.zmax,'hex_key_af_mm':8,'layouts':{}}
    for name,shape in layouts.items():
        s=solid(shape);bb=s.BoundingBox();size=[bb.xlen,bb.ylen,bb.zlen]
        assert s.isValid() and all(v<=lim for v,lim in zip(size,[260,260,250]))
        for ext in ['step','stl']:
            cq.exporters.export(s,str(ROOT/f'{name}.{ext}'),**({'tolerance':.012,'angularTolerance':.07} if ext=='stl' else {}))
        report['layouts'][name]={'size_mm':size,'solids':len(s.Solids()),'volume_mm3':s.Volume()}
    assembled=compound([a,b]+bolts)
    cq.exporters.export(assembled,str(ROOT/'book_reading_plate_assembled.step'))
    report['assembled_volume_mm3']=assembled.Volume()
    report['source_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'components.py',Path(__file__)]}
    (ROOT/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['layouts'])
    return assembled
result=build()
