"""MyoSim MyoArm kinematic screen of V3 rear release; SI inside MuJoCo.

Imported anatomy is unchanged. No dynamics, physiological or continuous-path claim.
Run via execute.py; receipts require source/asset identity and independent replay.
"""
from dataclasses import dataclass, asdict
from itertools import combinations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import mujoco
import myo_sim
import numpy as np
import scipy
from scipy.optimize import least_squares
from execution.identity import digest
import v3_components as cad

ROOT = Path(__file__).resolve().parent
MODEL_NAME = 'myoarm_r'
CONTACT_MM = .25
NORMAL_DEG = 10.
CLEARANCE_MM = .2
TOUCH_PENETRATION_MM = .05
JOINT_STEP_DEG = 2.
STARTS = 6
SEED = 7301
MAX_NFEV = 180
OPTIMIZATION_BUFFER_MM = .1
SETUPS = {'nominal': (80.,500.,550.), 'near': (80.,450.,550.), 'far': (80.,550.,550.)}


@dataclass(frozen=True)
class Setup:
    angle_deg: float
    shoulder_mm: tuple = SETUPS['nominal']

    def __post_init__(self):
        if self.angle_deg not in cad.ANGLES:
            raise ValueError('Select a current V3 lock angle explicitly')
        if len(self.shoulder_mm)!=3 or not np.isfinite(self.shoulder_mm).all():
            raise ValueError('Shoulder setup must be three finite mm coordinates')


def anatomy_identity():
    """Hash packaged source + assets, not generated caches or installation paths.

    Includes the compose pipeline and meshes/XML; a wheel version alone cannot
    detect locally edited anatomy. Conservative whole-package scope is small.
    """
    root=Path(myo_sim.__file__).parent
    files={str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*'))
           if p.is_file() and p.suffix in ('.py','.xml','.stl','.obj','.msh','.png')}
    return dict(model=MODEL_NAME,version=myo_sim.__version__,file_count=len(files),
                package_sha256=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest())


def sources():
    return {str(p.relative_to(ROOT.parents[1])):digest(p) for p in (
        ROOT/'v3_components.py',ROOT/'human_interaction.py',ROOT.parents[1]/'uv.lock')}


def tools():
    return dict(python=sys.version.split()[0],mujoco=mujoco.__version__,
                numpy=np.__version__,scipy=scipy.__version__,myo_sim=myo_sim.__version__)


def envelope(shape, name):
    """A deliberate conservative envelope for a selected actual CAD portion.

    These bounds construct a collision approximation, not an export audit.
    """
    b = shape.val().BoundingBox()
    return {'name': name, 'centre_mm': [(b.xmin+b.xmax)/2, (b.ymin+b.ymax)/2, (b.zmin+b.zmax)/2],
            'half_mm': [b.xlen/2, b.ylen/2, b.zlen/2]}


def product_fixture(angle):
    """Partition current CAD to avoid one hull sealing the rear-button access.

    Every portion is conservatively boxed, including holes/rounded edges. The
    partitions cover all base/cradle/slider/pin CAD; phone is an assumed envelope.
    No persisted simulator geometry is a second product source of truth.
    """
    base = cad.base()
    boxes = [envelope(base.intersect(cad.box(-200,-200,-100,400,600,100+cad.BASE_HEIGHT)), 'floor')]
    for name, x, width in (('left_shoulder',-200,184),('hood',-16,32),('right_shoulder',16,184)):
        boxes.append(envelope(base.intersect(cad.box(x,-200,cad.BASE_HEIGHT,width,600,300)), name))
    cradle = cad.place_cradle(cad.cradle(),angle)
    for name, x, width in (('left_fork',-200,170),('rotor_bridge',-30,60),('right_fork',30,170)):
        boxes.append(envelope(cradle.intersect(cad.box(x,-200,-100,width,600,500)), name))
    slider = cad.slider()
    for name,y,depth in (('slider_front',-200,266),('button',66,334)):
        portion=envelope(slider.intersect(cad.box(-200,y,-100,400,depth,500)),name)
        if name=='slider_front':
            # Swept Y reserve rather than translating anchored roots as rigid.
            # Actual spring-deformed surfaces remain outside this kinematic model.
            portion['half_mm'][1]+=cad.RELEASE
        boxes.append(portion)
    boxes.append(envelope(cad.place_pin(cad.pin()),'pin'))
    boxes.append(envelope(cad.phone(angle),'phone_envelope'))
    button = next(b for b in boxes if b['name']=='button')
    surface = np.array(button['centre_mm'])
    surface[1] += button['half_mm'][1]
    return boxes, surface


