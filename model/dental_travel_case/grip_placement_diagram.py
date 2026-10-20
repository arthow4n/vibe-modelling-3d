"""Editable placement comparison; dimensional proposal, not anatomical evidence."""
from pathlib import Path
from html import escape
import json
import cairosvg
from grip_placement import LAYOUTS,dimensions,describe

OUT=Path(__file__).resolve().parent/'notes/grip_human'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="930" viewBox="0 0 1200 930">',
          '<rect width="1200" height="930" fill="#faf9f5"/>',
          '<style>text{font-family:DejaVu Sans,sans-serif;fill:#243840} .small{font-size:15px} .label{font-size:18px}</style>',
          '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#c1742b"/></marker></defs>']
    def text(x,y,s,size=18,color='#243840'):
        rows.append(f'<text x="{x}" y="{y}" font-size="{size}" style="fill:{color}">{escape(s)}</text>')
    text(38,43,'Where should the two recessed grip bands sit?',30)
    text(38,74,'Selected shape: smooth full-wrap bands, 0.7 mm deep × 20 mm wide. Distances are from the seam.',17)
    text(38,104,'Opening: keep the body below the cap, upright or diagonal, to help keep the toothbrush inside.',17)
    scale=1.65;top=160
    def y(z):return top+(264-z)*scale
    d=dimensions()
    candidates=(('A — too near the backing','near','Cap band overlaps the backing blend.'),
                ('B — selected layout','selected','Clear of backing; useful room to either end.'),
                ('C — usable alternative','far','Less room above the cap band.'))
    for i,(label,key,comment) in enumerate(candidates):
        layout=LAYOUTS[key];cap=layout.cap_center_mm;body=layout.body_center_mm
        x=90+i*390;w=123
        text(x-45,142,label,20)
        rows.append(f'<rect x="{x}" y="{top}" width="{w}" height="{264*scale}" rx="10" fill="#e3ecee" stroke="#486775" stroke-width="2"/>')
        # Sleeve lies inside the cap. Backing shown as an exterior reserve strip.
        rows.append(f'<rect x="{x+7}" y="{y(204)}" width="{w-14}" height="{30*scale}" fill="#93adb5" opacity=".4" stroke="#486775" stroke-dasharray="5 4"/>')
        rows.append(f'<rect x="{x-4}" y="{y(213)}" width="7" height="{39*scale}" fill="#8b8d92"/>')
        rows.append(f'<line x1="{x-9}" x2="{x+w+9}" y1="{y(174)}" y2="{y(174)}" stroke="#243840" stroke-width="3"/>')
        for center,color in ((174+cap,'#d58c45'),(174+body,'#8873af')):
            rows.append(f'<rect x="{x}" y="{y(center+10)}" width="{w}" height="{20*scale}" rx="5" fill="{color}" opacity=".85"/>')
            rows.append(f'<line x1="{x-7}" x2="{x+w+7}" y1="{y(center)}" y2="{y(center)}" stroke="{color}" stroke-dasharray="3 3"/>')
        text(x+w+13,y(174+cap)+5,f'+{cap:g} mm',16)
        text(x+w+13,y(174+body)+5,f'−{abs(body):g} mm',16)
        arrow_start=y(174+cap)-8;arrow_end=max(top+6,arrow_start-35)
        rows.append(f'<path d="M{x+w/2} {arrow_start}V{arrow_end}" stroke="#c1742b" stroke-width="4" marker-end="url(#arrow)"/>')
        text(x-32,630,comment,15)
        text(x-32,658,f'Band centres: {cap-body:g} mm apart',16)
        text(x-32,684,f'Cap band: +{cap-10:g} to +{cap+10:g} mm',16)
        text(x-32,710,f'Body band: −{abs(body)+10:g} to −{abs(body)-10:g} mm',16)
    text(38,760,'Read the drawing',20)
    text(38,789,'Orange: lift the cap here. Purple: support the body here. Black line: seam.',17)
    text(38,817,'Dashed fill: internal sleeve ends at +30 mm. Grey strip: existing exterior backing blend ends at +39 mm.',17)
    text(38,845,'Choose B: cap centre +55 mm / body centre −30 mm. Cap band starts 6 mm beyond the backing.',17)
    text(38,873,'Location selected from layout and opening use. Printed traction/feel remains a separate physical question.',17)
    text(38,904,'Side view, schematic width. Bands wrap around all faces/corners. No printable CAD has been changed.',15)
    rows.append('</svg>')
    (OUT/'placement_comparison.svg').write_text('\n'.join(rows)+'\n')
    cairosvg.svg2png(url=str(OUT/'placement_comparison.svg'),write_to=str(OUT/'placement_comparison.png'))
    (OUT/'layout.json').write_text(json.dumps(dict(selected='selected',candidates={key:describe(layout,d) for key,layout in LAYOUTS.items()}),indent=2)+'\n')
    draw_opening(d,LAYOUTS['selected'])


