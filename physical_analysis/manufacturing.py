"""Narrow Orca path reader for local mechanical-feature slice review.

Not a printability, bed-fit or deposited-volume validator. Widths are slicer
metadata, not measured polymer or material-property evidence. The reviewed
profiles use linear moves, absolute XYZ and relative E; other modes fail.
"""
from pathlib import Path
import re


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
