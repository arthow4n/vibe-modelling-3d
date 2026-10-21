"""Actual imported collision-skin projections for the dental grip scene."""
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import mujoco


def outline(scene,g,axes):
    m,d=scene.model,scene.data
    c=d.geom_xpos[g]*1000;R=d.geom_xmat[g].reshape(3,3);s=m.geom_size[g]*1000
    kind=int(m.geom_type[g]);axes=list(axes)
    circle=np.c_[np.cos(np.linspace(0,2*np.pi,48)),np.sin(np.linspace(0,2*np.pi,48))]
    if kind==int(mujoco.mjtGeom.mjGEOM_CAPSULE):
        a=c-R[:,2]*s[1];b=c+R[:,2]*s[1]
        points=np.vstack((a[axes]+circle*s[0],b[axes]+circle*s[0]))
    elif kind in (int(mujoco.mjtGeom.mjGEOM_ELLIPSOID),int(mujoco.mjtGeom.mjGEOM_SPHERE)):
        if kind==int(mujoco.mjtGeom.mjGEOM_SPHERE):s=np.ones(3)*s[0]
        Q=(R@np.diag(s*s)@R.T)[np.ix_(axes,axes)]
        eigen,vectors=np.linalg.eigh(Q)
        points=c[axes]+circle@np.diag(np.sqrt(np.maximum(0,eigen)))@vectors.T
    elif kind==int(mujoco.mjtGeom.mjGEOM_BOX):
        from itertools import product
        points=(np.array(list(product((-1,1),repeat=3)))*s)@R.T+c
        points=points[:,axes]
    elif kind==int(mujoco.mjtGeom.mjGEOM_CYLINDER):
        ring=np.c_[circle*s[0],np.zeros(len(circle))]
        points=np.vstack(((ring+np.array((0,0,-s[1])))@R.T+c,
                          (ring+np.array((0,0,s[1])))@R.T+c))[:,axes]
    else:raise ValueError('Unreviewed projection type')
    return points[ConvexHull(points).vertices]


def draw_pose(scene,q,path,*,title,status,lift_mm=0.):
    scene.state(q,lift_mm)
    fig,axs=plt.subplots(1,3,figsize=(16,7),gridspec_kw={'width_ratios':[1.4,1.1,1.1]})
    projections=((0,2),(1,2),(0,1)) if scene.local_hands else ((0,2),(0,2),(1,2))
    for k,(ax,axes) in enumerate(zip(axs,projections)):
        for g in scene.products:
            points=outline(scene,g,axes)
            part=scene.box_by_id[g]['part']
            color='#39829c' if part=='cap' else '#87969d'
            ax.add_patch(Polygon(points,facecolor=color,edgecolor='none',alpha=.25))
        for g in scene.human:
            name=scene.model.body(scene.model.geom_bodyid[g]).name
            if k and not name.endswith(('_r','_l')):continue
            color='#d28a3d' if name.endswith('_r') else '#7765a0' if name.endswith('_l') else '#b7b7b0'
            ax.add_patch(Polygon(outline(scene,g,axes),facecolor=color,edgecolor=color,alpha=.32,lw=.5))
        for c in scene.contacts:
            point,normal=scene.pad(c)
            ax.scatter(*(point[list(axes)]*1000),color='#c3313b',s=14,zorder=5)
            a=point[list(axes)]*1000;b=a+normal[list(axes)]*12
            ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='#c3313b',lw=1),zorder=6)
        if scene.local_hands:
            if k==0:ax.set(xlim=(-180,180),ylim=(950,1310),title='Local hands / front projection')
            elif k==1:ax.set(xlim=(-530,-180),ylim=(950,1310),title='Local hands / side projection')
            else:ax.set(xlim=(-180,180),ylim=(-530,-180),title='Top projection (length collapsed)')
        elif k==0:ax.set(xlim=(-400,400),ylim=(750,1600),title='Whole two-arm setup')
        elif k==1:ax.set(xlim=(-180,180),ylim=(1000,1300),title='Hands and bands: front projection')
        else:ax.set(xlim=(-530,-180),ylim=(1000,1300),title='Side projection')
        ax.set_aspect('equal');ax.set_xlabel(('X' if axes[0]==0 else 'Y')+' (mm)');ax.set_ylabel(('Z' if axes[1]==2 else 'Y')+' (mm)');ax.grid(alpha=.15)
    fig.suptitle(title+'\n'+status,fontsize=14)
    fig.text(.02,.02,'Orange = right / cap. Purple = left / body. Red = skin points and outward normals (12 mm arrows). Native distances decide collision.',fontsize=10)
    fig.tight_layout(rect=(0,.09,1,.94))
    fig.savefig(path.with_suffix('.svg'));fig.savefig(path.with_suffix('.png'),dpi=130)
    svg=path.with_suffix('.svg')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)
