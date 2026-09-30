"""Local tab/pad fill and accessible support; not a printer-fit validator."""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from physical_analysis.manufacturing import orca_linear_paths,section_coverage
from components import *

def review(run):
    out=Path(__file__).parent/'notes';out.mkdir(exist_ok=True)
    gcode=Path(run)/'plate_1.gcode'
    paths=list(orca_linear_paths(gcode))
    tx=135.
    ty=135-((-(FRONT_Y+FIT+WALL)-LAYOUT_OFFSET)+BUTTON_FRONT)/2
    ly=ty-LAYOUT_OFFSET
    layers=sorted({p[4] for p in paths})
    def section(z,lo,hi):
        s=section_coverage(paths,x_mm=tx,z_mm=z,span_mm=(ty+lo,ty+hi))
        s['intervals_mm']=[[a-ty,b-ty] for a,b in s['intervals_mm']]
        return s
    beam={z:section(z,ARM_Y-ARM_T/2,ARM_Y+ARM_T/2) for z in layers if ROOT_Z+2<=z<=HEAD_Z-4}
    pad={z:section(z,HEAD_Y,BUTTON_FRONT) for z in layers if HEAD_Z-1<=z<=HEAD_Z+1}
    assert beam and pad,'Sliced layers missing from selected critical sections'
    report=dict(gcode=str(gcode),gcode_sha256=hashlib.sha256(gcode.read_bytes()).hexdigest(),
        path_reader_sha256=hashlib.sha256((Path(__file__).resolve().parents[2]/'physical_analysis/manufacturing.py').read_bytes()).hexdigest(),
        registration_mm=dict(x=tx,body_y=ty,lid_y=ly),tab_section_mm_by_layer=beam,pad_section_mm_by_layer=pad,
        maximum_tab_internal_gap_mm=max(s['internal_gap_mm'] for s in beam.values()),
        maximum_pad_internal_gap_mm=max(s['internal_gap_mm'] for s in pad.values()),
        maximum_tab_uncovered_width_mm=max(s['uncovered_width_mm'] for s in beam.values()),
        maximum_pad_uncovered_width_mm=max(s['uncovered_width_mm'] for s in pad.values()),
        support_roles=sorted({p[6] for p in paths if p[6].startswith('Support')}),
        limits='One representative X section of critical tab/pad layers; recorded-width approximation, not measured polymer, layer bonding or mechanical calibration. Support adhesion/removal remain physical checks.')
    fig,axes=plt.subplots(1,3,figsize=(13,5))
    z=min(beam,key=lambda h:abs(h-12))
    selected=[p for p in paths if abs(p[4]-z)<1e-5 and abs(p[0]-tx)<15 and abs(p[2]-tx)<15
        and ty+ARM_Y-3<p[1]<ty+ARM_Y+3 and ty+ARM_Y-3<p[3]<ty+ARM_Y+3 and not p[6].startswith('Support')]
    axes[0].add_collection(LineCollection([[(p[0]-tx,p[1]-ty),(p[2]-tx,p[3]-ty)] for p in selected],colors='black',linewidths=2))
    axes[0].set(xlim=(-15,15),ylim=(ARM_Y-3,ARM_Y+3),title=f'Tab paths at Z={z:g} mm',xlabel='Body X',ylabel='Body Y');axes[0].set_aspect('equal')
    for ax,center,ylo,yhi,title,zhi in ((axes[1],ty,HEAD_Y-4,BUTTON_FRONT+2,'Body pad/shoulder',RIM_Z+1),
        (axes[2],ly,-FRONT_Y-4,-HEAD_Y+4,'Roof-down cap catch',LID_TOP-CAP_BOTTOM+1)):
        selected=[p for p in paths if abs(p[0]-tx)<15 and abs(p[2]-tx)<15 and center+ylo<p[1]<center+yhi and center+ylo<p[3]<center+yhi]
        for support,color in ((False,'.65'),(True,'tab:blue')):
            segments=[[(p[0]-tx,p[4]),(p[2]-tx,p[4])] for p in selected if p[6].startswith('Support')==support]
            ax.add_collection(LineCollection(segments,colors=color,linewidths=.45,label='Support/interface' if support else 'Part'))
        ax.set(xlim=(-15,15),ylim=(0,zhi),title=title,xlabel='Local X (mm)',ylabel='Print Z (mm)');ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/'slice_features.png',dpi=170);plt.close(fig)
    (out/'path_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if not k.endswith('_by_layer')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');a=p.parse_args();review(a.run)
