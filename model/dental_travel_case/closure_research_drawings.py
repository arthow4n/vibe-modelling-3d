"""Actual CAD sections, recovered motion and native deformation witnesses."""
import hashlib
import html
import json
from pathlib import Path
import math
import cadquery as cq
import cairosvg
import closure_research_design as design
import m1_design as base

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/closure_research'
BLUE='#1769a6';ORANGE='#ce741c';RED='#c62f48'


def label(items,x,y,words,size=18):
    items.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(words)}</text>')


def canvas(title,height):
    items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">',
        f'<rect width="1200" height="{height}" fill="#fafaf7"/>','<style>text{font-family:sans-serif;fill:#243444}</style>']
    label(items,25,38,title,25)
    return items


def section(items,shape,plane,origin,xf,color,opacity=1.):
    sliced=cq.Workplane(plane,origin=origin).add(shape).section().val()
    lines=[]
    for wire in sliced.Wires():
        points,_=wire.sample(.01)
        lines.append('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in map(xf,points))+' Z')
    items.append(f'<path d="{" ".join(lines)}" fill="{color}" fill-rule="evenodd" fill-opacity="{opacity}" stroke="{color}" stroke-width=".7"/>')


def save(name,items,*,extra_sources=(),data_files=()):
    inputs=('m1_design.py','closure_research_design.py','closure_research_drawings.py')+extra_sources+data_files
    association={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in inputs}
    items.append('<metadata>'+html.escape(json.dumps(association))+'</metadata></svg>')
    path=OUT/(name+'.svg')
    path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


def draw():
    OUT.mkdir(parents=True,exist_ok=True)
    parts={kind:design.build(kind) for kind in design.KINDS}
    items=canvas('Four ways to retain the case without an internal spring box',1140)
    label(items,25,76,'Actual CAD sections. Blue = body; orange = cap/lid. Same 77 × 51.2 mm outer envelope.',17)
    titles=('R1 — your idea: broad-wall tip snap','R2 — same tip snap on end walls',
            'R3 — continuous perimeter bead','R4 — sliding lid, wall detents')
    captions=('The broad sleeve walls bend inward near their free rim.',
              'Shorter wall span should give a firmer snap.',
              'All around the rim participates; no separate arms.',
              'Rails block lifting; small detents resist sliding.')
    for i,kind in enumerate(design.KINDS):
        x0=(i%2)*600;y0=125+(i//2)*465
        p=parts[kind]
        label(items,x0+25,y0,titles[i],21)
        if kind=='slide_wall':
            p=design.slide(70.)
            xf=lambda v,x0=x0,y0=y0:(x0+300+4.4*v.x,y0+365-4.4*v.y)
            section(items,p['body'].val(),'XY',(0,0,47.5),xf,BLUE)
            section(items,p['cap'].val(),'XY',(0,0,47.5),xf,ORANGE)
            label(items,x0+105,y0+155,'Slide to open ↓',18)
        else:
            xf=lambda v,x0=x0,y0=y0:(x0+300+4.4*v.x,y0+180-4.4*v.y)
            section(items,p['body'].val(),'XY',(0,0,249),xf,BLUE)
            section(items,p['cap'].val(),'XY',(0,0,249),xf,ORANGE)
            label(items,x0+50,y0+335,'Clear central width: 69.5 mm (M5: 56.9 mm at catches)',16)
        label(items,x0+25,y0+395,captions[i],17)
        label(items,x0+25,y0+424,'No independent cantilever, release tunnel or inward guard.',16)
    label(items,25,1080,'These are research samples: opening resistance and recovery are not measured or guaranteed.',19)
    label(items,25,1114,'The sliding concept needs long clearance to open; its short coupon cannot represent full-length drag or warping.',16)
    save('concepts',items)

    p=parts['shell_broad'];d=design.D
    items=canvas('Your tip catch: a short retaining lip, then space to recover',880)
    label(items,25,77,'Actual central section through one broad-wall detent. Same magnification in each panel; rigid poses.',17)
    clip=base.box(0,24,247,4,10,15).val()
    for i,(lift,title) in enumerate(((0,'Seated'),(1.5,'Pulling against the retaining lip'),(6,'Past the lip — wall can recover'))):
        x0=400*i
        xf=lambda v,x0=x0:(x0+30+26*(v.y-20),140+26*(254-v.z))
        cap=p['cap'].val().translate((0,0,lift))
        section(items,p['body'].val().intersect(clip),'YZ',(0,0,0),xf,BLUE)
        section(items,cap.intersect(clip),'YZ',(0,0,0),xf,ORANGE)
        common=p['body'].val().intersect(cap)
        if common.Volume()>1e-5:section(items,common.intersect(clip),'YZ',(0,0,0),xf,RED)
        label(items,x0+25,125,title,18)
        label(items,x0+25,565,f'Cap lift: {lift:g} mm',18)
    label(items,25,616,'Red is blocked rigid overlap: real wall deformation is needed here. It is not an allowed interpenetrating pose.',17)
    label(items,25,654,'A recess alone would keep rubbing for almost the entire guide length after the catch popped out.',18)
    label(items,25,691,'The track below the retaining lip removes that drag after the first few millimetres. The lip is not cut away.',18)
    label(items,25,735,'No runout at 30 mm lift: still obstructed. Corrected samples at 6–90 mm: clear in the declared axial path.',17)
    label(items,25,779,'Guide and bearing remain 78 mm long. The cap stays complete so its roof and wall constraints are represented.',17)
    label(items,25,824,'Both shell and cap can flex in a print. CAD capture does not determine how many newtons are needed.',17)
    save('tip_motion',items)

    items=canvas('Sliding alternative: guide and retention live near the opening',740)
    p=design.slide(70.)
    xf=lambda v:(70+12*(v.x-31),165+24*(52-v.z))
    clip=base.box(36,35,47.5,12,80,12).val()
    section(items,p['body'].val().intersect(clip),'XZ',(0,35,0),xf,BLUE)
    section(items,p['cap'].val().intersect(clip),'XZ',(0,35,0),xf,ORANGE)
    label(items,25,100,'Cross-section at Y35 — plain rail, away from the detent',19)
    label(items,370,197,'Lid slides along the case length, into the page.',18)
    label(items,370,235,'Sloping keys sit under the sidewall rails.',18)
    label(items,370,273,'The rails block lifting even with detents removed.',18)
    label(items,370,311,'Only the upper few millimetres of the cavity contain rails.',18)
    label(items,25,455,'Detent section at Y10 — small ramp into a sidewall pocket',19)
    xf=lambda v:(70+12*(v.x-31),523+18*(51.2-v.z))
    detail=base.box(36,35,48.5,12,80,6).val()
    section(items,p['body'].val().intersect(detail),'XZ',(0,10,0),xf,BLUE)
    section(items,p['cap'].val().intersect(detail),'XZ',(0,10,0),xf,ORANGE)
    label(items,370,505,'The sidewall bows outward as the tooth crosses the lip.',18)
    label(items,370,543,'A clearance track avoids rubbing along the whole rail.',18)
    label(items,370,581,'Open body: 70.6 mm wide, with broad-face access.',18)
    label(items,25,650,'Tradeoff: about 264 mm of lid travel in the complete concept. The 70 mm sample tests the interface, not that handling.',17)
    label(items,25,690,'Body prints on its broad floor; lid prints outside-face down. Print-layer directions differ from the cap samples.',17)
    save('slide_section',items)


if __name__=='__main__':draw()
