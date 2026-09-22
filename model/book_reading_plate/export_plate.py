"""Build once, export print layouts and assembled inspection STEP, record checks.
Run with CadQuery MCP evaluate_file. Outputs stay beside the authoritative source.
"""
from pathlib import Path
from dataclasses import asdict, replace
import hashlib
import json
import cadquery as cq
from components import P, halves, key, coupon, print_half, print_key, assembled

def run():
    ROOT = Path(__file__).resolve().parent
    (ROOT/'notes').mkdir(exist_ok=True)
    left,right = halves()
    keys = [print_key(key()).translate((i*27,0,0)) for i in range(P.joint_count)]
    cl,cr,ck = coupon()
    clp,crp,ckp = print_half(cl,-1),print_half(cr,1),print_key(ck)
    clb = clp.val().BoundingBox()
    crp = crp.translate((clb.xlen+12,0,0))
    ckp = ckp.translate((0,clb.ylen+12,0))
    layouts = {
        'plate_left': print_half(left,-1),
        'plate_right': print_half(right,1),
        'locking_keys': cq.Compound.makeCompound([s.val() for s in keys]),
        'joint_test': cq.Compound.makeCompound([clp.val(),crp.val(),ckp.val()]),
    }

    def solid(s): return s.val() if isinstance(s,cq.Workplane) else s

    def overlap(a,b): return solid(a).intersect(solid(b)).Volume()

    def extent(s):
        b=solid(s).BoundingBox()
        return [b.xlen,b.ylen,b.zlen]

    report={'parameters':asdict(P),'print_layouts':{},'interfaces':{}}
    assert overlap(left,right)<1e-6
    for name,shape in layouts.items():
        s=solid(shape)
        assert s.isValid()
        dims=extent(s)
        assert all(a <= b+1e-5 for a,b in zip(dims,[260,260,250]))
        cq.exporters.export(s,str(ROOT/f'{name}.step'))
        cq.exporters.export(s,str(ROOT/f'{name}.stl'),tolerance=0.015,angularTolerance=0.08)
        report['print_layouts'][name]={'size_mm':dims,'solids':len(s.Solids()),'volume_mm3':s.Volume()}

    # All four complete tenons fit through their straight sockets on lateral insertion.
    # Constant section plus tip allowance makes endpoint and intermediate samples useful checks.
    report['interfaces']['panel_insertion_overlap_mm3']={}
    for dx in [-P.tenon_length,-P.tenon_length/2,-2,0]:
        v=overlap(left.translate((dx,0,0)),right)
        assert v<1e-5
        report['interfaces']['panel_insertion_overlap_mm3'][str(dx)]=v

    # Rear-inserted taper has a free approach, then defined bearing contact and interference.
    # Tiny virtual overdrive is only a contact check, not an elastic/force simulation.
    interface=[]
    for y in P.stations:
        k=key(y)
        assert overlap(k,left)<1e-5 and overlap(k,right)<1e-5
        free=[]
        for dz in [-12,-6,-2,0,0.3]:
            kl=k.translate((0,0,dz))
            a,b=overlap(kl,left),overlap(kl,right)
            assert max(a,b)<1e-5
            free.append({'advance_mm':dz,'male_overlap_mm3':a,'receiver_overlap_mm3':b})
        overdrive=overlap(k.translate((0,0,0.8)),left)
        assert overdrive>0.001
        pullout=overlap(left.translate((-0.5,0,0)),k)
        assert pullout>0.01
        interface.append({'station_y_mm':y,'free_approach':free,
            'overdrive_0_8_mm_contact_volume_mm3':overdrive,
            'male_pullout_0_5_mm_contact_volume_mm3':pullout})
    report['interfaces']['keys']=interface
    report['interfaces']['socket_clearance_per_side_mm']=P.socket_clearance
    report['interfaces']['receiver_skin_mm']=(P.wall-P.tenon_thickness)/2-P.socket_clearance
    report['interfaces']['nominal_key_contact_advance_mm']=P.key_seat_clearance/P.key_taper

    # An actual alternate build exercises the width/height/station dependencies.
    alt=replace(P,width=380,inner_height=240,inner_lip=35,tenon_width=44)
    a,b=halves(alt)
    assert a.val().isValid() and b.val().isValid() and overlap(a,b)<1e-5
    report['alternate_parameter_build']={'parameters':asdict(alt),'valid':True,'panel_overlap_mm3':overlap(a,b)}
    inspection=cq.Compound.makeCompound([left.val(),right.val()]+[key(y).val() for y in P.stations])
    cq.exporters.export(inspection,str(ROOT/'book_reading_plate_assembled.step'))
    report['source_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest()
        for f in [ROOT/'components.py',ROOT/'book_reading_plate.py',Path(__file__)]}
    (ROOT/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Four print layouts exported; insertion, contact, bounds and alternate build checks passed.')
    return layouts['joint_test']

result = run()
