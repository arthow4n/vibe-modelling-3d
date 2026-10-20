"""Three-line case with exact quintic wrap bands and an uninterrupted cap rim.

Horizontal wall sections remain 1.2 mm: both skins move inward together.
The maximum profile slope makes the true normal thickness about 1.172 mm.
The original matching-pair builder and its exports remain available unchanged.
"""
import cadquery as cq
import m1_design as base
import short_lap_design as joint
from short_lap_thin import build_three_line, WALL
from grip_placement import LAYOUTS, describe

RAMP=6.
JOIN_OVERLAP=.2


def transition(wp,radius,z0,z1,inset0,inset1,sign):
    # Quintic Bezier [a,a,a,b,b,b]: zero first/second derivatives at both ends.
    insets=(inset0,inset0,inset0,inset1,inset1,inset1)
    return wp.bezier([(sign*(radius-insets[i]),z0+(z1-z0)*i/5)
                     for i in range(1,6)],includeCurrent=True)


def profile(radius,center,width,depth,*,one_sided):
    lo=center-width/2;hi=center+width/2
    if width<=2*RAMP or radius<=depth:raise ValueError('Band requires a landing and positive radius')
    wp=cq.Workplane('XZ').moveTo(radius,lo-JOIN_OVERLAP).lineTo(radius,lo)
    wp=transition(wp,radius,lo,lo+RAMP,0.,depth,1)
    wp=wp.lineTo(radius-depth,hi-RAMP)
    wp=transition(wp,radius,hi-RAMP,hi,depth,0.,1).lineTo(radius,hi+JOIN_OVERLAP)
    if one_sided:
        return wp.lineTo(0.,hi+JOIN_OVERLAP).lineTo(0.,lo-JOIN_OVERLAP).close()
    wp=wp.lineTo(-radius,hi+JOIN_OVERLAP).lineTo(-radius,hi)
    wp=transition(wp,radius,hi,hi-RAMP,0.,depth,-1).lineTo(-(radius-depth),lo+RAMP)
    return transition(wp,radius,lo+RAMP,lo,depth,0.,-1).lineTo(-radius,lo-JOIN_OVERLAP).close()


def envelope(width,height,corner,center,band):
    """Exact rounded-rectangle variable offset: flat strips + four revolutions."""
    corex=width/2-corner;corey=height/2-corner
    x=profile(width/2,center,band.band_width_mm,band.depth_mm,one_sided=False).extrude(2*corey).translate((0,corey,0))
    y=profile(height/2,center,band.band_width_mm,band.depth_mm,one_sided=False).extrude(2*corex).translate((0,corex,0)).rotate((0,0,0),(0,0,1),90)
    corner_solid=profile(corner,center,band.band_width_mm,band.depth_mm,one_sided=True).revolve(360,(0,0),(0,1))
    result=x.union(y)
    for sx in (-1,1):
        for sy in (-1,1):result=result.union(corner_solid.translate((sx*corex,sy*corey,0)))
    return result.clean()


def band_shell(d,center,band):
    outer=envelope(d.width,d.depth,d.corner,center,band)
    inner=envelope(d.width-2*WALL,d.depth-2*WALL,d.corner-WALL,center,band)
    return outer.cut(inner).clean()


def build():
    parts=build_three_line();d=parts['dimensions'];band=LAYOUTS['selected']
    assert describe(band,d)['accepted'],'Selected band must avoid the functional joint/end regions'
    body=parts['body'];cap=parts['cap']
    # Restore exactly the rim material removed by the old front/back notches.
    # End-wall catch pockets/runouts are outside this cutter and stay untouched.
    rim=base.prism(d.width,d.depth,d.corner,d.seam,3.2).edges('<Z').fillet(.6)
    rim=rim.cut(base.prism(d.width-2*WALL,d.depth-2*WALL,d.corner-WALL,d.seam-1,5.2))
    cap=cap.union(rim.intersect(joint.grip_cut(d))).clean()
    for name,offset in (('body',band.body_center_mm),('cap',band.cap_center_mm)):
        center=d.seam+offset
        clip=base.box(0,0,center,d.width+4,d.depth+4,band.band_width_mm)
        shell=band_shell(d,center,band)
        if name=='body':body=body.cut(clip).union(shell).clean()
        else:cap=cap.cut(clip).union(shell).clean()
    result=cq.Assembly(name='three_line_wrap_grip_case')
    result.add(body,name='body')
    result.add(base.print_cap(cap,d.length),name='cap')
    return dict(parts,body=body,cap=cap,result=result,band=band)
