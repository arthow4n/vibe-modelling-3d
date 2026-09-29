"""Object-specific slice evidence: snap solidity and flagged support location.

Not a bed-fit/G-code validator. Reads Orca's relative-E, absolute-XYZ layer
paths, rejects arcs. Plots deposited centerlines with actual WIDTH metadata.
"""
from pathlib import Path
import argparse
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from components import OUT_Y, LID_HALF_Y, BASE_CAM_Y, CAM_R, ARM_Y, ARM_T
import math
from physical_analysis.manufacturing import orca_linear_paths as paths


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('output');a=p.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    primary=list(paths(Path(a.run)/'plate_1.gcode'))
    support=[r for r in paths(Path(a.run)/'support_probe/plate_1.gcode') if r[6].startswith('Support')]
    fig,axes=plt.subplots(1,2,figsize=(11,5))
    for ax,coord in zip(axes,('xy','xz')):
        def seg(r): return [(r[0],r[1] if coord=='xy' else r[4]),(r[2],r[3] if coord=='xy' else r[4])]
        ax.add_collection(LineCollection([seg(r) for r in primary[::8]],colors='.8',linewidths=.3))
        ax.add_collection(LineCollection([seg(r) for r in support],colors='red',linewidths=.7))
        ax.autoscale();ax.set_aspect('equal');ax.set_title('Support probe: '+coord);ax.set_xlabel('X (mm)')
    fig.tight_layout()
    if support: fig.savefig(out/'support_locations.png',dpi=160)
    plt.close(fig)
    # Centered layout's explicit translation, read from Orca object center/layout.
    # Recover the translation from the named layout dimensions. This is local
    # feature registration, not a second printer-envelope check.
    tx=135
    layout_min_y=-OUT_Y-12-LID_HALF_Y
    layout_max_y=max(OUT_Y/2,BASE_CAM_Y+CAM_R)
    ty=135-(layout_min_y+layout_max_y)/2-OUT_Y-12
    selected=[r for r in primary if .99<r[4]<1.01 and min(r[0],r[2])<tx-12 and max(r[0],r[2])>tx-38
              and min(r[1],r[3])<ty+31 and max(r[1],r[3])>ty+24]
    fig,ax=plt.subplots(figsize=(11,4))
    roles=sorted(set(r[6] for r in selected));colors=dict(zip(roles,plt.cm.tab10.colors))
    for role in roles:
        ax.add_collection(LineCollection([[(r[0]-tx,r[1]-ty),(r[2]-tx,r[3]-ty)] for r in selected if r[6]==role],
                          colors=[colors[role]],linewidths=2,label=role))
    ax.set(xlim=(-38,-12),ylim=(24,31),xlabel='Lid-local X (mm)',ylabel='Lid-local Y (mm)',title='Snap: actual paths at Z=1.0 mm');ax.set_aspect('equal');ax.legend();fig.tight_layout();fig.savefig(out/'snap_paths.png',dpi=180)
    # At a straight beam section, deposited-width intervals answer whether it is
    # hollow under this slice. This is a path approximation, not measured polymer.
    section_x=tx-25
    layer_gaps={}
    internal_gaps={}
    filled_widths={}
    for height in sorted({r[4] for r in primary if 0<r[4]<=3.21}):
        intervals=[]
        for x,y,nx,ny,z,width,role in primary:
            if abs(z-height)>1e-5 or abs(nx-x)<1e-8 or role=='Brim': continue
            if not min(x,nx)<=section_x<=max(x,nx): continue
            cy=y+(ny-y)*(section_x-x)/(nx-x)
            half=width/2*math.hypot(nx-x,ny-y)/abs(nx-x)
            lo,hi=cy-half-ty,cy+half-ty
            if hi>=ARM_Y-ARM_T/2 and lo<=ARM_Y+ARM_T/2: intervals.append((lo,hi))
        edge=ARM_Y-ARM_T/2; end=ARM_Y+ARM_T/2; gap=0.
        for lo,hi in sorted(intervals):
            if lo>edge: gap+=max(0,min(lo,end)-edge)
            edge=max(edge,hi)
            if edge>=end: break
        gap+=max(0,end-edge)
        layer_gaps[height]=gap
        merged=[]
        for lo,hi in sorted(intervals):
            lo=max(lo,ARM_Y-ARM_T/2);hi=min(hi,ARM_Y+ARM_T/2)
            if hi<lo: continue
            if merged and lo<=merged[-1][1]: merged[-1][1]=max(hi,merged[-1][1])
            else: merged.append([lo,hi])
        internal_gaps[height]=sum(max(0,b[0]-a[1]) for a,b in zip(merged,merged[1:]))
        filled_widths[height]=sum(hi-lo for lo,hi in merged)
    print(json.dumps(dict(support_roles=sorted(set(r[6] for r in support)),
        snap_layer_roles=roles,snap_segments=len(selected),beam_section_x_mm=-25,
        deposited_width_approximation=True,section_uncovered_width_mm_by_layer=layer_gaps,
        section_internal_gap_mm_by_layer=internal_gaps,section_filled_width_mm_by_layer=filled_widths,
        max_section_uncovered_width_mm=max(layer_gaps.values()),max_section_internal_gap_mm=max(internal_gaps.values())),indent=2))
