"""Evaluate with CadQuery MCP: export three layouts and verify the two-piece joint."""
from pathlib import Path
from dataclasses import asdict, replace
import hashlib
import json
import cadquery as cq
from components import P, halves, latch, coupon, print_half, exact_bounds


def run():
    root=Path(__file__).resolve().parent
    left,right=halves()
    retracted,_=halves(retracted=True)
    cl,cr=coupon()
    clp,crp=print_half(cl,-1),print_half(cr,1)
    crp=crp.translate((clp.val().BoundingBox().xlen+12,0,0))
    layouts={'plate_left':print_half(left,-1),'plate_right':print_half(right,1),
             'joint_test':cq.Compound.makeCompound([clp.val(),crp.val()])}

    def shape(s): return s.val() if isinstance(s,cq.Workplane) else s
    def volume(a,b): return shape(a).intersect(shape(b)).Volume()
    def size(s):
        b=exact_bounds(shape(s))
        return [b[i+3]-b[i] for i in range(3)]

    assert volume(left,right)<1e-5
    assert len(left.solids().vals())==len(right.solids().vals())==1
    report={'parameters':asdict(P),'print_layouts':{},'motion':{}}
    for name,item in layouts.items():
        s=shape(item)
        assert s.isValid()
        assert all(a<=b+1e-5 for a,b in zip(size(s),[260,260,250]))
        cq.exporters.export(s,str(root/f'{name}.step'))
        cq.exporters.export(s,str(root/f'{name}.stl'),tolerance=0.015,angularTolerance=0.08)
        report['print_layouts'][name]={'size_mm':size(s),'solids':len(s.Solids()),'volume_mm3':s.Volume()}

    # The spring nose intentionally meets the channel wall during insertion.
    # With the nose retracted, all sampled translation poses must clear.
    travel=P.height-P.rail_start
    poses=sorted(set([0,0.2,0.5,1,2,5,10,20,40,80,120,180,travel,travel+2]))
    sweep=[]
    for dy in poses:
        v=volume(retracted.translate((0,dy,0)),right)
        assert v<1e-5,(dy,v)
        sweep.append({'Y_offset_mm':dy,'interference_mm3':v})
    report['motion']['retracted_slide']=sweep
    report['motion']['unretracted_insertion_contact_mm3']=volume(left.translate((0,10,0)),right)
    assert report['motion']['unretracted_insertion_contact_mm3']>0.1
    blocked={}
    for name,offset in [('reverse_slide',(0,0.5,0)),('past_end_stop',(0,-0.2,0)),
                        ('pull_apart',(-0.5,0,0)),('lift_front',(0,0,0.5)),('lift_rear',(0,0,-0.5))]:
        v=volume(left.translate(offset),right)
        assert v>0.01,(name,v)
        blocked[name]={'offset_mm':offset,'interference_mm3':v}
    report['motion']['blocked_locked_motions']=blocked
    lo,hi=0.0,0.5
    for _ in range(18):
        mid=(lo+hi)/2
        if volume(left.translate((0,mid,0)),right)>1e-7: hi=mid
        else: lo=mid
    report['motion']['first_reverse_contact_mm']=hi
    report['motion']['release_travel_Z_mm']=P.latch_release
    report['motion']['limits']='Sampled rigid clearances; retracted leaf is displaced, not elastically simulated.'

    # The hook and flexure remain inside the broad face planes in both poses.
    for retracted_pose in [False,True]:
        b=latch(retracted=retracted_pose).val().BoundingBox()
        assert b.zmin>=-1e-5 and b.zmax<=P.wall+1e-5
    report['flat_faces']={'connector_Z_limit_mm':[0,P.wall],
                          'release_button_recess_mm':P.latch_tip_z,'loose_connector_count':0}
    length=28.0  # conservative length from root transition to hook force point
    strain=3*P.latch_thickness*P.latch_release/(2*length**2)
    inertia=P.latch_width*P.latch_thickness**3/12
    assert strain<0.01
    report['flexure_screen']={'effective_length_mm':length,'root_strain':strain,
        'assumed_effective_modulus_MPa':[800,1800],
        'lateral_force_N':[3*E*inertia*P.latch_release/length**3 for E in (800,1800)],
        'limits':'Assumed modulus and 1% screening ceiling; actual PETG snap action, wear and strength untested.'}
    # Reverse sliding loads the leaf across its wider dimension. Screen a 20 N
    # withdrawal demand separately from the much lighter release direction.
    retention_inertia=P.latch_thickness*P.latch_width**3/12
    retention_length=P.rail_depth-P.latch_root_x
    retention_deflection=20*retention_length**3/(3*1200*retention_inertia)
    report['flexure_screen']['retention_load_assumption_N']=20
    report['flexure_screen']['retention_modulus_assumption_MPa']=1200
    report['flexure_screen']['retention_effective_length_mm']=retention_length
    report['flexure_screen']['retention_deflection_mm']=retention_deflection
    report['flexure_screen']['retention_root_strain']=3*P.latch_width*retention_deflection/(2*retention_length**2)
    assert report['flexure_screen']['retention_root_strain']<0.01
    effective_length=P.rail_end-P.rail_start-(P.latch_width+2)
    section_modulus=effective_length*P.rail_neck**2/6
    report['load_screen']={'provisional_book_kg':P.design_book_kg,
        'total_central_load_assumption_N':40.5,'root_section_modulus_mm3':section_modulus,
        'nominal_root_stress_MPa':(40.5*P.width/4)/section_modulus,
        'limits':'Solid-section bending estimate only; no print strength rating or safety factor.'}
    alt=replace(P,width=380,inner_height=240,inner_lip=35)
    a,b=halves(alt)
    assert a.val().isValid() and b.val().isValid() and volume(a,b)<1e-5
    report['alternate_build']={'parameters':asdict(alt),'valid':True}
    assembly=cq.Compound.makeCompound([left.val(),right.val()])
    cq.exporters.export(assembly,str(root/'book_reading_plate_assembled.step'))
    report['source_sha256']={name:hashlib.sha256((root/name).read_bytes()).hexdigest()
                            for name in ['components.py','book_reading_plate.py','export_plate.py']}
    (root/'notes/geometry_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Three layouts exported; sliding, end stop, reverse lock, flat faces and alternate build passed.')
    return layouts['joint_test']

result=run()
