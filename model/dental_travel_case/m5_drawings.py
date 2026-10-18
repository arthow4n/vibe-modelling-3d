"""Actual-CAD interior comparison; committed exploration with a common scale."""
import hashlib
import html
import json
from dataclasses import replace
from pathlib import Path
import cadquery as cq
import cairosvg
import m1_design as m1
import m4_design as m4
import m5_design as m5
from m5_space_study import central_slice

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'notes/m5'


def label(items,x,y,value,size=18):
    items.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(value)}</text>')


def canvas(title,height):
    items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">',
           f'<rect width="1200" height="{height}" fill="#fafaf7"/>',
           '<style>text{font-family:sans-serif;fill:#243444}</style>']
    label(items,25,38,title,25)
    return items


def section(items,shape,plane,z,transform,color):
    # Wire sampling only controls drawing smoothness; the measurements use CAD.
    sectioned=cq.Workplane(plane,origin=(0,0,z)).add(shape).section().val()
    paths=[]
    for wire in sectioned.Wires():
        points,_=wire.sample(.01)
        coords=[transform(p) for p in points]
        paths.append('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in coords)+' Z')
    items.append(f'<path d="{" ".join(paths)}" fill="{color}" fill-rule="evenodd" stroke="{color}" stroke-width=".6"/>')


def save(name,items):
    association=dict(generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        data_sha256=hashlib.sha256((OUT/'space_study.json').read_bytes()).hexdigest(),
        contact_sha256=hashlib.sha256((OUT/'contact.json').read_bytes()).hexdigest())
    items.append('<metadata>'+html.escape(json.dumps(association))+'</metadata></svg>')
    path=OUT/(name+'.svg')
    path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))


