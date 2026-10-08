"""Product-local kinematic screen of V3's rear button; SI inside MuJoCo.

No dynamics, force, anatomical calibration or continuous collision proof.
Run via execute.py; output is a receipt, never an automatically reused result.
"""
from dataclasses import dataclass, asdict
from itertools import combinations
import argparse
import json
import math
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
import scipy
from scipy.optimize import least_squares
from execution.identity import digest
import v3_components as cad

ROOT = Path(__file__).resolve().parent
# Numerical/geometry screens, not ergonomic thresholds.
CONTACT_MM = .25
NORMAL_DEG = 10.
CLEARANCE_MM = .2
TOUCH_PENETRATION_MM = .05
JOINT_STEP_DEG = 2.
COUPLING = .65
STARTS = 6
SEED = 7301
MAX_NFEV = 180
OPTIMIZATION_BUFFER_MM = .1


@dataclass(frozen=True)
class Setup:
    angle_deg: float
    scale: float = 1.
    shoulder_mm: tuple = (80., 500., 330.)

    def __post_init__(self):
        if self.angle_deg not in cad.ANGLES:
            raise ValueError('Select a current V3 lock angle explicitly')
        if not math.isfinite(self.scale) or not .8 <= self.scale <= 1.2:
            raise ValueError('This local scale hypothesis is limited to 0.8–1.2')
        if len(self.shoulder_mm) != 3 or not np.isfinite(self.shoulder_mm).all():
            raise ValueError('Shoulder setup must be three finite mm coordinates')


def sources():
    return {str(p.relative_to(ROOT.parents[1])): digest(p) for p in (
        ROOT/'v3_components.py', ROOT/'human_interaction.py', ROOT.parents[1]/'uv.lock')}


