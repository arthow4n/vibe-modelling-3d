"""Discussion-only silhouettes: compact alternatives after rejection of V2.

Dimensions are targets, not CAD, print or stability qualification. SVG is editable.
"""
import math
import json
from pathlib import Path
from html import escape
import cairosvg

OUT = Path(__file__).parent/'renders/concepts'
PHONE_W, PHONE_H, PHONE_T = 85, 170, 13
ANGLE = math.radians(65)
SCALE = 1.55
CONCEPTS = (
    ('A', 'Hooded pedestal', 105, 140,
     'Closest to V1: one rising support, a quiet base.',
     'Support phone → press base button → tilt → release.',
     'Enclosed positive angle lock; no exposed teeth.',
     'Risk: lock torque, play and release effort.'),
    ('B', 'Compact side pivots', 115, 135,
     'Two short side pods; a wide open centre.',
     'Support phone → release side lock → tilt → release.',
     'Short load paths; paired locks need coordinated release.',
     'Risk: wider silhouette and two-sided assembly.'),
    ('C', 'Reseatable cradle', 105, 145,
     'A smooth low wedge; no permanent rotary hinge.',
     'Release clip → lift carrier → insert in another seat.',
     'Three keyed seats carry load; a small clip blocks lift.',
     'Risk: lifting/reseating is less convenient; seat play.'),
)


