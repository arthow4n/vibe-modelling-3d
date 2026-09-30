"""Review actual tab/head solidity and accessible support, not printer fit."""
from pathlib import Path
import argparse
import json
import math
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths
from components import *

def review(run,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rows=list(orca_linear_paths(Path(run)/'plate_1.gcode'))
    # Exact centered layout registration; no bed-footprint acceptance check.
    tx=135.
    ty=135-((-OUT_Y-14-(OUT_Y/2+FIT+1.6))+BUTTON_FRONT)/2
    ly=ty-OUT_Y-14
    def intervals(z,lo,hi):
        spans=[]
        for x,y,nx,ny,h,width,role in rows:
            if abs(h-z)>1e-5 or role.startswith('Support') or role=='Brim' or abs(nx-x)<1e-8: continue
            if not min(x,nx)<=tx<=max(x,nx): continue
            cy=y+(ny-y)*(tx-x)/(nx-x)-ty
            half=width/2*math.hypot(nx-x,ny-y)/abs(nx-x)
            a,b=max(lo,cy-half),min(hi,cy+half)
            if b>=a: spans.append((a,b))
        merged=[]
        for a,b in sorted(spans):
            if merged and a<=merged[-1][1]: merged[-1][1]=max(b,merged[-1][1])
            else: merged.append([a,b])
        filled=sum(b-a for a,b in merged)
        return dict(filled_width_mm=filled,uncovered_width_mm=max(0,hi-lo-filled),
            internal_gap_mm=sum(b[0]-a[1] for a,b in zip(merged,merged[1:])),intervals_mm=merged)
    layers=sorted({r[4] for r in rows})
    beam={h:intervals(h,ARM_Y-ARM_T/2,ARM_Y+ARM_T/2) for h in layers if ROOT_Z+2<=h<=HEAD_Z-4}
    button={h:intervals(h,HEAD_Y,BUTTON_FRONT) for h in layers if HEAD_Z-1<=h<=HEAD_Z+1}
    fig,axes=plt.subplots(1,3,figsize=(13,5))
    straight=[r for r in rows if abs(r[4]-35)<1e-5 and abs(r[0]-tx)<16 and abs(r[2]-tx)<16 and ty+29<r[1]<ty+37 and ty+29<r[3]<ty+37 and not r[6].startswith('Support')]
    axes[0].add_collection(LineCollection([[(r[0]-tx,r[1]-ty),(r[2]-tx,r[3]-ty)] for r in straight],colors='black',linewidths=2))
    axes[0].set(xlim=(-15,15),ylim=(29,38),title='Actual tab paths at Z=35 mm',xlabel='Body X',ylabel='Body Y');axes[0].set_aspect('equal')
    for ax,center,yrange,title,zlim in ((axes[1],ty,(30.4,40),'Body: pad/shoulder supports',(ROOT_Z-3,RIM_Z+1)),(axes[2],ly,(-41,-31),'Roof-down lid: catch supports',(0,13))):
        selected=[r for r in rows if abs(r[0]-tx)<15 and abs(r[2]-tx)<15 and center+yrange[0]<r[1]<center+yrange[1] and center+yrange[0]<r[3]<center+yrange[1]]
        for kind,color in ((False,'.65'),(True,'tab:blue')):
            segments=[[(r[0]-tx,r[4]),(r[2]-tx,r[4])] for r in selected if r[6].startswith('Support')==kind]
            ax.add_collection(LineCollection(segments,colors=color,linewidths=.45,label='Support/interface' if kind else 'Part'))
        ax.set(xlim=(-15,15),ylim=zlim,title=title,xlabel='Local X (mm)',ylabel='Print Z (mm)');ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'slice_features.png',dpi=170);plt.close(fig)
    summary=dict(gcode=str(Path(run)/'plate_1.gcode'),
        gcode_sha256=hashlib.sha256((Path(run)/'plate_1.gcode').read_bytes()).hexdigest(),
        process_sha256=hashlib.sha256((Path(__file__).parent/'notes/process.json').read_bytes()).hexdigest(),
        registration_mm=dict(x=tx,body_y=ty,lid_y=ly),
        tab_section_mm_by_layer=beam,button_section_mm_by_layer=button,
        maximum_tab_internal_gap_mm=max(v['internal_gap_mm'] for v in beam.values()),
        maximum_button_internal_gap_mm=max(v['internal_gap_mm'] for v in button.values()),
        maximum_tab_uncovered_width_mm=max(v['uncovered_width_mm'] for v in beam.values()),
        maximum_button_uncovered_width_mm=max(v['uncovered_width_mm'] for v in button.values()),
        support_roles=sorted({r[6] for r in rows if r[6].startswith('Support')}),
        limits='Deposited-width approximation at one representative X section, not measured polymer, isotropy or bonding. Support removal/adhesion requires the actual print.')
    (out/'path_review.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if not k.endswith('_by_layer')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('output');a=p.parse_args();review(a.run,a.output)
