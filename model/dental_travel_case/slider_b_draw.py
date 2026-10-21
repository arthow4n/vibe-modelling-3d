"""Explain the B1 coupon using actual CAD sections, not proposal geometry."""
from pathlib import Path
import cairosvg
import m1_design as base
from slider_b_design import build
from closure_research_drawings import canvas, label, section


def main():
    p=build();d=p['dimensions']
    items=canvas('B1 test piece — slide the lock before lifting the cap',660)
    label(items,25,78,'Actual XZ sections at Y = 28 mm through one lug; second side works the same way.',18)
    label(items,25,109,'Blue = body lug. Orange = cap rail. Green = sliding yoke. White = empty passage.',17)
    clip=base.box(0,28,33,34,10,40).val()
    for i,(shift,lift,title) in enumerate(((-d.travel,0,'1  LOCK'),(0,0,'2  UNLOCK'),(0,12,'3  LIFT'))):
        x0=400*i
        label(items,x0+30,155,title,24)
        xf=lambda v,x0=x0:(x0+195+7*v.x,195+7*(48-v.z))
        for name,color,delta in (('body','#3686af',(0,0,0)),('cap','#d69b43',(0,0,lift)),('yoke','#4c9c70',(shift,0,lift))):
            shape=p[name].translate(delta).val().intersect(clip)
            section(items,shape,'XZ',(0,28,0),xf,color)
        if i==0:
            label(items,x0+25,482,'Solid ledge is below the blue lug.',17)
            label(items,x0+25,510,'Pulling up meets that ledge.',17)
        elif i==1:
            label(items,x0+25,482,'Move the U-shaped yoke 10 mm.',17)
            label(items,x0+25,510,'Opening lines up below the lug.',17)
        else:
            label(items,x0+25,482,'Lift cap + yoke together.',17)
            label(items,x0+25,510,'The blue lug passes through the slot.',17)
    label(items,25,568,'Close in reverse: keep UNLOCK, seat the cap, then slide to LOCK. No strong snap is forced.',18)
    label(items,25,604,'Fit/action coupon only. The small detents hold slider position; they do not carry the cap pull load.',17)
    label(items,25,637,'Assemble the yoke onto the cap once; see the separate print layout and assembly instructions.',17)
    items.append('</svg>')
    path=Path(__file__).resolve().parent/'renders/tests/slider_b/operation.svg'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')))
    print(path)


if __name__=='__main__':main()
