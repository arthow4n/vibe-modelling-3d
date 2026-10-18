"""Exact M2B geometry and declared analytical operation screen; no holding rating."""
import hashlib
import json
from pathlib import Path
import sys
import cadquery as cq
import m1_design as m1
import m2b_design as design
from m1_checks import clear,fit,tube_aperture,end_rounds
from retention_geometry import seated_land

EPS=1e-5
ANGLE_RESOLUTION=.002


def volume(a,b):
    return a.intersect(b).Volume()


def tilted(cap,d,lift,axis,angle):
    end=(1,0,d.seam) if axis=='x' else (0,1,d.seam)
    return cap.rotate((0,0,d.seam),end,angle).translate((0,0,lift))


def guide_angle(fixed,cap,d,lift,axis,sign):
    lo,hi=0.,3.
    if volume(fixed,tilted(cap,d,lift,axis,sign*hi))<=EPS:
        return dict(angle_deg=None,reason='No contact within 3deg bracket')
    while hi-lo>ANGLE_RESOLUTION:
        mid=(lo+hi)/2
        if volume(fixed,tilted(cap,d,lift,axis,sign*mid))>EPS:
            hi=mid
        else:
            lo=mid
    posed=tilted(cap,d,lift,axis,sign*lo)
    return dict(angle_deg=lo,bracket_deg=[lo,hi],
        hook_interference_at_last_guide_clear_pose_mm3={str(s):volume(m1.at_end(design.hook(d),s).val(),posed) for s in (-1,1)})


def layer_connectivity(d,leaf,cap):
    samples=[]
    # Concrete regression against the rejected undercut's disconnected first
    # tooth/shelf layers. These are targeted thin sections, not topology audits.
    for part,start,direction in (('body_tooth',d.hook_bottom,1),
                                  ('cap_shelf',d.hook_bottom-d.axial_play,-1)):
        shape=leaf if part=='body_tooth' else cap
        for delta in (.02,.08,.14,.20,.26):
            z=start+direction*delta
            slab=m1.box(0,0,z,d.width+8,d.depth+4,.002).val()
            solids=shape.intersect(slab).Solids()
            samples.append(dict(part=part,z_mm=z,print_depth_mm=delta,
                section_components=len(solids),status='PASS' if len(solids)==1 else 'FAIL'))
    return dict(status='PASS' if all(x['status']=='PASS' for x in samples) else 'FAIL',
        scope='Exact 0.002mm layer slabs at the flat retaining features. Connectivity does not qualify overhang/bridge deposition.',
        samples=samples)


def mechanics(d):
    root=d.beam_root+1
    span=d.beam_tip-root
    contact=d.press_z-root
    second_moment=d.beam_width*d.beam_thickness**3/12
    values=[]
    for travel in (d.release,d.release+.3):
        pad=travel*2*contact/(3*span-contact)
        values.append(dict(terminal_travel_mm=travel,pad_travel_mm=pad,
            root_outer_fiber_strain=3*d.beam_thickness*pad/(2*contact**2),
            forces_N=[dict(effective_modulus_MPa=e,per_leaf_force_N=3*e*second_moment/contact**3*pad)
                      for e in (800,1200,2200)]))
    return dict(scope='Linear rectangular cantilever, fixed root and pad point load with unloaded overhang. No contact, printed material calibration, insertion or holding-force prediction.',
        root_z_mm=root,press_z_mm=d.press_z,tip_z_mm=d.beam_tip,
        root_to_press_mm=contact,flexible_span_mm=span,second_moment_mm4=second_moment,
        material_assumptions='Effective isotropic PETG stiffness bracket only; neither strength nor printed anisotropy is calibrated.',
        operation=values)


