"""Rebuild the useful assembly-context view and numerical force curves."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from components import assembled,box,placed,CRADLE_BOTTOM,CRADLE_THICKNESS,RELEASE_TRAVEL
from concept import screen

ROOT=Path(__file__).resolve().parent


def context_view():
    fig=plt.figure(figsize=(8,7),facecolor='white')
    ax=fig.add_subplot(projection='3d')
    parts=assembled(60)
    colors={'base':(.55,.61,.66),'arm':(.28,.38,.48),'cradle':(.68,.74,.78),'latch':(.91,.48,.20)}
    light=np.array([-.3,-.5,.8]);light/=np.linalg.norm(light)
    all_triangles=[];all_colors=[]
    for name,part in parts.items():
        vertices,indices=part.val().tessellate(.3,.15)
        vertices=np.array([v.toTuple() for v in vertices]);triangles=vertices[np.array(indices)]
        normals=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
        length=np.linalg.norm(normals,axis=1);normals/=np.maximum(length[:,None],1e-12)
        shade=.64+.36*np.abs(normals@light)
        colors_face=np.clip(np.asarray(colors[name])[None,:]*shade[:,None],0,1)
        all_triangles.extend(triangles);all_colors.extend(colors_face)
    ax.add_collection3d(Poly3DCollection(all_triangles,facecolors=all_colors,edgecolors='none'))
    # Display-only device envelope, deliberately outside all print entry points.
    phone=placed(box(-38,CRADLE_BOTTOM+6,CRADLE_THICKNESS,76,165,12),60)
    vertices,indices=phone.val().tessellate(1,.2)
    triangles=np.array([v.toTuple() for v in vertices])[np.array(indices)]
    ax.add_collection3d(Poly3DCollection(triangles,facecolors=(.13,.44,.51,.3),edgecolors='none'))
    ax.plot([-40,40,40,-40,-40],[0,0,125,125,0],[0]*5,color='.5',lw=.7)
    ax.set(xlim=(-50,50),ylim=(-10,140),zlim=(0,230))
    ax.set_box_aspect((100,150,230));ax.view_init(elev=19,azim=-58)
    ax.set_axis_off();ax.set_title('Phone stand • 60° position',fontsize=14)
    fig.text(.5,.04,'Orange: press-to-release catch   |   Translucent phone: reference only',ha='center',fontsize=10)
    target=ROOT/'renders/assembled/stand_in_use.png';target.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(target,dpi=180,bbox_inches='tight');plt.close(fig)


def force_curves():
    data=ROOT/'notes/analysis'
    release=json.loads((data/'release/result.json').read_text())
    holding=json.loads((data/'holding/result.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for ax,result,name,travel,title in (
        (axes[0],release,'thumb',RELEASE_TRAVEL,'Release • E = 1200 MPa'),
        (axes[1],holding,'drive',.75,'Local holding contact • E = 800 MPa')):
        x=[0]+[h['load_fraction']*travel for h in result['history']]
        y=[0]+[abs(h['motion_force_N'][name]) for h in result['history']]
        ax.plot(x,y,'o-',ms=3,color='#b76528')
        ax.set(xlabel='Prescribed travel (mm)',ylabel='Force along motion (N)',title=title)
        ax.grid(alpha=.2)
    service=max(c['tooth_tangential_force_N'] for c in screen()['cases'])
    axes[1].axhline(service,color='#32677b',linestyle='--',label=f'300 g phone + moving parts: {service:.1f} N')
    axes[1].legend(fontsize=8)
    fig.suptitle('Conditional numerical predictions — not physical measurements',fontsize=12)
    target=ROOT/'renders/analysis/force_curves.png';target.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(target,dpi=180);plt.close(fig)

if __name__=='__main__':
    context_view()
    if (ROOT/'notes/analysis/release/result.json').exists(): force_curves()
