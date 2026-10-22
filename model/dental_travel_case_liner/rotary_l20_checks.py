"""Conservative shell fit and actual L20 material/air witnesses; no force claim."""
from pathlib import Path
import hashlib,json
import cadquery as cq
from assembly_geometry import PairRequirement,check_pair
import rotary_l20_design as d

ROOT=Path(__file__).resolve().parent
INPUTS=('rotary_l20_design.py','rotary_l20_checks.py',
    '../dental_travel_case/rotary_case_design.py',
    '../dental_travel_case/rotary_refinement_design.py',
    '../dental_travel_case/rotary_covered_design.py',
    '../dental_travel_case/rotary_conical_design.py',
    '../dental_travel_case/rotary_printed_fastener_design.py',
    '../dental_travel_case/rotary_r1_design.py','../dental_travel_case/m1_design.py')
FREE=PairRequirement('Liner envelope must clear the rigid box and other liner',max_overlap_mm3=.001)


def hashes():
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in INPUTS}


def free(a,b):
    r=check_pair(a,b,FREE);r.require_passed()
    return r.to_dict()


def position(part,p):
    if part=='body':return p.translate((0,0,d.BODY_BOTTOM))
    if part=='cap':return p.rotate((0,0,0),(1,0,0),180).translate((0,0,d.CAP_TOP))
    raise ValueError(part)


