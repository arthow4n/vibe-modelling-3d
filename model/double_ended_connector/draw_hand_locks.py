"""R2 all-printed, hand-operated connector concepts; deliberately schematic.

Run with ./execute.py model/double_ended_connector/draw_hand_locks.py.
Existing R1 drawings remain historical. No CAD or printable geometry is generated.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import cairosvg
from draw_concepts import (txt, lines, rect, arrow, svg_start, end_svg,
                           c_frame, references, NAVY, TEAL, ORANGE, MUTED, INK, BORDER)

OUT = Path(__file__).resolve().parent / 'renders/hand_locks'
OPTIONS = [
    dict(key='D', title='Threaded barrel gate', file='d_barrel_gate',
         size='~44 × 22 × 10 mm', parts='5 printed parts proposed',
         tag='Recommended: simplest daily operation',
         steps=['1  Turn the barrel several turns downward.',
                '2  Lift the loop through the exposed mouth.',
                '3  Turn upward until the nose is covered.'],
         hold=['The barrel bridges the mouth and cups the nose.',
               'Coarse thread engagement prevents direct sliding.',
               'No hinge, spring or removable operating part.'],
         risk=['Repeated unscrewing is needed to uncover the gap.',
               'Rubbing could still unwind it: test this physically.']),
    dict(key='E', title='Captive screw-driven bolt', file='e_retracting_bolt',
         size='~48 × 24 × 11 mm', parts='8 printed parts proposed',
         tag='Positive translation; everything stays attached',
         steps=['1  Roll the recessed thumbwheel to retract.',
                '2  Pass the loop through the clear mouth.',
                '3  Reverse until the bolt seats in its socket.'],
         hold=['A guided rigid bolt bridges the mouth.',
               'A captive lead screw drives it into a receiver.',
               'The guide prevents bolt rotation; no snap catch.'],
         risk=['More turns and a longer central housing.',
               'Thread back-drive and grit sensitivity need a test.']),
    dict(key='F', title='Rotary gate + index lock', file='f_rotary_index',
         size='~46 × 24 × 11 mm', parts='8 printed parts proposed',
         tag='Two different motions to release',
         steps=['1  Back out the captive thumb lock ~2 turns.',
                '2  Rotate the gate 90° to uncover the mouth.',
                '3  Rotate closed; advance the lock into its hole.'],
         hold=['A rigid sector sweeps across the opening.',
               'A screw tip enters a hole in that sector.',
               'The tip blocks rotation, rather than clamping.'],
         risk=['Two deliberate controls; wider cheek housing.',
               'Both lock engagement and wear need a test.']),
]


def threads(x, y, w, h, spacing=1.2):
    return ''.join(f'<path d="M{x+i*spacing} {y} l-0.6 {h}" stroke="white" stroke-width=".22"/>'
                   for i in range(int(w/spacing)+1))


def icon(key, x, y, scale=6, opened=False):
    s=f'<g transform="translate({x},{y}) scale({scale})">'+references()+c_frame()
    for flip in (1,-1):
        is_open=opened and flip==1
        s+=f'<g transform="scale(1,{flip})">'
        if key=='D':
            # Sleeve moves axially down onto threaded stem, off the upper nose.
            s+=rect(5.7,-9.5,3.4,10,NAVY,NAVY,r=.3,sw=0)
            shift=7 if is_open else 0
            s+=rect(4.5,-16+shift,6,11,TEAL,'white',r=.7,sw=.2)
            s+=threads(4.8,-15.5+shift,5.1,9.5)
            s+=rect(6,-17,2.8,2.6,NAVY,NAVY,r=.3,sw=0)
        elif key=='E':
            s+=rect(3,-7,9.5,10,NAVY,NAVY,r=1,sw=0)
            shift=7 if is_open else 0
            s+=rect(5.8,-16+shift,3.2,12,TEAL,'white',r=.3,sw=.2)
            s+=rect(4.2,-17,6.5,3,NAVY,NAVY,r=.4,sw=0)
            s+=rect(3.8,-3,7.5,2.8,ORANGE,'white',r=.5,sw=.2)
            s+=''.join(f'<path d="M{q} -2.7 v2.1" stroke="white" stroke-width=".25"/>' for q in [4.6,5.8,7,8.2,9.4,10.6])
        elif key=='F':
            s+=rect(.5,-8.5,11,10,NAVY,NAVY,r=1.4,sw=0)
            angle=90 if is_open else 0
            s+=f'<g transform="rotate({angle},7.4,-6)">'
            s+=rect(5.8,-16,3.2,11.8,TEAL,'white',r=.4,sw=.2)
            s+=rect(5,-8,4.8,7.4,TEAL,'white',r=1.3,sw=.2)
            s+='<circle cx="7.4" cy="-2.5" r=".85" fill="white"/></g>'
            s+=f'<circle cx="7.4" cy="-6" r="1.1" fill="{NAVY}" stroke="white" stroke-width=".2"/>'
            s+=f'<circle cx="7.4" cy="-2.5" r="1.9" fill="{ORANGE}" stroke="white" stroke-width=".2"/>'
        else:
            raise ValueError(key)
        s+='</g>'
    return s+'</g>'


def overview():
    s=svg_start('Hand-openable locks — every connector part printed',
                'R2 SVG concepts • PLA or PETG • either end opens independently • no metal, springs, snap flexure or tools',1040)
    for i,o in enumerate(OPTIONS):
        x=28+i*520
        s+=rect(x,110,504,820,stroke=TEAL if i==0 else BORDER,sw=2)
        s+=txt(x+22,150,o['key']+'  '+o['title'],22,INK,'bold')
        s+=txt(x+22,179,o['tag'],14,TEAL,'bold')
        s+=icon(o['key'],x+235,360,5)
        s+=txt(x+252,550,o['size']+'  •  '+o['parts'],14,INK,'bold','middle')
        s+=lines(x+22,598,o['steps'],15,28)
        s+=lines(x+22,710,o['hold'],15,27)
        s+=lines(x+22,832,o['risk'],14,26)
    s+=txt(38,967,'Navy = body; teal = gate; orange = hand control. All three are printed in the same PLA or PETG. Gray = existing attachments.',15,MUTED)
    s+=txt(38,997,'Schematic concepts, not print files. No shake-resistance, force or load rating has been established; see the detailed lock sections.',15,MUTED)
    return s+end_svg()


def section(key,x,y):
    s=txt(x,y,'Enlarged lock section — one end',21,INK,'bold')
    if key=='D':
        # Vertical longitudinal section. White central void is a real cavity.
        s+=rect(x+100,y+40,44,50,NAVY,NAVY,r=2,sw=0)
        s+=rect(x+100,y+145,44,105,NAVY,NAVY,r=2,sw=0)
        s+=rect(x+74,y+65,96,150,TEAL,TEAL,r=6,sw=0)
        s+=rect(x+89,y+65,66,90,'white','white',r=0,sw=0)
        s+=rect(x+95,y+155,54,60,'white','white',r=0,sw=0)
        s+=rect(x+100,y+65,44,25,NAVY,NAVY,r=0,sw=0)
        s+=rect(x+100,y+145,44,75,NAVY,NAVY,r=0,sw=0)
        s+=rect(x+83,y+240,78,15,NAVY,NAVY,r=2,sw=0)
        for yy in range(153,208,11):
            s+=f'<path d="M{x+95} {y+yy} l10 5 l-10 5 M{x+149} {y+yy} l-10 5 l10 5" fill="{NAVY}"/>'
        s+=rect(x+93,y+140,58,12,ORANGE,ORANGE,r=1,sw=0)
        s+=arrow(x+190,y+100,x+190,y+205)
        s+=lines(x+220,y+65,['Nose seated inside cup','(upper horn, fixed)'],15,23)
        s+=lines(x+220,y+139,['Printed stop tip','installed during assembly'],15,23)
        s+=lines(x+220,y+210,['Coarse mating thread','barrel turns AND travels'],15,23)
        s+=lines(x,y+300,['White center = cavity; barrel walls shown in section.',
                             'Stop tip and base shoulder limit sleeve travel.',
                             'Retracted barrel parks below the ~6 mm mouth.'],16,26)
    elif key=='E':
        s+=rect(x+72,y+48,100,224,NAVY,NAVY,r=7,sw=0)
        s+=rect(x+91,y+40,62,210,'white','white',r=0,sw=0)
        s+=rect(x+98,y+40,48,108,TEAL,TEAL,r=3,sw=0)
        s+=rect(x+113,y+104,18,118,ORANGE,ORANGE,r=1,sw=0)
        for yy in range(110,162,10):
            s+=f'<path d="M{x+110} {y+yy} l24 7" stroke="white" stroke-width="2"/>'
        s+=rect(x+68,y+220,108,28,ORANGE,ORANGE,r=5,sw=0)
        s+=rect(x+109,y+247,26,21,ORANGE,ORANGE,r=1,sw=0)
        s+=arrow(x+190,y+60,x+190,y+134)
        s+=lines(x+220,y+65,['Flat-sided guided bolt','cannot turn with screw'],15,23)
        s+=lines(x+220,y+144,['Thread inside bolt','translates wheel rotation'],15,23)
        s+=lines(x+220,y+228,['Thumbwheel / shoulder','trapped in split bearing'],15,23)
        s+=lines(x,y+300,['White = running clearance; orange screw rotates in place.',
                             'Bolt seats ~2 mm into the opposite horn when closed.',
                             'Captive stops prevent winding bolt out during use.'],16,26)
    else:
        s+=rect(x+55,y+125,242,64,NAVY,NAVY,r=5,sw=0)
        s+=rect(x+74,y+70,206,48,TEAL,TEAL,r=4,sw=0)
        s+=rect(x+94,y+125,47,42,'white','white',r=1,sw=0)
        s+=rect(x+98,y+27,39,131,ORANGE,ORANGE,r=2,sw=0)
        s+=rect(x+75,y+12,85,25,ORANGE,ORANGE,r=5,sw=0)
        s+=rect(x+205,y+57,24,95,NAVY,NAVY,r=1,sw=0)
        s+=rect(x+55,y+41,115,20,NAVY,NAVY,r=1,sw=0)
        s+=rect(x+98,y+41,39,20,ORANGE,ORANGE,r=0,sw=0)
        for yy in [44,51]:
            s+=f'<path d="M{x+98} {y+yy} l39 5" stroke="white" stroke-width="2"/>'
        s+=arrow(x+172,y+47,x+172,y+18)
        s+=lines(x+315,y+45,['Captured screw head','hand-turn to lift tip'],15,23)
        s+=lines(x+315,y+108,['Tip crosses rotor hole','blocks rotation'],15,23)
        s+=lines(x+315,y+177,['Rigid shoulder pivot','rotor between cheeks'],15,23)
        s+=lines(x,y+253,['Section normal to face; white is running clearance.',
                             'Screw tip crosses a rotor hole; it does not clamp.',
                             'A clearance pocket below receives the advanced tip.',
                             'Withdraw tip first, then rotate gate clear of mouth.'],16,26)
    return s


def detail(o):
    key=o['key']
    s=svg_start(key+'  '+o['title'],
                'Hand operation • all connector components printed • no reliance on bending, spring return or friction-fit snaps',1220)
    s+=rect(28,110,760,540)+rect(808,110,764,540)
    s+=txt(52,151,'Both ends closed',22,INK,'bold')+icon(key,190,375,5.7)
    s+=txt(400,151,'Upper end open',22,INK,'bold')+icon(key,540,375,5.7,True)
    if key in ('D','E'):
        s+=arrow(625,285,625,330)
    else:
        s+=f'<path d="M610 280 Q651 280 651 328" fill="none" stroke="{ORANGE}" stroke-width="2" marker-end="url(#arrow)"/>'
    s+=lines(52,583,[o['size']+' • '+o['parts'],
                         'Lower attachment stays closed; neither attached loop is twisted.'],16,26)
    s+=txt(832,151,'Open / close by hand',22,INK,'bold')
    s+=lines(832,205,o['steps'],18,36)
    s+=txt(832,348,'Why it resists a direct pull',20,INK,'bold')
    s+=lines(832,390,o['hold'],17,30)
    s+=txt(832,514,'No loose operating pieces; no tools.',18,TEAL,'bold')
    s+=lines(832,555,o['risk'],16,28)
    s+=rect(28,670,760,480)+rect(808,670,764,480)
    s+=section(key,52,710)
    s+=txt(832,710,'Parts, printing and remaining work',22,INK,'bold')
    assembly={
        'D':['Body + 2 barrels + 2 printed stop tips = 5 parts.',
             'Thread barrels onto stems; install stop tips afterward.',
             'Base shoulders / tips trap each barrel for daily use.'],
        'E':['Body + cover + 2 bolts + 2 lead screws',
             '+ 2 printed cover screws = 8 parts.',
             'Fit bolts and screw shoulders, then close bearing cover.'],
        'F':['Body + cover + 2 rotors + 2 thumb locks',
             '+ 2 printed cover screws = 8 parts.',
             'Trap rotors and reduced-neck locks between cheeks.'],
    }
    s+=lines(832,758,assembly[key],16,27)
    s+=lines(832,868,['Proposed print: body / covers / gates broad face down;',
                         'coarse screws upright; barrels upright with open bore.',
                         'Separate assembly: no print-in-place joint to break free.',
                         'Target ~6 mm mouth; free horn ~3.2 × 4 mm section.',
                         '0.4 mm nozzle / 0.2 mm layers assumed for later CAD.'],16,27)
    s+=lines(832,1030,['Still needed: loading path, travel, capture, tolerances,',
                          'hand clearance, shaking, twisting and wear tests.',
                          'Two hands assumed. These locks do not self-close.'],16,27)
    s+=txt(38,1186,'Section is schematic and enlarged independently. Dimensions, fits, thread lead and assembly retention are not CAD- or print-qualified.',15,MUTED)
    return s+end_svg()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    drawings={'hand_lock_options':overview()}
    drawings.update({o['file']:detail(o) for o in OPTIONS})
    for name,svg in drawings.items():
        ET.fromstring(svg)
        path=OUT/f'{name}.svg'
        path.write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(path.with_suffix('.png')))
        print(path.relative_to(OUT.parent.parent))


if __name__=='__main__':
    main()