def vec(values):
    return ' '.join(f'{v:.12g}' for v in values)


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
    """One fixed setup, one index contact, explicit collision pairs."""
    def __init__(self, setup, fixture=None):
        self.setup = setup
        self.boxes, self.surface_mm = fixture if fixture is not None else product_fixture(setup.angle_deg)
        root = ET.Element('mujoco', model='V3_assumed_arm_index')
        ET.SubElement(root,'compiler',angle='degree')
        option = ET.SubElement(root,'option',gravity='0 0 0')
        ET.SubElement(option,'flag',nativeccd='enable')
        default = ET.SubElement(root,'default')
        ET.SubElement(default,'geom',density='1000',contype='0',conaffinity='0')
        world = ET.SubElement(root,'worldbody')
        product = ET.SubElement(world,'body',name='product')
        for box in self.boxes:
            ET.SubElement(product,'geom',name=box['name'],type='box',
                pos=vec(np.array(box['centre_mm'])/1000),size=vec(np.array(box['half_mm'])/1000))
        # Desk as an explicit setup obstacle, separate from product CAD.
        ET.SubElement(world,'geom',name='desk',type='plane',size='1 1 .01')
        s = setup.scale
        def body(parent,name,pos):
            return ET.SubElement(parent,'body',name=name,pos=vec(np.array(pos)*s))
        def joint(parent,name,axis,limits):
            ET.SubElement(parent,'joint',name=name,type='hinge',axis=axis,range=vec(limits),limited='true')
        def capsule(parent,name,length,radius):
            ET.SubElement(parent,'geom',name=name,type='capsule',fromto=vec((0,0,0,0,-length*s,0)),size=str(radius*s))
        upper = ET.SubElement(world,'body',name='upper',pos=vec(np.array(setup.shoulder_mm)/1000))
        joint(upper,'shoulder_x','1 0 0',(-100,100))
        joint(upper,'shoulder_z','0 0 1',(-100,100))
        joint(upper,'shoulder_y','0 1 0',(-90,90))
        capsule(upper,'upper_arm',.28,.035)
        forearm = body(upper,'forearm',(0,-.28,0))
        joint(forearm,'elbow','1 0 0',(0,145))
        capsule(forearm,'forearm_proxy',.25,.028)
        palm = body(forearm,'palm',(0,-.25,0))
        joint(palm,'pronation','0 1 0',(-80,80))
        joint(palm,'wrist_flex','1 0 0',(-70,70))
        joint(palm,'wrist_deviation','0 0 1',(-25,25))
        ET.SubElement(palm,'geom',name='palm_proxy',type='box',pos=vec((0,-.04*s,0)),size=vec((.038*s,.04*s,.014*s)))
        # The other fingers are a fixed curled-hand envelope; thumb absent.
        ET.SubElement(palm,'geom',name='curled_fingers',type='box',pos=vec((.013*s,-.086*s,.012*s)),size=vec((.025*s,.022*s,.023*s)))
        proximal = body(palm,'proximal',(-.025,-.08,0))
        joint(proximal,'index_abduction','0 0 1',(-15,15))
        joint(proximal,'index_mcp','1 0 0',(-10,85))
        capsule(proximal,'index_proximal',.045,.009)
        middle = body(proximal,'middle',(0,-.045,0))
        joint(middle,'index_pip','1 0 0',(0,100))
        capsule(middle,'index_middle',.025,.008)
        distal = body(middle,'distal',(0,-.025,0))
        joint(distal,'index_dip','1 0 0',(0,70))
        # End the shaft before the pad; same-body overlap is intentional.
        capsule(distal,'index_distal',.010,.007)
        self.pad_radius = .007*s
        ET.SubElement(distal,'geom',name='pad',type='sphere',pos=vec((0,-.018*s,0)),size=str(self.pad_radius))
        ET.SubElement(distal,'site',name='tip',pos=vec((0,-.018*s,0)),size='.001')
        self.xml = ET.tostring(root,encoding='unicode')
        self.model = mujoco.MjModel.from_xml_string(self.xml)
        self.data = mujoco.MjData(self.model)
        self.names = [self.model.joint(j).name for j in range(self.model.njnt)]
        self.free = [j for j,n in enumerate(self.names) if n!='index_dip']
        self.bounds = self.model.jnt_range[self.free].T.copy()
        self.pad = self.model.geom('pad').id
        self.button = self.model.geom('button').id
        self.tip = self.model.site('tip').id
        self.human = [g for g in range(self.model.ngeom) if self.model.geom(g).name in (
            'upper_arm','forearm_proxy','palm_proxy','curled_fingers','index_proximal','index_middle','index_distal','pad')]
        obstacles = [self.model.geom(b['name']).id for b in self.boxes]+[self.model.geom('desk').id]
        self.product_pairs = [(h,p) for h in self.human for p in obstacles]
        # Explicit coverage independent of MuJoCo's parent/weld contact filtering.
        # Exclude composite same-body overlaps and neighbours sharing a joint.
        neighbouring = {frozenset(p) for p in (('upper','forearm'),('forearm','palm'),
            ('palm','proximal'),('proximal','middle'),('middle','distal'))}
        self.self_pairs = []
        for a,b in combinations(self.human,2):
            ba,bb = self.model.geom_bodyid[[a,b]]
            pair = frozenset((self.model.body(ba).name,self.model.body(bb).name))
            if ba!=bb and pair not in neighbouring:
                self.self_pairs.append((a,b))
        self.pairs = self.product_pairs+self.self_pairs
        self.required_mm = np.array([-TOUCH_PENETRATION_MM if (a,b)==(self.pad,self.button)
            else CLEARANCE_MM for a,b in self.pairs])
        self.state((self.bounds[0]+self.bounds[1])/2,0)

    def state(self,q,stroke_mm):
        q = np.asarray(q,dtype=float)
        if q.shape!=(len(self.free),) or not np.isfinite(q).all():
            raise ValueError('Wrong/nonfinite independent joint coordinates')
        if not math.isfinite(stroke_mm) or not 0 <= stroke_mm <= cad.RELEASE:
            raise ValueError('Stroke outside V3 travel')
        self.data.qpos[self.free]=q
        self.data.qpos[self.names.index('index_dip')]=COUPLING*q[self.free.index(self.names.index('index_pip'))]
        # Button translates; front slider uses the fixed swept Y reserve.
        for b in self.boxes:
            g = self.model.geom(b['name']).id
            self.model.geom_pos[g,1] = b['centre_mm'][1]/1000 - (stroke_mm/1000 if b['name']=='button' else 0)
        mujoco.mj_forward(self.model,self.data)

    def distances_mm(self):
        # Finite distmax clips distant pairs to 1 m; no clearance claim beyond it.
        return np.array([mujoco.mj_geomDistance(self.model,self.data,a,b,1.,None)*1000 for a,b in self.pairs])

    def target(self,offset_mm,stroke_mm):
        return self.surface_mm/1000 + np.array((0,self.pad_radius+(offset_mm-stroke_mm)/1000,0))

    def diagnostics(self,q,*,offset_mm=0.,stroke_mm=0.):
        self.state(q,stroke_mm)
        distances = self.distances_mm()
        margins = np.minimum(self.data.qpos-self.model.jnt_range[:,0],self.model.jnt_range[:,1]-self.data.qpos)
        error = np.linalg.norm(self.data.site_xpos[self.tip]-self.target(offset_mm,stroke_mm))*1000
        direction = -self.data.site_xmat[self.tip].reshape(3,3)[:,1]
        normal = math.degrees(math.acos(float(np.clip(direction@np.array((0,-1,0)),-1,1))))
        forbidden = [(self.model.geom(a).name,self.model.geom(b).name,float(d))
            for (a,b),d,limit in zip(self.pairs,distances,self.required_mm) if d<limit-1e-7]
        touch_index = self.pairs.index((self.pad,self.button))
        rear_patch_error = np.linalg.norm(self.data.site_xpos[self.tip]-self.target(0.,stroke_mm))*1000
        requested_contact_only = (distances[touch_index]>=CLEARANCE_MM or
                                  (rear_patch_error<=CONTACT_MM and normal<=NORMAL_DEG))
        accepted = (error<=CONTACT_MM and normal<=NORMAL_DEG and min(margins)>=-1e-9 and not forbidden and requested_contact_only)
        return dict(accepted=bool(accepted),requested_contact_only=bool(requested_contact_only),contact_error_mm=float(error),normal_error_deg=normal,
            pad_button_distance_mm=float(distances[touch_index]),
            minimum_forbidden_clearance_mm=float(np.min(np.delete(distances,touch_index))),
            minimum_joint_margin_deg=float(np.degrees(min(margins))),
            joints_deg={n:float(np.degrees(v)) for n,v in zip(self.names,self.data.qpos)},
            joint_margins_deg={n:float(np.degrees(v)) for n,v in zip(self.names,margins)},
            palm_mm=(self.data.xpos[self.model.body('palm').id]*1000).tolist(),
            elbow_mm=(self.data.xpos[self.model.body('forearm').id]*1000).tolist(),
            clearance_violations=[{'human':a,'other':b,'distance_mm':d} for a,b,d in forbidden],
            penetrations=[{'human':self.model.geom(a).name,'other':self.model.geom(b).name,'distance_mm':float(d)}
                for (a,b),d in zip(self.pairs,distances) if d < 0],
            minimum_product_clearance_mm=float(min(d for (a,b),d in zip(self.product_pairs,distances)
                if b!=self.model.geom('desk').id and (a,b)!=(self.pad,self.button))),
            minimum_desk_clearance_mm=float(min(d for (a,b),d in zip(self.product_pairs,distances)
                if b==self.model.geom('desk').id)),
            minimum_self_clearance_mm=float(min(distances[len(self.product_pairs):])))

    def solve(self,target_offset_mm,stroke_mm,initial):
        initial = np.clip(initial,self.bounds[0]+1e-7,self.bounds[1]-1e-7)
        def residual(q):
            self.state(q,stroke_mm)
            position = (self.data.site_xpos[self.tip]-self.target(target_offset_mm,stroke_mm))*1000
            direction = -self.data.site_xmat[self.tip].reshape(3,3)[:,1]
            optimization_limits = self.required_mm + OPTIMIZATION_BUFFER_MM
            optimization_limits[self.pairs.index((self.pad,self.button))] = -TOUCH_PENETRATION_MM
            deficits = np.minimum(0,self.distances_mm()-optimization_limits)
            return np.r_[position, 15*(direction-np.array((0,-1,0))), 5*deficits, .01*(q-initial)]
        r = least_squares(residual,initial,bounds=self.bounds,max_nfev=MAX_NFEV,
                          ftol=1e-8,xtol=1e-8,gtol=1e-8)
        return r.x, {'solver_terminated':bool(r.success),'nfev':r.nfev,
                     'diagnostics':self.diagnostics(r.x,offset_mm=target_offset_mm,stroke_mm=stroke_mm)}

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
            initial=rng.uniform(self.bounds[0],self.bounds[1])
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
            print(f'scale={self.setup.scale} start={i}: endpoint={end["diagnostics"]["accepted"]}',file=sys.stderr,flush=True)
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


