"""Stock-only hardware coverage, shoulder and indexed-release CAD sections."""
from pathlib import Path
import cairosvg
import m1_design as base
from rotary_refinement_design import D,build,rotor_pose
from closure_research_drawings import canvas,label,section

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'renders/concepts/rotary_refinement'
BLUE='#357b9b';CAP='#c4d0d1';GREEN='#436c60';METAL='#bf8e46';RED='#c45d50'


def save(name,a):
    a.append('</svg>');p=OUT/(name+'.svg');p.write_text('\n'.join(a)+'\n')
    cairosvg.svg2png(url=str(p),write_to=str(p.with_suffix('.png')))


def packaging(p):
    d=p['dimensions'];z=d.pivot;a=canvas('Stock-only revision · smooth storage walls, recessed printed axle',870)
    label(a,25,77,'Actual side section at X0. Blue body · grey cap · green rotor/printed axle · gold one stock M6 nut.',17)
    clip=base.box(0,-26,z+4,2,29,37).val()
    xf=lambda v:(45+13*(-v.y-18),140+14*(z+20-v.z))
    for n,c in (('body',BLUE),('cap',CAP),('rotor',GREEN),('pivot_axle',GREEN),('pivot_nut',METAL)):
        section(a,p[n].val().intersect(clip),'YZ',(0,0,0),xf,c)
    for i,t in enumerate([
        'No metal keeper screw, protruding screw tip or jam nuts.',
        'The stock M6 nut sits in a blind outboard pocket.',
        'The printed shoulder axle stops against the fixed body.',
        'The wheel has 0.5 mm nominal total axial freedom.',
        'Its 8 mm external hex head is recessed 0.3 mm.',
        'A standard 8 mm socket assembles it; no printed tool.',
        'All original storage-facing walls and the full guide remain.',
        'The cap keeper is now integral printed material.',
        'Its small exterior overhang needs accessible support.']):label(a,460,150+41*i,t,17)
    label(a,25,738,'Tradeoff: the rounded mounting area is deeper. Maximum control projection is 10.4 mm (previous study: 6.3 mm).',18)
    label(a,25,779,'Four printed parts + one stock M6 nut. No purchases, shorter metal screws, glue or extra materials.',18)
    label(a,25,824,'Thread fit, subjective turning effort, wear and resistance to real bag shaking remain physical checks.',17)
    save('packaging',a)


def detent(p):
    d=p['dimensions'];z=d.pivot;a=canvas('A deliberate detent acts before the cap can release',1010)
    label(a,25,77,'Actual XZ section through the rear spring / fixed pins. Green rotor · blue fixed pins. Red = blocked rigid overlap.',16)
    for i,(angle,title) in enumerate(((0,'LOCK · spring rests in its pocket'),(10,'TURN · spring must move outward'),(90,'OPEN · second resting pocket'))):
        x0=i*400;label(a,x0+20,124,title,18)
        xf=lambda v,x0=x0:(x0+200+8*v.x,180+8*(z+18-v.z))
        rotor=rotor_pose(p,angle)
        section(a,rotor.val(),'XZ',(0,-33.0,0),xf,GREEN)
        for n in ('detent_pin','stop_pin'):
            section(a,p[n].val(),'XZ',(0,-33.0,0),xf,BLUE)
        common=rotor.intersect(p['detent_pin'])
        if common.val().Volume()>1e-5:section(a,common.val(),'XZ',(0,-33.,0),xf,RED)
        label(a,x0+20,490,f'Wheel angle {angle}°',17)
    label(a,25,555,'The curved spring is part of the flat-printed wheel. Its outer relief frees radial movement.',19)
    label(a,25,595,'Nominal radial movement: 0.35 mm. Resting pockets unload the spring at LOCK and OPEN.',18)
    label(a,25,635,'The small inner peg/track sets travel limits; the larger outer pin provides the detent.',18)
    label(a,25,675,'At 5°, 10° and 15° the detent is engaged while the cap is still captured by the nose.',18)
    label(a,25,715,'The shoulder axle can be seated firmly without squeezing the wheel to create friction.',18)
    label(a,25,777,'The red region must be accommodated by spring bending in a print. It is not permitted rigid interpenetration.',17)
    label(a,25,817,'This establishes a designed release barrier, not a measured torque or a bag-shake rating.',17)
    label(a,25,867,'If the real wheel turns freely, does not return or cracks, revise the spring; do not compensate by clamping the axle.',17)
    label(a,25,925,'A matching 70 mm closed-ended sample preserves this mechanism and both production print orientations.',17)
    label(a,25,969,'Use PLA for the trial and the stock M6 nut. Printed M6 thread fit must be tried gently before assembly.',17)
    save('detent',a)


def manufacture(p):
    d=p['dimensions'];a=canvas('Stock-only manufacture · closed-end-down shells and flat-printed moving parts',870)
    label(a,25,77,'Actual sections. The full layout has four printed parts; the stock nut is installed afterward.',17)
    cap=p['cap'].val().rotate((0,0,0),(1,0,0),180).translate((100,0,d.length))
    xf=lambda v:(205+3*v.y,650-2.3*v.z)
    section(a,p['body'].val(),'YZ',(0,0,0),xf,BLUE)
    xf=lambda v:(610+3*v.y,650-2.3*v.z)
    section(a,cap,'YZ',(100,0,0),xf,CAP)
    a.append('<path d="M80 654 H335 M490 654 H755" stroke="#333" stroke-width="4"/>')
    label(a,80,133,'Body · bottom down',20);label(a,80,697,'204 mm full / 54 mm sample',17)
    label(a,490,400,'Cap · closed top down',20);label(a,490,697,'87 mm full / 43 mm sample',17)
    label(a,800,155,'Wheel · outer face on bed',20)
    rotor=p['rotor'].val().rotate((0,0,0),(1,0,0),90).translate((0,80+d.pivot,d.wheel_front))
    xf=lambda v:(980+10*(v.y-80),415-12*v.z)
    section(a,rotor,'YZ',(0,0,0),xf,GREEN)
    a.append('<path d="M790 419 H1170" stroke="#333" stroke-width="4"/>')
    for i,t in enumerate(['Axle · hex head on bed, thread up.', 'No socket roof faces the bed.', 'Prints with the same PLA as the shell.', 'Only one stock M6 nut is needed.', 'Cap keeper support is outside;', 'no support is trapped in storage.']):label(a,800,470+32*i,t,17)
    label(a,25,765,'The final profile-specific support locations and removal limits are recorded in the notes.',18)
    label(a,25,810,'The sample tests actual thread fit, detent return and effort; it does not qualify the complete travel box.',17)
    label(a,25,851,'Use the current sample / axle files, not older full-study artifacts or the R1a sample to qualify this new detent.',17)
    save('manufacture',a)


def main():
    OUT.mkdir(parents=True,exist_ok=True);p=build('wheel',dimensions=D)
    packaging(p);detent(p);manufacture(p)
    print(OUT)


if __name__=='__main__':main()
