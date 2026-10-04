"""R1 archive: 15 nominal 2 mm swatches, EXACT accepted G hood / I key 3.

One floor and a close-fitting vertical pocket, no individual clips or spring.
Higher corners/side walls contain a sparse leaning stack during desk browsing.
Print floor down: PETG, .4 nozzle/.2 layers, two walls/7% adaptive cubic.
"""
import cadquery as cq
import math
import cap_g_module_5 as g
import cap_h_module_5 as h
import recessed_grips as grips
from study import CARD_THICKNESS, UPRIGHT_WIDTH

COUNT = 15
FLOOR = 2.4
STACK_DEPTH = COUNT * CARD_THICKNESS
WIDTH_ALLOWANCE = .4  # TOTAL side-to-side play, not per side.
STACK_ALLOWANCE = .3  # TOTAL stack-direction play, not friction preload.
POCKET_WIDTH = UPRIGHT_WIDTH + WIDTH_ALLOWANCE
POCKET_DEPTH = STACK_DEPTH + STACK_ALLOWANCE
POCKET_RADIUS = .5
WALL_HEIGHT = 45.0
TOP_Z = FLOOR + WALL_HEIGHT
FUNNEL_HEIGHT = 4.0
FUNNEL_EXPANSION = 1.2  # Per side, entry only.
STRAIGHT_TOP = TOP_Z - FUNNEL_HEIGHT
OUTER_TOP_RADIUS = 1.0
SCOOP_HEIGHT = 27.0  # Minimum rim height above the floor.
SCOOP_RADIUS = 12.0
SCOOP_EDGE_RADIUS = .6

assert COUNT == 15 and CARD_THICKNESS == 2.0
assert POCKET_DEPTH + 2*FUNNEL_EXPANSION < g.BODY_DEPTH
assert POCKET_WIDTH + 2*FUNNEL_EXPANSION < g.OUTER_WIDTH


def pocket():
    lower = g.rounded_block(POCKET_WIDTH, POCKET_DEPTH,
                            STRAIGHT_TOP-FLOOR+.02, FLOOR, POCKET_RADIUS)
    lower_wire = rounded_wire(POCKET_WIDTH,POCKET_DEPTH,POCKET_RADIUS,STRAIGHT_TOP)
    upper_wire = rounded_wire(POCKET_WIDTH+2*FUNNEL_EXPANSION,
        POCKET_DEPTH+2*FUNNEL_EXPANSION,POCKET_RADIUS+FUNNEL_EXPANSION,TOP_Z)
    funnel = cq.Workplane('XY').add(lower_wire).add(upper_wire).toPending().loft()
    above = g.block(-POCKET_WIDTH/2-FUNNEL_EXPANSION,
        POCKET_WIDTH/2+FUNNEL_EXPANSION,
        -POCKET_DEPTH/2-FUNNEL_EXPANSION,
        POCKET_DEPTH/2+FUNNEL_EXPANSION, TOP_Z-.01, TOP_Z+2)
    return lower.union(funnel).union(above)


def rounded_wire(width,depth,radius,z):
    x,y,r = width/2,depth/2,radius
    return (cq.Workplane('XY',origin=(0,0,z)).moveTo(-x+r,-y)
        .lineTo(x-r,-y).radiusArc((x,-y+r),-r)
        .lineTo(x,y-r).radiusArc((x-r,y),-r)
        .lineTo(-x+r,y).radiusArc((-x,y-r),-r)
        .lineTo(-x,-y+r).radiusArc((-x+r,-y),-r).close().val())


