"""Generate editable SVG connector proposals and PNG previews; no printable CAD.

Run from repository root with ./execute.py model/double_ended_connector/draw_concepts.py.
"""
from html import escape
from pathlib import Path
from textwrap import wrap
import cairosvg

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'renders/concepts'
NAVY='#263d53'; TEAL='#138c83'; ORANGE='#cb7629'; GRAY='#aebbc7'
INK='#203247'; MUTED='#53677b'; BG='#f2f5f9'; BORDER='#d7e0e8'


def txt(x,y,value,size=18,fill=INK,weight='normal',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'


def lines(x,y,values,size=17,step=25,fill=MUTED):
    return ''.join(txt(x,y+i*step,s,size,fill) for i,s in enumerate(values))


def rect(x,y,w,h,fill='white',stroke=BORDER,r=10,sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def arrow(x1,y1,x2,y2,color=ORANGE,dash=False):
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="2" marker-end="url(#arrow)"'+(' stroke-dasharray="5 4"' if dash else '')+'/>'


def leader(x1,y1,x2,y2,label):
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{MUTED}" stroke-width="1.3"/>'+txt(x2+5,y2+4,label,15)


def svg_start(title,subtitle,height=1100):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}">
<title>{escape(title)}</title><desc>{escape(subtitle)}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="{ORANGE}"/></marker>
<pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M-2 2 L2 -2 M0 8 L8 0 M6 10 L10 6" stroke="#b7c4cf" stroke-width="1"/></pattern></defs>
<rect width="1600" height="{height}" fill="{BG}"/><g font-family="DejaVu Sans,Arial,sans-serif">'''+txt(38,49,title,30,INK,'bold')+txt(38,81,subtitle,17,MUTED)


def end_svg():return '</g></svg>\n'


C_PATH='M9 -14 Q9 -20 3 -20 H-3 Q-9 -20 -9 -14 V-8 Q-9 -2 -3 -2 H3 Q9 -2 9 -8 H5.8 V-8.4 Q5.8 -5.2 2.6 -5.2 H-2.6 Q-5.8 -5.2 -5.8 -8.4 V-13.6 Q-5.8 -16.8 -2.6 -16.8 H2.6 Q5.8 -16.8 5.8 -13.6 V-14 Z'


def c_frame():
    return f'<path d="{C_PATH}" fill="{NAVY}"/><path d="{C_PATH}" transform="scale(1,-1)" fill="{NAVY}"/>'+rect(-3,-4,6,8,NAVY,NAVY,r=0,sw=0)


def references(top=-25,bottom=25):
    # Gray is existing cord/key ring, shown edge-on schematically, not another part.
    return (f'<path d="M-5 {top-10} L-5 {top+5} Q0 {top+12} 5 {top+5} L5 {top-10}" fill="none" stroke="{GRAY}" stroke-width="2.6"/>'
            f'<ellipse cx="0" cy="{bottom-4}" rx="5" ry="10" fill="none" stroke="{GRAY}" stroke-width="2"/>')


def screw_pin(x,y,open_state=False):
    dx=-12 if open_state else 0
    return f'<g transform="translate({x+dx},{y})">'+rect(-5.3,-1.3,12,2.6,ORANGE,ORANGE,r=.3,sw=.15)+rect(-7.5,-2.4,2.2,4.8,ORANGE,ORANGE,r=.4,sw=.15)+f'<path d="M-7.5 0 H-5.3" stroke="white" stroke-width=".4"/>'+''.join(f'<path d="M{q} -1.25 l-.6 2.5" stroke="white" stroke-width=".28"/>' for q in (3.2,4,4.8,5.6))+'</g>'


def a_icon(x,y,scale=5,upper_open=False,refs=True):
    s=f'<g transform="translate({x},{y}) scale({scale})">'
    if refs:s+=references(-21,21)
    for flip in (1,-1):
        s+=f'<g transform="scale(1,{flip})">'
        s+=f'<path d="M-4.3 -13 V-8 Q-4.3 -3 0 -3 Q4.3 -3 4.3 -8 V-13" fill="none" stroke="{NAVY}" stroke-width="3.1" stroke-linecap="butt"/>'
        s+=rect(-5.25,-15.75,2.5,5.5,NAVY,NAVY,r=.45,sw=0)
        s+=rect(2.75,-16.7,4.0,7.4,NAVY,NAVY,r=.6,sw=0)
        s+=f'<path d="M3.15 -14.6 l1.4 -.8 1.4 .8 v1.6 l-1.4 .8 -1.4 -.8 Z" fill="{ORANGE}" stroke="white" stroke-width=".2"/>'
        s+=screw_pin(0,-13,upper_open and flip==1)+'</g>'
    s+=rect(-2,-5,4,10,NAVY,NAVY,r=1,sw=0)
    s+='</g>'
    if upper_open:
        s+=arrow(x-36*scale/5,y-65*scale/5,x-91*scale/5,y-65*scale/5)
    return s


def keeper(cx,cy):
    return f'<circle cx="{cx}" cy="{cy}" r="3.4" fill="{ORANGE}" stroke="white" stroke-width=".25"/><path d="M{cx-1.7} {cy} H{cx+1.7}" stroke="white" stroke-width=".45"/>'


def b_icon(x,y,scale=5,upper_open=False,refs=True):
    s=f'<g transform="translate({x},{y}) scale({scale})">'
    if refs:s+=references()
    s+=c_frame()
    for flip in (1,-1):
        s+=f'<g transform="scale(1,{flip})">'
        # Central guide is deliberately larger than the slim free horn.
        s+=rect(0,-8.7,9.7,7.8,NAVY,NAVY,r=1,sw=0)
        s+=rect(4.3,-17,5.5,3.2,NAVY,NAVY,r=.6,sw=0)
        delta=2.2 if upper_open and flip==1 else 0
        offset=14 if upper_open and flip==1 else 0
        s+=f'<g transform="translate({offset},{delta})">'
        s+=rect(5.8,-16,3.2,11.8,TEAL,'white',r=.35,sw=.18)
        s+=rect(.6,-8.1,7.9,6.8,TEAL,'white',r=1,sw=.18)
        if not (upper_open and flip==1):s+=keeper(4.5,-4.7)
        else:s+=f'<circle cx="4.5" cy="-4.7" r="1.5" fill="white"/>'
        s+='</g></g>'
    s+='</g>'
    if upper_open:
        s+=arrow(x+7.4*scale,y-15*scale,x+7.4*scale,y-12.8*scale)
        s+=f'<circle cx="{x+19*scale}" cy="{y-23*scale}" r="{2.5*scale}" fill="{ORANGE}"/>'
        s+=txt(x+19*scale,y-23*scale+4,'1',13,'white','bold','middle')
    return s


def c_icon(x,y,scale=5,upper_open=False,refs=True):
    s=f'<g transform="translate({x},{y}) scale({scale})">'
    if refs:s+=references()
    s+=c_frame()
    for flip in (1,-1):
        s+=f'<g transform="scale(1,{flip})">'
        s+=rect(-4.5,-10,14.5,9.2,NAVY,NAVY,r=1.2,sw=0)
        s+=rect(4.3,-17,5.5,3.2,NAVY,NAVY,r=.6,sw=0)
        rot=70 if upper_open and flip==1 else 0
        s+=f'<g transform="rotate({rot},7.4,-7.4)">'
        s+=rect(5.8,-16,3.2,10,TEAL,'white',r=.5,sw=.18)
        s+=rect(-4.2,-8.8,13.5,4.8,TEAL,'white',r=1,sw=.18)
        if not (upper_open and flip==1):s+=keeper(-.5,-6.4)
        else:s+=f'<circle cx="-.5" cy="-6.4" r="1.3" fill="white"/>'
        s+='</g>'
        s+=f'<circle cx="7.4" cy="-7.4" r="1.35" fill="{ORANGE}" stroke="white" stroke-width=".2"/>'
        s+='</g>'
    s+='</g>'
    if upper_open:s+=f'<path d="M{x+35} {y-91} Q{x+100} {y-95} {x+105} {y-40}" fill="none" stroke="{ORANGE}" stroke-width="2" marker-end="url(#arrow)"/>'
    return s


OPTIONS=[
 dict(key='A',name='Screw-pin shackles',size='~35 × 16 × 7 mm',count='1 printed body + 4 stock metal parts',
      icon=a_icon,file='a_screw_pin',tag='Compact hardware option',
      benefit=['Each screw is the gate across an open U-eye.','Use an existing M3 screw and nut at each end.','Remove one pin; lift that loop off the slim horn.'],
      trade=['Needs a tool; each removed pin is a loose part.','Metal threads avoid small printed screw threads.']),
 dict(key='B',name='Sliding gates + keeper screws',size='~42 × 20 × 9 mm',count='5 printed parts; no metal or springs',
      icon=b_icon,file='b_sliding_gates',tag='Recommended all-printed starting point',
      benefit=['A straight gate seats in the opposite horn.','A separate screw indexes the gate in its guide.','Remove keeper, retract gate, then lift it out.'],
      trade=['Three deliberate actions; two loose pieces per end.','Guide clearance and printed threads need a trial.']),
 dict(key='C',name='Hinged gates + screw latches',size='~44 × 20 × 10 mm',count='7 printed parts; no metal or springs',
      icon=c_icon,file='c_hinged_gates',tag='Gate stays attached',
      benefit=['A rigid hinged gate seats into the opposite horn.','A screw through the gate heel blocks rotation.','Remove latch screw, swing gate outward; no flexing.'],
      trade=['More parts and hinge wear to qualify.','Gate needs temporary clearance while opening.']),
]


def overview():
    s=svg_start('A connector that opens at either end',
        'SVG proposals for PLA or PETG • independent closures • no spring, snap flexure or press-fit retention',1080)
    for i,o in enumerate(OPTIONS):
        x=28+i*520
        s+=rect(x,105,504,880,stroke=TEAL if i==1 else BORDER,sw=2 if i==1 else 1)
        s+=txt(x+22,143,o['key']+'  '+o['name'],21,INK,'bold')
        s+=txt(x+22,174,o['tag'],15,TEAL if i==1 else MUTED,'bold')
        s+=o['icon'](x+252,372,5.0)
        s+=txt(x+252,606,o['size'],18,INK,'bold','middle')
        s+=txt(x+252,635,o['count'],16,MUTED,'normal','middle')
        s+=lines(x+22,682,o['benefit'],15,27)
        s+=f'<path d="M{x+22} 770 H{x+480}" stroke="{BORDER}"/>'
        s+=lines(x+22,803,o['trade'],15,27)
        s+=txt(x+22,886,'Open either end without rotating the attached loop.',14,INK)
        s+=txt(x+22,917,'Detailed opening / lock / print views in '+o['key']+'.',14,MUTED)
        s+=txt(x+22,954,'Schematic views; dimensions are design targets.',12,MUTED)
    s+=txt(38,1018,'Color key: navy = rigid body; teal = moving gate; orange = fastener (metal in A, printed in B/C); gray = existing loops.',14,MUTED)
    s+=txt(38,1045,'Generic fit target: 3.2 mm cord, key-ring wire up to 3 mm, ~6 mm loading gap. Concepts only; no load or print qualification.',14,MUTED)
    return s+end_svg()


def lock_detail(o,x,y):
    s=''
    if o['key']=='A':
        s+=txt(x,y,'Section along a screw-pin axis',18,INK,'bold')
        s+=rect(x+10,y+48,55,62,NAVY,NAVY,r=3,sw=0)
        s+=rect(x+205,y+48,80,62,NAVY,NAVY,r=3,sw=0)
        s+=rect(x-15,y+65,285,26,ORANGE,ORANGE,r=3,sw=0)
        s+=rect(x-35,y+54,20,48,ORANGE,ORANGE,r=3,sw=0)
        s+=rect(x+224,y+52,40,54,ORANGE,'white',r=2,sw=2)
        s+=txt(x+128,y+143,'5.5 mm clear loading gap',15,INK,'normal','middle')
        s+=arrow(x+68,y+125,x+203,y+125)
        s+=leader(x+40,y+47,x+5,y+22,'slim horn')
        s+=leader(x+245,y+111,x+225,y+174,'nut pocket')
        s+=lines(x,y+210,['Threaded metal capture closes the opening.','The nut is trapped against rotation in the body.','No elastic gate or friction-fit clip is required.'],15,25)
    elif o['key']=='B':
        s+=txt(x,y,'Positive lock through the gate tail',18,INK,'bold')
        s+=rect(x+6,y+42,286,105,NAVY,NAVY,r=8,sw=0)
        s+=rect(x+27,y+49,242,34,TEAL,'white',r=2,sw=2)
        s+=rect(x+133,y+21,31,110,ORANGE,ORANGE,r=2,sw=0)
        s+=rect(x+108,y+4,82,22,ORANGE,ORANGE,r=6,sw=0)
        s+=f'<path d="M{x+136} {y+85} l25 12 m-25 0 l25 12 m-25 0 l25 12" stroke="white" stroke-width="2"/>'
        s+=arrow(x+44,y+176,x+250,y+176)
        s+=txt(x+148,y+203,'Gate cannot slide while the screw crosses it.',14,INK,'normal','middle')
        s+=lines(x,y+240,['Screw enters a closed hole in the moving gate.','Clamping pressure is not the retaining feature.','Seat the nose ~2 mm into the opposite horn.'],15,25)
    else:
        s+=txt(x,y,'Heel index + seated gate nose',18,INK,'bold')
        s+=rect(x+15,y+48,282,90,NAVY,NAVY,r=8,sw=0)
        s+=rect(x+22,y+55,263,28,TEAL,'white',r=3,sw=2)
        s+=f'<circle cx="{x+75}" cy="{y+69}" r="17" fill="{ORANGE}" stroke="white" stroke-width="2"/>'
        s+=f'<circle cx="{x+146}" cy="{y+69}" r="19" fill="{ORANGE}" stroke="white" stroke-width="2"/>'
        s+=rect(x+262,y+34,44,72,NAVY,'white',r=2,sw=2)
        s+=leader(x+75,y+86,x+25,y+183,'index screw')
        s+=leader(x+146,y+88,x+135,y+211,'hinge pin')
        s+=lines(x,y+248,['Gate tongue bears against a rigid horn pocket.','A screw through the heel blocks rotation.','Hinge allows movement only after unlocking.'],15,25)
    return s


def printing(o,x,y):
    s=txt(x,y,'How the whole concept prints and assembles',21,INK,'bold')
    s+=rect(x,y+24,630,232,'#f6f9fb',BORDER,r=8)
    # Schematic plate with every primary part counted.
    s+=rect(x+18,y+42,310,184,'white','#a9bac8',r=7)
    if o['key']=='A':
        s+=a_icon(x+117,y+135,3.3,refs=False)
        s+=txt(x+200,y+89,'1 body',15,INK,'bold')
        s+=txt(x+200,y+114,'flat on bed',14,MUTED)
        detail=['Printed: one body, large face down.','Add 2 × M3×12 screws + 2 × M3 nuts.','Seat each nut in an accessible anti-turn pocket.','No bought spring or printed tool is needed.']
    else:
        s+=rect(x+56,y+68,60,120,NAVY,NAVY,r=15,sw=0)
        s+=rect(x+69,y+79,34,39,'white','white',r=10,sw=0)
        s+=rect(x+69,y+138,34,39,'white','white',r=10,sw=0)
        s+=txt(x+32,y+239,'1 body: flat face down',12,MUTED)
        for j in range(2):
            s+=rect(x+153+j*48,y+75,19,67,TEAL,TEAL,r=4,sw=0)
            s+=rect(x+147+j*48,y+132,31,22,TEAL,TEAL,r=4,sw=0)
        s+=txt(x+144,y+179,'2 gates: flat',12,MUTED)
        n=2 if o['key']=='B' else 4
        for j in range(n):
            xx=x+155+j*30
            s+=rect(xx,y+199,19,9,ORANGE,ORANGE,r=3,sw=0)+rect(xx+6,y+187,7,12,ORANGE,ORANGE,r=1,sw=0)
        s+=txt(x+350,y+61,f'{n} printed fasteners',15,INK,'bold')
        s+=txt(x+350,y+87,'head on bed, shaft upright',14,MUTED)
        detail=(['5 printed parts: body, 2 gates, 2 keepers.','Print gates on a broad face; use solid gate bars.','Insert each gate, then install its keeper screw.','Coarse custom threads; no metal nut required.'] if o['key']=='B' else
                ['7 printed parts: body, 2 gates, 2 hinge pins,','and 2 latch screws. Assemble gates onto pins,','Pins enter from back; latch screws enter from front.','Coarse printed threads; hinge wear needs a trial.'])
    s+=lines(x+18,y+291,detail,16,27)
    s+=txt(x+18,y+420,'PLA or PETG • 0.4 mm nozzle / 0.2 mm layers assumed',15,INK,'bold')
    s+=txt(x+18,y+448,'No spring, live hinge, snap flexure or press-fit retention.',15,MUTED)
    return s


def detail(o):
    s=svg_start(o['key']+'  '+o['name'],o['tag']+' • '+o['size']+' proposed assembled envelope • '+o['count'],1260)
    s+=rect(28,105,760,543)+rect(808,105,764,543)
    s+=txt(52,142,'1  Locked on both ends',22,INK,'bold')
    s+=o['icon'](244,341,5.4)
    s+=txt(75,595,'Gray: existing cord loop above and key ring below.',15,MUTED)
    s+=txt(75,622,'Only the connector parts are newly made.',15,MUTED)
    s+=lock_detail(o,440,188)
    s+=txt(832,142,'2  Open only the upper end',22,INK,'bold')
    s+=o['icon'](1040,343,5.4,upper_open=True)
    if o['key']=='A':
        steps=['a. Unscrew the upper pin from its trapped nut.','b. Withdraw pin sideways; pass the loop off the horn.','c. Replace pin and fully engage its nut to close.']
    elif o['key']=='B':
        steps=['a. Withdraw only the upper keeper screw.','b. Retract 2.2 mm, then lift gate toward you (shown offset).','c. Insert loop; seat gate nose and reinstall keeper.']
    else:
        steps=['a. Remove only the upper heel-index screw.','b. Swing the upper gate outward about 70°.','c. Reseat tongue; reinstall the index screw.']
    s+=lines(1210,228,[line for step in steps for line in wrap(step,42)+['']],14,22)
    s+=txt(1210,442,'The lower closure is untouched.',14,TEAL,'bold')
    s+=txt(1210,473,'Move the gate, not the attached ring.',15,INK)
    s+=txt(832,595,'Orange arrows show the user motion; these gates do not self-close.',15,MUTED)
    s+=txt(832,622,'Small free horns target the existing ~7.6 mm cord-loop bore.',15,MUTED)
    s+=rect(28,672,760,520)+rect(808,672,764,520)
    s+=printing(o,52,713)
    s+=txt(832,714,'Why it stays closed / what still needs testing',21,INK,'bold')
    keep=(['The screw pin physically bridges each mouth.','Metal thread engagement captures the pin; the nut','cannot spin inside its shaped pocket. A standard tool','is needed. There is no independent anti-loosening latch.'],
          ['Each gate is supported by a guide and an opposite','socket. The keeper crosses a closed indexing hole,','so loss of clamp pressure alone does not free the gate.','Remove keeper, retract nose, then lift gate out.'],
          ['A tongue/socket seat supports the closed gate.','The heel screw passes through an indexing hole and','prevents hinge rotation. The hinge pin and index screw','are separate; no resilient gate return is required.'])['ABC'.index(o['key'])]
    s+=lines(832,759,keep,17,28)
    s+=txt(832,914,'Next qualification, if selected',18,INK,'bold')
    s+=lines(832,948,['Confirm horn-to-loop entry and gate/socket fit.','Check both closed ends under pull, twist and shaking.','Check thread back-out, wear and finger access.','Proposed geometry has no measured load rating.'],16,28)
    s+=txt(38,1220,'Concept drawing only: dimensions, fits, threads and strength are not CAD-, slicer- or print-qualified.',15,MUTED)
    return s+end_svg()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    drawings={'connector_options':overview()}
    drawings.update({o['file']:detail(o) for o in OPTIONS})
    for name,svg in drawings.items():
        path=OUT/f'{name}.svg'
        path.write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(path.with_suffix('.png')))
        print(path.relative_to(ROOT))


if __name__=='__main__':main()
