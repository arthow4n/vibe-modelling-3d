"""Matte-PLA repair: thicker cap and printable male flank; existing shells fit."""
import cadquery as cq
from math import cos,radians
import m1_design as base
from rotary_covered_design import covered_case,KEY_X,KEY_ENGAGEMENT,KEY_WIDTH,KEY_HEIGHT
from rotary_printed_fastener_design import ROOT_RADIUS,CREST_RADIUS,PITCH,THREAD_START,TIP,printed_nut
from rotary_conical_design import HEAD_RADIUS,JOURNAL_RADIUS,HEAD_DEPTH,SOCKET_AF,SOCKET_DEPTH,SOCKET_ROOF

FACE=2.
WALL=2.
GAP=.4
RADIAL_CLEARANCE=.6
OUTLINE_OFFSET=WALL+RADIAL_CLEARANCE
EXTENSION=.3+GAP+FACE
SOCKET_ROOF_TOP=.8  # printable short closing bridge, replacing the 0.04mm face
CREST_WIDTH=.6
LOWER_FLANK=CREST_RADIUS-(ROOT_RADIUS-.1)  # 45 degrees on the rising print flank
UPPER_FLANK=.6
TIP_RADIUS=ROOT_RADIUS+.05  # avoid a tangential thread/cone termination


def outline(*,offset):
    """Build circular scallops directly, avoiding fragile offset-curve surfaces.

    Radii grow/shrink by the offset. Small junctions retain a 0.6mm fillet
    instead of reproducing the old offset fillet patches.
    """
    blank=cq.Workplane('XY').circle(17.+offset).extrude(1.)
    for x in (-20.5,20.5):
        blank=blank.cut(cq.Workplane('XY',origin=(x,0,-.1)).circle(6.5-offset).extrude(1.2))
    blank=blank.edges('|Z').fillet(.6)
    wire=blank.faces('>Z').val().outerWire().translate((0,0,-1.))
    return cq.Workplane('XY').add(wire).toPending()


def printed_axle():
    start=THREAD_START-2*PITCH;length=TIP-THREAD_START+4*PITCH
    path=cq.Wire.makeHelix(PITCH,length,ROOT_RADIUS,center=(0,0,start))
    profile=[(ROOT_RADIUS-.1,start-CREST_WIDTH/2-LOWER_FLANK),
             (CREST_RADIUS,start-CREST_WIDTH/2),(CREST_RADIUS,start+CREST_WIDTH/2),
             (ROOT_RADIUS-.1,start+CREST_WIDTH/2+UPPER_FLANK)]
    ridge=cq.Workplane('XZ').polyline(profile).close().sweep(path,isFrenet=True)
    core=cq.Workplane('XY',origin=(0,0,start-1.)).circle(ROOT_RADIUS).extrude(length+2.)
    thread=core.union(ridge).intersect(base.box(0,0,(THREAD_START+TIP)/2,10,10,TIP-THREAD_START))
    lead=(cq.Workplane('XY',origin=(0,0,TIP-.7)).circle(CREST_RADIUS+.1)
          .workplane(offset=.7).circle(TIP_RADIUS).loft(ruled=True))
    thread=thread.intersect(base.box(0,0,(THREAD_START+TIP-.7)/2,10,10,TIP-.7-THREAD_START).union(lead))
    head=(cq.Workplane('XY',origin=(0,0,-EXTENSION)).circle(HEAD_RADIUS)
          .workplane(offset=HEAD_DEPTH).circle(JOURNAL_RADIUS).loft(ruled=True))
    neck=(cq.Workplane('XY',origin=(0,0,HEAD_DEPTH-EXTENSION-.05))
          .circle(JOURNAL_RADIUS).extrude(THREAD_START-HEAD_DEPTH+EXTENSION+.05))
    socket=(cq.Workplane('XY',origin=(0,0,-EXTENSION-.01))
            .polygon(6,SOCKET_AF/cos(radians(30))).extrude(SOCKET_DEPTH+.01))
    roof=(cq.Workplane('XY',origin=(0,0,SOCKET_DEPTH-EXTENSION))
          .polygon(6,SOCKET_AF/cos(radians(30))).workplane(offset=SOCKET_ROOF)
          .polygon(6,SOCKET_ROOF_TOP).loft(ruled=True))
    return head.union(neck).union(thread).cut(socket.union(roof)).clean()


def screw_print_pose(part):
    return part.translate((0,0,EXTENSION))


def matte_case():
    p=covered_case();d=p['dimensions'];back=d.wheel_front+GAP;front=back+FACE
    depth=front-d.wheel_back
    cup=outline(offset=OUTLINE_OFFSET).extrude(depth)
    cavity=outline(offset=RADIAL_CLEARANCE).extrude(depth).translate((0,0,FACE))
    # Plain substantial front/rear sections avoid the old sliver roundovers.
    cup=cup.cut(cavity)
    recess=cq.Workplane(obj=cq.Solid.makeCone(HEAD_RADIUS+.2,JOURNAL_RADIUS+.2,
        HEAD_DEPTH,cq.Vector(0,0,0),cq.Vector(0,0,1)))
    cup=cup.cut(recess)
    ring=cq.Workplane('XY',origin=(0,0,FACE)).circle(8.6).circle(6.4).extrude(GAP)
    cover=cup.union(ring).clean();without_keys=cover
    keys=[]
    for x in (-KEY_X,KEY_X):
        k=(cq.Workplane('XY',origin=(x,0,FACE)).rect(KEY_WIDTH,KEY_HEIGHT)
            .extrude(GAP+KEY_ENGAGEMENT).edges('|Z').fillet(.2))
        cover=cover.union(k).clean();keys.append(k)
    def installed(part):
        return part.rotate((0,0,0),(1,0,0),90).translate((0,front,d.pivot)).mirror('XZ')
    axle=printed_axle().rotate((0,0,0),(1,0,0),90).translate((0,d.axle_front,d.pivot)).mirror('XZ')
    return dict(p,facecap=installed(cover),facecap_without_keys=installed(without_keys),
                facecap_print=cover,drive_keys=[installed(k) for k in keys],pivot_axle=axle,control_front=front)


def cover_print_pose(part,p):
    # The canonical print geometry avoids an unnecessary inverse placement.
    if part is not p['facecap']:raise ValueError('Expected the matte facecap')
    return p['facecap_print']


def repair_layout(p):
    # Heal orientation after placement; actual STEP reimport is checked separately.
    return (cq.Assembly(name='matte_PLA_cap_and_screw_repair')
        .add(cq.Workplane(obj=cover_print_pose(p['facecap'],p).val().translate((60,60,0)).fix()),name='thicker_wheel_cap')
        .add(screw_print_pose(printed_axle()).translate((100,60,0)),name='matching_solid_screw'))
