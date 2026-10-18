"""Actual CAD sections for the shortened samples, including the pull gaps."""
import json
from closure_research_drawings import canvas, label, section, save, BLUE, ORANGE
import closure_short_design as design


def draw():
    items = canvas('Short retention trials: preserve the full perimeter, remove long walls', 1110)
    label(items,25,78,'Blue = base, orange = cap. Actual CAD: left = XY at catches/rails; right = section through the gripping recess.',17)
    for i, kind in enumerate(design.KINDS):
        x0 = (i%2)*600; y0 = 110+(i//2)*460
        p = design.build(kind)
        label(items,x0+25,y0+20,('R1-S broad-wall snap','R2-S end-wall snap','R3-S perimeter bead','R4-S shallow rail trial')[i],22)
        if kind == 'slide_wall':
            xy = lambda v:(x0+150+2.7*v.x,y0+190-2.7*(v.y-35))
            yz = lambda v:(x0+440+2.5*(v.y-35),y0+270-5*(v.z-design.SLIDE_BOTTOM))
            for name,color in (('body',BLUE),('cap',ORANGE)):
                section(items,p[name].val(),'XY',(0,0,47.5),xy,color)
                section(items,p[name].val(),'YZ',(0,0,0),yz,color)
            label(items,x0+25,y0+315,'77 × 70 mm XY; assembled height 14.2 mm.',17)
            label(items,x0+25,y0+349,'Open-bottom base: 12.2 mm high, formerly 49.2 mm.',17)
            label(items,x0+25,y0+383,'Front recess exposes the lid underside for sliding.',16)
            label(items,x0+25,y0+417,'Rails/detents unchanged; shallow tray stiffness is different.',16)
        else:
            xy = lambda v:(x0+150+2.7*v.x,y0+190-2.7*v.y)
            axis = 'y' if kind=='shell_end' else 'x'
            longitudinal = lambda v:(x0+440+2.5*getattr(v,axis),y0+270-3.5*(v.z-design.BOTTOM))
            plane = 'YZ' if kind=='shell_end' else 'XZ'
            for name,color in (('body',BLUE),('cap',ORANGE)):
                section(items,p[name].val(),'XY',(0,0,design.D.latch_z),xy,color)
                section(items,p[name].val(),plane,(0,0,0),longitudinal,color)
            label(items,x0+25,y0+315,'77 × 51.2 mm XY; 24 mm overlap; 42 mm assembled.',17)
            label(items,x0+25,y0+349,'Base band: 6 mm. Recessed seam gap: 3 mm.',17)
            label(items,x0+25,y0+383,'Corners still seat the cap; catches and ramps unchanged.',16)
            label(items,x0+25,y0+417,'Shorter walls change stiffness: earlier force values do not transfer.',15)
    label(items,25,1063,'These test fit, snap/recovery and grip access with less material. Full-box guidance, force and ergonomics require re-checking.',17)
    save('short_samples',items,extra_sources=('closure_short_design.py','closure_short_drawings.py'))


if __name__=='__main__': draw()