def apply_hood_interfaces(part, include_detents=True):
    """Reuse G's actual leaves; self-supporting reliefs suit taller walls."""
    face = g.OUTER_WIDTH/2
    for y in g.detent_centres(g.COUNT):
        outer = g.block(face-g.STEM_THICKNESS, face+1.5,
            y-g.STEM_WIDTH/2-g.SIDE_RELIEF, y+g.STEM_WIDTH/2+g.SIDE_RELIEF,
            g.ROOT_Z, g.TIP_TOP_Z+.5)
        rear = g.block(face-g.STEM_THICKNESS-g.BACK_RELIEF,
            face-g.STEM_THICKNESS, y-g.STEM_WIDTH/2, y+g.STEM_WIDTH/2,
            g.ROOT_Z, g.TIP_TOP_Z+.5).edges('|Y and <Z').chamfer(g.ROOT_BLEND)
        # Grow the added ceiling outward at 45 degrees instead of roofing
        # the former open-top relief with a horizontal, trapped-support ledge.
        inner = face-g.STEM_THICKNESS-g.BACK_RELIEF
        top = g.TIP_TOP_Z+.5
        ceiling = (cq.Workplane('XZ',origin=(0,y+g.STEM_WIDTH/2+g.SIDE_RELIEF,0))
            .polyline([(inner,top-.01),(face+1.5,top-.01),
                       (face+1.5,top+face+1.5-inner)]).close()
            .extrude(g.STEM_WIDTH+2*g.SIDE_RELIEF))
        for side in (-1,1):
            part = part.cut(g.mirrored(outer,side)).cut(g.mirrored(rear,side))
            part = part.cut(g.mirrored(ceiling,side))
            for edge in (-1,1):
                lo,hi = sorted((y+edge*g.STEM_WIDTH/2,
                    y+edge*(g.STEM_WIDTH/2+g.SIDE_RELIEF)))
                part = part.cut(g.mirrored(g.block(
                    face-g.STEM_THICKNESS-g.BACK_RELIEF, face+1.5, lo,hi,
                    g.ROOT_Z,g.TIP_TOP_Z+.5),side))
            part = part.union(g.leaf(y,side,include_detents))
    return part


def scoop_tool(end=1):
    """Revolved circular tool with explicit quarter-round lips at both faces.

    The radius changes smoothly across the wall thickness. This avoids a
    post-boolean fillet where the scoop intersects the already rounded top.
    """
    r,e = SCOOP_RADIUS,SCOOP_EDGE_RADIUS
    inside,outside = POCKET_DEPTH/2,g.BODY_DEPTH/2
    d = e/math.sqrt(2)
    profile = (cq.Workplane('XY').moveTo(0,inside-1)
        .lineTo(r+e,inside-1).lineTo(r+e,inside)
        .threePointArc((r+e-d,inside+e-d),(r,inside+e))
        .lineTo(r,outside-e)
        .threePointArc((r+e-d,outside-e+d),(r+e,outside))
        .lineTo(r+e,outside+2).lineTo(0,outside+2).close())
    tool = profile.revolve(360,(0,0),(0,1)).translate(
        (0,0,FLOOR+SCOOP_HEIGHT+r+e))
    return tool if end>0 else tool.mirror('XZ')


def base(include_detents=True):
    body = (g.rounded_block(g.OUTER_WIDTH,g.BODY_DEPTH,TOP_Z,0,5.0)
        .faces('<Z').edges().chamfer(.4)
        .faces('>Z').edges().fillet(OUTER_TOP_RADIUS))
    foot = (g.rounded_block(g.FOOT_X,g.FOOT_DEPTH,g.SEAM_Z,0,g.FOOT_RADIUS)
        .faces('<Z').edges().chamfer(g.FOOT_BOTTOM_CHAMFER)
        .faces('>Z').edges().fillet(g.FOOT_TOP_ROUND))
    foot = foot.cut(g.rounded_block(g.OUTER_WIDTH-.4,g.BODY_DEPTH-.4,
        g.SEAM_Z+.2,-.1,4.8))
    body = body.union(foot).cut(grips.pocket()).cut(grips.pocket(-1))
    body = body.cut(pocket())
    # Scoops are on Y ends, leaving full-height X walls and end corners.
    # Even a middle card meets those corners when leaning front/back.
    body = body.cut(scoop_tool()).cut(scoop_tool(-1))
    body = apply_hood_interfaces(body,include_detents)
    for end in (-1,1):
        body = body.cut(h.socket(end))
        # Taller basket walls must not roof over the accepted key entry.
        cy = end*g.MODULE_PITCH/2
        reach = g.MODULE_GAP/2+h.KEY_EMBED+h.KEY_FIT_GAP
        body = body.cut(g.block(-h.KEY_HEAD_HALF_X-h.KEY_FIT_GAP,
            h.KEY_HEAD_HALF_X+h.KEY_FIT_GAP, cy-reach,cy+reach,
            g.SEAM_Z,TOP_Z+1))
    mouth = body.edges('|Z').filter(lambda e:
        abs(abs(e.Center().x)-(h.KEY_HEAD_HALF_X+h.KEY_FIT_GAP))<1e-5
        and abs(abs(e.Center().y)-g.BODY_DEPTH/2)<1e-5)
    return mouth.fillet(h.ENTRY_EDGE_ROUND)


if __name__ in ('__main__','__cqgi__'):
    result = base().translate(g.PRINT_ANCHOR)