def baseline_guide_comparison():
    d=m1.D
    fixed,upper=m1.body_fixed(d).val(),m1.cap(d).val()
    candidate_d=design.D
    candidate_fixed,candidate_cap=design.body_fixed(candidate_d).val(),design.cap(candidate_d).val()
    return dict(scope='Authoritative full-size M1 and M2B rigid guide/seat contact. Both designs rotate about the seam center with zero cap-center translation; this is a prescribed seam-pivot bound, not the freely floating optimum rotation or angular stiffness.',
        samples=[dict(lift_mm=lift,axis=axis,direction=sign,
                    **guide_angle(fixed,upper,d,lift,axis,sign))
                 for lift in (.325,.65,.9) for axis in ('x','y') for sign in (-1,1)],
        m2b_same_pose_samples=[dict(lift_mm=lift,axis=axis,direction=sign,
                    **guide_angle(candidate_fixed,candidate_cap,candidate_d,lift,axis,sign))
                 for lift in (.325,.65,.9) for axis in ('x','y') for sign in (-1,1)])


def inspect():
    print('M2B: build and contents',file=sys.stderr,flush=True)
    parts=design.build()
    d=parts['dimensions']
    for name in ('body','cap'):
        assert parts[name].val().isValid(),name+' invalid'
        assert len(parts[name].solids().vals())==1,name+' disconnected'
    fit(parts)
    tube_aperture(parts)
    end_rounds(parts)
    fixed,upper=parts['fixed'].val(),parts['cap'].val()
    tests=[]
    def record(intent,a,b,**inputs):
        v=volume(a,b)
        tests.append(dict(intent=intent,overlap_mm3=v,status='PASS' if v<=EPS else 'FAIL',**inputs))
    record('Nominal seated complete parts clear',parts['body'].val(),upper)
    offsets=((-.25,0),(0,0),(.25,0),(0,-.25),(0,.25))
    print('M2B: squeeze and withdrawal',file=sys.stderr,flush=True)
    for delta in (0,.5,1,1.5,2,d.release):
        for sign in (-1,1):
            leaf=m1.mirrored(design.tongue(d,delta),sign).val()
            for dz in (-.15,0,.15):
                for dx,dy in offsets:
                    record('Seated return and squeeze clear',leaf,upper.translate((dx,dy,dz)),
                           catch=sign,terminal_travel_mm=delta,dx_mm=dx,dy_mm=dy,dz_mm=dz)
            lo,hi=d.beam_root+2,d.beam_tip+1.6
            span=m1.box(0,0,(lo+hi)/2,d.width+8,d.beam_width+8,hi-lo).val()
            clear(cq.Workplane(obj=leaf.intersect(span)),parts['fixed'],
                  'Raised control and free leaf clear guard/liner',gap=.1)
    leaves={s:m1.mirrored(design.tongue(d,d.release),s).val() for s in (-1,1)}
    for lift in (0,.25,.65,1,2,4,8,12,20,30,40,60,90,106):
        for dx,dy in offsets:
            posed=upper.translate((dx,dy,lift))
            record('Long guide allows withdrawal',fixed,posed,lift_mm=lift,dx_mm=dx,dy_mm=dy)
            for sign,leaf in leaves.items():
                record('Deliberately released leaf clears withdrawal',leaf,posed,
                       lift_mm=lift,catch=sign,dx_mm=dx,dy_mm=dy)
    print('M2B: capture, guide and print layers',file=sys.stderr,flush=True)
    lands={str(s):seated_land(d,upper,s) for s in (-1,1)}
    guide=[dict(lift_mm=lift,axis=axis,direction=sign,
                **guide_angle(fixed,upper,d,lift,axis,sign))
           for lift in (0,d.axial_play/2,d.axial_play)
           for axis in ('x','y') for sign in (-1,1)]
    controls=[]
    for label,delta in (('engaged',0),('half_pressed',d.release/2),('released',d.release)):
        controls.append(dict(name=label,terminal_travel_mm=delta,
            catch_overlap_mm3={str(s):volume(m1.at_end(design.hook(d,delta),s).val(),upper.translate((0,0,1))) for s in (-1,1)}))
    removed=volume(fixed,upper.translate((0,0,1)))
    layers=layer_connectivity(d,design.tongue(d).val(),upper)
    failures=[r for r in tests if r['status']=='FAIL']
    captured=all(lands.values())
    return dict(status='PASS' if not failures and captured and layers['status']=='PASS' and removed<=EPS else 'FAIL',
        scope='Finite exact-CAD operations, nominal flat land, guide contact and first-layer connectivity. Separate analytical release estimate. No holding-force or physical acceptance claim.',
        source_sha256={name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                       for name,module in (('m1_design',m1),('m2b_design',design))},
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        dimensions=dict(lap_mm=d.lap,beam_length_mm=d.beam_length,beam_thickness_mm=d.beam_thickness,
            press_z_mm=d.press_z,hook_width_mm=d.hook_width,axial_play_mm=d.axial_play,
            nominal_tooth_to_pocket_outer_clearance_mm=d.width/2-d.pocket_outer_skin-(d.beam_outer+d.hook_projection),
            reinforced_pocket_skin_mm=d.pocket_outer_skin+d.skin_reinforcement),
        boolean_overlap_epsilon_mm3=EPS,angle_resolution_deg=ANGLE_RESOLUTION,
        retaining_lands=lands,operation_tests=tests,operation_failures=failures,
        unchanged_individual_brush_and_tube_aperture_checked=True,
        rigid_guide_angular_freeplay=guide,hook_controls=controls,
        guide_pose_scope="Both designs rotate about seam center with zero cap-center translation. This is a prescribed seam-pivot bound, not freely floating optimum angle, stiffness or equilibrium.",
        baseline_m1_guide_comparison=baseline_guide_comparison(),
        removed_hook_control_overlap_mm3=removed,first_layer_connectivity=layers,
        analytical_release=mechanics(d),
        liner_compatibility='Not established; existing liner is M1-specific.',
        manufacturing_status='Unqualified pending actual slice and retaining-feature toolpath inspection.',
        limitations=['Guide-clear angular motion excludes hooks and is not equilibrium or stiffness; hook obstruction is reported separately.',
            'Offsets test X or Y separately, avoiding assertion that combined corner translations are guide-admissible.',
            'Negative cap Z offsets test leaf clearance only; the circumferential seat separately blocks actual negative whole-cap motion.',
            'Seated leaf recovery is a kinematic return envelope, not material recovery or a simulated snap closure.',
            'Actual holding requires deformable eccentric loading and receiver/full-shell contact evidence; planar overlap is insufficient.'])


