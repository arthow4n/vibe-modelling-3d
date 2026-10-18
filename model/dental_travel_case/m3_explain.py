"""CAD-derived SVG sections and practical response plots for the M3 prototype."""
import html
import json
from pathlib import Path

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

import m1_design as m1
import m3_design as m3

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m3'


def section_paths(shape,clip,origin,scale,plane_y=0):
    # Exact solid/plane intersection, sampled only for the displayed SVG edges.
    cut=shape.translate((0,-plane_y,0)).intersect(clip)
    section=cq.Workplane('XZ').add(cut).section().val()
    paths=[]
    ox,oy=origin
    for edge in section.Edges():
        points,_=edge.sample(2 if edge.geomType()=='LINE' else 32)
        coords=[(ox+scale*(-p.x-25),oy+scale*(210-p.z)) for p in points]
        paths.append('M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in coords))
    return paths


def svg():
    OUT.mkdir(exist_ok=True,parents=True)
    content=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="970" viewBox="0 0 1200 970">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#343c49"/></marker></defs>',
        '<rect width="1200" height="970" fill="#fafaf7"/>',
        '<style>text{font-family:sans-serif;fill:#202b38} .label{font-size:17px} .small{font-size:15px} .note{font-size:18px}</style>',
        '<text x="36" y="38" font-size="26">Why M3 should hold better — actual CAD center sections</text>',
        '<text x="36" y="67" class="note">CAD cut Y=0; body blue, cap orange. Dashed purple: guide cut at Y=12. Same scale.</text>']
    clip=m1.box(-35,0,175,30,4,74).val()
    for title,module,ox in [('M1 · printed weak baseline',m1,42),('M3 · practical prototype',m3,620)]:
        parts=module.build()
        d=module.D
        oy,scale=112,8.0
        content.append(f'<text x="{ox}" y="101" font-size="21">{html.escape(title)}</text>')
        for name,color in [('body','#1666a7'),('cap','#c05f11')]:
            paths=section_paths(parts[name].val(),clip,(ox,oy),scale)
            for path in paths:content.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"/>')
        guide_clip=m1.box(-34,0,d.seam+d.lap/2,5,4,d.lap+.1).val()
        for path in section_paths(parts['fixed'].val(),guide_clip,(ox,oy),scale,plane_y=12):
            content.append(f'<path d="{path}" fill="none" stroke="#7f3d9a" stroke-dasharray="5,4" stroke-width="2"/>')
        def position(x,z):return ox+scale*(-x-25),oy+scale*(210-z)
        x1,y1=position(-d.sleeve_width/2,d.seam)
        x2,y2=position(-d.sleeve_width/2,d.seam+d.lap)
        bx=ox+160
        content.extend([f'<path d="M{bx},{y1} H{bx+12} M{bx+6},{y1} V{y2} M{bx},{y2} H{bx+12}" fill="none" stroke="#454545"/>',
            f'<text x="{bx+20}" y="{(y1+y2)/2}" class="label">{d.lap:g} mm overlap</text>'])
        labels=[(d.hook_bottom,-d.beam_outer-1,'Flat retaining shoulder'),
                (d.press_z,-d.beam_outer-1.1,'Press inward to release'),
                (d.beam_root+9,-d.beam_outer+d.beam_thickness/2,f'{d.beam_thickness:g} mm leaf'),
                (d.seam+d.lap-3,-d.sleeve_width/2,'Guide beside slot (Y=12)')]
        for i,(z,x,label) in enumerate(labels):
            xx,yy=position(x,z)
            ty=220+i*90
            content.append(f'<text x="{ox+235}" y="{ty}" class="label">{label}</text>')
            content.append(f'<path d="M{ox+230},{ty-5} L{xx},{yy}" fill="none" stroke="#343c49" marker-end="url(#arrow)"/>')
        content.append(f'<text x="{ox}" y="735" class="note">{d.width:g} mm shell · {d.hook_width:g} mm tooth width</text>')
    notes=[
        'Holding: cap shoulder pulls on the tooth; a long guide carries the bearing couple.',
        'Weak route: leaf bends inward → tooth face rotates → edge contact may add inward force.',
        'M3: 30 mm guide, 2 mm leaf, 9 mm retaining land width, stronger pocket skin.',
        'Opening: squeeze both recessed pads, then withdraw. Entry ramps permit push-on closing.',
        'Proxy predicts loss of flat capture, not complete escape. Printed fit, friction and recovery remain unmeasured.',
        'No liner assumption. STEP/STL are prototype geometry; no new print has been performed.']
    for i,line in enumerate(notes):content.append(f'<text x="36" y="{786+i*30}" class="note">{html.escape(line)}</text>')
    content.append('</svg>')
    target=OUT/'joint_sections.svg'
    target.write_text('\n'.join(content)+'\n')
    # Raster preview is for headless visual inspection; SVG is the delivered explanation.
    import cairosvg
    cairosvg.svg2png(url=str(target),write_to=str(OUT/'joint_sections.png'))


def plots():
    record=json.loads((OUT/'proxy.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(11,4.3),layout='constrained')
    for name,v in record['variants'].items():
        curve=v['central_response']
        axes[0].plot([x['per_catch_axial_N'] for x in curve],
                     [x['remaining_flat_capture_mm'] for x in curve],label=name)
        fixed=v['fixed_world_12N']['inward_mm']
        axes[1].bar(name,fixed,label=name)
    axes[0].axhline(0,color='black',lw=.8)
    axes[0].set(xlabel='Axial force on ONE catch (N)',ylabel='Remaining flat capture (mm)',
        title='Rotating-face proxy; E1200, fit loss .25 mm\nSimply supported pocket strip; stop at capture loss')
    axes[0].legend()
    axes[1].set(ylabel='Inward shoulder motion (mm)',
        title='Fixed-world 12 N traction beam proxy\nDifferent contact assumption; no holding-force claim')
    fig.savefig(OUT/'proxy_comparison.svg')
    vector=OUT/'proxy_comparison.svg'
    vector.write_text('\n'.join(line.rstrip() for line in vector.read_text().splitlines())+'\n')
    fig.savefig(OUT/'proxy_comparison.png',dpi=160)
    plt.close(fig)


if __name__=='__main__':
    svg()
    plots()
