"""Editable operating diagram using the current CAD's named dimensions."""
import math
from pathlib import Path
import cairosvg
import v3_components as d


def draw():
    target=Path(__file__).parent/'renders/concepts/v3_adjustment.svg'
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="590" viewBox="0 0 1200 590">',
         '<rect width="1200" height="590" fill="#f5f3ed"/>',
         '<style>text{font-family:DejaVu Sans,sans-serif;fill:#24332e}.title{font-size:23px;font-weight:bold}.body{font-size:16px}.small{font-size:13px}</style>',
         '<text x="30" y="35" class="title">Compact printed pedestal — support, press, tilt, release</text>',
         '<text x="30" y="65" class="body">Four printed core parts. One pin holds the cradle and both spring roots; no screws to adjust.</text>']
    for i,(label,angle,travel) in enumerate((('1  Seated',60,0),('2  Hold phone + press',60,d.RELEASE),('3  Tilt + release',75,0))):
        ox=30+i*397
        def p(y,z):return ox+80+y*1.15,410-z*1.15
        def polygon(coords,fill,stroke='#355b50'):
            pts=' '.join(f'{x:.2f},{y:.2f}' for x,y in (p(*v) for v in coords))
            svg.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        def line(a,b,color,width=5):
            x,y=p(*a);nx,ny=p(*b)
            svg.append(f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{nx:.2f}" y2="{ny:.2f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
        t=math.radians(angle)
        def pose(u,v):return d.PIVOT_Y+u*math.cos(t)-v*math.sin(t),d.PIVOT_Z+u*math.sin(t)+v*math.cos(t)
        svg.append(f'<text x="{ox}" y="108" class="title">{label}</text>')
        polygon([(0,0),(140,0),(140,10),(0,10)],'#638c7e')
        x,y=p(d.PIVOT_Y,d.PIVOT_Z)
        svg.append(f'<circle cx="{x}" cy="{y}" r="{d.HOOD_R*1.15}" fill="#87a79b" stroke="#355b50" stroke-width="2"/>')
        svg.append(f'<circle cx="{x}" cy="{y}" r="{d.ROTOR_R*1.15}" fill="#b1c1b9" stroke="#355b50" stroke-dasharray="3 3"/>')
        line(pose(0,0),pose(120,0),'#355b50',8)
        for u in (32,98):line(pose(u,0),pose(u,d.PHONE_V),'#355b50',5)
        polygon([pose(28,40),pose(198,40),pose(198,53),pose(28,53)],'#c4cdd1','#536572')
        line((14-travel,19),(72-travel,19),'#bd8635',5)
        polygon([(19.8-travel,24.5),(23-travel,24.5),(23-travel,27.5),(19.8-travel,27.5)],'#bd8635')
        line((72-travel,18),(72-travel,27),'#bd8635',7)
        svg.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#e4be64" stroke="#796033"/>')
        if i==1:
            line((95,32),(76-d.RELEASE,32),'#bc5c3d',3)
            svg.append(f'<text x="{ox+175}" y="345" class="small">push forward {d.RELEASE:g} mm to stop</text>')
        captions=('A square dog bears on the hidden pocket.',
                  'The dog withdraws; keep the phone supported.',
                  'Choose 45°, 60° or 75°; check full engagement.')
        svg.append(f'<text x="{ox}" y="445" class="small">{captions[i]}</text>')
    svg.extend(['<text x="30" y="490" class="body">The spring returns the dog. Pocket faces carry the angle load; spring friction does not hold the angle.</text>',
        '<text x="30" y="520" class="small">Simplified side section: side rails, folded springs and outboard phone contacts overlap in this projection.</text>',
        '<text x="30" y="548" class="small">Cable opening: 20 mm wide × 30 mm below the phone. Rear ring reserve: broad open area, 33 mm deep.</text>',
        '</svg>'])
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text('\n'.join(svg)+'\n')
    cairosvg.svg2png(url=str(target),write_to=str(target.with_suffix('.png')))
    print(target)


if __name__=='__main__':draw()
