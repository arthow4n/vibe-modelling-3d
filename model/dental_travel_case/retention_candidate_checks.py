"""M2 exact-CAD operation/capture evidence; no holding-force prediction.

Run with execute.py. Geometry remains owned by m2_design. The output distinguishes
geometric obstruction, nominal sloping retaining land and guide-limited motion.
Prescribed leaf shapes remain kinematic envelopes, not structural solutions.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq
import m1_design as m1
import m2_design as m2
from m1_checks import clear, fit, tube_aperture, end_rounds

EPS = 1e-5  # inherited CAD Boolean overlap discrimination, mm3
ANGLE_RESOLUTION = .002  # degree bisection interval, not physical uncertainty


def volume(a,b):
    return a.intersect(b).Volume()


def retaining_land(d,upper,sign):
    tooth=m1.at_end(m2.hook(d),sign).val()
    angle=math.radians(d.retaining_angle_deg)
    hook_faces=[f for f in tooth.Faces() if f.geomType()=='PLANE'
                and abs(f.normalAt().z+math.cos(angle))<1e-6]
    receiver_faces=[f for f in upper.Faces() if f.geomType()=='PLANE'
                    and abs(f.normalAt().z-math.cos(angle))<1e-6
                    and f.Center().x*sign<0]
    records=[]
    for hface in hook_faces:
        for rface in receiver_faces:
            common=hface.intersect(rface.translate((0,0,d.axial_play)))
            if common.Area()>EPS:
                hn,rn=hface.normalAt(),rface.normalAt()
                bb=common.BoundingBox()
                records.append(dict(area_mm2=common.Area(),
                    radial_projected_width_mm=bb.xlen,
                    transverse_width_mm=bb.ylen,
                    hook_normal=list(hn.toTuple()),receiver_normal=list(rn.toTuple()),
                    receiver_normal_outward_component=-sign*rn.x,
                    axial_alignment_translation_mm=d.axial_play,
                    outward_seating_contact_direction=(-sign*rn.x>0 and rn.z>0)))
    return records


def pose(cap,d,lift,axis,angle):
    end=(1,0,d.seam) if axis=='x' else (0,1,d.seam)
    return cap.rotate((0,0,d.seam),end,angle).translate((0,0,lift))


def angular_freeplay(fixed,upper,d,lift,axis,sign):
    """First fixed-guide/seat interference about seam; hooks excluded on purpose.

    The local search assumes monotonically increasing obstruction up to 3deg.
    It is rigid clearance, not angular stiffness, equilibrium or a release path.
    """
    def obstruction(a):
        return volume(fixed,pose(upper,d,lift,axis,sign*a))
    lo,hi=0.,3.
    if obstruction(hi)<=EPS:
        return dict(angle_deg=None,reason='No guide contact within 3deg bracket')
    while hi-lo>ANGLE_RESOLUTION:
        mid=(lo+hi)/2
        if obstruction(mid)>EPS:
            hi=mid
        else:
            lo=mid
    at=pose(upper,d,lift,axis,sign*lo)
    return dict(angle_deg=lo,bracket_deg=[lo,hi],
        hook_interference_at_last_guide_clear_pose_mm3={str(s):volume(m1.at_end(m2.hook(d),s).val(),at) for s in (-1,1)})


def first_tooth_layers(d):
    """Targeted disconnected-print-island control; not a generic solid audit.

    The suspected failure is an undercut tooth beginning above air. Thin layer
    slabs test whether its earliest sections connect to the beam through gussets.
    A connected section still needs a viable slicer bridge across the tooth.
    """
    core=m1.at_end(m2.hook_core(d),1)
    unsupported=m1.tongue(d).cut(m1.at_end(m1.hook(d),1)).union(core).val()
    supported=m2.tongue(d).val()
    start=core.val().BoundingBox().zmin
    samples=[]
    for delta in (.02,.08,.14,.20,.26):
        z=start+delta
        slab=m1.box(0,0,z,d.width+8,d.beam_width+8,.002).val()
        counts={name:len(shape.intersect(slab).Solids())
                for name,shape in (('gussets_present',supported),('gussets_removed',unsupported))}
        samples.append(dict(z_mm=z,offset_above_first_tooth_mm=delta,section_components=counts))
    return dict(scope='Exact thin-layer connectivity. A single section is not proof of a printable bridge.',
        samples=samples,
        expected='All gusseted sections connect; at least one removed-gusset early layer has a detached tooth island.',
        status='PASS' if all(x['section_components']['gussets_present']==1 for x in samples)
            and any(x['section_components']['gussets_removed']>1 for x in samples) else 'FAIL',
        nominal_bridge_span_mm=d.hook_width)


def cap_first_shelf_layers(d,upper):
    """Print-direction connectivity of the inverted cap's sloping receiver shelf.

    Actual first shelf surfaces supply the start height. The complete ring is
    included, so separate tiny solids are a direct nominal floating-layer witness.
    This asks a specific suspected manufacturing failure, not generic topology.
    """
    cosine=math.cos(math.radians(d.retaining_angle_deg))
    floors=[f for f in upper.Faces() if f.geomType()=='PLANE'
            and abs(f.normalAt().z-cosine)<1e-6 and abs(f.Center().x)>d.width*.4]
    if not floors:
        raise ValueError('No actual sloping receiver floor found')
    start=max(f.BoundingBox().zmax for f in floors)
    samples=[]
    for delta in (.02,.08,.14,.20,.26,.32):
        z=start-delta  # cap prints inverted: descending assembly Z
        slab=m1.box(0,0,z,d.width+8,d.depth+4,.002).val()
        pieces=upper.intersect(slab).Solids()
        samples.append(dict(z_mm=z,print_depth_below_first_shelf_mm=delta,
            section_components=len(pieces),pieces=[dict(volume_mm3=p.Volume(),
                center_mm=list(p.Center().toTuple())) for p in pieces]))
    return dict(status='FAIL' if any(x['section_components']>1 for x in samples) else 'PASS',
        scope='Exact 0.002 mm-thick sections of complete cap in its inverted print direction; isolated shelf strips are unsupported nominal layer islands.',
        first_receiver_shelf_z_mm=start,samples=samples,
        expected='No detached section besides the continuous outer wall ring. More than one component demonstrates a floating shelf strip.',
        limitation='Connectivity alone is insufficient to qualify a bridge or actual deposition.')


def inspect():
    print("M2 exact CAD: building and checking contents",file=sys.stderr,flush=True)
    parts=m2.build()
    d=parts['dimensions']
    for name in ('body','cap'):
        assert parts[name].val().isValid(),name
        assert len(parts[name].solids().vals())==1,name+' disconnected'
    clear(parts['body'],parts['cap'],'Seated M2 has no interference')
    fit(parts)
    tube_aperture(parts)
    end_rounds(parts)
    upper,fixed=parts['cap'].val(),parts['fixed'].val()
    tests=[]
    offsets=((-.25,0),(0,0),(.25,0),(0,-.25),(0,.25))
    def record(intent,a,b,**inputs):
        v=volume(a,b)
        tests.append(dict(intent=intent,overlap_mm3=v,status='PASS' if v<=EPS else 'FAIL',**inputs))
    print("M2 exact CAD: deliberate squeeze and withdrawal",file=sys.stderr,flush=True)
    for displacement in (0,.5,1,1.5,2,d.release):
        for sign in (-1,1):
            leaf=m1.mirrored(m2.tongue(d,displacement),sign).val()
            for dz in (-.15,0,.15):
                for dx,dy in offsets:
                    record('Squeeze remains clear under axial/lateral deviations',leaf,
                        upper.translate((dx,dy,dz)),terminal_travel_mm=displacement,
                        catch=sign,dx_mm=dx,dy_mm=dy,dz_mm=dz)
            span=m1.box(0,0,(d.beam_root+2+d.beam_tip+1.6)/2,
                d.width+8,d.beam_width+8,d.beam_tip+1.6-d.beam_root-2).val()
            free=leaf.intersect(span)
            clear(cq.Workplane(obj=free),parts['fixed'],'Free leaf clears unchanged liner',gap=.1)
    leaves={s:m1.mirrored(m2.tongue(d,d.release),s).val() for s in (-1,1)}
    for lift in (0,.25,.65,1,2,4,8,12,20,30,40,60,90,106):
        for dx,dy in offsets:
            posed=upper.translate((dx,dy,lift))
            record('Long guide allows prescribed withdrawal',fixed,posed,lift_mm=lift,dx_mm=dx,dy_mm=dy)
            for sign,leaf in leaves.items():
                record('Deliberately released hook clears withdrawal',leaf,posed,
                       lift_mm=lift,dx_mm=dx,dy_mm=dy,catch=sign)
    print("M2 exact CAD: retaining faces and guide motion",file=sys.stderr,flush=True)
    lands={str(s):retaining_land(d,upper,s) for s in (-1,1)}
    guide=[]
    for lift in (0,d.axial_play/2,d.axial_play,.9):
        for axis in ('x','y'):
            for sign in (-1,1):
                guide.append(dict(lift_mm=lift,axis=axis,direction=sign,
                    **angular_freeplay(fixed,upper,d,lift,axis,sign)))
    controls=[]
    for name,delta in (('engaged',0.),('half_pressed',d.release/2),('released',d.release)):
        control=dict(name=name,terminal_travel_mm=delta,catch_overlap_mm3={})
        for sign in (-1,1):
            control['catch_overlap_mm3'][str(sign)]=volume(m1.at_end(m2.hook(d,delta),sign).val(),upper.translate((0,0,1)))
        controls.append(control)
    removed=volume(fixed,upper.translate((0,0,1)))
    layers=first_tooth_layers(d)
    cap_layers=cap_first_shelf_layers(d,upper)
    failures=[r for r in tests if r['status']=='FAIL']
    capture_ok=all(v and all(x['outward_seating_contact_direction'] for x in v) for v in lands.values())
    return dict(status='PASS' if not failures and capture_ok and removed<=EPS and layers['status']=='PASS' and cap_layers['status']=='PASS' else 'FAIL',
        scope='Exact CAD nominal and declared finite poses; no structural/contact-force or physical acceptance claim',
        source_sha256={name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
            for name,module in (('m1_design',m1),('m2_design',m2))},
        lap_mm=d.lap,axial_play_mm=d.axial_play,retaining_angle_deg=d.retaining_angle_deg,
        nominal_tooth_to_pocket_outer_clearance_mm=d.width/2-d.pocket_outer_skin-(d.beam_outer+d.hook_projection),
        unreinforced_pocket_skin_mm=d.pocket_outer_skin,
        reinforced_pocket_skin_mm=d.pocket_outer_skin+d.skin_reinforcement,
        boolean_overlap_epsilon_mm3=EPS,angle_resolution_deg=ANGLE_RESOLUTION,
        unchanged_individual_brush_and_tube_aperture=True,
        sleeve_interior_width_mm=d.sleeve_width-2*d.lap_wall,
        sleeve_interior_depth_mm=d.sleeve_depth-2*d.lap_wall,
        retaining_lands=lands,operation_tests=tests,operation_failures=failures,
        first_tooth_layer_control=layers,cap_first_shelf_layer_control=cap_layers,
        receiver_central_shelf_width_mm=2*d.gusset_relief_inner,
        nominal_transverse_gusset_relief_margin_mm=min(d.hook_width/2-d.gusset_relief_inner,d.gusset_relief_outer-(d.hook_width/2+d.gusset_width)),
        iteration_history=[
            dict(rejected_feature="Original M2 pocket outer skin .8 mm",
                 observation="At +/- .25 mm X, one zero-travel hook intersected the pocket skin by 1.1024719403 mm3 at each of Z offsets -.15, 0, +.15. Deliberate release was clear.",
                 correction="Pocket skin .5 mm plus external .8 mm reinforcement; nominal radial clearance .45 mm. Subsequent 234-pose study had no operation collisions."),
            dict(rejected_feature="Unsupported outward-descending 7 degree hook underside",
                 observation="Earliest tooth layers can be detached from the beam. The removed-gusset thin-layer control retains this mechanism.",
                 correction="Integral end gussets support a nominal 9 mm bridge; receiver side relief preserves a central shelf. Actual slice still required.")],
        operation_failure_interpretation='FAIL marks violation of the requested pure-clearance envelope. Zero-travel lateral-offset interference may require seated elastic leaf preload; it does not alone establish absent capture or product rejection. A deformable equilibrium is needed to resolve it.',
        rigid_guide_angular_freeplay=guide,hook_controls=controls,
        removed_hook_control_overlap_mm3=removed,
        liner_compatibility='NOT established; existing S16 is M1-specific',
        manufacturing_status=('REJECTED: exact inverted-cap sections show detached first receiver-shelf layers after side relief removes transverse anchors. Body gussets alone do not solve printable undercut capture.' if cap_layers['status']=='FAIL' else 'UNQUALIFIED pending actual slice and first-tooth bridge toolpath inspection. Integral gussets address disconnected first-layer geometry; thin-section connectivity alone does not establish bridge deposition.'),
        limitations=['Normal direction establishes outward-seating geometry only; it does not predict holding force.',
            'Hook contact may limit rocking before the fixed guide does; its interference is recorded separately.',
            'First guide contact is not a bearing stiffness result or a full cap/body equilibrium.',
            'Fixed-hook pose obstruction does not prove a force/energy barrier or continuous retention.',
            'Axial negative deviations apply to leaf-vs-cap clearances; the hard seat independently blocks negative whole-cap travel.',
            'Dimensional deviations are declared sensitivities, not measured print-error distributions.'])


if __name__=='__main__':
    path=Path(__file__).resolve().parent/'notes/retention/m2_geometry.json'
    if sys.argv[1:]==['--cap-layers']:
        result=json.loads(path.read_text())
        current={name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                 for name,module in (('m1_design',m1),('m2_design',m2))}
        if result['source_sha256']!=current:
            raise ValueError('Existing operation report is not associated with current geometry')
        witness=cap_first_shelf_layers(m2.D,m2.cap(m2.D).val())
        result['cap_first_shelf_layer_control']=witness
        if witness['status']=='FAIL':
            result['status']='FAIL'
            result['manufacturing_status']='REJECTED: exact inverted-cap sections show detached first receiver-shelf layers after side relief removes transverse anchors. Body gussets alone do not solve printable undercut capture.'
    elif not sys.argv[1:]:
        result=inspect()
    else:
        raise SystemExit('Usage: retention_candidate_checks.py [--cap-layers]')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],report=str(path),
        operation_failures=result['operation_failures'],retaining_lands=result['retaining_lands'],
        cap_first_shelf_layer_control=result.get('cap_first_shelf_layer_control'))))
