"""J: centered, wider card panels; unchanged H ports and G hood interfaces, mm.

Print floor down in PETG, .4 mm nozzle / .2 mm layers / two walls / 7% infill.
The wide clip contacts the swatch's plain back; engraved face points away from
it. Accepted I key 3 remains unchanged. Previous printed sources are preserved.
"""
import cadquery as cq
import card_base_test as slots
import card_base_corner_seat_5 as seats
import cap_common as common
import cap_g_module_5 as g
import cap_h_module_5 as h
from physical_analysis.screening import rectangular_cantilever

COUNT = 5
PANEL_CENTRE_X = 0.0
PANEL_WIDTH = 40.0
PANEL_THICKNESS = 1.2
CONTACT_WIDTH = 16.0
CONTACT_HEIGHT = 14.0  # From the floor; old contact was 13 mm above it.
PANEL_HEIGHT = 17.0
RAMP_START = 10.0
CONTACT_RADIUS = .25
ROOT_BLEND = .6
ROOT_Y = slots.SLOT_WIDTH/2
FREE_CONTACT_Y = .25  # Mirrored to the plain-back side; same nominal .35 squeeze.
RELIEF_BACK_Y = 3.6
RELIEF_SIDE_GAP = .8
ROOT_OVERLAP = .1

assert PANEL_CENTRE_X == 0, 'This revision promises centered card panels'
assert PANEL_WIDTH/2+RELIEF_SIDE_GAP < seats.SEAT_HALF_SPAN
assert CONTACT_WIDTH <= PANEL_WIDTH
assert RELIEF_BACK_Y-ROOT_Y-PANEL_THICKNESS >= 1.0-1e-9
assert slots.FLOOR+PANEL_HEIGHT < slots.TOP_Z


def card_panel(y):
    """One centered spring on negative Y; plain card back faces this panel."""
    x=PANEL_CENTRE_X
    stem=g.block(x-PANEL_WIDTH/2,x+PANEL_WIDTH/2,
                 y+ROOT_Y,y+ROOT_Y+PANEL_THICKNESS,
                 slots.FLOOR-ROOT_OVERLAP,slots.FLOOR+PANEL_HEIGHT)
    profile=[(ROOT_Y,slots.FLOOR+RAMP_START),
             (ROOT_Y,slots.FLOOR+PANEL_HEIGHT),
             (FREE_CONTACT_Y,slots.FLOOR+CONTACT_HEIGHT)]
    pad=(cq.Workplane('YZ',origin=(x-CONTACT_WIDTH/2,y,0))
         .polyline(profile).close().extrude(CONTACT_WIDTH))
    panel=stem.union(pad).edges(cq.selectors.NearestToPointSelector(
        (x,y+FREE_CONTACT_Y,slots.FLOOR+CONTACT_HEIGHT))).fillet(CONTACT_RADIUS)
    return panel.mirror('XZ',(0,y,0))


def seating_base(include_panels=True):
    # Reuse the original four-direction funnels and exact bottom-corner seats.
    part=slots.build_base(COUNT)
    for index in range(COUNT):
        y=slots.slot_y(index,COUNT)
        part=part.cut(g.block(-slots.INNER_WIDTH/2,slots.INNER_WIDTH/2,
            y-slots.SLOT_WIDTH/2,y+slots.SLOT_WIDTH/2,
            slots.FLOOR-seats.FLOOR_RELIEF_DEPTH,slots.FLOOR+.05))
        part=part.union(seats.corner_seat(y,-1)).union(seats.corner_seat(y,1))
        relief=g.block(PANEL_CENTRE_X-PANEL_WIDTH/2-RELIEF_SIDE_GAP,
            PANEL_CENTRE_X+PANEL_WIDTH/2+RELIEF_SIDE_GAP,
            y+ROOT_Y-.05,y+RELIEF_BACK_Y,slots.FLOOR,slots.TOP_Z+.2)
        # Rounded relief-floor transitions leave material around the root.
        relief=relief.edges('|X and <Z').fillet(ROOT_BLEND).mirror('XZ',(0,y,0))
        part=part.cut(relief)
        if include_panels:
            part=part.union(card_panel(y))
    original_envelope=(g.rounded_block(g.OUTER_WIDTH,slots.outer_depth(COUNT),g.TOP_Z,
                                     0,common.BASE_CORNER)
                       .faces('<Z').edges().chamfer(.4)
                       .faces('>Z').edges().fillet(common.BASE_RIM_RADIUS))
    part=part.intersect(original_envelope)
    envelope=(g.rounded_block(g.OUTER_WIDTH,g.BODY_DEPTH,g.TOP_Z,0,5.0)
              .faces('>Z').edges().fillet(1.0))
    return part.intersect(envelope)


