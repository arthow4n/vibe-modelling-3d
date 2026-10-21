"""Select the outward side of imported fingertip skins, including mirrored axes."""
import numpy as np
import mujoco


def outward_pad_sign(model,data,pad_name,capsule_name):
    pad=model.geom(pad_name).id;bone=model.geom(capsule_name).id
    if int(model.geom_type[pad])!=int(mujoco.mjtGeom.mjGEOM_ELLIPSOID) or int(model.geom_type[bone])!=int(mujoco.mjtGeom.mjGEOM_CAPSULE):
        raise ValueError('This contact qualification requires imported pad ellipsoid and distal capsule')
    axis=data.geom_xmat[bone].reshape(3,3)[:,2]
    along=np.clip((data.geom_xpos[pad]-data.geom_xpos[bone])@axis,-model.geom_size[bone,1],model.geom_size[bone,1])
    radial=data.geom_xpos[pad]-(data.geom_xpos[bone]+along*axis)
    length=np.linalg.norm(radial)
    if length<1e-9:raise ValueError('Pad side is ambiguous: inspect imported geometry')
    radial/=length
    alignment=float(radial@data.geom_xmat[pad].reshape(3,3)[:,2])
    if abs(alignment)<.9:raise ValueError('Pad minor axis does not identify an unambiguous outward patch')
    return dict(sign=1 if alignment>0 else -1,outward_axis_alignment=alignment,
                pad_name=pad_name,capsule_name=capsule_name)


def palmar_capsule_contact(model,data,*,digit,side):
    """Flexor-facing native capsule surface, qualified by imported tendon motion.

    Flattened distal ellipsoids are on the opposite side in these assets. Their
    axis orientation alone must not be interpreted as a palmar finger pad.
    Tendon shortening selects motion direction only; no muscle force is solved.
    """
    if digit not in ('thumb','index') or side not in ('r','l'):raise ValueError((digit,side))
    prefix='distal_thumb' if digit=='thumb' else 'distph2'
    name=prefix+'_coll_'+side;g=model.geom(name).id
    j=model.joint(('ip_flexion_' if digit=='thumb' else 'md2_flexion_')+side).id
    base=('FPL' if digit=='thumb' else 'FDP2')+'_tendon'
    known=[base+'_'+side]+([base] if side=='r' else [])
    available=[model.tendon(i).name for i in range(model.ntendon)]
    names=[n for n in known if n in available]
    if len(names)!=1:raise ValueError('Ambiguous flexor tendon identity')
    tendon=model.tendon(names[0]).id;address=model.jnt_qposadr[j]
    before=float(data.ten_length[tendon]);q=float(data.qpos[address])
    delta=1e-5 if q+1e-5<=model.jnt_range[j,1] else -1e-5
    data.qpos[address]=q+delta;mujoco.mj_forward(model,data)
    derivative=(float(data.ten_length[tendon])-before)/delta
    data.qpos[address]=q;mujoco.mj_forward(model,data)
    if abs(derivative)<1e-6:raise ValueError('Flexor motion is not identified at this pose')
    direction=-np.sign(derivative)
    curl=direction*np.cross(data.xaxis[j],data.geom_xpos[g]-data.xanchor[j])
    R=data.geom_xmat[g].reshape(3,3);axis=R[:,2]
    curl-=axis*(curl@axis)
    if np.linalg.norm(curl)<1e-9:raise ValueError('Flexor-side surface direction is ambiguous')
    normal=curl/np.linalg.norm(curl)
    ellipse=model.geom(prefix+'_coll_2_'+side).id
    return dict(geom=name,joint=model.joint(j).name,tendon=names[0],
        local_normal=(R.T@normal).tolist(),shortening_joint_direction=float(direction),
        tendon_length_derivative_m_per_rad=derivative,
        flexor_dot_ellipse_positive_axis=float(normal@data.geom_xmat[ellipse].reshape(3,3)[:,2]))
