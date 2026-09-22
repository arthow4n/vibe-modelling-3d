"""Build once, export print layouts and assembled inspection STEP, record checks.
Run with CadQuery MCP evaluate_file. Outputs stay beside the authoritative source.
"""
from pathlib import Path
from dataclasses import asdict, replace
import hashlib
import json
import cadquery as cq
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from components import P, halves, key, coupon, print_half, print_key, assembled, receiver_clips

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

    # Two integral receiver catches block reverse key travel independently of friction.
    # Positive taper contact at the locked advance is intentional elastic preload.
    interface=[]
    for y in P.stations:
        k=key(y)
        clips=receiver_clips(y)
        released=receiver_clips(y,released=True)
        seated=k.translate((0,0,P.key_lock_advance))
        assert overlap(seated,right)<1e-5
        assert max(overlap(seated,c) for c in clips)<1e-5
        preload=overlap(seated,left)
        assert preload>0.001
        withdrawal=[]
        # Check extraction, including side shifts larger than the nominal side clearance.
        for dx,dy in [(0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)]:
            moved=k.translate((dx,dy,P.key_lock_advance-0.5))
            contact=[overlap(moved,c) for c in clips]
            assert min(contact)>0.01
            withdrawal.append({'offset_xy_mm':[dx,dy],'catch_contact_mm3':contact})
        release=[]
        for dz in [P.key_lock_advance,0.3,0,-1,-3,-6,-10,-14]:
            moved=k.translate((0,0,dz))
            contact=[overlap(moved,c) for c in released]
            assert max(contact)<1e-5
            release.append({'key_advance_mm':dz,'released_catch_contact_mm3':contact})
        # The ramp deliberately interferes during insertion while the hooks are at rest.
        snap_contact=sum(overlap(k.translate((0,0,-2)),c) for c in clips)
        assert snap_contact>0.1
        # Recover minimum axial slack by bisection on the actual shapes.
        low,high=0.0,0.5
        for _ in range(18):
            mid=(low+high)/2
            if sum(overlap(k.translate((0,0,P.key_lock_advance-mid)),c) for c in clips)>1e-7:
                high=mid
            else: low=mid
        interface.append({'station_y_mm':y,'locked_key_advance_mm':P.key_lock_advance,
            'taper_preload_interference_mm3':preload,
            'first_reverse_contact_mm':high,'withdrawal_tests':withdrawal,
            'spread_catches_release_sweep':release,'insertion_ramp_contact_mm3':snap_contact})
    report['interfaces'].update({'keys':interface,
        'socket_clearance_per_side_mm':P.socket_clearance,
        'receiver_skin_mm':(P.wall-P.tenon_thickness)/2-P.socket_clearance,
        'nominal_taper_contact_advance_mm':P.key_seat_clearance/P.key_taper,
        'catch_nominal_overlap_y_mm':P.latch_overlap,
        'catch_flat_overlap_after_head_chamfer_mm':P.latch_overlap-0.6,
        'release_spread_each_side_mm':P.latch_overlap+0.25})
    # Small-deflection screening, not material certification or measured actuation force.
    length=P.latch_length-6  # conservative loaded length: root transition + hook contact offset
    delta=P.latch_overlap+0.25
    strain=3*P.latch_thickness*delta/(2*length**2)
    inertia=P.latch_depth*P.latch_thickness**3/12
    assert strain<0.01  # provisional 1% design screen, requires PETG print validation
    report['latch_screen']={'effective_length_mm':length,'deflection_mm':delta,
        'root_strain_estimate':strain,'provisional_strain_screen':0.01,
        'assumed_effective_modulus_MPa':[800,1800],
        'predicted_lateral_force_per_arm_N':[3*E*inertia*delta/length**3 for E in (800,1800)],
        'limits':'Ideal cantilevers; ignores local contact, fillets, layer defects, wear and creep.'}

    # Flat-envelope checks: every retained key/catch remains inside the wall.
    for y in P.stations:
        for shape in receiver_clips(y)+[key(y).translate((0,0,P.key_lock_advance))]:
            box=shape.val().BoundingBox()
            assert box.zmin>=-1e-5 and box.zmax<=P.wall+1e-5
        # The flange stops on the recess floor before its tip protrudes at the front.
        stop_advance=P.head_pocket_depth-(-5+P.latch_recess_shift+P.key_head_thickness)
        assert key(y).translate((0,0,stop_advance)).val().BoundingBox().zmax<=P.wall+1e-5
    report['flat_surfaces']={'catch_and_key_z_range_limit_mm':[0,P.wall],
        'head_depth_below_rear_at_lock_mm':-5+P.latch_recess_shift+P.key_lock_advance,
        'key_tip_below_front_at_lock_mm':1-P.key_lock_advance,
        'mechanical_stop_advance_mm':stop_advance,
        'catch_release_side_clearance_mm':0.35,'catch_floor_gap_mm':P.latch_pocket_depth-6}
    # Screening now uses real 1 mm tenon sections including the recessed lock reliefs.
    # It is a sampled solid-section estimate, not a printed strength rating.
    sections=[]
    for x in [0.5,10,17,20,24,28,31,34]:
        slab=left.intersect(cq.Workplane('XY').box(1,P.height+2,P.wall+2)
                            .translate((x,P.height/2,P.wall/2))).val()
        props=GProp_GProps()
        BRepGProp.VolumeProperties_s(slab.wrapped,props)
        area=props.Mass()  # one millimetre slab width
        inertia=props.MatrixOfInertia().Value(2,2)-area/12
        box=slab.BoundingBox()
        z=props.CentreOfMass().Z()
        modulus=inertia/max(box.zmax-z,z-box.zmin)
        moment=40.5*(P.width/2-x)/2
        sections.append({'x_mm':x,'section_modulus_approx_mm3':modulus,
                         'nominal_stress_at_40_5_N_MPa':moment/modulus})
    report['tenon_section_screen']=sections

    # An actual alternate build exercises the width/height/station dependencies.
    alt=replace(P,width=380,inner_height=240,inner_lip=35,tenon_width=44)
    a,b=halves(alt)
    assert a.val().isValid() and b.val().isValid() and overlap(a,b)<1e-5
    report['alternate_parameter_build']={'parameters':asdict(alt),'valid':True,'panel_overlap_mm3':overlap(a,b)}
    inspection=cq.Compound.makeCompound([left.val(),right.val()]+[key(y).translate((0,0,P.key_lock_advance)).val() for y in P.stations])
    cq.exporters.export(inspection,str(ROOT/'book_reading_plate_assembled.step'))
    report['source_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest()
        for f in [ROOT/'components.py',ROOT/'book_reading_plate.py',Path(__file__)]}
    (ROOT/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Four print layouts exported; panel insertion, snap retention/release, bounds and alternate build checks passed.')
    return layouts['joint_test']

result = run()
