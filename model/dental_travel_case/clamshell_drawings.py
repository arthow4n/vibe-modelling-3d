"""Commit actual CAD comparisons, the cropped-loop issue, and release sections."""
import json
import html
from pathlib import Path
import cairosvg
from closure_research_drawings import canvas,label,section,BLUE,ORANGE,RED
from clamshell_study import hashes
import clamshell_design as design
from clamshell_design import base,D

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'renders/concepts/clamshell'


def save(name,items):
    source=hashes(('clamshell_design.py','clamshell_drawings.py','m1_design.py','../sunglasses_case/e_closure.py'))
    items.append('<metadata>'+html.escape(json.dumps(source))+'</metadata></svg>')
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/(name+'.svg');path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


def draw():
    items=canvas('Same slim storage, horizontal access: three smaller rear connections',750)
    label(items,25,78,'Actual XY sections near the seam; blue = base, orange = lid. 264 × 74.2 × 51.2 mm shell; closure stays outside storage.',17)
    kinds=design.KINDS
    for i,kind in enumerate(kinds):
        x0=400*i;p=design.build(kind)
        label(items,x0+20,133,('A — compact M3 pin hinge','B — filament pin hinge','C — removable rear tongues')[i],20)
        xf=lambda v,x0=x0:(x0+200+1.25*v.x,245-1.25*v.y)
        for name,color in (('body',BLUE),('lid',ORANGE)):
            section(items,p[name].val(),'XY',(0,0,D.seam-1),xf,color)
        label(items,x0+20,344,('7.6 mm barrel / 7.9 mm rear projection','5.2 mm barrel / 5.5 mm rear projection','4.3 mm rear projection; no axle')[i],16)
        label(items,x0+20,384,('Two M3 × 12 screws + four jam nuts.','Cut filament pins; pin walkout unresolved.','Drop-in locators do not capture rear lift.')[i],16)
        label(items,x0+20,424,('Selected: captive lid, available hardware.','Smaller, but less defensible retention.','Rejected in this form: rear can peel up.')[i],16)
        label(items,x0+20,464,'Shared front: pull loop outward, then lift.',16)
    label(items,25,540,'Reference sunglasses hinge: 11.2 mm barrel, 20 mm axial modules, about 14.32 mm rear projection.',19)
    label(items,25,583,'Selected A reduces rear projection about 45%; each module is 7 mm wide. Pins replace bulky conical bearing ears.',18)
    label(items,25,626,'The whole lid remains attached. Broad access replaces the long cap sleeve; storage has no inward latch guards.',18)
    label(items,25,672,'A and B pass sampled shell rotation. B pin retention and C rear capture are unresolved; neither is a print recommendation.',17)
    label(items,25,716,'Prototypes are unprinted. E supplies a proven closure principle, not proof of the new short flexure or hinge.',17)
    save('connections',items)

    items=canvas('Shorten the front loop without turning it into another force-open snap',920)
    label(items,25,78,'Actual YZ leaf sections at X7.5. Same placement against the 51.2 mm case roof; the short loop changes root position and thickness.',16)
    clip=base.box(0,-40,34,22,20,46).val()
    for i,kind in enumerate(('accepted_e','short')):
        x0=400*i
        xf=lambda v,x0=x0:(x0+65+17*(-v.y-33),120+9*(57-v.z))
        loop=design.front_parts(kind)[2]
        p=design.build('screw_pin')
        section(items,p['shell_lid'].val().intersect(clip),'YZ',(7.5,0,0),xf,'#b4bfc9',.65)
        section(items,loop.val().intersect(clip),'YZ',(7.5,0,0),xf,BLUE if kind=='short' else ORANGE)
        yy=120+9*(57-D.length)
        items.append(f'<path d="M{x0+25},{yy} H{x0+365}" stroke="{RED}" stroke-dasharray="6 4"/>')
        label(items,x0+25,535,'E: root-to-upper-rail 27.5 mm / 2.8 mm thick' if i==0 else 'Short: root-to-upper-rail 20 mm / 1.8 mm thick',16)
        label(items,x0+25,567,'Unchanged copy extends 2.9 mm above roof.' if i==0 else 'Root fits 4.75 mm below the roof.',16)
    p=design.build('screw_pin')
    x0=800
    xf=lambda v:(x0+35+17*(-v.y-33),120+13*(30-v.z))
    c=base.box(0,-40,22,12,20,20).val()
    section(items,p['keeper'].val().intersect(c),'YZ',(0,0,0),xf,ORANGE)
    section(items,p['loop'].val().intersect(c),'YZ',(0,0,0),xf,BLUE)
    section(items,p['loop'].val().translate((0,-3.5,0)).intersect(c),'YZ',(0,0,0),xf,BLUE,.25)
    label(items,x0+25,535,'Rail section: solid = seated; pale = released.',16)
    label(items,x0+25,567,'Pull outward 3.2 mm before lifting.',17)
    label(items,25,636,'Keeper and radial capture stay the same; axial gap is .35 mm. Shorter leaves are thinner for release.',18)
    label(items,25,685,'Nominal end-load screen: about 69% of E actuation force. Rail/root coupling is uncertain; strain is higher.',18)
    label(items,25,728,'These are provisional comparisons, not measured PETG properties, fatigue acceptance or holding-force predictions.',17)
    label(items,25,773,'Print the matching small front-wall crop first. Check engage/release effort, recovery, whitening and noise; full box is unprinted.',17)
    label(items,25,819,'Closing method: hold loop outward, lower lid onto its rims, then release the loop. Avoid forcing it over the keeper.',17)
    label(items,25,868,'Rounded loop roots and keeper geometry are retained. The new flexure and 2 mm supporting walls still need the physical trial.',17)
    save('short_loop',items)


if __name__=='__main__':draw()