def draw_opening(d,layout):
    rows=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1060" viewBox="0 0 1200 1060">',
        '<rect width="1200" height="1060" fill="#faf9f5"/>',
        '<style>text{font-family:DejaVu Sans,sans-serif;fill:#243840}</style>',
        '<defs><marker id="pull" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto"><path d="M0 0L7 3.5L0 7" fill="#b86820"/></marker></defs>']
    def text(x,y,s,size=17):
        rows.append(f'<text x="{x}" y="{y}" font-size="{size}">{escape(s)}</text>')
    text(35,42,'Chosen grip layout: hold the body, lift the cap',29)
    text(35,74,'Cap band +55 mm · body band −30 mm · both 20 mm wide × 0.7 mm deep',19)
    text(35,103,'Upright opening shown. A modest diagonal works with the same hand roles; keep the body underneath.',16)
    scale=1.;top=160;extent=d.length+(d.length-d.seam)
    band_gap=layout.cap_center_mm-layout.body_center_mm-layout.band_width_mm
    y=lambda z:top+extent-z
    for i,(lift,title) in enumerate(((0.,'1  Find the bands'),(6.,'2  Start the lift'),(d.length-d.seam,'3  Keep supporting the body'))):
        x=105+i*390;w=d.width
        text(x-50,139,title,20)
        rows.append(f'<rect x="{x}" y="{y(d.seam)}" width="{w}" height="{d.seam}" rx="6" fill="#d9e3e6" stroke="#486775" stroke-width="2"/>')
        rows.append(f'<rect x="{x+5}" y="{y(d.seam+d.lap)}" width="{w-10}" height="{d.lap}" fill="#c7d6da" stroke="#486775" stroke-dasharray="4 3"/>')
        rows.append(f'<rect x="{x}" y="{y(d.length+lift)}" width="{w}" height="{d.length-d.seam}" rx="6" fill="#f1d7ba" fill-opacity=".7" stroke="#b86820" stroke-width="2"/>')
        for z,color in ((d.seam+layout.cap_center_mm+lift,'#d58c45'),(d.seam+layout.body_center_mm,'#8873af')):
            rows.append(f'<rect x="{x}" y="{y(z+10)}" width="{w}" height="20" rx="4" fill="{color}"/>')
            for at in (x-8,x+w+8):
                rows.append(f'<ellipse cx="{at}" cy="{y(z)}" rx="9" ry="13" fill="{color}" stroke="#faf9f5" stroke-width="2"/>')
        rows.append(f'<line x1="{x-8}" x2="{x+w+8}" y1="{y(d.seam)}" y2="{y(d.seam)}" stroke="#243840" stroke-dasharray="3 3"/>')
        rows.append(f'<path d="M{x+w+40} {y(d.seam+layout.cap_center_mm+lift)+18}v-45" stroke="#b86820" stroke-width="3" marker-end="url(#pull)"/>')
        text(x+w+23,y(d.seam+layout.body_center_mm)+40,'hold',16)
        text(x-50,546,f'Cap lift: {lift:g} mm',18)
        text(x-50,574,f'Gap between band edges: {band_gap+lift:g} mm',16)
    text(35,615,'The lower grip stays on the body. The upper grip travels with the cap; the two zones move farther apart.',17)
    text(35,643,'The sleeve is 30 mm long. Clearing it alone does not fully uncover a toothbrush that extends above it.',16)
    text(35,671,'At 90 mm lift, the cap mouth reaches the old closed top: enough axial travel to clear fully enclosed contents.',16)
    text(35,699,'Ovals mark suggested contact zones, not anatomical hand shapes. Diagrams show motion, not measured forces.',15)
    text(35,746,'What makes the shallow band useful?',23)
    # Same quintic profile as the selected G2 concept: 6 mm ramps, 8 mm landing.
    for i,(title,direction) in enumerate((('CAP: pull toward the closed cap end',1),('BODY: resist in the opposite direction',-1))):
        x=100+i*580;base=805;axial=16.;depth_scale=70.
        text(x-50,780,title,18)
        points=[]
        for k in range(201):
            z=-10+k/10;u=(z+10)/6 if z<-4 else (10-z)/6
            dep=.7 if -4<=z<=4 else .7*u**3*(10-15*u+6*u*u)
            points.append(f'{x+(z+10)*axial:.2f},{base+dep*depth_scale:.2f}')
        rows.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#486775" stroke-width="3"/>')
        at=x+(17.5 if direction==1 else 2.5)*axial
        rows.append(f'<circle cx="{at}" cy="{base+24}" r="8" fill="#d58c45"/>')
        start=x+160;end=start+direction*90
        rows.append(f'<path d="M{start} {base+80}H{end}" stroke="#b86820" stroke-width="3" marker-end="url(#pull)"/>')
        text(x-50,925,'Press against this curved shoulder as you pull.',16)
    text(35,971,'Both ramps blend smoothly into the wall. They give a shoulder to press against without an outward tab.',17)
    text(35,1000,'Profile depth is enlarged: 16 px/mm along the band, 70 px/mm into the wall. Traction/feel is unmeasured.',15)
    text(35,1032,'Decision complete for placement exploration. Finished CAD, contents fit at the reshaped band, and print feel belong to implementation.',14)
    rows.append('</svg>')
    path=OUT/'selected_opening.svg';path.write_text('\n'.join(rows)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


if __name__=='__main__':main()
