"""Bimanual MyoSim grip placement: kinematic contact, never grip force/comfort.

Use execute.py. Production CAD stays unchanged; collision envelopes derive from
its dimensions and the selected 0.7 x 20 mm conceptual band. SI in MuJoCo.
"""
from dataclasses import dataclass, asdict
from itertools import combinations
from pathlib import Path
import hashlib
import json
import math
import sys
import importlib.metadata
import mujoco
import myo_sim
import numpy as np
import scipy
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from execution.identity import digest
from short_lap_thin import build_three_line
from grip_skin_contacts import outward_pad_sign, palmar_capsule_contact

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/grip_human'
DEPTH=.7
BAND_WIDTH=20.
SLAB=.5
CONTACT_MM=.30
NORMAL_DEG=15.
PAD_PATCH_DEG=45.
CLEARANCE_MM=.2
PENETRATION_MM=.05
OPT_BUFFER=.12
JOINT_STEP_DEG=2.
TRAVEL_STEP_MM=.5
SEED=8417
STARTS=4
MAX_NFEV=220
CANDIDATES={'near':(40.,-15.),'balanced':(50.,-30.),'separated':(65.,-50.)}

@dataclass(frozen=True)
class Setup:
    candidate: str
    tilt_deg: float
    forward_mm: float
    seam_height_mm: float
    def __post_init__(self):
        if self.candidate not in CANDIDATES:raise ValueError(self.candidate)
        if self.tilt_deg not in (0.,-25.):raise ValueError('Declared upright/diagonal poses only')
        if not np.isfinite((self.forward_mm,self.seam_height_mm)).all():raise ValueError('Nonfinite setup')


def sources():
    names=('grip_human_study.py','grip_skin_contacts.py','short_lap_thin.py','short_lap_design.py','m1_design.py',
           'closure_research_design.py','short_lap_refinement.py','../../uv.lock')
    return {n:digest(ROOT/n) for n in names}


def anatomy_identity():
    root=Path(myo_sim.__file__).parent
    files={str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*'))
        if p.is_file() and p.suffix in ('.py','.xml','.stl','.obj','.msh','.png')}
    return dict(models=['myoarms','myohands'],version=myo_sim.__version__,files=len(files),
        package_sha256=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest())


def depth_at(z,center):
    a=center-BAND_WIDTH/2
    u=(z-a)/6 if z<a+6 else (a+BAND_WIDTH-z)/6
    if z<a or z>a+BAND_WIDTH:return 0.,0.
    if a+6<=z<=a+14:return DEPTH,0.
    u=float(np.clip(u,0,1));s=u**3*(10-15*u+6*u*u)
    ds=30*u*u*(1-u)**2/6*(1 if z<a+6 else -1)
    return DEPTH*s,DEPTH*ds


def fixture(d,centers):
    """Conservative solid exterior slabs; rounded corners and notch voids filled.

    Half-mm axial band partitions bound the monotone profile from the outside.
    Filling the interior is intentional: skin cannot pass through the shell.
    Guide sleeve and pad reserve remain separate body/cap obstructions.
    """
    boxes=[]
    def rounded(part,a,b,width,depth,radius,inset):
        w=width/2-inset;h=depth/2-inset;r=radius-inset
        for hx,hy in ((w-r,h),(w,h-r)):
            boxes.append(dict(name=f'{part}_{len(boxes)}',part=part,shape='box',
                center_mm=[0.,0.,(a+b)/2],half_mm=[hx,hy,(b-a)/2]))
        for sx in (-1,1):
            for sy in (-1,1):
                boxes.append(dict(name=f'{part}_{len(boxes)}',part=part,shape='cylinder',
                    center_mm=[sx*(w-r),sy*(h-r),(a+b)/2],half_mm=[r,(b-a)/2,0.]))
    for part,lo,hi,center in (('body',0.,d.seam,d.seam+centers[1]),
                              ('cap',d.seam,d.length,d.seam+centers[0])):
        edges=sorted(set([lo,hi,center-10,center-4,center+4,center+10]+
                         np.arange(center-10,center+10+SLAB/2,SLAB).tolist()))
        for a,b in zip(edges,edges[1:]):
            inset=min(depth_at(a,center)[0],depth_at(b,center)[0])
            rounded(part,a,b,d.width,d.depth,d.corner,inset)
    rounded('body',d.seam,d.seam+d.lap,d.sleeve_width,d.sleeve_depth,d.sleeve_corner,0.)
    for sign in (-1,1):
        boxes.append(dict(name=f'cap_backing_{sign}',part='cap',
            shape='box',
            center_mm=[sign*(d.width/2+.65/2),0,d.seam+(d.lap+9)/2],
            half_mm=[.65/2,19/2,(d.lap+9)/2]))
    return boxes


