"""Custom coarse printed axle/nut for the unchanged indexed-wheel sample.

Not an ISO thread. Both parts need solid (100% infill) printing. The male has
no axial hole; the nut's through-hole is the intended mating interface.
"""
from math import cos, radians
import cadquery as cq
import m1_design as base

PITCH=2.4
ROOT_RADIUS=2.3
CREST_RADIUS=3.0
RADIAL_CLEARANCE=.24
AXIAL_CLEARANCE=.08  # each flank, additional to radial allowance
HEAD_HEIGHT=2.2
SHOULDER_LENGTH=2.
THREAD_START=HEAD_HEIGHT+SHOULDER_LENGTH
TIP=10.6
NUT_THICKNESS=5.2


def thread(*, clearance, flank_clearance):
    """Continuous root cylinder plus rounded-resolution trapezoidal helix."""
    root=ROOT_RADIUS+clearance;crest=CREST_RADIUS+clearance
    start=THREAD_START-2*PITCH
    height=TIP-THREAD_START+4*PITCH
    path=cq.Wire.makeHelix(PITCH,height,root,center=(0,0,start))
    profile=[(root-.12,start-.85-flank_clearance),
             (crest,start-.25-flank_clearance),
             (crest,start+.25+flank_clearance),
             (root-.12,start+.85+flank_clearance)]
    ridge=cq.Workplane('XZ').polyline(profile).close().sweep(path,isFrenet=True)
    core=cq.Workplane('XY',origin=(0,0,start-1.)).circle(root).extrude(height+2.)
    return core.union(ridge)


def printed_axle():
    body=thread(clearance=0.,flank_clearance=0.)
    body=body.intersect(base.box(0,0,(THREAD_START+TIP)/2,10,10,TIP-THREAD_START))
    lead=(cq.Workplane('XY',origin=(0,0,TIP-.7)).circle(CREST_RADIUS)
          .workplane(offset=.7).circle(ROOT_RADIUS).loft())
    body=body.intersect(base.box(0,0,(THREAD_START+TIP-.7)/2,10,10,TIP-.7-THREAD_START).union(lead))
    head=cq.Workplane('XY').polygon(6,8/cos(radians(30))).extrude(HEAD_HEIGHT)
    head=head.edges('|Z').fillet(.25)
    shoulder=cq.Workplane('XY',origin=(0,0,HEAD_HEIGHT-.05)).circle(4.).extrude(SHOULDER_LENGTH+.05)
    return head.union(shoulder).union(body).clean()


def printed_nut():
    """10 x 11 x 5.2 keyed block; axis +Z in the shared screw coordinate."""
    # Installed location matches the old nut: 5.5..10.7 from the screw head.
    block=base.box(0,0,8.1,10.,11.,NUT_THICKNESS)
    block=block.edges('|Z').fillet(.3)
    cutter=thread(clearance=RADIAL_CLEARANCE,flank_clearance=AXIAL_CLEARANCE)
    # Symmetric, open lead-ins; no blind roof or internal support is required.
    for z,ra,rb in ((5.5,3.45,ROOT_RADIUS+RADIAL_CLEARANCE),
                    (10.2,ROOT_RADIUS+RADIAL_CLEARANCE,3.45)):
        cutter=cutter.union(cq.Workplane('XY',origin=(0,0,z)).circle(ra)
                            .workplane(offset=.5).circle(rb).loft())
    return block.cut(cutter).clean()


def replacement_layout():
    a=cq.Assembly(name='coarse_printed_replacement_pair')
    a.add(printed_axle(),name='solid_coarse_axle')
    a.add(printed_nut().translate((22,0,-5.5)),name='keyed_printed_nut')
    return a
