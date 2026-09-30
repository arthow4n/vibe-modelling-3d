"""Narrow Orca path reader for local mechanical-feature slice review.

Not a printability, bed-fit or deposited-volume validator. Widths are slicer
metadata, not measured polymer or material-property evidence. The reviewed
profiles use linear moves, absolute XYZ and relative E; other modes fail.
"""
from pathlib import Path
import re
import math


def section_coverage(paths, *, x_mm, z_mm, span_mm):
    """Width approximation on a local Y section of one layer, in global XYZ.

    Extrusion segments are planar capsules of the recorded width. Clip and
    union their intersections with X=x_mm; omit supports and brims. This is
    local sliced fill evidence, not actual deposited polymer or solid material
    calibration. It does not determine printability, bed fit or layer bonding.
    """
    lo,hi=span_mm
    if hi<=lo: raise ValueError('Section span must have positive length')
    spans=[]
    def add(a,b):
        a,b=max(lo,a),min(hi,b)
        if b>=a: spans.append((a,b))
    for x,y,nx,ny,z,width,role in paths:
        if abs(z-z_mm)>1e-5 or role.startswith(('Support','Brim')): continue
        radius=width/2
        if radius<=0: raise ValueError('Deposited path width must be positive')
        dx,dy=nx-x,ny-y
        length=math.hypot(dx,dy)
        if not length: continue
        if x_mm<min(x,nx)-radius or x_mm>max(x,nx)+radius: continue
        ox,oy=-dy*radius/length,dx*radius/length
        corners=((x+ox,y+oy),(nx+ox,ny+oy),(nx-ox,ny-oy),(x-ox,y-oy))
        crossings=[]
        for (ax,ay),(bx,by) in zip(corners,(*corners[1:],corners[0])):
            if abs(bx-ax)<1e-12:
                if abs(x_mm-ax)<1e-10: crossings.extend((ay,by))
            elif min(ax,bx)<=x_mm<=max(ax,bx):
                crossings.append(ay+(by-ay)*(x_mm-ax)/(bx-ax))
        if crossings: add(min(crossings),max(crossings))
        for cx,cy in ((x,y),(nx,ny)):
            if abs(x_mm-cx)<=radius:
                half=math.sqrt(max(0,radius**2-(x_mm-cx)**2))
                add(cy-half,cy+half)
    merged=[]
    for a,b in sorted(spans):
        if merged and a<=merged[-1][1]+1e-10: merged[-1][1]=max(b,merged[-1][1])
        else: merged.append([a,b])
    filled=sum(b-a for a,b in merged)
    return dict(filled_width_mm=filled,uncovered_width_mm=max(0,hi-lo-filled),
        internal_gap_mm=sum(b[0]-a[1] for a,b in zip(merged,merged[1:])),intervals_mm=merged)


def orca_linear_paths(path):
    """Yield (x0,y0,x1,y1,z,width,role) for deposited linear layer moves."""
    x=y=z=0.
    width=.42
    role=''
    started=False
    absolute=True
    relative_e=True
    for line in Path(path).read_text().splitlines():
        if line.startswith(';LAYER_CHANGE'):
            started=True
        if line.startswith(';TYPE:'): role=line[6:]
        if line.startswith(';WIDTH:'): width=float(line[7:])
        command=line.split(';',1)[0].strip()
        opcode=command.split(' ',1)[0]
        if opcode=='G90': absolute=True
        if opcode=='G91': absolute=False
        if opcode=='M83': relative_e=True
        if opcode=='M82': relative_e=False
        if started and (not absolute or not relative_e or opcode in ('G2','G3')):
            raise ValueError('Local path review requires linear moves, absolute XYZ and relative E')
        if opcode not in ('G0','G1'): continue
        args={k:float(v) for k,v in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',command)}
        nx,ny,nz=args.get('X',x),args.get('Y',y),args.get('Z',z)
        if started and args.get('E',0)>0 and (nx!=x or ny!=y) and role!='Custom':
            yield x,y,nx,ny,nz,width,role
        x,y,z=nx,ny,nz
