"""Explicit headless SVG illustration of current M1, derived from its parameters."""
from html import escape
from pathlib import Path
from m1_design import D, leaf_offset


def draw():
    d = D
    content = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="670" viewBox="0 0 1200 670">',
               '<rect width="1200" height="670" fill="#faf9f6"/>',
               '<style>text{font-family:DejaVu Sans,sans-serif;fill:#263b48}.title{font-size:27px;font-weight:700}.label{font-size:18px}.small{font-size:15px}.body{fill:#a8c9bb;stroke:#386e5a;stroke-width:2}.cap{fill:#b9d3e9;stroke:#46769c;stroke-width:2}.leaf{fill:#efbe75;stroke:#996429;stroke-width:2}</style>']
    def text(x,y,value,style='label'):
        content.append(f'<text x="{x}" y="{y}" class="{style}">{escape(value)}</text>')
    def arrow(x,y,nx,ny):
        import math
        a = math.atan2(ny-y,nx-x)
        ux,uy = math.cos(a),math.sin(a)
        content.append(f'<path d="M{x} {y}L{nx} {ny}" fill="none" stroke="#263b48" stroke-width="2"/>')
        points = [(nx,ny),(nx-9*ux+4*uy,ny-9*uy-4*ux),(nx-9*ux-4*uy,ny-9*uy+4*ux)]
        content.append('<polygon points="'+' '.join(f'{a:.2f},{b:.2f}' for a,b in points)+'" fill="#263b48"/>')
    text(35,43,'M1 revision — 25 mm narrower, catches at BOTH widthwise ends','title')
    text(35,78,'Pinch the two end-wall contacts with one hand; pull the separate cap with the other.')
    scale,x,y = 1.4,90,140
    w,h = d.width*scale,d.length*scale
    seam = y+(d.length-d.seam)*scale
    content.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="body"/>')
    content.append(f'<path d="M{x+9} {y}H{x+w-9}Q{x+w} {y} {x+w} {y+9}V{seam}H{x}V{y+9}Q{x} {y} {x+9} {y}Z" class="cap"/>')
    press_y = y+(d.length-d.press_z)*scale
    arrow(x-55,press_y,x+5,press_y)
    arrow(x+w+55,press_y,x+w-5,press_y)
    text(38,551,f'{d.length:g} × {d.width:g} × {d.depth:g} mm','small')
    text(38,579,'Two cups; no internal item insert','small')
    text(38,605,'End controls shown schematically','small')
    for ox,released in ((445,False),(825,True)):
        def pt(v,z):
            return ox+(v-27)*10,565-(z-d.beam_root)*8.4
        def poly(points,style):
            mapped = ' '.join(f'{x:.2f},{y:.2f}' for x,y in (pt(v,z) for v,z in points))
            content.append(f'<polygon points="{mapped}" class="{style}"/>')
        text(ox-10,133,'RELEASED' if released else 'CLOSED')
        outer = d.width/2
        inner = outer-d.receiver_wall
        skin = outer-.8
        normal = d.beam_outer
        liner = normal-d.beam_thickness-(d.release+.3)
        port_half = d.beam_width/2+1
        lo,hi = d.seam-1-2*port_half-4,d.seam-1
        poly([(liner-1.2,d.beam_root-2),(liner,d.beam_root-2),
              (liner,d.seam+d.lap),(liner-1.2,d.seam+d.lap)],'body')
        poly([(normal-3.4,d.beam_root-2),(outer,d.beam_root-2),
              (outer,d.beam_root),(normal-3.4,d.beam_root)],'body')
        for bottom,top in ((d.beam_root,lo),(hi,d.seam)):
            poly([(outer-d.wall,bottom),(outer,bottom),(outer,top),(outer-d.wall,top)],'body')
        lift = 6 if released else 0
        pocket = d.hook_bottom-d.axial_play
        poly([(inner,d.seam+lift),(outer,d.seam+lift),(outer,d.hook_bottom+11+lift),
              (skin,d.hook_bottom+11+lift),(skin,pocket+lift),(inner,pocket+lift)],'cap')
        delta = d.release if released else 0
        zs = [d.beam_root,d.beam_root+1]+[d.beam_root+1+s*(d.beam_length-1) for s in (.15,.3,.45,.6,.75,.9,1)]
        poly([(normal-d.beam_thickness-leaf_offset(d,z,delta),z) for z in zs]+
             [(normal-leaf_offset(d,z,delta),z) for z in reversed(zs)],'leaf')
        points = [(normal-.3,d.hook_bottom),(normal+d.hook_projection,d.hook_bottom),
                  (normal+d.hook_projection,d.hook_bottom+1.2),(normal,d.beam_tip),(normal-.3,d.beam_tip)]
        poly([(v-leaf_offset(d,z,delta),z) for v,z in points],'leaf')
        z = d.press_z
        points = [(normal-.2,z-2.4),(normal,z-2.4),(normal+1.2,z-1),
                  (normal+1.2,z+1),(normal,z+2.4),(normal-.2,z+2.4)]
        poly([(v-leaf_offset(d,z,delta),z) for v,z in points],'leaf')
        px,py = pt(normal+1.2-leaf_offset(d,z,delta),z)
        arrow(px+65,py,px+3,py)
        if released:
            px,py = pt(outer,d.hook_bottom+11+lift)
            arrow(px+25,py+70,px+25,py+5)
        text(ox-15,610,'Section through one end catch','small')
    text(642,240,'Deeper / wider bite','small')
    text(642,265,'Hidden pocket','small')
    arrow(642,280,538,265)
    text(35,649,'Diagonal packing is user-confirmed. Revised holding and end comfort still need the new print; no force rating.','small')
    content.append('</svg>')
    path = Path(__file__).resolve().parent/'renders/assembled/m1/m1_closure.svg'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(content)+'\n')


if __name__ == '__main__':
    draw()
