"""Explain the actual R1a nose and curved keeper using CAD sections."""
from pathlib import Path
import cairosvg
import m1_design as base
from rotary_r1_design import build,tab_pose
from closure_research_drawings import canvas,label,section


def main():
    p=build();d=p['dimensions'];items=canvas('R1a — a small swivel tab, not a pull-apart snap',735)
    label(items,25,77,'Blue = body. Orange = cap / keeper. Green = rotating tab. Hardware omitted from sections.',17)
    # Front sections through the keeper: Y=-25.8, same scale in both poses.
    for i,(angle,title) in enumerate(((0.,'LOCK: inward nose above keeper'),(90.,'OPEN: turn tab sideways'))):
        x0=600*i;label(items,x0+25,125,title,21)
        xf=lambda v,x0=x0:(x0+280+8*v.x,160+8*(30-v.z))
        clip=base.box(0,-26,16,42,8,36).val()
        for name,color,part in (('body','#3686af',p['body']),('cap','#d69b43',p['cap']),('tab','#4c9c70',tab_pose(p,angle))):
            shape=part.val().intersect(clip)
            section(items,shape,'XZ',(0,-25.8,0),xf,color)
        label(items,x0+25,431,'True sections through the inward nose; outer stem is outside this plane.',15)
    label(items,25,477,'Side section in LOCK — the stem stays outside the cap; only its nose reaches inward.',19)
    xf=lambda v:(180+15*(-v.y-23),515+10*(25-v.z))
    clip=base.box(0,-27,18,2,12,14).val()
    for name,color in (('body','#3686af'),('cap','#d69b43'),('tab','#4c9c70')):
        section(items,p[name].val().intersect(clip),'YZ',(0,0,0),xf,color)
    label(items,390,532,'The concentric curved faces let the nose swing without catching a square corner.',17)
    label(items,390,563,'Nominal 0.8 mm radial clearance makes this a loose capture, not a draw-down cam.',17)
    label(items,390,594,'Push cap onto four corner seats, then turn the tab upright. Turn sideways to lift.',17)
    label(items,390,625,'The 3 mm seam reveal remains between the corner pads. No full-size case is built.',17)
    label(items,25,690,'Print three PLA parts + assemble one M3×12 screw and two jammed M3 nuts. Fit/feel remain a physical trial.',17)
    label(items,25,721,'This sample explains the motion; it does not validate bag retention, final exterior bulk or the printed keeper strength.',16)
    items.append('</svg>');path=Path(__file__).resolve().parent/'renders/tests/rotary_r1/operation.svg'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text('\n'.join(items)+'\n')
    cairosvg.svg2png(url=str(path),write_to=str(path.with_suffix('.png')));print(path)


if __name__=='__main__':main()