if __name__=='__main__':
    path=Path(__file__).resolve().parent/'notes/retention/m2b_geometry.json'
    if sys.argv[1:]==['--baseline-guide']:
        result=json.loads(path.read_text())
        current={name:hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                 for name,module in (('m1_design',m1),('m2b_design',design))}
        if result['source_sha256']!=current:
            raise ValueError('Existing M2B operation evidence does not match current source')
        if result.get('producer_sha256')!=hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
            raise ValueError('Existing producer changed; review retained operation evidence before supplementing')
        result['baseline_m1_guide_comparison']=baseline_guide_comparison()
        result['guide_pose_scope']='Both designs rotate about seam center with zero cap-center translation. This is a prescribed seam-pivot bound, not freely floating optimum angle, stiffness or equilibrium.'
    elif not sys.argv[1:]:
        result=inspect()
    else:
        raise SystemExit('Usage: retention_m2b_checks.py [--baseline-guide]')
    path.parent.mkdir(parents=True,exist_ok=True)
    result['producer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],report=str(path),
        operation_failures=result['operation_failures'],retaining_lands=result['retaining_lands'],
        analytical_release=result['analytical_release'],first_layer_connectivity=result['first_layer_connectivity'],
        baseline_m1_guide_comparison=result.get('baseline_m1_guide_comparison'))))
