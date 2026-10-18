"""Commit-worthy CAD motion/section drawings: physical meaning, not angle labels.

All case outlines come from the actual sectioned CAD, all poses from the retained
contact exploration. Red intersections deliberately identify blocked rigid ghost
poses. They must never be interpreted as accepted full-assembly configurations.
"""
from dataclasses import replace
import html
import hashlib
import json
from pathlib import Path

import cadquery as cq
import cairosvg
import m1_design as m1
import m3_design as m3
import m4_design as m4
from overlap_exploration import peel,point_after_peel

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/overlap_exploration'
BLUE='#1769a6'
ORANGE='#cf741d'
RED='#cc2947'


def start(title,height):
    return ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="'+str(height)+'" viewBox="0 0 1200 '+str(height)+'">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#263746"/></marker></defs>',
        '<rect width="1200" height="'+str(height)+'" fill="#fafaf7"/>',
        '<style>text{font-family:sans-serif;fill:#243444}.small{font-size:16px}.note{font-size:19px}.title{font-size:25px;font-weight:bold}</style>',
        f'<text x="30" y="40" class="title">{html.escape(title)}</text>']


def text(items,x,y,words,css='note',color=None):
    style='' if color is None else f' style="fill:{color}"'
    items.append(f'<text x="{x}" y="{y}" class="{css}"{style}>{html.escape(words)}</text>')


def section(items,shape,*,plane,clip,transform,color,opacity=1.,width=1.):
    shape=shape.translate((0,-plane,0)).intersect(clip)
    if not shape.Edges():return
    sectioned=cq.Workplane('XZ').add(shape).section().val()
    for wire in sectioned.Wires():
        points,_=wire.sample(.005)
        coords=[transform(p.x,p.z) for p in points]
        path='M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in coords)+' Z'
        items.append(f'<path d="{path}" fill="{color}" fill-opacity="{opacity*.20}" stroke="{color}" stroke-opacity="{opacity}" stroke-width="{width}"/>')