def base(include_panels=True,include_detents=True):
    """Complete five-card base; unchanged foot, hood leaves and H sockets."""
    body=seating_base(include_panels)
    foot=(g.rounded_block(g.FOOT_X,g.FOOT_DEPTH,g.SEAM_Z,0,g.FOOT_RADIUS)
          .faces('<Z').edges().chamfer(g.FOOT_BOTTOM_CHAMFER)
          .faces('>Z').edges().fillet(g.FOOT_TOP_ROUND))
    grip=(cq.Workplane('XZ',origin=(0,9,0))
          .polyline([(g.FOOT_X/2-2,-.1),(g.FOOT_X/2-2,1),
                     (g.FOOT_X/2+.5,3.5),(g.FOOT_X/2+2,3.5),(g.FOOT_X/2+2,-.1)])
          .close().extrude(18).edges('|Y').fillet(.35))
    foot=foot.cut(grip).cut(grip.mirror('YZ'))
    foot=foot.cut(g.rounded_block(g.OUTER_WIDTH-.4,g.BODY_DEPTH-.4,g.SEAM_Z+.2,-.1,4.8))
    body=body.union(foot)
    face=g.OUTER_WIDTH/2
    for y in g.detent_centres(COUNT):
        outer=g.block(face-g.STEM_THICKNESS,face+1.5,y-g.STEM_WIDTH/2-g.SIDE_RELIEF,
            y+g.STEM_WIDTH/2+g.SIDE_RELIEF,g.ROOT_Z,g.TIP_TOP_Z+.5)
        rear=g.block(face-g.STEM_THICKNESS-g.BACK_RELIEF,face-g.STEM_THICKNESS,
            y-g.STEM_WIDTH/2,y+g.STEM_WIDTH/2,g.ROOT_Z,g.TIP_TOP_Z+.5)
        rear=rear.edges('|Y and <Z').fillet(g.ROOT_BLEND)
        for side in (-1,1):
            body=body.cut(g.mirrored(outer,side)).cut(g.mirrored(rear,side))
            for edge in (-1,1):
                lo,hi=sorted((y+edge*g.STEM_WIDTH/2,
                             y+edge*(g.STEM_WIDTH/2+g.SIDE_RELIEF)))
                body=body.cut(g.mirrored(g.block(face-g.STEM_THICKNESS-g.BACK_RELIEF,
                    face+1.5,lo,hi,g.ROOT_Z,g.TIP_TOP_Z+.5),side))
            body=body.union(g.leaf(y,side,include_detents))
    body=body.cut(h.socket(1)).cut(h.socket(-1))
    mouth=body.edges('|Z').filter(lambda e:
        abs(abs(e.Center().x)-(h.KEY_HEAD_HALF_X+h.KEY_FIT_GAP))<1e-5
        and abs(abs(e.Center().y)-g.BODY_DEPTH/2)<1e-5)
    if len(mouth.vals())!=4:
        raise ValueError('Expected four H mouth edges for rounding')
    return mouth.fillet(h.ENTRY_EDGE_ROUND)


def grip_screen(thickness=2.0,modulus=1200):
    travel=thickness-slots.SLOT_WIDTH/2-FREE_CONTACT_Y
    # Conservative effective length accounts for the root blend. Uniform-width
    # bending is an explicit short-term idealization, not a plate/creep solve.
    return rectangular_cantilever(length_mm=CONTACT_HEIGHT-ROOT_BLEND,
        width_mm=PANEL_WIDTH,thickness_mm=PANEL_THICKNESS,
        youngs_modulus_MPa=modulus,tip_displacement_mm=travel)


if __name__ in ('__main__','__cqgi__'):
    result=base().translate(g.PRINT_ANCHOR)
