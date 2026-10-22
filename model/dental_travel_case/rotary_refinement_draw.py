"""Schematics plus actual sections for the cap-inverted rotary exploration."""
from pathlib import Path
import html
import cairosvg
import m1_design as base
from rotary_refinement_design import build,rotor_pose
from closure_research_drawings import canvas,label,section

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'renders/concepts/rotary_refinement'
BLUE='#357b9b';CAP='#c4d0d1';GREEN='#436c60';METAL='#bf8e46'


def save(name,items):
    items.append('</svg>');p=OUT/(name+'.svg');p.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(p),write_to=str(p.with_suffix('.png')))


def rect(items,x,y,w,h,r,fill,stroke='#384e55'):
    items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')


def circle(items,x,y,r,fill):
    items.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#384e55" stroke-width="1.5"/>')


def comparison(p):
    a=canvas('A cleaner rotary closure — production orientation first',990)
    label(a,25,76,'Front schematics at common scale. Same 75.8 × 52.8 × 264 mm shell; no wrap bands.',17)
    for i,(title,kind) in enumerate((('A · rounded exposed paddle','paddle'),('B · covered wheel — preferred','wheel'),('C · fixed outer housing','housing'))):
        x=200+i*400;scale=1.5;bottom=555;pivot=bottom-172*scale
        label(a,x-175,119,title,20)
        rect(a,x-75.8*scale/2,bottom-174*scale,75.8*scale,174*scale,8,'#e0e7e5')
        rect(a,x-75.8*scale/2,bottom-264*scale,75.8*scale,87*scale,8,'#e0e7e5')
        if kind=='housing':
            rect(a,x-21*scale,pivot-23*scale,42*scale,43*scale,18,'#abbabc')
            circle(a,x,pivot,9*scale,'#36545a')
        elif kind=='wheel':
            xf=lambda v,x=x:(x+scale*v.x,bottom-scale*v.z)
            section(a,p['rotor'].val(),'XZ',(0,-31.,0),xf,'#36545a')
        else:
            circle(a,x,pivot-9.75*scale,2.75*scale,METAL)
            rect(a,x-4.5*scale,pivot-16.5*scale,9*scale,21*scale,5,GREEN)
            circle(a,x,pivot,6*scale,GREEN)
        circle(a,x,pivot,2.75*scale,'#aab2b2')
        captions={
            'paddle':['Smallest visible control.', 'Screw-head keeper is exposed.', '3 printed + 2 screws + 3 nuts.', 'No cover; less unified when open.'],
            'wheel':['One Ø34 mm curved outline.', 'Nose / keeper hidden when closed.', '3 printed + 2 screws + 3 nuts.', '6.3 mm maximum nominal projection.'],
            'housing':['Hides the moving outline too.', 'At least 4 printed parts.', 'Cover mounting still unresolved.', 'Adds bulk for little extra benefit.']}
        for j,t in enumerate(captions[kind]):label(a,x-175,603+j*31,t,17)
    label(a,25,770,'B changes the mechanism, rather than putting a large guard around the old window.',21)
    label(a,25,811,'A stock M3 screw head is the cap keeper. The nose turns outside the shell; the cap needs no large cutout.',18)
    label(a,25,847,'Body prints bottom-down. Cap prints closed-top-down. Wheel prints flat-face-down; hardware installs afterward.',18)
    label(a,25,883,'Two broad perimeter scoops give turning purchase and a visible quarter-turn indication; feel is not yet tested.',17)
    label(a,25,927,'Rough concepts only. B has CAD motion and manufacturing-study evidence; no new full-case print is recommended.',17)
    label(a,25,960,'C is screened out for added envelope/assembly. Existing R1a print remains the action experiment.',17)
    save('comparison',a)