def save(name,items):
    association=dict(data_sha256=hashlib.sha256((OUT/'contact_sequence.json').read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    items.append('<metadata id="engineering_source_association">'+html.escape(json.dumps(association))+'</metadata>')
    items.append('</svg>')
    path=OUT/(name+'.svg')
    path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


def draw():
    record=json.loads((OUT/'contact_sequence.json').read_text())
    choices=[('M3_overlap_12_floating','1.2 cm control (M3 catch)',m3,replace(m3.D,lap=12.)),
             ('M3_overlap_30_floating','3 cm overlap — previous M3',m3,m3.D),
             ('M4','7.8 cm overlap — revised M4',m4,m4.D)]
    parts={name:module.build(d) for name,_,module,d in choices}
    items=start('What the angle means on the actual case',875)
    text(items,30,74,'Blue = body/guide. Orange = tilted cap. Gray = straight cap. All panels use the same scale.','small')
    text(items,30,98,'Guide section Y=12 mm. Cap uses its available side movement before tilting; old poses conflict with catches.','small')
    clip=m1.box(0,0,215,90,4,110).val()
    for index,(name,title,module,d) in enumerate(choices):
        x0=index*400
        data=record['cases'][name]
        angle=data['guide_only_onset']['angle_deg']
        xf=lambda x,z,x0=x0:(x0+200+4*x,120+4*(270-z))
        text(items,x0+24,133,title)
        p=parts[name]
        section(items,p['cap'].val(),plane=12,clip=clip,transform=xf,color='#999999',opacity=.45)
        section(items,p['body'].val(),plane=12,clip=clip,transform=xf,color=BLUE)
        section(items,peel(p['cap'].val(),d,angle,transverse=data['transverse_shift_mm']),plane=12,clip=clip,transform=xf,color=ORANGE)
        cx,_,cz=data['guide_only_onset']['contact_center_mm']
        x,y=xf(cx,cz)
        items.append(f'<circle cx="{x}" cy="{y}" r="6" fill="none" stroke="#172f3c" stroke-width="2"/>')
        text(items,x0+26,580,'Opposite guide bearing meets at circle.','small')
        lateral=abs(data['top_center_motion_mm'][0])
        text(items,x0+26,610,f'Cap top moves sideways {lateral:.2f} mm.','small')
        # Explicit enlarged movement inset avoids invisible nominal differences.
        bx=x0+70
        items.append(f'<path d="M{bx},635 V675 M{bx+40*lateral},635 V675" stroke="#263746" stroke-width="2"/>')
        items.append(f'<path d="M{bx},655 H{bx+40*lateral}" stroke="#263746" marker-start="url(#arrow)" marker-end="url(#arrow)"/>')
        text(items,x0+26,703,'Movement inset above is enlarged 10×.','small')
        conflicts=sum(data['hook_intersection_at_guide_only_pose_mm3'].values())
        text(items,x0+26,736,'Catch already loaded — see next drawing.' if conflicts>1e-5 else 'Guide meets first; catches are still clear.','small',RED if conflicts>1e-5 else BLUE)
    text(items,30,792,'A smaller angle alone was not enough evidence: we must see which surface stops the motion first.')
    text(items,30,824,'The revised guide reaches near the cap end, giving the shell support before peel demands catch bending.','small')
    text(items,30,852,'M4 also uses 0.15 mm side clearance and 0.40 mm axial catch play; these changes are identified, not hidden.','small')
    save('case_motion',items)

    items=start('The important difference: does the guide help before the catch has to bend?',970)
    text(items,30,76,'Same magnification in all panels. Actual catch plane Y=0. Orange cap is at first guide contact.','small')
    text(items,30,100,'Red = blocked rigid overlap. The blue tooth could escape by bending inward (left); deformation is not drawn.','small')
    clip=m1.box(35,0,179,12,4,12).val()
    for index,(name,title,module,d) in enumerate(choices):
        x0=index*400
        data=record['cases'][name]
        angle=data['guide_only_onset']['angle_deg']
        xf=lambda x,z,x0=x0:(x0+35+28*(x-29),155+28*(185-z))
        text(items,x0+22,138,title)
        p=parts[name]
        posed=peel(p['cap'].val(),d,angle,transverse=data['transverse_shift_mm'])
        section(items,p['body'].val(),plane=0,clip=clip,transform=xf,color=BLUE,opacity=1.)
        section(items,posed,plane=0,clip=clip,transform=xf,color=ORANGE,opacity=.8)
        common=p['body'].val().intersect(posed)
        if common.Volume()>1e-5:
            section(items,common,plane=0,clip=clip,transform=xf,color=RED,opacity=1.,width=2.)
        _,yy=xf(35,d.hook_bottom)
        items.append(f'<path d="M{x0+35},{yy} H{x0+343}" stroke="#344651" stroke-dasharray="5 4"/>')
        text(items,x0+30,530,'Dashed line: tooth shoulder height.','small')
        demand=data['demanded_far_land_axial_motion_mm']
        text(items,x0+30,563,f'Cap demands {demand:.2f} mm extra rise.' if demand>0 else f'Catch still has {-demand:.2f} mm clearance.','note',RED if demand>0 else BLUE)
        first=data['first_catch_contact_deg']
        guide=data['guide_only_onset']['angle_deg']
        text(items,x0+30,600,f'Catch touches: {first:.2f}°', 'small')
        text(items,x0+30,625,f'Guide touches: {guide:.2f}°','small')
        text(items,x0+30,663,'Guide arrives after catch loading.' if first<guide else 'Guide arrives before catch loading.','small')
        items.append(f'<path d="M{x0+35},699 H{x0+63} M{x0+35},694 V704 M{x0+63},694 V704" stroke="#263746"/>')
        text(items,x0+72,705,'1 mm ruler','small')
    text(items,30,759,'Even centered, the old 3 cm design demands ~0.38 mm of catch rise; side movement makes it worse.')
    text(items,30,793,'The earlier catch proxy loses capture after only about 0.06–0.16 mm in its adverse scenarios.','small')
    text(items,30,823,'That exposed a missing load-path check. The drawing does not claim those scenarios measured a real print.','small')
    text(items,30,863,'M4 puts the guide into contact while the catches remain clear in this nominal peel path.',color=BLUE)
    text(items,30,899,'The guide can now carry the rocking load first; the catches retain the cap against straight withdrawal.','small')
    text(items,30,932,'Nominal CAD + declared peel path. Shell flexibility, tolerances and printed recovery still need their stated evidence.','small')
    save('catch_before_guide',items)

    items=start('Why overlap length alone was not enough',790)
    text(items,30,79,'Controlled rows: same M3 catches/clearances with side play allowed. Last row is the complete M4 revision.','small')
    text(items,30,109,'Bars show how far the far retaining shoulder must rise before the guide bears. Shorter is better.','small')
    rows=[('M3_overlap_'+str(n)+'_floating',str(n)+' mm') for n in (12,30,36,48,60,66,72,78)]+[('M4','M4: 78 mm + fit')]
    largest=max(record['cases'][name]['demanded_far_land_axial_motion_mm'] for name,_ in rows)
    scale=600/largest
    for i,(name,label) in enumerate(rows):
        y=158+i*48
        amount=record['cases'][name]['demanded_far_land_axial_motion_mm']
        text(items,35,y,label)
        items.append(f'<rect x="195" y="{y-21}" width="{max(1,amount*scale)}" height="27" fill="{ORANGE if amount>0 else BLUE}"/>')
        text(items,210+max(0,amount)*scale,y,f'{amount:.3f} mm' if amount>0 else f'Guide first: {-amount:.3f} mm catch gap','small')
    low=min(x['tooth_centroid_axial_rise_mm'] for x in record['cases']['M3']['proxy_contact_edge_controls'])
    x=195+scale*low
    items.append(f'<path d="M{x},130 V575" stroke="{RED}" stroke-dasharray="6 5" stroke-width="2"/>')
    text(items,875,177,'Dashed reference:', 'small')
    text(items,875,204,'adverse local catch', 'small')
    text(items,875,231,'proxy loses capture', 'small')
    text(items,875,258,f'after ~{low:.3f} mm rise.', 'small')
    text(items,30,630,'Side play exposed a weak route that the centered angle comparison hid; making a sleeve longer alone was insufficient.')
    text(items,30,676,'M4 combines longer support with .15 mm side clearance and .40 mm axial play; nominal guide bearing comes first.','small')
    text(items,30,722,'Assembled size is unchanged. The body is taller to print; the test uses the full reusable cap plus a shortened body.','small')
    save('overlap_choice',items)


if __name__=='__main__':draw()
