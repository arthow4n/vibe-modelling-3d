"""Editable SVG operating explanation from the current named dimensions."""
import math
from pathlib import Path
import cairosvg
import v2_components as d

def draw():
    out=Path(__file__).parent/'renders/concepts'
    out.mkdir(parents=True,exist_ok=True)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="540" viewBox="0 0 1200 540">',
         '<rect width="1200" height="540" fill="#f5f3ed"/>',
         '<style>text{font-family:DejaVu Sans,sans-serif;fill:#24332e}.title{font-size:24px;font-weight:bold}.body{font-size:16px}.small{font-size:13px}</style>',
         '<text x="32" y="38" class="title">Raised open easel — support, release, reseat</text>',
         '<text x="32" y="64" class="body">The V seats carry the load. A separate sliding keeper prevents the rear bar lifting out.</text>']
    t=math.radians(65)
    fy,beta=d.prop_pose(65)
    hy=d.PIVOT_Y+78*math.cos(t); hz=d.PIVOT_Z+78*math.sin(t)
    def local(u,v):
        return (d.PIVOT_Y+(u+8)*math.cos(t)-(v+40)*math.sin(t),
                d.PIVOT_Z+(u+8)*math.sin(t)+(v+40)*math.cos(t))
    for i,(title,shift,lift,caption) in enumerate([
        ('1  Locked',0,0,'Phone weight presses the round bar into the V seats.'),
        ('2  Support + release',-7,24,'Push the rear button; lift the bar above the catches.'),
        ('3  Reseat + let go',0,0,'Lower into another seat; release and check capture.')]):
        ox=35+i*395
        angle=75 if i==2 else 65
        t=math.radians(angle)
        fy,beta=d.prop_pose(angle)
        hy=d.PIVOT_Y+78*math.cos(t); hz=d.PIVOT_Z+78*math.sin(t)
        def p(y,z):return (ox+55+y*1.15,410-z*1.15)
        def points(coords):return ' '.join(f'{x:.2f},{y:.2f}' for x,y in map(lambda yz:p(*yz),coords))
        def line(a,b,color,width=5):
            x,y=p(*a);nx,ny=p(*b)
            svg.append(f'<line x1="{x}" y1="{y}" x2="{nx}" y2="{ny}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
        svg.append(f'<text x="{ox}" y="108" class="title">{title}</text>')
        line((-35,0),(211,0),'#9eaaa3',2)
        line((-35,4),(211,4),'#47786a',8)
        line((d.PIVOT_Y,8),(d.PIVOT_Y,55),'#47786a',9)
        svg.append(f'<polygon points="{points([local(0,0),local(170,0),local(170,13),local(0,13)])}" fill="#c4cbd0" stroke="#536572" stroke-width="2"/>')
        line(local(-8,-40),local(70,-40),'#47786a',8)
        for u in (4,70):line(local(u,-36),local(u,0),'#47786a',5)
        # Raised pose rotates the prop around its fixed upper hinge.
        foot_z=d.FOOT_Z+lift
        foot_y=hy+math.sqrt(d.PROP_LENGTH**2-(hz-foot_z)**2)
        line((hy,hz),(foot_y,foot_z),'#47786a',6)
        for sy in d.SEAT_YS:
            svg.append(f'<polyline points="{points([(sy-8,d.SEAT_VERTEX_Z+8),(sy,d.SEAT_VERTEX_Z),(sy+8,d.SEAT_VERTEX_Z+8)])}" fill="none" stroke="#47786a" stroke-width="4"/>')
            line((sy-8+shift,8),(sy-8+shift,d.HOOK_UNDERSIDE+5),'#c08732',3)
            line((sy-8+shift,d.HOOK_UNDERSIDE+1),(sy-1+shift,d.HOOK_UNDERSIDE+1),'#c08732',3)
        line((d.SPINE_FRONT+shift,10),(210+shift,10),'#c08732',4)
        x,y=p(foot_y,foot_z)
        svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#31574b"/>')
        if i==1:
            line((225,28),(202,28),'#bc5c3d',3)
            svg.append(f'<text x="{ox+228}" y="358" class="small">push 7 mm</text>')
        svg.append(f'<text x="{ox}" y="448" class="small">{caption}</text>')
    svg.extend(['<text x="32" y="487" class="body">Use two hands: one supports the cradle, the other presses the button and lifts/repositions the rear bar.</text>',
                '<text x="32" y="513" class="small">Simplified side projection of current CAD; bolts stay assembled. Guide caps and the paired outboard struts overlap in this view.</text>','</svg>'])
    target=out/'v2_adjustment.svg'
    target.write_text('\n'.join(svg)+'\n')
    cairosvg.svg2png(url=str(target),write_to=str(target.with_suffix('.png')))
    print(target)

if __name__=='__main__':draw()
