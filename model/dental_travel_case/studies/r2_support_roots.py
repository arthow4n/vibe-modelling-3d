"""Headless dump of actual Orca paths at the originally unsupported mount roots.

Arguments: probe G-code, SVG destination. Reads only; writes the requested SVG.
Purple support at Z=2.2 is overlaid on black part paths at Z=2.4 before correction.
This local diagnostic locates support; it is not a print-quality or footprint audit.
"""
from pathlib import Path
import re
import sys


def paths(source):
    x=y=z=0.;role=''
    found=[]
    for line in Path(source).read_text().splitlines():
        if line.startswith(';TYPE:'): role=line[6:].strip()
        if not line.startswith(('G0 ','G1 ')): continue
        values={k:float(v) for k,v in re.findall(r'([XYZE])(-?[0-9.]+)',line)}
        end_x,end_y,end_z=values.get('X',x),values.get('Y',y),values.get('Z',z)
        if values.get('E',0)>0 and (x!=end_x or y!=end_y):
            if role in ('Support','Support interface') and abs(end_z-2.2)<1e-4:
                found.append((x,y,end_x,end_y,'#a13daa'))
            elif role not in ('Support','Support interface') and abs(end_z-2.4)<1e-4:
                found.append((x,y,end_x,end_y,'#333'))
        x,y,z=end_x,end_y,end_z
    return found


def dump(source,destination):
    segments=paths(source)
    pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="310" viewBox="0 0 1000 310">',
            '<rect width="1000" height="310" fill="white"/>',
            '<text x="20" y="25" font-size="17">Before bed foundations: purple support at Z=2.2, black part paths at Z=2.4</text>']
    for offset,minimum in ((20,0),(520,220)):
        pieces.append(f'<text x="{offset}" y="55" font-size="14">Hinge bearing bases, plate X={minimum}..{minimum+50} mm</text>')
        for x,y,a,b,colour in segments:
            if minimum<=x<=minimum+50 and minimum<=a<=minimum+50 and 173<=y<=198 and 173<=b<=198:
                pieces.append(f'<line x1="{offset+9*(x-minimum):.3f}" y1="{75+9*(198-y):.3f}" x2="{offset+9*(a-minimum):.3f}" y2="{75+9*(198-b):.3f}" stroke="{colour}" stroke-width=".8"/>')
    pieces.append('</svg>')
    Path(destination).write_text('\n'.join(pieces)+'\n')


if __name__=='__main__':
    dump(sys.argv[1],sys.argv[2])
