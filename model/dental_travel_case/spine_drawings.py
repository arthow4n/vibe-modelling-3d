"""Actual CAD comparisons: cavity obstruction, flush mounting and flat opening."""
import html
import json
from pathlib import Path
import cairosvg
from closure_research_drawings import canvas,label,section,BLUE,ORANGE
from clamshell_study import hashes
import spine_design as d
import internal_hinge_design as old

ROOT=Path(__file__).resolve().parent


def draw():
    items=canvas('Keep the storage clear: move the folding connection into the rear wall',1050)
    label(items,25,75,'Actual YZ sections at equal scale. Blue = base; orange = lid; green = TPU spine. No rigid shelf inside C8.',17)
    new=d.build('tpu_spine',size=d.MINI)
    baseline=old.build('internal_screw',size=old.MINI)
    clip=d.base.box(0,21,28,100,36,48).val()
    cases=(('C7 at 100°: intrusive pivot and skirt',baseline,100),
        ('C8 closed: flush heads inside wall',new,0),('C8 at 180°: bends between backs',new,180))
    for i,(title,p,angle) in enumerate(cases):
        x0=i*400
        xf=lambda v,x0=x0:(x0+40+7*(v.y-3),480-7*(v.z-4))
        label(items,x0+20,130,title,17)
        cap=old.rotate(p,p['structural_lid'],angle) if i==0 else d.moving(p,p['structural_lid'],angle)
        x=p['centers'][1]+(0 if i==0 else 3.2)
        section(items,p['body'].val().intersect(clip),'YZ',(x,0,0),xf,BLUE)
        section(items,cap.val().intersect(clip),'YZ',(x,0,0),xf,ORANGE,.85)
        if i:
            s=d.strap(d.MINI,p['centers'][1],angle)
            section(items,s.val().intersect(clip),'YZ',(x,0,0),xf,'#26966b')
        # The C8 continuous clear plane; not an invented contents shape.
        xx,yy=xf(type('V',(),dict(y=17.2,z=24.8))())
        items.append(f'<path d="M{x0+30},{yy} H{xx}" stroke="#64877d" stroke-dasharray="5 4"/>')
        label(items,x0+20,530,('7.8 mm local interior intrusion.','0.8 mm uniform rear-wall increase.','Same panel level; about 9.4 mm gap.')[i],16)
    label(items,25,590,'The spine is printed separately in TPU 95A and pressed into recessed holes. PETG shells stay separate material prints.',17)
    label(items,25,632,'Its heads sit flush with the inner rear surface. Eight small buttons replace the hinge barrels, webs and hardware.',17)
    label(items,25,674,'Closed back is flush; front loop/keeper still project. Flexibility, button retention and life are unmeasured until a print.',17)
    c=new['centers'][1];x=c+3.2
    crop=d.base.box(x,18.6,12.6,6,5,6).val()
    xf=lambda v:(45+34*(v.y-16),935-34*(v.z-9.6))
    section(items,new['body'].val().intersect(crop),'YZ',(x,0,0),xf,BLUE)
    section(items,d.pad(d.MINI,c,False).val().intersect(crop),'YZ',(x,0,0),xf,'#26966b')
    label(items,340,765,'Button section: flat retaining shoulder, not a pull-out ramp.',18)
    label(items,340,810,'A soft head must fold/compress to pass the hole. CAD capture',17)
    label(items,340,839,'does not establish pull-out force; the mini box must test it.',17)
    label(items,340,888,'Alternative: a 4.6 mm edge-pin barrel opens flat with almost',17)
    label(items,340,917,'no interior intrusion, but leaves a 2.6 mm exterior bump.',17)
    label(items,25,1008,'The C8 sample is a complete hinged box with the same shortened front loop and keeper. No physical success is inferred.',17)
    sources=('spine_design.py','spine_drawings.py','internal_hinge_design.py','clamshell_design.py','m1_design.py','../sunglasses_case/e_closure.py')
    items.append('<metadata>'+html.escape(json.dumps(hashes(sources)))+'</metadata></svg>')
    out=ROOT/'renders/concepts/spine';out.mkdir(parents=True,exist_ok=True)
    svg=out/'clear_interior.svg';svg.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(svg),write_to=str(svg.with_suffix('.png')))


if __name__=='__main__':draw()
