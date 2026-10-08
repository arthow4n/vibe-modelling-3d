"""Side projection and native desk-gap witnesses for the retained access study.

This is a diagnostic figure, not product export or anatomical evidence.
"""
import json
from pathlib import Path
from itertools import product

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

import synthetic_human_interaction as h
from execution.identity import digest


def projection(model,geom):
    m,d=model.model,model.data
    centre=d.geom_xpos[geom]*1000
    rotation=d.geom_xmat[geom].reshape(3,3)
    size=m.geom_size[geom]*1000
    kind=m.geom_type[geom]
    if kind==h.mujoco.mjtGeom.mjGEOM_BOX:
        points=np.array(list(product((-1,1),repeat=3)))*size
        points=(points@rotation.T+centre)[:,1:]
    else:
        t=np.linspace(0,2*np.pi,32,endpoint=False)
        circle=size[0]*np.c_[np.cos(t),np.sin(t)]
        if kind==h.mujoco.mjtGeom.mjGEOM_CAPSULE:
            ends=[centre-rotation[:,2]*size[1],centre+rotation[:,2]*size[1]]
        else:
            ends=[centre]
        points=np.vstack([circle+end[1:] for end in ends])
    return points[ConvexHull(points).vertices]


def main():
    receipt=json.loads((h.ROOT/'notes/v3_human_interaction.json').read_text())
    if receipt['schema_version']!=1 or receipt['sources']['model/analysis_phone_stand/v3_components.py']!=digest(h.ROOT/'v3_components.py'):
        raise ValueError('Historical CAD source association changed; do not transfer this figure')
    fig,axes=plt.subplots(2,2,figsize=(12,8),gridspec_kw={'width_ratios':[2,1]})
    for row,scale in enumerate((.9,1.)):
        run=next(r for r in receipt['runs'] if r['setup']['scale']==scale)
        candidate=run['candidates'][0]
        model=h.Interaction(h.Setup(60.,scale=scale))
        pre,q=np.array(candidate['approach_q_rad']),np.array(candidate['q_rad'])
        ax,plot=axes[row]
        model.state(q,0.)
        for box in model.boxes:
            p=projection(model,model.model.geom(box['name']).id)
            ax.fill(p[:,0],p[:,1],color='#bb9b85',alpha=.25,lw=.5,edgecolor='#644732')
        for t,color in ((0,'#9aa6ae'),(.5,'#ef8a32'),(1,'#117f9b')):
            model.state(pre+t*(q-pre),0.)
            for geom in model.human:
                p=projection(model,geom)
                ax.fill(p[:,0],p[:,1],color=color,alpha=.22,edgecolor=color,lw=.7)
        ax.axhline(0,color='black',lw=1,label='Desk')
        ax.scatter(*model.surface_mm[1:],c='#be3030',s=30,zorder=4)
        ax.set(xlim=(0,540),ylim=(-10,370),xlabel='Rearward Y (mm)',ylabel='Z (mm)',
               title=f'Scale {scale}: pre-contact / mid-transition / contact')
        ax.set_aspect('equal',adjustable='box')
        ax.text(.01,.02,'Side projection omits X separation; use native pair diagnostics',transform=ax.transAxes,fontsize=8)
        samples=np.linspace(0,1,41)
        gaps=[]
        palm=model.model.geom('palm_proxy').id
        desk=model.model.geom('desk').id
        for t in samples:
            model.state(pre+t*(q-pre),0.)
            gaps.append(h.mujoco.mj_geomDistance(model.model,model.data,palm,desk,1.,None)*1000)
        plot.plot(samples,gaps,color='#117f9b',lw=2)
        plot.axhline(0,color='#be3030',lw=1,label='Desk penetration boundary')
        plot.axhline(h.CLEARANCE_MM,color='#777777',ls='--',label='Declared clearance screen')
        plot.set(xlabel='Approach interpolation fraction',ylabel='Palm–desk signed distance (mm)',
                 title='Nonlinear native distance along the transition')
        plot.grid(alpha=.2)
        plot.legend(fontsize=8)
    fig.suptitle('Historical synthetic V3 study: valid endpoints can hide an invalid approach',fontsize=13)
    fig.tight_layout()
    output=h.ROOT/'notes/v3_synthetic_interaction_replay.png'
    fig.savefig(output,dpi=160)
    print(json.dumps({'diagnostic_figure':str(output)}))


if __name__=='__main__':
    main()