class Interaction:
    """Imported arm + passive torso; polynomial equalities eliminated exactly."""
    def __init__(self,setup,fixture=None):
        self.setup=setup
        self.boxes,self.surface_mm=fixture if fixture is not None else product_fixture(setup.angle_deg)
        spec=myo_sim.load_spec(MODEL_NAME)
        # Remove upstream demonstration floor/slab; keep anatomical bodies/geoms.
        for geom in list(spec.worldbody.geoms):
            spec.delete(geom)
        # Kinematic-only: do not integrate dynamics or infer muscle forces.
        spec.option.gravity[:]=0
        spec.option.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_ACTUATION)
        spec.option.disableflags &= ~int(mujoco.mjtDisableBit.mjDSBL_NATIVECCD)
        reference=spec.compile()
        data=mujoco.MjData(reference)
        mujoco.mj_forward(reference,data)
        # Rotate the entire unchanged model +90deg around world Z, then translate
        # its neutral humerus origin to the declared shoulder reference. The
        # shoulder girdle subsequently moves it under imported equalities.
        rotation=np.array(((0,-1,0),(1,0,0),(0,0,1)))
        torso=spec.body('Full Body')
        torso.quat=(math.sqrt(.5),0,0,math.sqrt(.5))
        torso.pos=rotation@reference.body('Full Body').pos + np.array(setup.shoulder_mm)/1000 - rotation@data.xpos[reference.body('humerus_r').id]
        product=spec.worldbody.add_body(name='product')
        for box in self.boxes:
            product.add_geom(name=box['name'],type=mujoco.mjtGeom.mjGEOM_BOX,
                pos=np.array(box['centre_mm'])/1000,size=np.array(box['half_mm'])/1000,
                contype=0,conaffinity=0)
        spec.worldbody.add_geom(name='desk',type=mujoco.mjtGeom.mjGEOM_PLANE,
                                size=(1,1,.01),contype=0,conaffinity=0)
        self.model=spec.compile()
        self.data=mujoco.MjData(self.model)
        m=self.model
        if m.nq!=m.njnt or np.any(m.jnt_type!=mujoco.mjtJoint.mjJNT_HINGE):
            raise ValueError('This qualified solver requires scalar imported hinge coordinates')
        self.names=[m.joint(j).name for j in range(m.njnt)]
        self.couplings=[]
        for i in range(m.neq):
            if not m.eq_active0[i] or m.eq_type[i]!=mujoco.mjtEq.mjEQ_JOINT or m.eq_obj2id[i]<0:
                raise ValueError('Unsupported imported equality; qualify it before solving')
            self.couplings.append((int(m.eq_obj1id[i]),int(m.eq_obj2id[i]),m.eq_data[i,:5].copy()))
        dependent={a for a,b,c in self.couplings}
        if len(dependent)!=len(self.couplings) or any(b in dependent for a,b,c in self.couplings):
            raise ValueError('Coupled dependency topology needs explicit qualification')
        self.free=[j for j in range(m.njnt) if j not in dependent]
        self.bounds=m.jnt_range[self.free].T.copy()
        # Restrict masters to the intersection of ALL imported dependent ranges.
        # MuJoCo mj_forward alone does not project qpos onto equalities/limits.
        for a,b,coeff in self.couplings:
            if np.any(coeff[2:]!=0) or coeff[1]==0:
                raise ValueError('Non-affine imported coupling needs a qualified constrained solver')
            i=self.free.index(b)
            bounds=np.sort((m.jnt_range[a]-coeff[0])/coeff[1])
            self.bounds[0,i]=max(self.bounds[0,i],bounds[0])
            self.bounds[1,i]=min(self.bounds[1,i],bounds[1])
        if np.any(self.bounds[0]>=self.bounds[1]):
            raise ValueError('Imported coupling/ranges have no usable master interval')
        self.pad=m.geom('distph2_coll_2_r').id
        self.tip=m.site('IFtip_r').id
        self.button=m.geom('button').id
        # Collision proxies imported as contype=1/conaffinity=0. Visual bones and
        # muscle wrap geoms stay out of collision reasoning; they are not skin.
        self.human=[g for g in range(m.ngeom) if m.geom_contype[g] or m.geom_conaffinity[g]]
        obstacles=[m.geom(b['name']).id for b in self.boxes]+[m.geom('desk').id]
        self.product_pairs=[(h,p) for h in self.human for p in obstacles]
        self.imported_pairs=[(int(a),int(b)) for a,b in zip(m.pair_geom1,m.pair_geom2)]
        self.self_pairs=self.imported_pairs.copy()
        self.exclusions=[]
        # Keep composite overlaps (forearm's radius+ulna, palm's metacarpals),
        # proximal neighbours within each digit, and shoulder attachment out of
        # supplemental checks. Cross-digit phalanges + hand/forearm + hand/upper
        # arm are screened explicitly; no claim about excluded anatomy.
        def region(g):
            name=m.body(m.geom_bodyid[g]).name
            for digit,names in enumerate((('firstmc_r','proximal_thumb_r','distal_thumb_r'),
                ('secondmc_r','2proxph_r','midph2_r','distph2_r'),
                ('thirdmc_r','3proxph_r','midph3_r','distph3_r'),
                ('fourthmc_r','4proxph_r','midph4_r','distph4_r'),
                ('fifthmc_r','5proxph_r','midph5_r','distph5_r'))):
                if name in names:return ('digit',digit,names.index(name))
            if name in ('humerus_r','radius_r','ulna_r'):return ('arm',name)
            return ('torso',name)
        for a,b in combinations(self.human,2):
            if (a,b) in self.self_pairs or (b,a) in self.self_pairs:continue
            ra,rb=region(a),region(b)
            same=m.geom_bodyid[a]==m.geom_bodyid[b]
            digit_pair=ra[0]==rb[0]=='digit'
            screen=(digit_pair and ((ra[1]!=rb[1] and ra[2]>0 and rb[2]>0) or
                                     (ra[1]==rb[1] and abs(ra[2]-rb[2])>1)))
            # Metacarpals and forearm capsules overlap at the imported wrist
            # even in neutral anatomy; do not activate those composite pairs.
            screen |= ({ra[0],rb[0]}=={'digit','arm'} and
                       (ra[0]!='digit' or ra[2]>0) and (rb[0]!='digit' or rb[2]>0))
            # Audited proximal middle/ring skin envelopes overlap throughout
            # a 2401-state MCP grid; upstream masks deliberately do not check
            # them. Keep this representation limitation explicit, not smaller.
            web=frozenset((m.geom(a).name,m.geom(b).name))==frozenset(('proxph3_coll_r','proxph4_coll_r'))
            if screen and not same and not web:self.self_pairs.append((a,b))
            else:self.exclusions.append((a,b))
        self.pairs=self.product_pairs+self.self_pairs
        self.required_mm=np.array([-TOUCH_PENETRATION_MM if (a,b)==(self.pad,self.button)
            else CLEARANCE_MM for a,b in self.pairs])
        self.state(m.qpos0[self.free],0.)

    def state(self,q,stroke_mm):
        q=np.asarray(q,dtype=float)
        if q.shape!=(len(self.free),) or not np.isfinite(q).all():
            raise ValueError('Wrong/nonfinite independent joint coordinates')
        if not math.isfinite(stroke_mm) or not 0<=stroke_mm<=cad.RELEASE:
            raise ValueError('Stroke outside V3 travel')
        self.data.qpos[self.free]=q
        for a,b,coeff in self.couplings:
            self.data.qpos[a]=np.polynomial.polynomial.polyval(self.data.qpos[b],coeff)
        for box in self.boxes:
            self.model.geom_pos[self.model.geom(box['name']).id,1]=box['centre_mm'][1]/1000-(stroke_mm/1000 if box['name']=='button' else 0)
        mujoco.mj_forward(self.model,self.data)

    def contact_geometry(self):
        # Imported pad is an ellipsoid; declared patch is its +local-Z pole.
        # Preserve size/orientation, rather than adding an invented fingertip.
        direction=self.data.geom_xmat[self.pad].reshape(3,3)[:,2]
        point=self.data.geom_xpos[self.pad]+direction*self.model.geom_size[self.pad,2]
        return point,direction

    def target(self,offset_mm,stroke_mm):
        return self.surface_mm/1000+np.array((0,(offset_mm-stroke_mm)/1000,0))

    def distances_mm(self):
        return np.array([mujoco.mj_geomDistance(self.model,self.data,a,b,1.,None)*1000 for a,b in self.pairs])

    def diagnostics(self,q,*,offset_mm=0.,stroke_mm=0.):
        self.state(q,stroke_mm)
        distances=self.distances_mm()
        point,direction=self.contact_geometry()
        error=np.linalg.norm(point-self.target(offset_mm,stroke_mm))*1000
        normal=math.degrees(math.acos(float(np.clip(direction@np.array((0,-1,0)),-1,1))))
        margins=np.minimum(self.data.qpos-self.model.jnt_range[:,0],self.model.jnt_range[:,1]-self.data.qpos)
        forbidden=[dict(human=self.model.geom(a).name or f'geom#{a}',other=self.model.geom(b).name or f'geom#{b}',distance_mm=float(d))
            for (a,b),d,limit in zip(self.pairs,distances,self.required_mm) if d<limit-1e-7]
        touch=self.pairs.index((self.pad,self.button))
        patch_error=np.linalg.norm(point-self.target(0.,stroke_mm))*1000
        requested=distances[touch]>=CLEARANCE_MM or (patch_error<=CONTACT_MM and normal<=NORMAL_DEG)
        equality_error=max(abs(self.data.qpos[a]-np.polynomial.polynomial.polyval(self.data.qpos[b],c)) for a,b,c in self.couplings)
        accepted=error<=CONTACT_MM and normal<=NORMAL_DEG and min(margins)>=-1e-9 and equality_error<1e-10 and not forbidden and requested
        return dict(accepted=bool(accepted),requested_contact_only=bool(requested),contact_error_mm=float(error),normal_error_deg=normal,
            pad_button_distance_mm=float(distances[touch]),minimum_forbidden_clearance_mm=float(np.min(np.delete(distances,touch))),
            minimum_joint_margin_deg=float(np.degrees(min(margins))),equality_error_rad=float(equality_error),
            joints_deg=dict(zip(self.names,np.degrees(self.data.qpos).tolist())),
            joint_margins_deg=dict(zip(self.names,np.degrees(margins).tolist())),
            palm_mm=(self.data.xpos[self.model.body('lunate_r').id]*1000).tolist(),
            elbow_mm=(self.data.xpos[self.model.body('radius_r').id]*1000).tolist(),
            imported_tip_marker_mm=(self.data.site_xpos[self.tip]*1000).tolist(),contact_patch_mm=(point*1000).tolist(),
            clearance_violations=forbidden,
            penetrations=[dict(human=self.model.geom(a).name or f'geom#{a}',other=self.model.geom(b).name or f'geom#{b}',distance_mm=float(d))
                for (a,b),d in zip(self.pairs,distances) if d<0],
            minimum_product_clearance_mm=float(min(d for (a,b),d in zip(self.product_pairs,distances)
                if b!=self.model.geom('desk').id and (a,b)!=(self.pad,self.button))),
            minimum_desk_clearance_mm=float(min(d for (a,b),d in zip(self.product_pairs,distances) if b==self.model.geom('desk').id)),
            minimum_self_clearance_mm=float(min(distances[len(self.product_pairs):])))

    def solve(self,target_offset_mm,stroke_mm,initial):
        initial=np.clip(initial,self.bounds[0]+1e-7,self.bounds[1]-1e-7)
        def residual(q):
            self.state(q,stroke_mm)
            point,direction=self.contact_geometry()
            limits=self.required_mm+OPTIMIZATION_BUFFER_MM
            limits[self.pairs.index((self.pad,self.button))]=-TOUCH_PENETRATION_MM
            return np.r_[(point-self.target(target_offset_mm,stroke_mm))*1000,
                15*(direction-np.array((0,-1,0))),5*np.minimum(0,self.distances_mm()-limits),.01*(q-initial)]
        r=least_squares(residual,initial,bounds=self.bounds,max_nfev=MAX_NFEV,ftol=1e-8,xtol=1e-8,gtol=1e-8)
        return r.x,dict(solver_terminated=bool(r.success),nfev=r.nfev,
                        diagnostics=self.diagnostics(r.x,offset_mm=target_offset_mm,stroke_mm=stroke_mm))

    def audit(self):
        m=self.model
        def pair_names(pairs):return [[m.geom(a).name or f'geom#{a}',m.geom(b).name or f'geom#{b}'] for a,b in pairs]
        return dict(model=MODEL_NAME,nq=m.nq,independent_joints=[self.names[j] for j in self.free],
            joints=[dict(name=self.names[j],body=m.body(m.jnt_bodyid[j]).name,range_rad=m.jnt_range[j].tolist(),axis=m.jnt_axis[j].tolist()) for j in range(m.njnt)],
            equalities=[dict(name=m.equality(i).name,dependent=self.names[a],independent=self.names[b],polycoef=c.tolist()) for i,(a,b,c) in enumerate(self.couplings)],
            collision_geoms=[dict(name=m.geom(g).name or f'geom#{g}',body=m.body(m.geom_bodyid[g]).name,type=int(m.geom_type[g]),size_m=m.geom_size[g].tolist(),contype=int(m.geom_contype[g]),conaffinity=int(m.geom_conaffinity[g])) for g in self.human],
            imported_self_pairs=pair_names(self.imported_pairs),screened_self_pairs=pair_names(self.self_pairs),excluded_self_pairs=pair_names(self.exclusions),
            actuators=m.nu,tendons=m.ntendon,dynamics_used=False,
            transform='Whole model rotated +90deg world Z; translated neutral humerus origin to shoulder_mm; no anatomy scaling')

    def segment(self,a,b,*,stroke_a=0.,stroke_b=0.,contact=False):
        """Validate actual nonlinear FK between solved states at <=2° joint steps.

        Contact tracking is also checked at interior states during a held press.
        No requirement for target tracking during a free approach transition.
        """
        count = max(2,int(math.ceil(np.max(np.abs(np.degrees(b-a)))/JOINT_STEP_DEG))+1,
                    int(math.ceil(abs(stroke_b-stroke_a)/.5))+1)
        bad=[]
        minimum=1000.
        max_error=0.
        for i,t in enumerate(np.linspace(0,1,count)):
            q=(1-t)*a+t*b
            diag=self.diagnostics(q,stroke_mm=stroke_a+t*(stroke_b-stroke_a))
            minimum=min(minimum,diag['minimum_forbidden_clearance_mm'])
            max_error=max(max_error,diag['contact_error_mm'])
            if diag['clearance_violations'] or not diag['requested_contact_only'] or diag['minimum_joint_margin_deg'] < -1e-7 or (contact and not diag['accepted']):
                bad.append({'sample':i,'fraction':float(t),'diagnostics':diag})
        return dict(accepted=not bad,samples=count,joint_step_limit_deg=JOINT_STEP_DEG,
            stroke_step_limit_mm=.5,minimum_forbidden_clearance_mm=minimum,
            max_contact_error_mm=max_error if contact else None,first_invalid=bad[0] if bad else None)

    def discover(self):
        rng=np.random.default_rng(SEED)
        candidates=[]
        for i in range(STARTS):
            initial=self.model.qpos0[self.free] if i==0 else rng.uniform(self.bounds[0],self.bounds[1])
            q,end=self.solve(0.,0.,initial)
            record={'start':i,'endpoint':end,'q_rad':q.tolist(),'approach':None,'press':None,'withdrawal':None}
            if end['diagnostics']['accepted']:
                pre,pre_solve=self.solve(40.,0.,q)
                approach=self.segment(pre,q)
                approach['start_solve']=pre_solve
                approach['accepted'] &= pre_solve['diagnostics']['accepted']
                record['approach']=approach
                press_states=[q]
                press_steps=[]
                last=q
                previous_stroke=0.
                for stroke in np.linspace(0,cad.RELEASE,7)[1:]:
                    nxt,solved=self.solve(0.,float(stroke),last)
                    transition=self.segment(last,nxt,stroke_a=previous_stroke,stroke_b=float(stroke),contact=True)
                    press_steps.append({'stroke_mm':float(stroke),'solve':solved,'transition':transition})
                    press_states.append(nxt)
                    last=nxt
                    previous_stroke=float(stroke)
                record['press']={'accepted':all(x['solve']['diagnostics']['accepted'] and x['transition']['accepted'] for x in press_steps),
                    'steps':press_steps,'q_rad':[v.tolist() for v in press_states]}
                out,out_solve=self.solve(40.,cad.RELEASE,last)
                withdrawal=self.segment(last,out,stroke_a=cad.RELEASE,stroke_b=cad.RELEASE)
                withdrawal['end_solve']=out_solve
                withdrawal['accepted'] &= out_solve['diagnostics']['accepted']
                record['withdrawal']=withdrawal
                record['approach_q_rad']=pre.tolist()
                record['withdrawal_q_rad']=out.tolist()
            candidates.append(record)
            print(f'shoulder_mm={self.setup.shoulder_mm} start={i}: endpoint={end["diagnostics"]["accepted"]}',file=sys.stderr,flush=True)
        valid=[c for c in candidates if c['endpoint']['diagnostics']['accepted']]
        complete=[c for c in valid if all(c[k]['accepted'] for k in ('approach','press','withdrawal'))]
        # Descriptive clustering by elbow displacement OR max joint difference.
        # Not a physiological classification or uniqueness certificate.
        distinct=[]
        for c in valid:
            if all(np.linalg.norm(np.array(c['endpoint']['diagnostics']['elbow_mm'])-d['endpoint']['diagnostics']['elbow_mm'])>=30
                   or np.max(np.abs(np.degrees(np.array(c['q_rad'])-d['q_rad'])))>=20 for d in distinct):
                distinct.append(c)
        return dict(setup=asdict(self.setup),status='PASS' if complete else 'INCONCLUSIVE',
            meaning='Found a declared-model sampled interaction' if complete else 'No complete candidate found under this finite search; physical impossibility not established',
            endpoint_count=len(valid),complete_count=len(complete),distinct_endpoint_count=len(distinct),
            diversity_rule='greedy representatives separated by >=30 mm elbow OR >=20 deg max independent joint',
            distinct_starts=[c['start'] for c in distinct],candidates=candidates,
            collision_boxes=self.boxes,contact_surface_mm=self.surface_mm.tolist(),
            product_pairs=len(self.product_pairs),self_pairs=len(self.self_pairs))


