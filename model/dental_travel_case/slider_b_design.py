"""B1 three-piece sliding-yoke mechanism coupon; dimensions in millimetres.

Assembly Z is opening direction. Yoke travels along X: 0 unlock, -10 lock.
No production case builder is modified. Geometry construction has no exports.
"""
from dataclasses import dataclass
import cadquery as cq
import m1_design as base


@dataclass(frozen=True)
class Dimensions:
    width: float = 75.8
    depth: float = 52.8
    seam: float = 12.
    sleeve_top: float = 34.
    cap_top: float = 42.
    reveal: float = 3.
    guide_clearance: float = .3  # per side, not a diametral allowance
    travel: float = 10.
    lug_width: float = 8.
    exit_width: float = 9.4
    lug_bottom: float = 27.
    gate_top: float = 26.7
    yoke_bottom: float = 15.7
    yoke_top: float = 34.
    arm_inner: float = 26.65
    arm_outer: float = 32.2
    peg_x: float = 18.
    detent_x: float = -18.


D = Dimensions()


def yz_prism(points, start, length):
    return cq.Workplane('YZ', origin=(start, 0, 0)).polyline(points).close().extrude(length)


def paired(part):
    return part.union(part.mirror('XZ'))


def build():
    d = D
    sleeve_w, sleeve_h = 71.2, 48.2
    inner_w = sleeve_w + 2*d.guide_clearance
    inner_h = sleeve_h + 2*d.guide_clearance
    body = base.prism(d.width, d.depth, 6., 0., d.seam).edges('>Z').chamfer(2.2)
    body = body.union(base.prism(sleeve_w, sleeve_h, 4., d.seam-.5,
                                 d.sleeve_top-d.seam+.5))
    cavity = cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (-1.,71.8,48.8,4.),(6.,71.8,48.8,4.),
            (d.seam,67.2,44.2,2.),(d.sleeve_top+1,67.2,44.2,2.))],ruled=True))
    body = body.cut(cavity)
    # Flat underside retains. Sloping top makes the inverted print self-supporting.
    lug = yz_prism([(23.8,d.lug_bottom),(29.8,d.lug_bottom),
                    (24.1,32.7),(23.8,32.7)],-d.lug_width/2,d.lug_width)
    body = body.union(paired(lug)).clean()

    rim = d.seam+d.reveal
    cap = base.prism(d.width,d.depth,6.,rim,d.cap_top-rim)
    lower = base.prism(inner_w,inner_h,4.3,rim-1,d.sleeve_top-rim+1)
    upper = cq.Workplane(obj=cq.Solid.makeLoft([
        base.rounded_wire(w,h,r,z) for z,w,h,r in (
            (d.sleeve_top,inner_w-2,inner_h-2,3.3),
            (d.sleeve_top+1.5,inner_w,inner_h,4.3),
            (d.cap_top+1,inner_w,inner_h,4.3))],ruled=True))
    cap = cap.cut(lower.union(upper))
    rail = yz_prism([(26.2,16.5),(28.9,19.5),(28.9,21.5),(26.2,24.5)],-32.,64.)
    cap = cap.union(paired(rail))
    opening = base.box(0,29.,(rim-1+33.2)/2,d.exit_width,14.,33.2-rim+1)
    cap = cap.cut(paired(opening))
    # One-time assembly pegs enter closed travel slots in the yoke arms.
    peg = yz_prism([(26.2,20.1),(31.,20.1),(26.2,24.9)],d.peg_x-1,2.)
    cap = cap.union(paired(peg))
    detent = cq.Workplane('XY').sphere(1.).translate((d.detent_x,28.4,21.4))
    nose = base.box(-38.4,0,23.,2.,16.,8.)
    cap_guide = cap.union(nose).clean()
    cap = cap_guide.union(paired(detent)).clean()

    # A U around the left end; all rails remain outside the contents passage.
    left, right = -43.1, 38.4
    zc = (d.yoke_bottom+d.yoke_top)/2
    arm = base.box((left+right)/2,(d.arm_inner+d.arm_outer)/2,zc,
                   right-left,d.arm_outer-d.arm_inner,d.yoke_top-d.yoke_bottom)
    yoke = paired(arm).union(base.box(-41.4,0,zc,3.4,2*d.arm_outer,
                                     d.yoke_top-d.yoke_bottom))
    yoke = yoke.edges('|Z').fillet(.5)
    channel = yz_prism([(26.35,16.2),(29.2,19.2),(29.2,21.8),(26.35,24.8)],left-1,right-left+2)
    yoke = yoke.cut(paired(channel))
    # Horizontal lug tunnel with a 45-degree roof, not a long unsupported bridge.
    tunnel = yz_prism([(26.4,d.gate_top),(30.1,d.gate_top),
                       (30.1,27.2),(26.4,30.9)],-20.,40.)
    yoke = yoke.cut(paired(tunnel))
    # Open notch behind a 1.8 mm outer backing, not a roofed through-window.
    # Lug tip is Y29.8; Y30.4 clearance also allows the checked guide play.
    exit_cut = base.box(0,(26.3+30.4)/2,(d.yoke_bottom+d.yoke_top)/2,
                        d.exit_width,30.4-26.3,d.yoke_top-d.yoke_bottom+2)
    yoke = yoke.cut(paired(exit_cut))
    # Closed-end travel slot: peg fixes the operating range at -10.3 to +0.3.
    # Gabled roof closes at 45 degrees rather than bridging the 12.6 mm slot.
    travel_slot = (cq.Workplane('XZ').polyline([(16.7,19.8),(29.3,19.8),
                   (29.3,24.9),(23.,31.2),(16.7,24.9)]).close().extrude(70.,both=True))
    yoke = yoke.cut(travel_slot)
    for x in (d.detent_x,d.detent_x+d.travel):
        recess = cq.Workplane('XY').sphere(1.3).translate((x,28.4,21.4))
        yoke = yoke.cut(paired(recess))
    # Small inspection holes expose the two lugs in LOCK without removing the tunnel roof.
    peephole = cq.Workplane('XZ').center(10.,28.6).circle(1.2).extrude(70.,both=True)
    yoke = yoke.cut(peephole).clean()
    return dict(body=body, cap=cap, cap_guide=cap_guide, yoke=yoke, lug=paired(lug),
                detent=paired(detent), dimensions=d)


def configuration(parts, state):
    if state not in ('print','locked','unlocked','open'):
        raise ValueError('Unknown B1 configuration: '+str(state))
    d = parts['dimensions']
    out = cq.Assembly(name='B1_'+state)
    if state == 'print':
        out.add(parts['body'].rotate((0,0,0),(1,0,0),180).translate((0,0,d.sleeve_top)),name='body',color=cq.Color(.4,.65,.8))
        out.add(parts['cap'].rotate((0,0,0),(1,0,0),180).translate((100,0,d.cap_top)),name='cap',color=cq.Color(.9,.7,.4))
        out.add(parts['yoke'].translate((50,80,-d.yoke_bottom)),name='yoke',color=cq.Color(.35,.7,.5))
    else:
        shift = -d.travel if state == 'locked' else 0.
        lift = 28. if state == 'open' else 0.
        out.add(parts['body'],name='body',color=cq.Color(.4,.65,.8))
        out.add(parts['cap'].translate((0,0,lift)),name='cap',color=cq.Color(.9,.7,.4))
        out.add(parts['yoke'].translate((shift,0,lift)),name='yoke',color=cq.Color(.35,.7,.5))
    return out