class GripScene:
    def __init__(self,setup,dimensions,*,local_hands=False):
        self.local_hands=local_hands
        self.setup=setup;self.d=dimensions
        self.centers=CANDIDATES[setup.candidate]
        self.rotation=Rotation.from_euler('y',setup.tilt_deg,degrees=True).as_matrix()
        self.origin=np.array((0.,-setup.forward_mm,setup.seam_height_mm))/1000
        self.boxes=fixture(dimensions,self.centers)
        spec=myo_sim.load_spec('myohands' if local_hands else 'myoarms')
        for geom in list(spec.worldbody.geoms):spec.delete(geom)
        spec.option.gravity[:]=0
        spec.option.disableflags|=int(mujoco.mjtDisableBit.mjDSBL_ACTUATION)
        spec.option.disableflags&=~int(mujoco.mjtDisableBit.mjDSBL_NATIVECCD)
        quat=Rotation.from_matrix(self.rotation).as_quat(scalar_first=True)
        for part in ('body','cap'):
            body=spec.worldbody.add_body(name='case_'+part,pos=self.origin,quat=quat)
            for box in self.boxes:
                if box['part']==part:
                    body.add_geom(name=box['name'],type=mujoco.mjtGeom.mjGEOM_BOX if box['shape']=='box' else mujoco.mjtGeom.mjGEOM_CYLINDER,
                        pos=(np.array(box['center_mm'])-[0,0,dimensions.seam])/1000,
                        size=np.array(box['half_mm'])/1000,contype=0,conaffinity=0)
        self.model=spec.compile();m=self.model;self.data=mujoco.MjData(m)
        mujoco.mj_forward(m,self.data)
        self.patch_selection={}
        self.palmar_contacts={}
        for side in ('r','l'):
            for prefix in ('distph2','distal_thumb'):
                name=prefix+'_coll_2_'+side
                self.patch_selection[name]=outward_pad_sign(m,self.data,name,prefix+'_coll_'+side)
            for digit in ('thumb','index'):
                self.palmar_contacts[side,digit]=palmar_capsule_contact(m,self.data,digit=digit,side=side)
        self.placements=[]
        if local_hands:
            for side in ('r','l'):
                root=m.body('clavicle_'+side).id;parent=m.body_parentid[root]
                wrist=self.data.xpos[m.body('lunate_'+side).id].copy()
                long=self.data.xpos[m.body('2proxph_'+side).id]-wrist
                selected=self.palmar_contacts[side,'index']
                normal=self.data.geom_xmat[m.geom(selected['geom']).id].reshape(3,3)@np.array(selected['local_normal'])
                long-=normal*(long@normal);long/=np.linalg.norm(long)
                frame=np.column_stack((long,np.cross(normal,long),normal))
                target_long=np.array((1.,0,0)) if side=='r' else np.array((-1.,0,0))
                target_normal=np.array((0.,1.,0))
                target_frame=np.column_stack((target_long,np.cross(target_normal,target_long),target_normal))
                self.placements.append(dict(side=side,root=root,parent=parent,
                    parent_R=self.data.xmat[parent].reshape(3,3).copy(),parent_p=self.data.xpos[parent].copy(),
                    delta=self.data.xpos[root].copy()-wrist,root_R=self.data.xmat[root].reshape(3,3).copy(),
                    grasp_delta=self.data.site_xpos[m.site('S_grasp_'+side).id].copy()-wrist,
                    initial_rotation=Rotation.from_matrix(self.rotation@target_frame@frame.T).as_rotvec()))
        if m.nq!=m.njnt or not np.all(m.jnt_type==mujoco.mjtJoint.mjJNT_HINGE):
            raise ValueError('Only independent scalar hinge formulation qualified')
        self.names=[m.joint(i).name for i in range(m.njnt)]
        self.couplings=[]
        for i in range(m.neq):
            if not m.eq_active0[i] or m.eq_type[i]!=mujoco.mjtEq.mjEQ_JOINT or m.eq_obj2id[i]<0:
                raise ValueError('Unqualified equality topology')
            self.couplings.append((int(m.eq_obj1id[i]),int(m.eq_obj2id[i]),m.eq_data[i,:5].copy()))
        dependent={a for a,b,c in self.couplings}
        if len(dependent)!=len(self.couplings) or any(b in dependent for a,b,c in self.couplings):
            raise ValueError('Dependent joint topology needs qualification')
        self.free=[j for j in range(m.njnt) if j not in dependent]
        if local_hands:
            # Global hand placement already supplies these rigid motions. Keep
            # imported wrists neutral rather than optimize duplicate motions.
            self.free=[j for j in self.free if not self.names[j].startswith(('pro_sup_','deviation_','flexion_'))]
        self.bounds=m.jnt_range[self.free].T.copy()
        for a,b,c in self.couplings:
            if np.any(c[2:]!=0) or not c[1]:raise ValueError('Only affine imported equalities qualified')
            i=self.free.index(b);limits=np.sort((m.jnt_range[a]-c[0])/c[1])
            self.bounds[0,i]=max(self.bounds[0,i],limits[0]);self.bounds[1,i]=min(self.bounds[1,i],limits[1])
        if np.any(self.bounds[0]>=self.bounds[1]):raise ValueError('Empty coupled interval')
        self.human=[g for g in range(m.ngeom) if m.geom_contype[g] or m.geom_conaffinity[g]]
        if local_hands:
            self.human=[g for g in self.human if m.body(m.geom_bodyid[g]).name.endswith(('_r','_l'))
                        and not m.body(m.geom_bodyid[g]).name.startswith(('humerus','radius','ulna'))]
        self.products=[m.geom(b['name']).id for b in self.boxes]
        self.box_by_id={m.geom(b['name']).id:b for b in self.boxes}
        self.contacts=[]
        for side,part,center in (('r','cap',self.centers[0]),('l','body',self.centers[1])):
            for digit,face in (('thumb',-1),('index',1)):
                selected=self.palmar_contacts[side,digit]
                self.contacts.append(dict(side=side,part=part,center=dimensions.seam+center,
                    digit=digit,face=face,geom=m.geom(selected['geom']).id,
                    local_normal=selected['local_normal']))
        self.contact_by_id={c['geom']:c for c in self.contacts}
        pairs=[];required=[];self.exclusions=[]
        for a in self.human:
            for b in self.products:
                pairs.append((a,b))
                c=self.contact_by_id.get(a)
                name=m.body(m.geom_bodyid[a]).name
                resting=(name.endswith('_r') and self.box_by_id[b]['part']=='cap') or (name.endswith('_l') and self.box_by_id[b]['part']=='body')
                resting &= not name.startswith(('humerus','radius','ulna'))
                required.append(-PENETRATION_MM if resting else CLEARANCE_MM)
        self.product_pair_count=len(pairs)
        self.imported_pairs=[(int(a),int(b)) for a,b in zip(m.pair_geom1,m.pair_geom2)
                             if a in self.human and b in self.human]
        def region(g):
            name=m.body(m.geom_bodyid[g]).name
            for side in ('r','l'):
                for digit,segments in enumerate((('firstmc','proximal_thumb','distal_thumb'),
                    ('secondmc','2proxph','midph2','distph2'),('thirdmc','3proxph','midph3','distph3'),
                    ('fourthmc','4proxph','midph4','distph4'),('fifthmc','5proxph','midph5','distph5'))):
                    if name in tuple(s+'_'+side for s in segments):return side,'digit',digit,tuple(s+'_'+side for s in segments).index(name)
                if name in tuple(s+'_'+side for s in ('humerus','radius','ulna')):return side,'arm',0,0
            return None,'torso',0,0
        for a,b in combinations(self.human,2):
            ra,rb=region(a),region(b)
            imported=(a,b) in self.imported_pairs or (b,a) in self.imported_pairs
            cross=ra[0] is not None and rb[0] is not None and ra[0]!=rb[0]
            digits=ra[1]==rb[1]=='digit'
            screen=imported or cross or (digits and ((ra[2]!=rb[2] and ra[3]>0 and rb[3]>0) or (ra[2]==rb[2] and abs(ra[3]-rb[3])>1)))
            screen|=set((ra[1],rb[1]))=={'digit','arm'} and (ra[1]!='digit' or ra[3]>0) and (rb[1]!='digit' or rb[3]>0)
            screen|=set((ra[1],rb[1]))=={'digit','torso'}
            web=any(frozenset((m.geom(a).name,m.geom(b).name))==frozenset(('proxph3_coll_'+side,'proxph4_coll_'+side)) for side in ('r','l'))
            if screen and m.geom_bodyid[a]!=m.geom_bodyid[b] and not web:
                pairs.append((a,b));required.append(CLEARANCE_MM)
            else:self.exclusions.append((a,b))
        self.pairs=np.array(pairs,dtype=int);self.required=np.array(required)
        self.human_index={g:i for i,g in enumerate(self.human)}
        self.aggregate=np.array([self.human_index[a] for a,b in pairs])
        if local_hands:
            self.anatomy_bounds=self.bounds.copy()
            lower=[];upper=[]
            for side,center in (('r',self.centers[0]),('l',self.centers[1])):
                lower.extend(((-180. if side=='r' else 20.),-120.,center-100.,-math.pi,-math.pi,-math.pi))
                upper.extend(((-20. if side=='r' else 180.),120.,center+140.,math.pi,math.pi,math.pi))
            self.bounds=np.column_stack((self.bounds,np.array((lower,upper))))
        self.state(self.initial(0),0.)

    def state(self,q,lift_mm):
        q=np.asarray(q)
        if q.shape!=(self.bounds.shape[1],) or not np.isfinite(q).all():raise ValueError('Wrong joint state')
        if not 0<=lift_mm<=6.:raise ValueError('This screen covers only first 6 mm opening')
        self.data.qpos[self.free]=q[:len(self.free)]
        for a,b,c in self.couplings:self.data.qpos[a]=np.polynomial.polynomial.polyval(self.data.qpos[b],c)
        self.model.body_pos[self.model.body('case_cap').id]=self.origin+self.rotation[:,2]*lift_mm/1000
        if self.local_hands:
            for i,pose in enumerate(self.placements):
                xyz=q[len(self.free)+6*i:len(self.free)+6*i+3]
                R=Rotation.from_rotvec(q[len(self.free)+6*i+3:len(self.free)+6*i+6]).as_matrix()
                root_world=self.origin+self.rotation@xyz/1000+R@pose['delta']
                self.model.body_pos[pose['root']]=pose['parent_R'].T@(root_world-pose['parent_p'])
                self.model.body_quat[pose['root']]=Rotation.from_matrix(pose['parent_R'].T@R@pose['root_R']).as_quat(scalar_first=True)
        mujoco.mj_forward(self.model,self.data)

    def pad(self,c):
        g=c['geom'];R=self.data.geom_xmat[g].reshape(3,3)
        normal=R@np.array(c['local_normal'])
        return self.data.geom_xpos[g]+normal*self.model.geom_size[g,0],normal

    def contact_geometry(self,c,lift_mm,offset_mm=0.):
        point,normal=self.pad(c)
        origin=self.origin+self.rotation[:,2]*((lift_mm if c['part']=='cap' else 0)-self.d.seam)/1000
        local=self.rotation.T@(point-origin)*1000
        z=float(np.clip(local[2],c['center']-7,c['center']+7))
        depth,slope=depth_at(z,c['center'])
        xy=np.array(local[:2]);core=np.array((self.d.width/2-self.d.corner,self.d.depth/2-self.d.corner))
        nearest=np.clip(xy,-core,core);direction=xy-nearest
        if np.linalg.norm(direction)<1e-10:
            axis=int(np.argmin(core+self.d.corner-depth-np.abs(xy)))
            direction=np.zeros(2);direction[axis]=1 if xy[axis]>=0 else -1
            nearest[axis]=direction[axis]*core[axis]
        else:direction/=np.linalg.norm(direction)
        surface=nearest+(self.d.corner-depth+offset_mm)*direction
        target=np.r_[surface,z]
        product_normal=np.r_[direction,slope];product_normal/=np.linalg.norm(product_normal)
        desired=-self.rotation@product_normal
        error=point-(origin+self.rotation@target/1000)
        return error*1000,normal-desired,local,math.degrees(math.acos(float(np.clip(normal@desired,-1,1)))),0.

    def distances(self):
        """Vector AABB lower bounds only prune certainly nonviolating pairs."""
        m,d=self.model,self.data
        rot=d.geom_xmat.reshape(-1,3,3)
        ext=np.zeros((m.ngeom,3))
        for g in self.human+self.products:
            size=m.geom_size[g]
            kind=m.geom_type[g]
            if kind==mujoco.mjtGeom.mjGEOM_CAPSULE:ext[g]=size[0]+np.abs(rot[g,:,2])*size[1]
            elif kind==mujoco.mjtGeom.mjGEOM_ELLIPSOID:ext[g]=np.sqrt((rot[g]**2)@(size**2))
            elif kind==mujoco.mjtGeom.mjGEOM_BOX:ext[g]=np.abs(rot[g])@size
            elif kind==mujoco.mjtGeom.mjGEOM_CYLINDER:
                axis=rot[g,:,2];ext[g]=np.abs(axis)*size[1]+size[0]*np.sqrt(np.maximum(0,1-axis*axis))
            elif kind==mujoco.mjtGeom.mjGEOM_SPHERE:ext[g]=size[0]
            else:raise ValueError('Unhandled imported collision skin type')
        a,b=self.pairs.T
        gap=np.maximum(0,np.abs(d.geom_xpos[a]-d.geom_xpos[b])-ext[a]-ext[b])
        lower=np.linalg.norm(gap,axis=1)*1000
        values=lower.copy()
        # Every threshold violation must have a lower bound below this query band.
        for i in np.flatnonzero(lower<max(CLEARANCE_MM+OPT_BUFFER,1.)):
            values[i]=mujoco.mj_geomDistance(m,d,int(a[i]),int(b[i]),1.,None)*1000
        return values

    def residual(self,q,lift_mm,offset_mm,initial,collision_weight):
        self.state(q,lift_mm)
        items=[]
        for c in self.contacts:
            error,normal,local,angle,patch_angle=self.contact_geometry(c,lift_mm,offset_mm)
            items.extend(error);items.extend(12*normal)
            items.extend((0.,.015*(local[2]-c['center'])))
        for side in ('r','l'):
            cs=[c for c in self.contacts if c['side']==side]
            (a,na),(b,nb)=[self.pad(c) for c in cs]
            items.extend((20*max(0.,float(na@nb)-.5),max(0.,20.-np.linalg.norm(a-b)*1000)))
        # Search guidance, not anatomy or an acceptance criterion: initialize
        # palms beside/behind the box instead of through the enclosed volume.
        for side,center,sign in (('r',self.centers[0],-1),('l',self.centers[1],1)):
            wrist=self.data.xpos[self.model.body('lunate_'+side).id]
            local=self.rotation.T@(wrist-self.origin)*1000
            desired=np.array((sign*55.,-45.,center+10.+(lift_mm if side=='r' else 0)))
            items.extend((.2 if collision_weight<6 else .02)*(local-desired))
        distances=self.distances() if collision_weight else np.ones(len(self.pairs))*10
        limits=self.required+OPT_BUFFER
        limits[self.required<0]=self.required[self.required<0]
        if offset_mm:limits[:self.product_pair_count]=CLEARANCE_MM+OPT_BUFFER
        violations=np.minimum(0,distances-limits)
        grouped=np.zeros(len(self.human));np.minimum.at(grouped,self.aggregate,violations)
        # Native capsule/box penetration can be flat once the capsule axis is
        # deeply inside. This interior-only search hint restores an escape
        # gradient; independent acceptance still uses every native pair.
        hints=[]
        for g in self.human:
            c=self.rotation.T@(self.data.geom_xpos[g]-self.origin)*1000
            c[2]+=self.d.seam
            points=[c]
            if self.model.geom_type[g]==mujoco.mjtGeom.mjGEOM_CAPSULE:
                axis=self.rotation.T@self.data.geom_xmat[g].reshape(3,3)[:,2]*self.model.geom_size[g,1]*1000
                points.extend((c-axis,c+axis))
            depth=0.
            for point in points:
                margins=np.array((self.d.width/2-abs(point[0]),self.d.depth/2-abs(point[1]),point[2],self.d.length+lift_mm-point[2]))
                depth=max(depth,float(max(0,min(margins))))
            hints.append(depth)
        return np.r_[items,collision_weight*grouped,collision_weight*np.array(hints),.008*(q-initial)]

    def solve(self,initial,*,lift_mm,offset_mm=0.,collision_weight=6.):
        initial=np.clip(initial,self.bounds[0]+1e-7,self.bounds[1]-1e-7)
        result=least_squares(lambda q:self.residual(q,lift_mm,offset_mm,initial,collision_weight),
            initial,bounds=self.bounds,max_nfev=MAX_NFEV,x_scale='jac',diff_step=1e-4,
            ftol=1e-8,xtol=1e-8,gtol=1e-8)
        return result.x,dict(nfev=result.nfev,terminated=bool(result.success),
                            message=result.message,cost=float(result.cost),optimality=float(result.optimality),
                            diagnostics=self.diagnostics(result.x,lift_mm=lift_mm,offset_mm=offset_mm))

    def diagnostics(self,q,*,lift_mm,offset_mm=0.):
        self.state(q,lift_mm);values=self.distances()
        limits=self.required.copy()
        if offset_mm:limits[:self.product_pair_count]=CLEARANCE_MM
        bad=np.flatnonzero(values<limits-1e-7)
        contacts=[]
        for c in self.contacts:
            err,normal,local,angle,patch_angle=self.contact_geometry(c,lift_mm,offset_mm)
            contacts.append(dict(side=c['side'],part=c['part'],digit=c['digit'],geom=self.model.geom(c['geom']).name,
                error_mm=float(np.linalg.norm(err)),normal_deg=angle,pad_patch_angle_deg=patch_angle,local_mm=local.tolist()))
        margins=np.minimum(self.data.qpos-self.model.jnt_range[:,0],self.model.jnt_range[:,1]-self.data.qpos)
        equality=max((abs(self.data.qpos[a]-np.polynomial.polynomial.polyval(self.data.qpos[b],c)) for a,b,c in self.couplings),default=0.)
        bounded=bool(np.all(q>=self.bounds[0]-1e-9) and np.all(q<=self.bounds[1]+1e-9))
        opposition=[]
        for side in ('r','l'):
            cs=[c for c in self.contacts if c['side']==side]
            (a,na),(b,nb)=[self.pad(c) for c in cs]
            opposition.append(dict(side=side,normal_angle_deg=math.degrees(math.acos(float(np.clip(na@nb,-1,1)))),separation_mm=float(np.linalg.norm(a-b)*1000)))
        valid=bounded and not len(bad) and min(margins)>=-1e-9 and equality<1e-10 and all(c['error_mm']<=CONTACT_MM and c['normal_deg']<=NORMAL_DEG for c in contacts) and all(c['normal_angle_deg']>=60. and c['separation_mm']>=20. for c in opposition)
        def witness(i):
            a,b=self.pairs[i]
            return dict(a=self.model.geom(a).name,b=self.model.geom(b).name,distance_mm=float(values[i]),required_mm=float(limits[i]))
        return dict(accepted=bool(valid),parameter_bounds_respected=bounded,contacts=contacts,opposition=opposition,minimum_joint_margin_deg=float(np.degrees(min(margins))),
            equality_error_rad=float(equality),violations=[witness(i) for i in bad],
            worst_clearance=witness(int(np.argmin(values-limits))),
            minimum_between_hands_mm=self.cross_hand_distance(values),
            q_rad=np.asarray(q).tolist())

    def cross_hand_distance(self,values):
        result=[]
        for i,(a,b) in enumerate(self.pairs[self.product_pair_count:],self.product_pair_count):
            an=self.model.body(self.model.geom_bodyid[a]).name;bn=self.model.body(self.model.geom_bodyid[b]).name
            if (an.endswith('_r') and bn.endswith('_l')) or (an.endswith('_l') and bn.endswith('_r')):result.append(values[i])
        return float(min(result)) if result else None

    def initial(self,start):
        q=self.model.qpos0[self.free].copy();rng=np.random.default_rng(SEED+start)
        for i,j in enumerate(self.free):
            name=self.names[j]
            if 'elbow_flexion' in name:q[i]=1.5
            elif 'shoulder_elv' in name:q[i]=.8
            elif 'elv_angle' in name:q[i]=.6
            elif 'shoulder_rot' in name:q[i]=.1
            elif 'pro_sup' in name:q[i]=.3
            elif 'cmc_abduction' in name:q[i]=.2
            elif 'cmc_flexion' in name:q[i]=.0
            elif 'abduction' in name and name.startswith('mcp'):q[i]=0.
            elif name.startswith(('mcp','pm')):q[i]=1.1
            elif name.startswith('md'):q[i]=.7
            if start:q[i]+=(self.bounds[1,i]-self.bounds[0,i])*rng.uniform(-.15,.15)
        if self.local_hands:
            for i,pose in enumerate(self.placements):
                center=self.centers[i]
                rotation=pose['initial_rotation'].copy()
                xyz=-(self.rotation.T@Rotation.from_rotvec(rotation).as_matrix()@pose['grasp_delta'])*1000
                xyz[2]+=center
                if start:
                    xyz+=rng.uniform(-15.,15.,3)
                    rotation+=rng.uniform(-.3,.3,3)
                q=np.r_[q,xyz,rotation]
        return np.clip(q,self.bounds[0]+1e-6,self.bounds[1]-1e-6)

    def audit(self):
        m=self.model
        return dict(model='myohands' if self.local_hands else 'myoarms',nq=m.nq,independent=len(self.free),actuators=m.nu,tendons=m.ntendon,
            placement_variables=12 if self.local_hands else 0,patch_selection=self.patch_selection,
            palmar_contacts=list(self.palmar_contacts.values()),
            dynamics_used=False,anatomy_transform='Imported hand joints/skin unchanged; independent rigid hand placement, torso/upper arms excluded' if self.local_hands else 'Original passive torso and two imported arms; no anatomy scaling or hand remodelling',
            joints=[dict(name=self.names[j],body=m.body(m.jnt_bodyid[j]).name,axis=m.jnt_axis[j].tolist(),range_rad=m.jnt_range[j].tolist()) for j in range(m.njnt)],
            couplings=[dict(dependent=self.names[a],master=self.names[b],coefficients=c.tolist()) for a,b,c in self.couplings],
            skin=[dict(name=m.geom(g).name,body=m.body(m.geom_bodyid[g]).name,kind=int(m.geom_type[g]),size_m=m.geom_size[g].tolist(),contype=int(m.geom_contype[g]),conaffinity=int(m.geom_conaffinity[g])) for g in self.human],
            explicit_imported_pairs=[[m.geom(a).name,m.geom(b).name] for a,b in self.imported_pairs],
            screened_pairs=[[m.geom(a).name,m.geom(b).name] for a,b in self.pairs],
            excluded_self_pairs=[[m.geom(a).name,m.geom(b).name] for a,b in self.exclusions])


def main():
    # Focused discovery first; study/replay and views consume these same scenes.
    d=build_three_line()['dimensions']
    scene=GripScene(Setup('balanced',-25.,350.,1150.),d,local_hands=True)
    OUT.mkdir(parents=True,exist_ok=True)
    identity=sources();anatomy=anatomy_identity();rows=[]
    for start in range(STARTS):
        q,warm=scene.solve(scene.initial(start),lift_mm=0.,collision_weight=3.)
        q,result=scene.solve(q,lift_mm=0.)
        rows.append(dict(start=start,warm=warm,result=result))
        (OUT/'discovery.json').write_text(json.dumps(dict(sources=identity,anatomy=anatomy,setup=asdict(scene.setup),audit=scene.audit(),attempts=rows),indent=2)+'\n')
        diag=result['diagnostics']
        print(json.dumps(dict(start=start,accepted=diag['accepted'],contacts=diag['contacts'],violations=diag['violations'][:4])),flush=True)
        if diag['accepted']:break
    if sources()!=identity:raise RuntimeError('Study Python inputs changed')


if __name__=='__main__':main()