def study():
    input_sources=sources()
    fixture=product_fixture(60.)
    runs=[Interaction(Setup(60.,scale=scale),fixture).discover() for scale in (.9,1.,1.1)]
    if sources()!=input_sources:
        raise RuntimeError('Inputs changed during study; receipt not published')
    return dict(schema_version=1,sources=input_sources,tools={'python':sys.version.split()[0],'mujoco':mujoco.__version__,'numpy':np.__version__,'scipy':scipy.__version__},
        search={'starts':STARTS,'seed':SEED,'max_nfev':MAX_NFEV},
        screens={'contact_mm':CONTACT_MM,'normal_deg':NORMAL_DEG,'clearance_mm':CLEARANCE_MM,
                 'touch_penetration_mm':TOUCH_PENETRATION_MM,'joint_step_deg':JOINT_STEP_DEG,'coupling':COUPLING,
                 'optimization_buffer_mm':OPTIMIZATION_BUFFER_MM},
        scope='V3 60-degree portrait phone; rear release only; fixed shoulder, assumed arm/palm/index; conservative CAD boxes; desk plane',
        limitations=['No thumb, skin, soft tissue or independently articulated other fingers',
            'Self pairs exclude same-body/composite and adjacent joint neighbours; not complete anatomical nonpenetration',
            'Uniform scale is a geometric hypothesis, not a population percentile or personalization',
            'Sampled nonlinear transitions only; no continuous-path proof or dynamics',
            'Button rigidly prescribed; fixed front-slider swept Y reserve is a proxy, not spring-deformed CAD',
            'No force, friction, fatigue, comfort, safety or physical validation; support hand and actual ring/cable excluded'],
        runs=runs)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Explicit receipt destination; otherwise JSON stdout only')
    args=parser.parse_args()
    report=study()
    encoded=json.dumps(report,indent=2,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(encoded)
        print(json.dumps({'output':str(args.output),'runs':[{k:r[k] for k in ('setup','status','endpoint_count','complete_count','distinct_endpoint_count')} for r in report['runs']]}))
    else:
        print(encoded,end='')