def draw():
    data=json.loads((OUT/'space_study.json').read_text())['cases']
    parts={'M4':m4.build(),'flat77':m5.build()}
    items=canvas('Where M5 returns space to the contents',960)
    label(items,25,75,'Actual CAD sections at the same scale. Blue = body/guide; orange = cap; green = central storage space.',16)
    for col,(name,title) in enumerate((('M4','Previous M4'),('flat77','M5: flat sides + shorter guards'))):
        x0=col*600
        label(items,x0+35,117,title,22)
        for row,z in enumerate((180,220)):
            y0=155+row*350
            transform=lambda p,x0=x0,y0=y0:(x0+300+5.6*p.x,y0+145-5.6*p.y)
            p=parts[name]
            section(items,central_slice(p,z),'XY',z,transform,'#cbe7ca')
            section(items,p['body'].val(),'XY',z,transform,'#1769a6')
            section(items,p['cap'].val(),'XY',z,transform,'#cf741d')
            area=data[name]['sections_mm2'][str(z)]
            label(items,x0+35,y0-12,('At the catches' if row==0 else 'Above the catches')+f' — section Z={z} mm',18)
            label(items,x0+35,y0+308,f'Central area: {area:.0f} mm²',18)
    label(items,25,860,'Above the catches, the middle passage widens from 56.9 to 66.1 mm; full 78 mm guidance remains.',19)
    label(items,25,894,'The catch-level bottleneck stays 56.9 mm. M5 recovers room beyond it; larger objects still must pass the mouth.',17)
    label(items,25,929,'M5 is flat at 77 mm: the previous maximum is unchanged, but its broad sides are 2 mm wider than M4.',17)
    save('interior_sections',items)

    items=canvas('Keep the spring protection; remove the empty continuation',875)
    label(items,25,76,'Actual central longitudinal section Y=0. Same scale; only the joint region and right-hand wall are shown.',17)
    for col,(name,title) in enumerate((('M4','M4: guard continues to guide tip'),('flat77','M5: guard stops beyond spring'))):
        x0=col*600
        p=parts[name]
        xf=lambda v,x0=x0:(x0+70+14*(v.x-25),150+4.7*(258-v.z))
        clip=m1.box(32,0,197,20,4,122).val()
        for component,color in (('cap','#cf741d'),('body','#1769a6')):
            section(items,p[component].val().intersect(clip),'XZ',0,xf,color)
        label(items,x0+25,120,title,21)
        for z,words in ((252,'Guide tip: 252'),(190,'Guard can end: 190'),(182.4,'Spring tip: 182.4'),(174,'Case seam: 174')):
            _,y=xf(cq.Vector(25,0,z))
            items.append(f'<path d="M{x0+45},{y} H{x0+460}" stroke="#556572" stroke-dasharray="5 5" stroke-width=".8"/>')
            label(items,x0+320,y-5,words,15)
    label(items,25,767,'The spring is unchanged. Its protective liner is needed beside the moving leaf, not another 62 mm above it.',19)
    label(items,25,805,'The guide remains a continuous closed, stepped ring above the guard, with the same 1.6 mm wall.',18)
    label(items,25,842,'Clearance channels on the guide let the reinforced receivers slide all the way off; they are not storage space.',17)
    save('guard_length',items)

    items=canvas('Alternatives actually explored',720)
    label(items,25,83,'Same contents checks; actual section area at Z220. Volume is approximate central space, not proven packing.',17)
    columns=(30,265,450,660)
    for x,title in zip(columns,('Variant','Area at Z220','Tube gap','Decision')):label(items,x,134,title,19)
    decisions={'M4':'Historical baseline; excessive guard length',
        'short_guard':'Useful +11 mL, but keeps raised outer ribs',
        'thin_sleeve':'Rejected: local plate rigidity falls to 42%',
        'flat75':'Rejected: worsens the tube entrance',
        'flat77_light_cap':'Avoided: cap section loses bending stiffness',
        'flat77_loose_corners':'Rejected: diagonal rocking loads catch early',
        'flat77':'Selected: same old maximum width; flat sides'}
    names={'M4':'M4','short_guard':'Short guard only','thin_sleeve':'1.2 mm sleeve','flat75':'Flat 75 mm','flat77_light_cap':'Flat, thinner cap','flat77_loose_corners':'Flat, loose corners','flat77':'Flat 77 mm / M5'}
    for i,name in enumerate(decisions):
        y=185+i*61
        case=data[name]
        for x,value in zip(columns,(names[name],f"{case['sections_mm2']['220']:.0f} mm²",f"{case['individual_tube_gap_mm']:.2f} mm",decisions[name])):label(items,x,y,value,16)
    label(items,25,675,'The selected variant preserves the original leaf and reinforced retaining strip; it does not claim measured holding force.',17)
    save('variants',items)

    contacts=json.loads((OUT/'contact.json').read_text())['cases']
    items=canvas('Corner bearing matters too: the rejected M5 arrangement',650)
    label(items,25,78,'Actual corner sections at equal magnification, Z220. Same adverse fit: .20 mm side gap / .35 mm axial play.',17)
    clip=m1.box(35,23,220,14,14,4).val()
    for index,(name,matched,title) in enumerate((
        ('rejected_loose_corners',False,'Rejected: mismatched corner profiles'),
        ('fit_0.2_0.35',True,'M5: matching bearing profiles'))):
        x0=index*600
        p=m5.build(replace(m5.D,lap_clearance=.2,axial_play=.35,matched_corner_bearing=matched))
        xf=lambda v,x0=x0:(x0+90+22*(v.x-28),145+22*(28-v.y))
        label(items,x0+25,130,title,21)
        section(items,p['body'].val().intersect(clip),'XY',220,xf,'#1769a6')
        section(items,p['cap'].val().intersect(clip),'XY',220,xf,'#cf741d')
        demand=contacts[name]['diagonal']['maximum_land_axial_demand_mm']
        label(items,x0+25,510,f'Catch rise demanded before bearing: {demand:.3f} mm',18)
    label(items,25,557,'The mismatched corner adds diagonal freedom even when the flat-face clearance is unchanged.',19)
    label(items,25,595,'Correcting the bearing contours preserves the space gain without accepting that newly exposed weak route.',17)
    label(items,25,627,'Finite CAD motion and inherited local proxy; no shell deformation or printed force rating is implied.',16)
    save('corner_bearing',items)


if __name__=='__main__':draw()