def mechanism(p):
    d=p['dimensions'];z=d.pivot
    a=canvas('B · screw-head keeper + a wheel that conceals its inward nose',1010)
    label(a,25,77,'Actual CAD sections. Blue body · grey cap · green rotor · gold nominal M3 hardware. Same-material role colours.',16)
    clip=base.box(0,-28, z+4,42,8,38).val()
    for i,(angle,title) in enumerate(((0,'LOCK · nose above screw head'),(90,'OPEN · nose swings sideways'))):
        x0=600*i;label(a,x0+25,120,title,21)
        xf=lambda v,x0=x0:(x0+285+8*v.x,180+8*(z+20-v.z))
        for name,color,shape in (('body',BLUE,p['body']),('cap',CAP,p['cap']),
                                 ('rotor',GREEN,rotor_pose(p,angle)),('keeper',METAL,p['keeper_screw'])):
            section(a,shape.val().intersect(clip),'XZ',(0,-27.7,0),xf,color)
        label(a,x0+25,438,'Section through the nose/head; wheel face lies in front of this plane.',15)
    label(a,25,494,'Side section · all retention motion is outside the unbroken cap wall',21)
    clip=base.box(0,-25,z+5,2,24,34).val()
    xf=lambda v:(40+14*(-v.y-14),550+9*(z+20-v.z))
    for name,color in (('body',BLUE),('cap',CAP),('rotor',GREEN),('keeper_screw',METAL),('keeper_nut',METAL)):
        section(a,p[name].val().intersect(clip),'YZ',(0,0,0),xf,color)
    for j,t in enumerate([
        'The metal head replaces the upside-down printed keeper lip.',
        'The cap has only a small screw bore; no exposed gabled aperture.',
        'Nominal radial capture clearance stays 0.8 mm. No draw-down cam.',
        'Cap screw: M3×10 + nut. Pivot: M3×12 + two jam nuts.',
        'The screw/nut travel in a 10.4 mm open-ended sleeve track.',
        'The full shell size stays unchanged; body loading is checked separately.',
        'The wheel hides the journal and stop track; no wraparound guard.']):label(a,430,548+j*35,t,17)
    label(a,25,930,'Missing physical qualification: real screw-head size, indexing, turning feel, printed strength, peel and loaded handling.',17)
    label(a,25,970,'Do not treat capture overlap or the clean exterior as a measured holding force or accidental-opening guarantee.',17)
    save('mechanism',a)


def manufacture(p):
    d=p['dimensions'];a=canvas('B · the actual closed-end-down print arrangement',890)
    label(a,25,77,'Actual CAD sections, no metal hardware. These are diagnostic manufacturing studies, not released print files.',17)
    body=p['body'].val();cap=p['cap'].val().rotate((0,0,0),(1,0,0),180).translate((100,0,d.length))
    wheel=p['rotor'].val().rotate((0,0,0),(1,0,0),90).translate((50,80+d.pivot,d.wheel_front))
    xf=lambda v:(210+3*v.y,680-2.5*v.z)
    section(a,body,'YZ',(0,0,0),xf,BLUE)
    xf=lambda v:(625+3*v.y,680-2.5*v.z)
    section(a,cap,'YZ',(100,0,0),xf,CAP)
    a.append('<path d="M90 684 H330 M505 684 H745" stroke="#333" stroke-width="4"/>')
    label(a,90,123,'Body · bottom on bed',21);label(a,90,724,'204 mm high · floor is present',17)
    label(a,505,424,'Cap · closed top on bed',21);label(a,505,724,'87 mm high · roof is present',17)
    label(a,790,180,'Wheel · outer flat face on bed',20)
    xf=lambda v:(980+11*(v.y-80),430-18*v.z)
    section(a,wheel,'YZ',(50,0,0),xf,GREEN)
    a.append('<rect x="956" y="398" width="48" height="31" fill="#d6ad63" fill-opacity=".7"/>')
    a.append('<path d="M795 434 H1180" stroke="#333" stroke-width="4"/>')
    label(a,790,478,'5.6 mm total build height',17)
    label(a,790,509,'Nose grows from the face plate.',17)
    label(a,790,540,'Counterbore and rear stop slot',17)
    label(a,790,569,'are reviewed in the actual slice.',17)
    label(a,790,612,'Amber: support location, schematic.',15)
    label(a,790,640,'Accessible via outside screw recess.',15)
    label(a,25,795,'Keeper screw installs after printing. Removing the plastic keeper eliminates its orientation-dependent island.',18)
    label(a,25,838,'Both shells retain 3 mm end rounds, 2 mm floor/roof, 30 mm sleeve, and a 3 mm reveal on corner seats.',17)
    label(a,25,875,'No detent or strength qualification is implied. Final profile-specific support outcome is recorded in the notes.',17)
    save('manufacture',a)


def main():
    OUT.mkdir(parents=True,exist_ok=True);p=build('wheel')
    comparison(p);mechanism(p);manufacture(p)
    print(OUT)


if __name__=='__main__':main()
