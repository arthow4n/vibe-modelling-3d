"""Editable placement comparison; dimensional proposal, not anatomical evidence."""
from pathlib import Path
from html import escape
import cairosvg

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
    text(38,74,'Proposal: smooth full-wrap bands, 0.7 mm deep × 20 mm wide. All distances measured from the seam.',17)
    text(38,104,'Opening: keep the body below the cap, upright or diagonal, to help keep the toothbrush inside.',17)
    scale=1.65;top=160
    def y(z):return top+(264-z)*scale
    candidates=(('A — near the seam',40,-15,'Bands crowd the joint region.'),
                ('B — balanced starting point',50,-30,'Clears the joint; leaves room on the cap.'),
                ('C — farther apart',65,-50,'More separation; upper band nearer cap end.'))
    for i,(label,cap,body,comment) in enumerate(candidates):
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
        text(x+w+13,y(174+cap)+5,f'+{cap} mm',16)
        text(x+w+13,y(174+body)+5,f'−{abs(body)} mm',16)
        arrow_start=y(174+cap)-8;arrow_end=max(top+6,arrow_start-35)
        rows.append(f'<path d="M{x+w/2} {arrow_start}V{arrow_end}" stroke="#c1742b" stroke-width="4" marker-end="url(#arrow)"/>')
        text(x-32,630,comment,15)
        text(x-32,658,f'Band centres: {cap-body} mm apart',16)
        text(x-32,684,f'Cap band: +{cap-10} to +{cap+10} mm',16)
        text(x-32,710,f'Body band: −{abs(body)+10} to −{abs(body)-10} mm',16)
    text(38,760,'Read the drawing',20)
    text(38,789,'Orange: lift the cap here. Purple: support the body here. Black line: seam.',17)
    text(38,817,'Dashed fill: internal sleeve ends at +30 mm. Grey strip: existing exterior backing blend ends at +39 mm.',17)
    text(38,845,'B starts at +40 mm: 10 mm beyond the sleeve, only 1 mm beyond the backing blend.',17)
    text(38,873,'These are layout facts. The native-hand search is recorded separately; no location is proven comfortable.',17)
    text(38,904,'Side view, schematic width. Bands wrap around all faces/corners. No printable CAD has been changed.',15)
    rows.append('</svg>')
    (OUT/'placement_comparison.svg').write_text('\n'.join(rows)+'\n')
    cairosvg.svg2png(url=str(OUT/'placement_comparison.svg'),write_to=str(OUT/'placement_comparison.png'))


if __name__=='__main__':main()