def main():
    identity=hashes();rigid=d.rigid();parts={part:d.cup(part) for part in ('body','cap')}
    envelopes={part:position(part,d.loft(d.outer_rows(part))) for part in parts}
    rows=[]
    # Filled outer envelopes conservatively cover every possible liner material
    # and avoid recutting thousands of irrelevant enclosed tie faces for fit.
    for name,envelope in envelopes.items():
        for component in ('body','cap','rotor','facecap','pivot_axle','pivot_nut'):
            rows.append(dict(liner=name,component=component,result=free(envelope,rigid[component])))
    rows.append(dict(liners='body/cap',result=free(envelopes['body'],envelopes['cap'])))
    for lift in (.4,2.,6.,15.,30.,80.):
        rows.append(dict(lift_mm=lift,rigid_cap=free(envelopes['body'],rigid['cap'].translate((0,0,lift))),
                         cap_liner=free(envelopes['body'],envelopes['cap'].translate((0,0,lift)))))
    assert check_pair(envelopes['body'].translate((1.,0,0)),rigid['body'],FREE).status=='failed'
    # Complete 1.6mm floor slab, rather than just the bottom outline, fits
    # through the sleeve's narrow mouth without any prescribed deformation.
    floor=d.loft(d.outer_rows('body')).intersect(d.block(100,80,d.FLOOR_TOTAL))
    mouth=cq.Workplane(obj=cq.Solid.extrudeLinear(
        d.rounded_wire(67.2,44.2,2.,0.),[],cq.Vector(0,0,d.FLOOR_TOTAL+.1)))
    floor_missing=floor.cut(mouth).val().Volume();assert floor_missing<1e-5,floor_missing
    probes=[];solids={name:p.val().Solids() for name,p in parts.items()}
    def probe(part,point,expected,meaning):
        actual=any(s.isInside(cq.Vector(*point),1e-6) for s in solids[part])
        assert actual==expected,(part,point,meaning,actual)
        probes.append(dict(part=part,xyz_mm=point,material=actual,meaning=meaning))
    for part in parts:
        for zone in d.wall_zones(part):
            for axis in ('x','y'):
                for sign in (-1,1):
                    pattern=d.wall_spec(part,zone,axis,sign)
                    a=(pattern['along'][1]+pattern['along'][2])/2
                    z=pattern['vertical'][1]
                    depth=pattern['depth']
                    def point(along,normal,height):
                        return (along,normal,height) if axis=='y' else (normal,along,height)
                    for inset,material,meaning in ((.4,True,'outer 0.8mm skin'),
                        (1.,False,'0.4mm upright air gap'),(1.6,True,'inner 0.8mm skin')):
                        probe(part,point(a,sign*(depth/2-inset),z),material,meaning)
                    probe(part,point(pattern['along'][1],pattern['radial'],z),True,'0.8mm discrete tie')
                    probe(part,point(pattern['along'][1],pattern['radial'],
                        (z+pattern['vertical'][2])/2),False,'ties remain separated vertically')
        grid=d.floor_spec(part)
        x=(grid['x'][1]+grid['x'][2])/2;y=(grid['y'][1]+grid['y'][2])/2
        for z,expected,label in ((.2,True,'floor backing'),(.8,False,'floor air'),(1.4,True,'floor contact skin')):
            probe(part,(x,y,z),expected,label)
        probe(part,(grid['x'][1],grid['y'][1],.8),True,'floor post')
    installed={name:position(name,p) for name,p in parts.items()}
    contact=installed['cap'].intersect(rigid['cap'])
    contact_volume=contact.val().Volume();assert contact_volume>.01
    # Only the four declared retention pads are allowed to enter the cap wall.
    outside=contact.cut(position('cap',d.cap_pads())).val().Volume()
    assert outside<1e-5,outside
    pad_centres=[]
    w,h,_=d.profile_at('cap',8.)
    allowed=[]
    for axis,depth in (('x',w),('y',h)):
        for sign in (-1,1):
            radial=sign*(depth/2+d.ALLOWANCE+(d.PAD_INTERFERENCE+.001)/2)
            shape=(d.block(d.PAD_INTERFERENCE+.001,4.2,4.2,x=radial,z=5.9) if axis=='x'
                else d.block(4.2,d.PAD_INTERFERENCE+.001,4.2,y=radial,z=5.9))
            allowed.append(shape.val());pad_centres.append((axis,sign))
    extra=contact.cut(position('cap',cq.Workplane(obj=cq.Compound.makeCompound(allowed)))).val().Volume()
    assert extra<1e-5,extra
    brush=cq.Workplane('XY',origin=(0,0,d.BODY_BOTTOM+d.FLOOR_TOTAL)).circle(15.).extrude(255.)
    tube=d.block(55.,40.,160.,z=5.)
    gauges=[]
    for name,gauge in (('brush_30x255',brush),('paste_55x40x160_stored_individually',tube)):
        for part,liner in installed.items():gauges.append(dict(gauge=name,liner=part,result=free(gauge,liner)))
    assert hashes()==identity
    out=dict(source_sha256=identity,fit=rows,profile_probes=probes,individual_storage_gauges=gauges,
        floor_mouth_missing_mm3=floor_missing,
        cap_retention=dict(pads=pad_centres,contact_mm3=contact_volume,
            overlap_outside_pads_mm3=outside,overlap_beyond_0p101_mm_mm3=extra,
            nominal_interference_mm=d.PAD_INTERFERENCE,
            limit='Intentional local TPU compression; actual retention and installation force unmeasured'),
        dimensions=dict(body_height_mm=d.height('body'),cap_height_mm=d.height('cap'),
            throat_mm=[67.2-2*d.ALLOWANCE-2*d.WALL,44.2-2*d.ALLOWANCE-2*d.WALL],
            lower_cavity_mm=[71.8-2*d.ALLOWANCE-2*d.WALL,48.8-2*d.ALLOWANCE-2*d.WALL],
            clear_length_mm=d.CAP_TOP-d.FLOOR_TOTAL-d.BODY_BOTTOM-d.FLOOR_TOTAL,
            installation_clearance_per_side_mm=d.ALLOWANCE,liner_rim_gap_mm=d.RIM_GAP),
        limits='Two preformed cups. Floor passes sleeve rigidly; wider walls require unmeasured elastic compression. Individual stored gauges do not establish simultaneous brush/paste packing or toothpaste insertion through the 39.6mm throat. Tall-wall durability, printed gap separation, retention and quietness remain physical.')
    target=ROOT/'notes/rotary_l20/cad.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(fit_poses=len(rows),profile_probes=len(probes),dimensions=out['dimensions'])))


if __name__=='__main__':main()