def screen_settings():
    return dict(contact_mm=CONTACT_MM,normal_deg=NORMAL_DEG,clearance_mm=CLEARANCE_MM,
        touch_penetration_mm=TOUCH_PENETRATION_MM,joint_step_deg=JOINT_STEP_DEG,
        optimization_buffer_mm=OPTIMIZATION_BUFFER_MM)


def study():
    inputs=sources()
    anatomy=anatomy_identity()
    fixture=product_fixture(60.)
    runs=[Interaction(Setup(60.,shoulder),fixture).discover() for shoulder in SETUPS.values()]
    if sources()!=inputs or anatomy_identity()!=anatomy:
        raise RuntimeError('Inputs/assets changed during study; receipt not published')
    return dict(schema_version=2,sources=inputs,anatomy=anatomy,tools=tools(),
        search=dict(starts=STARTS,seed=SEED,max_nfev=MAX_NFEV),
        screens=screen_settings(),
        scope='V3 60-degree portrait phone; rear release; MyoArm right arm and passive torso; conservative CAD boxes; desk plane',
        anatomy_audit=Interaction(Setup(60.),fixture).audit(),
        limitations=['Imported skin proxies are approximate; meshes/wrap geoms are not collision skin',
            'Supplemental self pairs omit composite/adjacent/palm overlaps, audited middle/ring proximal web pair and hand/torso; incomplete self-nonpenetration coverage',
            'Shoulder/torso placement unmeasured; model not a user or population profile',
            'Sampled joint transitions only; no continuous collision proof or dynamics',
            'Button prescribed rigidly; front-slider swept reserve excludes actual spring deformation',
            'No force, friction, fatigue, comfort, safety or physical validation; support hand, ring/cable absent'],runs=runs)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Explicit receipt destination; otherwise JSON stdout only')
    args=parser.parse_args()
    report=study()
    encoded=json.dumps(report,indent=2,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(encoded)
        print(json.dumps(dict(output=str(args.output),runs=[{k:r[k] for k in ('setup','status','endpoint_count','complete_count','distinct_endpoint_count')} for r in report['runs']])))
    else:print(encoded,end='')