def rough_screen():
    """Rear tipping only: an explicit mass assumption, not complete stability."""
    answers=[]
    for key,title,width,depth,*_ in CONCEPTS:
        cases=[]
        for angle in (50,65,75):
            theta=math.radians(angle)
            for landscape in (False,True):
                height=PHONE_W if landscape else PHONE_H
                cy=20+height/2*math.cos(theta)-PHONE_T/2*math.sin(theta)
                ty=20+(height-10)*math.cos(theta)-PHONE_T*math.sin(theta)
                tz=55+(height-10)*math.sin(theta)+PHONE_T*math.cos(theta)
                reaction=.30*9.81+2*math.cos(theta)
                moment=.30*9.81*cy+2*math.cos(theta)*ty+2*math.sin(theta)*tz
                rear_limit=depth-8-5
                mass=max(0,(moment-rear_limit*reaction)/(9.81*(rear_limit-depth/2)))
                cases.append(dict(angle_deg=angle,landscape=landscape,
                    assumed_stand_mass_for_rear_margin_kg=mass))
        answers.append(dict(concept=key,target_base_mm=[width,depth],
            maximum_assumed_stand_mass_kg=max(c['assumed_stand_mass_for_rear_margin_kg'] for c in cases),cases=cases))
    report=dict(scope='Illustrative static rear tipping only; not complete contact, sliding, impact or product qualification',
        assumptions=dict(phone_kg=.30,phone_bottom_y_mm=20,phone_bottom_z_mm=55,
            normal_upper_tap_N=2,stand_cg_y='mid-depth',rear_foot_inset_mm=8,rear_margin_mm=5,
            pose_basis='same illustrative lower phone location at all angles; actual hinge travel changes this'),
        limitations='No actual stand mass/CG, desk friction, lock strength or print process established. Sideways taps and opposite force directions not qualified. No ballast purchase or solid-base process agreed.',concepts=answers)
    notes=Path(__file__).parent/'notes';notes.mkdir(exist_ok=True)
    (notes/'compact_proposal_screen.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def draw():
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1440" viewBox="0 0 1440 1440">',
         '<rect width="1440" height="1440" fill="#f5f3ed"/>',
         '<style>text{font-family:DejaVu Sans,sans-serif;fill:#253a35}.title{font-size:32px;font-weight:bold}.head{font-size:25px;font-weight:bold}.body{font-size:17px}.small{font-size:15px}.tiny{font-size:13px}</style>']
    def text(x,y,s,cls='body',**attrs):
        extra=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
        svg.append(f'<text x="{x}" y="{y}" class="{cls}" {extra}>{escape(s)}</text>')
    def path(points,fill='none',stroke='#47786a',width=3,close=False,**attrs):
        d='M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in points)+(' Z' if close else '')
        extra=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
        svg.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" {extra}/>')
    def rect(x,y,w,h,fill,stroke='none',r=0,**attrs):
        extra=' '.join(f'{k.replace("_","-")}="{v}"' for k,v in attrs.items())
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" {extra}/>')
    text(34,48,'Compact phone stand — three directions to discuss','title')
    text(34,80,'Keep V1’s compact visual idea; carry forward V2’s case, ring, cable and hand-adjustment requirements.')
    text(34,110,'Same scale and 85 × 170 × 13 mm phone. Shown at 65°. Candidate angles: 50° / 65° / 75°.')
    text(34,138,'Footprints are targets. Locks, accessory clearance, assembly and tapping stability remain unqualified.','small')
    for index,(key,title,w,depth,intro,action,mechanism,risk) in enumerate(CONCEPTS):
        x=24+index*472
        rect(x,166,448,777,'#ffffff',r=16)
        text(x+20,205,f'{key}  {title}','head')
        text(x+20,235,intro,'small')
        ox,ground=x+62,630
        def world(y,z):return ox+SCALE*y,ground-SCALE*z
        def local(u,v):
            return world(20+u*math.cos(ANGLE)-v*math.sin(ANGLE),
                         55+u*math.sin(ANGLE)+v*math.cos(ANGLE))
        def side(points,**kw):path([world(y,z) for y,z in points],**kw)
        # Broad rear accessory zone. Side support contacts are outboard in X.
        path([local(u,v) for u,v in [(10,-33),(125,-33),(125,0),(10,0)]],
             fill='#fff1cb',stroke='#c68b2f',width=1.5,close=True,stroke_dasharray='6 5')
        side([(-12,0),(depth+12,0)],stroke='#adb6af',width=1.5)
        side([(0,0),(depth,0),(depth,6),(0,6)],fill='#47786a',close=True,width=1.5)
        if key=='A':
            # Enclosure covers the candidate radial seat and release feature.
            side([(32,6),(32,20),(42,34),(80,34),(94,22),(94,6)],fill='#47786a',close=True)
            side([(32,17),(27,17),(27,21),(34,21)],fill='#86a899',close=True,width=1)
        elif key=='B':
            # This side view overlays the two outboard pods.
            side([(34,6),(36,33),(44,47),(58,49),(71,38),(75,6)],fill='#47786a',close=True)
            svg.append(f'<circle cx="{world(54,34)[0]}" cy="{world(54,34)[1]}" r="{SCALE*8}" fill="#a8c0b5" stroke="#47786a" stroke-width="2"/>')
        else:
            side([(26,6),(39,30),(104,30),(118,6)],fill='#47786a',close=True)
            # Visible seams mark selectable seats, not qualified socket geometry.
            for yy in (51,72,93):side([(yy,29),(yy+5,22)],stroke='#d2e1d9',width=3)
        # Same fork carrier; frame sits beyond the illustrated 33 mm rear zone.
        path([local(-15,-38),local(88,-38)],stroke='#47786a',width=10)
        for u in (0,70):path([local(u,-38),local(u,0)],stroke='#47786a',width=7)
        # Case envelope and two lower ledges (one overlaid in this side view).
        path([local(u,v) for u,v in [(0,0),(PHONE_H,0),(PHONE_H,PHONE_T),(0,PHONE_T)]],
             fill='#c4d1d6',stroke='#637d88',width=1.5,close=True)
        path([local(-3,-3),local(-3,16),local(6,16)],stroke='#47786a',width=5)
        # Generous illustrative plug and front cable route.
        path([local(-27,6),local(-1,6)],stroke='#647989',width=6)
        p=local(-27,6)
        path([p,(p[0]-12,p[1]+18),(ox+14,ground-6)],stroke='#647989',width=3)
        text(x+20,662,f'Target base: {w} W × {depth} D mm','body')
        text(x+20,686,'Side silhouette · same scale in every column','small')
        text(x+20,717,action,'tiny')
        text(x+20,743,mechanism,'tiny')
        text(x+20,769,risk,'tiny')
        # Shared carrier in front projection: open fork, not a backplate.
        fx,fy=x+222,890
        fs=.64
        def front(a,b):return fx+fs*a,fy-fs*b
        path([front(a,b) for a,b in [(-42.5,0),(-42.5,170),(42.5,170),(42.5,0)]],
             fill='#e9eef0',stroke='#99aab2',width=1.1,close=True)
        # Landscape reference makes orientation-dependent accessory routing explicit.
        path([front(a,b) for a,b in [(-85,0),(-85,85),(85,85),(85,0)]],
             stroke='#99aab2',width=1,close=True,stroke_dasharray='4 4')
        path([front(a,b) for a,b in [(-47,87),(-47,-9),(47,-9),(47,87)]],stroke='#47786a',width=7)
        for a in (-37,37):
            path([front(a-5,70),front(a+5,70)],stroke='#47786a',width=5)
            path([front(a-6,0),front(a+6,0)],stroke='#47786a',width=6)
        # Front projection exposes the architecture hidden by a side silhouette.
        path([front(a,b) for a,b in [(-w/2,-55),(w/2,-55),(w/2,-49),(-w/2,-49)]],fill='#47786a',close=True,width=1)
        if key=='B':
            for side_sign in (-1,1):
                path([front(side_sign*a,b) for a,b in [(40,-49),(53,-49),(53,-18),(47,-8),(40,-18)]],fill='#47786a',close=True,width=1)
        else:
            path([front(0,-9),front(0,-26)],stroke='#47786a',width=6)
            half=20 if key=='A' else (w/2-8)
            path([front(a,b) for a,b in [(-half,-49),(half,-49),(half-5,-25),(-half+5,-25)]],fill='#47786a',close=True,width=1)
        text(x+20,936,'Front form · open fork / split ledges','tiny')
    text(34,988,'Desk footprint comparison','head')
    text(34,1017,'All rectangles at 1 px = 1 mm. Height/empty space in perspective must not hide occupied desk area.','small')
    for index,(key,title,w,depth,*_) in enumerate(CONCEPTS):
        x=48+index*472
        rect(x,1040,224,246,'none','#b2b9b3',r=7,stroke_dasharray='7 5')
        rect(x+(224-w)/2,1040+246-depth,w,depth,'#d5e5dc','#47786a',r=6)
        rect(x+(224-80)/2,1040+246-125,80,125,'none','#778da1',r=5,stroke_dasharray='3 3')
        text(x+242,1070,'V2: 224 × 246','tiny')
        text(x+242,1094,'V1: 80 × 125','tiny')
        text(x+242,1122,f'{key}: {w} × {depth}','small')
        text(x+242,1146,'candidate target','tiny')
        text(x+242,1185,'Front edges aligned.','tiny')
    text(34,1327,'Amber = rear accessory allowance; blue-grey = phone/cable; green = proposed structure.','small')
    text(34,1352,'55 mm under-phone height is illustrative. Ring width/swing and actual plug/bend space still need checking.','small')
    text(34,1377,'Smaller footprints may need more base weight; the earlier 2 N tap assumption is provisional, not measured.','small')
    text(34,1402,'Concept sketches only: no print recommendation, calibrated material properties or mechanism qualification.','small')
    svg.append('</svg>')
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'compact_revision_directions.svg';target.write_text('\n'.join(svg)+'\n')
    cairosvg.svg2png(url=str(target),write_to=str(target.with_suffix('.png')))
    print(target)

if __name__=='__main__':
    rough_screen()
    draw()
