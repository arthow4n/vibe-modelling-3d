"""Actual-CAD sections explain recessed hinge collision and the segmented seam."""
import html
import json
import hashlib
from pathlib import Path
import cairosvg
import internal_hinge_design as d
from closure_research_drawings import canvas,label,section,BLUE,ORANGE,RED

ROOT=Path(__file__).resolve().parent


def draw():
    items=canvas('Hidden rear hinges: the rear wall has to let the lid turn',1050)
    label(items,25,76,'Actual YZ sections. Blue = base; orange = lid; red = unintended intersection. Closed rear outline remains flat.',17)
    for i,(kind,angle,title) in enumerate((('naive_internal',5,'A: move the pivot inside only — jams'),
        ('internal_screw',0,'B: recessed pivot, revised rear seam'),
        ('internal_screw',90,'C: same mechanism at 90 degrees'))):
        p=d.build(kind,size=d.MINI);moving=d.rotate(p,p['structural_lid'],angle)
        xf=lambda v,i=i:(i*400+45+9*(v.y-4),445-9*(v.z-12))
        clip=d.base.box(0,15,28,70,28,30).val()
        x=0 if kind=='naive_internal' else p['centers'][1]
        label(items,i*400+20,126,title,17)
        section(items,p['body'].val().intersect(clip),'YZ',(x,0,0),xf,BLUE)
        section(items,moving.val().intersect(clip),'YZ',(x,0,0),xf,ORANGE,.8)
        hit=p['body'].intersect(moving)
        if hit.val().Volume()>1e-6:
            section(items,hit.val().intersect(clip),'YZ',(x,0,0),xf,RED)
        xx,yy=xf(type('V',(),dict(y=d.MINI.axis_y,z=d.MINI.seam))())
        items.append(f'<circle cx="{xx}" cy="{yy}" r="3" fill="#202020"/>')
    label(items,25,505,'A fails immediately: the ordinary rear rim sweeps into the base. Moving the axle alone does not make a hidden hinge.',17)
    label(items,25,550,'B/C: a curved rear split changes sides at the fixed ears. Each hinge web keeps its own wall; the opposite part clears it.',17)
    label(items,25,593,'Pivot centre is 6.2 mm inside the back. The 7.2 mm barrel reaches 7.8 mm inward from the normal storage wall.',17)

    p=d.build('internal_screw',size=d.MINI)
    # Side-by-side rear elevation sections expose why the wall seam switches.
    for i,(x,title) in enumerate(((p['centers'][1],'At moving ear'),(p['centers'][1]-2.7,'At fixed ear'))):
        xf=lambda v,i=i:(50+360*i+9*(v.y-5),900-8*(v.z-14))
        c=d.base.box(0,15,27,70,24,30).val()
        label(items,40+360*i,655,title,18)
        section(items,p['body'].val().intersect(c),'YZ',(x,0,0),xf,BLUE)
        section(items,p['lid'].val().intersect(c),'YZ',(x,0,0),xf,ORANGE,.8)
    label(items,825,680,'Closed outline: flat rear.',17)
    label(items,825,720,'Screw option: 2 M3 x 12',17)
    label(items,825,750,'plus 4 jam nuts.',17)
    label(items,825,800,'Printed option: captive cones,',17)
    label(items,825,830,'90-degree-open V print pose.',17)
    label(items,25,977,'Complete mini boxes include the real front loop and keeper. CAD motion is not printed fit, quietness or strength approval.',17)
    paths=('internal_hinge_design.py','internal_hinge_drawings.py','clamshell_design.py','m1_design.py','../sunglasses_case/e_closure.py')
    metadata={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in paths}
    items.append('<metadata>'+html.escape(json.dumps(metadata))+'</metadata></svg>')
    out=ROOT/'renders/concepts/internal_hinge';out.mkdir(parents=True,exist_ok=True)
    svg=out/'rear_motion.svg';svg.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(svg),write_to=str(svg.with_suffix('.png')))


if __name__=='__main__':draw()
